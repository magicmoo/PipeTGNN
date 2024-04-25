import argparse
from distutils.dep_util import newer_group
import logging
import math
import os
import random
import threading
import time
import sys
from venv import create
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path)

import GPUtil

import numpy as np
import torch
import torch.distributed as dist
import torch.nn
import torch.nn.parallel
import torch.utils.data
from sklearn.metrics import average_precision_score, roc_auc_score
from torch.utils.data import BatchSampler, SequentialSampler
from tqdm import tqdm
from torch.multiprocessing import Process, Queue
from dgl.utils.shared_mem import create_shared_mem_array, get_shared_mem_array
import torch.multiprocessing as mp

import gnnflow.cache as caches
from config import get_default_config
from gnnflow.data import (EdgePredictionDataset,
                          RandomStartBatchSampler, default_collate_ndarray)
from modules.tgnn import TGNN
from modules.sampler import DistributedBatchSampler
from gnnflow.models.dgnn import DGNN
from gnnflow.models.gat import GAT
from gnnflow.models.graphsage import SAGE
from gnnflow.temporal_sampler import TemporalSampler
from gnnflow.utils import (DstRandEdgeSampler, EarlyStopMonitor,
                           build_dynamic_graph, get_pinned_buffers,
                           get_project_root_dir, load_dataset, load_feat,
                           mfgs_to_cuda)

datasets = ['REDDIT', 'GDELT', 'LASTFM', 'MAG', 'MOOC', 'WIKI']
model_names = ['TGNN']
cache_names = sorted(name for name in caches.__dict__
                     if not name.startswith("__")
                     and callable(caches.__dict__[name]))

parser = argparse.ArgumentParser()
parser.add_argument("--model", choices=model_names, default='TGNN',
                    help="model architecture" + '|'.join(model_names))
parser.add_argument("--data", choices=datasets, default='REDDIT',
                    help="dataset:" + '|'.join(datasets))
parser.add_argument("--epoch", help="maximum training epoch",
                    type=int, default=50)
parser.add_argument("--lr", help='learning rate', type=float, default=0.0001)
parser.add_argument("--num-workers", help="num workers for dataloaders",
                    type=int, default=1)
parser.add_argument("--num-chunks", help="number of chunks for batch sampler",
                    type=int, default=1)
parser.add_argument("--print-freq", help="print frequency",
                    type=int, default=100)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--ingestion-batch-size", type=int, default=10000000,
                    help="ingestion batch size")
parser.add_argument("--edge-cache-ratio", type=float, default=0,
                    help="cache ratio for edge feature cache")
parser.add_argument("--node-cache-ratio", type=float, default=0,
                    help="cache ratio for node feature cache")
parser.add_argument("--snapshot-time-window", type=float, default=0,
                    help="time window for sampling")
parser.add_argument("--cache", choices=cache_names, default='LRUCache', help="feature cache:" +
                    '|'.join(cache_names))

args = parser.parse_args()
logging.basicConfig(level=logging.DEBUG)
logging.info(args)

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


set_seed(args.seed)


def evaluate(dataloader, sampler, model, criterion, cache, device, groups):
    dist.barrier()
    model.eval()
    val_losses = list()
    aps = list()
    aucs_mrrs = list()

    sign = True
    flag = False
    iteration_now = args.rank
    sends_thread = None
    with torch.no_grad():
        total_loss = 0
        for target_nodes, ts, eid in dataloader:
            mfgs = sampler.sample(target_nodes, ts)
            mfgs_to_cuda(mfgs, device)
            mfgs = cache.fetch_feature(
                mfgs, eid)

            update_length = mfgs[-1][0].num_dst_nodes() * 2 // 3
            
            if sends_thread != None:
               sends_thread.join() 
            if args.rank!=0 or flag:
                src = (args.rank-1+args.world_size)%args.world_size
                idx = src
                recv(None, src, groups[idx])

            if args.use_memory:
                b = mfgs[0][0]
                updated_memory = model.update_memory_and_mail(b, update_length, edge_feats=cache.target_edge_features)

            if iteration_now+1 != int(len(dataloader)):
                dst = (args.rank+1)%args.world_size
                idx = args.rank
                sends_thread = threading.Thread(target=send, args=(None, dst, groups[idx]))
                sends_thread.start()
            iteration_now += args.world_size
            flag = True
            
            if args.use_memory:
                b = mfgs[0][0]
                input = model.memory.prepare_input(b, update_length)
                model.get_updated_memory(b, updated_memory, **input)

            pred_pos, pred_neg = model(mfgs)

            total_loss += criterion(pred_pos, torch.ones_like(pred_pos))
            total_loss += criterion(pred_neg, torch.zeros_like(pred_neg))
            y_pred = torch.cat([pred_pos, pred_neg], dim=0).sigmoid().cpu()
            y_true = torch.cat(
                [torch.ones(pred_pos.size(0)),
                 torch.zeros(pred_neg.size(0))], dim=0)
            aucs_mrrs.append(roc_auc_score(y_true, y_pred))
            aps.append(average_precision_score(y_true, y_pred))

        val_losses.append(float(total_loss))

    ap = float(torch.tensor(aps).mean())
    auc_mrr = float(torch.tensor(aucs_mrrs).mean())
    return ap, auc_mrr

def main():

    args.distributed = True
    args.local_rank = int(os.environ['LOCAL_RANK'])
    args.local_world_size = int(os.environ['LOCAL_WORLD_SIZE'])
    torch.cuda.set_device(args.local_rank)
    dist.init_process_group('nccl')
    args.rank = torch.distributed.get_rank()
    args.world_size = torch.distributed.get_world_size()

    logging.info("rank: {}, world_size: {}".format(args.rank, args.world_size))

    model_config, data_config = get_default_config(args.model, args.data)
    if model_config["snapshot_time_window"] > 0 and args.data == "GDELT":
        model_config["snapshot_time_window"] = 25
    else:
        model_config["snapshot_time_window"] = args.snapshot_time_window
    logging.info("snapshot_time_window's value is {}".format(model_config["snapshot_time_window"]))
    args.use_memory = model_config['use_memory']

    # graph is stored in shared memory
    data_config["mem_resource_type"] = "shared"

    data_path = os.path.join(path, 'data')
    train_data, val_data, test_data, full_data = load_dataset(args.data, data_path)
    train_rand_sampler = DstRandEdgeSampler(
        train_data['dst'].to_numpy(dtype=np.int32))
    val_rand_sampler = DstRandEdgeSampler(
        full_data['dst'].to_numpy(dtype=np.int32))
    test_rand_sampler = DstRandEdgeSampler(
        full_data['dst'].to_numpy(dtype=np.int32))

    train_ds = EdgePredictionDataset(train_data, train_rand_sampler)
    val_ds = EdgePredictionDataset(val_data, val_rand_sampler)
    test_ds = EdgePredictionDataset(test_data, test_rand_sampler)
    batch_size = model_config['batch_size']
    # NB: learning rate is scaled by the number of workers
    args.lr = args.lr * math.sqrt(args.world_size)
    logging.info("batch size: {}, lr: {}".format(batch_size, args.lr))

    train_sampler = DistributedBatchSampler(
        SequentialSampler(train_ds), batch_size=batch_size,
        drop_last=False, rank=args.rank, world_size=args.world_size,
        num_chunks=args.num_chunks)
    val_sampler = DistributedBatchSampler(
        SequentialSampler(val_ds),
        batch_size=batch_size, drop_last=False, rank=args.rank,
        world_size=args.world_size)
    test_sampler = DistributedBatchSampler(
        SequentialSampler(test_ds),
        batch_size=batch_size, drop_last=False, rank=args.rank,
        world_size=args.world_size)

    train_loader = torch.utils.data.DataLoader(
        train_ds, sampler=train_sampler,
        collate_fn=default_collate_ndarray, num_workers=args.num_workers)
    val_loader = torch.utils.data.DataLoader(
        val_ds, sampler=val_sampler,
        collate_fn=default_collate_ndarray, num_workers=args.num_workers)
    test_loader = torch.utils.data.DataLoader(
        test_ds, sampler=test_sampler,  
        collate_fn=default_collate_ndarray, num_workers=args.num_workers)

    dgraph = build_dynamic_graph(
        **data_config, device=args.local_rank)

    torch.distributed.barrier()
    # insert in batch
    for i in tqdm(range(0, len(full_data), args.ingestion_batch_size)):
        batch = full_data[i:i + args.ingestion_batch_size]
        src_nodes = batch["src"].values.astype(np.int64)
        dst_nodes = batch["dst"].values.astype(np.int64)
        timestamps = batch["time"].values.astype(np.float32)
        eids = batch["eid"].values.astype(np.int64)
        dgraph.add_edges(src_nodes, dst_nodes, timestamps,
                         eids, add_reverse=False)
        torch.distributed.barrier()

    num_nodes = dgraph.max_vertex_id() + 1
    num_edges = dgraph.num_edges()
    # put the features in shared memory when using distributed training
    node_feats, edge_feats = load_feat(
        args.data, data_dir=data_path, shared_memory=args.distributed,
        local_rank=args.local_rank, local_world_size=args.local_world_size)

    dim_node = 0 if node_feats is None else node_feats.shape[1]
    dim_edge = 0 if edge_feats is None else edge_feats.shape[1]

    device = torch.device('cuda:{}'.format(args.local_rank))
    logging.debug("device: {}".format(device))

    model = TGNN(dim_node, dim_edge, **model_config, num_nodes=num_nodes,
                    memory_device=device, memory_shared=args.distributed)
    model.to(device)

    model_data = []
    i = 0
    if args.local_rank == 0:
        for param in model.parameters():
            data = create_shared_mem_array('data'+str(i), param.data.shape, param.data.dtype)
            model_data.append(data)
            i += 1
        dist.barrier()
        push_model(model, model_data)
    else:
        dist.barrier()
        for param in model.parameters():
            data = get_shared_mem_array('data'+str(i), param.data.shape, param.data.dtype)
            model_data.append(data)
            i += 1
    

    sampler = TemporalSampler(dgraph, **model_config)

    # model = torch.nn.parallel.DistributedDataParallel(
    #     model, device_ids=[args.local_rank], find_unused_parameters=False)

    pinned_nfeat_buffs, pinned_efeat_buffs = get_pinned_buffers(
        model_config['fanouts'], model_config['num_snapshots'], batch_size,
        dim_node, dim_edge)

    # Cache
    cache = caches.__dict__[args.cache](args.edge_cache_ratio, args.node_cache_ratio,
                                        num_nodes, num_edges, device,
                                        node_feats, edge_feats,
                                        dim_node, dim_edge,
                                        pinned_nfeat_buffs, 
                                        pinned_efeat_buffs,
                                        None,
                                        False)

    # only gnnlab static need to pass param
    if args.cache == 'GNNLabStaticCache':
        cache.init_cache(sampler=sampler, train_df=train_data,
                         pre_sampling_rounds=2)
    else:
        cache.init_cache()

    logging.info("cache mem size: {:.2f} MB".format(
        cache.get_mem_size() / 1000 / 1000))

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = torch.nn.BCEWithLogitsLoss()

    best_e = train(train_loader, val_loader, sampler,
                   model, optimizer, criterion, cache, device, model_data)

    logging.info('Loading model at epoch {}...'.format(best_e))

    # ap, auc = evaluate(test_loader, sampler, model,
    #                    criterion, cache, device)
    
    # metrics = torch.tensor([ap, auc], device=device)
    # torch.distributed.all_reduce(metrics)
    # metrics /= args.world_size
    # ap, auc = metrics.tolist()
    # if args.rank == 0:
    #     logging.info('Test ap:{:4f}  test auc:{:4f}'.format(ap, auc))

    torch.distributed.barrier()


def train(train_loader, val_loader, sampler, model, optimizer, criterion,
          cache, device, model_data):
    best_ap = 0
    best_e = 0
    epoch_time_sum = 0
    early_stopper = EarlyStopMonitor()

    next_data = None

    def sampling(target_nodes, ts, eid):
        nonlocal next_data
        mfgs = sampler.sample(target_nodes, ts)
        next_data = (mfgs, eid)

    logging.info('Start training...')
    torch.distributed.barrier()

    groups = []
    auc_list, tb_list = [0], [0]
    for i in range(args.world_size):
        g = dist.new_group([i, (i+1)%args.world_size])
        groups.append(g)
    for i in range(args.world_size):
        g = dist.new_group([i, (i+1)%args.world_size])
        groups.append(g)
    for e in range(args.epoch):
        model.train()
        cache.reset()
        if e > 0:
            model.reset()
        total_loss = 0
        cache_edge_ratio_sum = 0
        cache_node_ratio_sum = 0
        total_sampling_time = 0
        total_feature_fetch_time = 0
        total_memory_update_time = 0
        total_memory_write_back_time = 0
        total_model_train_time = 0
        total_model_update_time = 0
        total_samples = 0

        epoch_time_start = time.time()

        train_iter = iter(train_loader)
        target_nodes, ts, eid = next(train_iter)
        mfgs = sampler.sample(target_nodes, ts)
        next_data = (mfgs, eid)

        sampling_thread = None
        flag = False
        iteration_now = args.rank   

        i = 0 
        
        global tb
        tb = time.perf_counter()
        sends_thread1 = None
        sends_thread2 = None

        ttt = 0
        
        while True:
            sample_start_time = time.perf_counter()
            if sampling_thread is not None:
                sampling_thread.join()

            mfgs, eid = next_data
            num_target_nodes = len(eid) * 3

            # Sampling for next batch
            try:
                next_target_nodes, next_ts, next_eid = next(train_iter)
            except StopIteration:
                break
            sampling_thread = threading.Thread(target=sampling, args=(
                next_target_nodes, next_ts, next_eid))
            sampling_thread.start()
            total_sampling_time += time.perf_counter() - sample_start_time

            # Feature
            feature_start_time = time.perf_counter()
            mfgs_to_cuda(mfgs, device)
            mfgs = cache.fetch_feature(
                mfgs, eid)
            total_feature_fetch_time += time.perf_counter() - feature_start_time

            update_length = mfgs[-1][0].num_dst_nodes() * 2 // 3

            memory_update_start_time = time.perf_counter()
            
            tmp = time.perf_counter()

            if sends_thread1 != None:
               sends_thread1.join() 
            if args.rank!=0 or flag:
                src = (args.rank-1+args.world_size)%args.world_size
                idx = src
                recv(None, src, groups[idx])
                
            ttt += time.perf_counter() - tmp

            if args.use_memory:
                b = mfgs[0][0]
                updated_memory = model.update_memory_and_mail(b, update_length, edge_feats=cache.target_edge_features)

            if iteration_now+1+args.world_size != int(len(train_loader)):
                dst = (args.rank+1)%args.world_size
                idx = args.rank
                sends_thread1 = threading.Thread(target=send, args=(None, dst, groups[idx]))
                sends_thread1.start()

            total_memory_update_time += time.perf_counter() - memory_update_start_time
            
            model_train_start_time = time.perf_counter()
            if args.use_memory:
                b = mfgs[0][0]
                input = model.memory.prepare_input(b, update_length)
                model.get_updated_memory(b, updated_memory, **input)
            # Train
            optimizer.zero_grad()
            pred_pos, pred_neg = model(mfgs)
            loss = criterion(pred_pos, torch.ones_like(pred_pos))
            loss += criterion(pred_neg, torch.zeros_like(pred_neg))
            total_loss += float(loss) * num_target_nodes
            loss.backward()

            total_model_train_time += time.perf_counter() - model_train_start_time
            model_update_start_time = time.perf_counter()

            # transfer
            tmp = time.perf_counter()
            if sends_thread2 != None:
               sends_thread2.join() 
            if args.rank!=0 or flag:
                src = (args.rank-1+args.world_size)%args.world_size
                idx = src + args.world_size
                # params = [param.data for param in model.parameters()]
                recv(None, src, groups[idx])
            flag = True
            ttt += time.perf_counter() - tmp
            pull_model(model, model_data)

            # update the model
            optimizer.step()

            push_model(model, model_data)

            total_model_update_time += time.perf_counter() - model_update_start_time

            if iteration_now+1+args.world_size != int(len(train_loader)):
                dst = (args.rank+1)%args.world_size
                idx = args.rank + args.world_size
                # params = [param.data.clone() for param in model.parameters()]
                sends_thread2 = threading.Thread(target=send, args=(None, dst, groups[idx]))
                sends_thread2.start()
            else:
                push_model(model, model_data)
            iteration_now += args.world_size

            cache_edge_ratio_sum += cache.cache_edge_ratio
            cache_node_ratio_sum += cache.cache_node_ratio
            # total_samples += num_target_nodes
            i += 1

        epoch_time = time.time() - epoch_time_start
        epoch_time_sum += epoch_time
        # Validation
        val_start = time.time()
        val_ap, val_auc = evaluate(
            val_loader, sampler, model, criterion, cache, device, groups)

        val_res = torch.tensor([val_ap, val_auc]).to(device)
        torch.distributed.all_reduce(val_res)
        val_res /= args.world_size
        val_ap, val_auc = val_res[0].item(), val_res[1].item()

        val_end = time.time()
        val_time = val_end - val_start

        metrics = torch.tensor([val_ap, val_auc, cache_edge_ratio_sum,
                                cache_node_ratio_sum, total_samples,
                                total_sampling_time, total_feature_fetch_time,
                                total_memory_update_time,
                                total_memory_write_back_time,
                                total_model_train_time,
                                total_model_update_time]).to(device)
        torch.distributed.all_reduce(metrics)
        metrics /= args.world_size
        val_ap, val_auc, cache_edge_ratio_sum, cache_node_ratio_sum, \
            total_samples, total_sampling_time, total_feature_fetch_time, \
            total_memory_update_time, total_memory_write_back_time, \
            total_model_train_time, total_model_update_time = metrics.tolist()

        if args.rank == 0:
            logging.info("Epoch {:d}/{:d} | Validation ap {:.4f} | Validation auc {:.4f} | Train time {:.2f} s | Validation time {:.2f} s | Train Throughput {:.2f} samples/s | Cache node ratio {:.4f} | Cache edge ratio {:.4f} | Total Sampling Time {:.2f}s | Total Feature Fetching Time {:.2f}s | Total Memory Update Time {:.2f}s | Total Model Train Time {:.2f}s | Total Model Update Time {:.2f}s".format(

                e + 1, args.epoch, val_ap, val_auc, epoch_time, val_time, total_samples * args.world_size / epoch_time, cache_node_ratio_sum / (i + 1), cache_edge_ratio_sum / (i + 1), total_sampling_time, total_feature_fetch_time, total_memory_update_time, total_model_train_time, total_model_update_time))
            print(ttt)
            auc_list.append(val_auc)
            tb_list.append(epoch_time+tb_list[-1])
        if args.rank == 0 and val_ap > best_ap:
            best_e = e + 1
            best_ap = val_ap
            logging.info(
                "Best val AP: {:.4f} & val AUC: {:.4f}".format(val_ap, val_auc))

    if args.rank == 0:
        logging.info('Avg epoch time: {}'.format(epoch_time_sum / args.epoch))
        print(auc_list)
        print(tb_list)

    torch.distributed.barrier()

    return best_e

tb = 0

def push_model(model, model_data):
    i = 0
    for param in model.parameters():
        model_data[i][:] = param.data.clone()[:].to('cpu')
        i += 1

def pull_model(model, model_data):
    i = 0
    for param in model.parameters():
        param.data[:] = model_data[i][:].to(f'cuda:{args.local_rank}')
        i += 1

def send(tensors: list, target: int, group: object = None):
    
    if tensors == None:
        tensor = torch.tensor([args.local_rank]).to(f'cuda:{args.local_rank}')
        # print(f'send1: {args.rank} {tensor}')
        req = dist.isend(tensor, target, group)
        # req.wait()
        # print(f'send1 finished: {args.rank}')
    else:
        # print(f'send2: {args.rank} at {time.perf_counter()-tb:.6f}')
        ops = []
        for tensor in tensors:
            ops.append(dist.P2POp(dist.isend, tensor, target, group))
        reqs = dist.batch_isend_irecv(ops)
        for req in reqs:
            req.wait()
        # print(f'send2 finished: {args.rank}')
    
    
def recv(tensors: list, target: int, group: object = None):
    if tensors == None:
        # print(f'recv1: {args.rank} from {target} at {time.perf_counter()-tb:.6f}')
        tensor = torch.tensor([args.local_rank]).to(f'cuda:{args.local_rank}')
        req = dist.irecv(tensor, target, group)
        req.wait()
        if tensor.sum() == target:
            return True
        else:
            return False
        # print(f'recv1 finished: {args.rank}, {tensor}')
    else:
        # print(f'recv2: {args.rank} from {target} at {time.perf_counter()-tb:.6f}')
        ops = []
        for tensor in tensors:
            ops.append(dist.P2POp(dist.irecv, tensor, target, group))
        reqs = dist.batch_isend_irecv(ops)
        for req in reqs:
            req.wait()
        # print(f'recv2 finished: {args.rank}')

if __name__ == '__main__':
    main()

    # powered by tyf
    # 🤔️ = 1
    # 😄 = 🤔️ + 📖
    # print(f"{😄+💧}")