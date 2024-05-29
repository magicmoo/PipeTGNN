import gnnflow

tb_list=[0.02672600746154785, 0.019466638565063477, 0.018413066864013672, 0.017525672912597656, 0.017203092575073242, 0.017701387405395508, 0.017826318740844727, 0.017360687255859375, 0.017682790756225586, 0.01740407943725586, 0.018634319305419922, 0.01726388931274414, 0.014520406723022461, 0.016867399215698242, 0.017241716384887695, 0.01756739616394043, 0.017606019973754883, 0.016640901565551758, 0.017426490783691406, 0.017390966415405273, 0.017468929290771484, 0.017745256423950195, 0.017172813415527344, 0.017312288284301758, 0.017444133758544922, 0.017671823501586914, 0.016901731491088867, 0.016259431838989258, 0.019664287567138672, 0.017339706420898438, 0.017768383026123047, 0.017682790756225586, 0.017673969268798828, 0.017705202102661133, 0.01654648780822754, 0.018736600875854492, 0.01759052276611328, 0.01627349853515625, 0.01836681365966797, 0.017651796340942383, 0.017510414123535156, 0.018114089965820312, 0.0179903507232666, 0.01769256591796875, 0.018157243728637695, 0.02166008949279785, 0.01796126365661621, 0.01759481430053711, 0.017505645751953125, 0.01739025115966797, 0.017505407333374023, 0.017458200454711914, 0.017594575881958008, 0.017450332641601562, 0.01617741584777832, 0.018222570419311523, 0.017665863037109375, 0.017543792724609375, 0.01741647720336914, 0.01741504669189453, 0.01750016212463379, 0.01735520362854004, 0.017351865768432617, 0.017922639846801758, 0.01777172088623047, 0.018014907836914062, 0.015889883041381836, 0.017520666122436523, 0.017833232879638672, 0.017516613006591797, 0.017504215240478516, 0.01746678352355957, 0.017423152923583984, 0.018159866333007812, 0.018018007278442383, 0.016930103302001953, 0.017374277114868164, 0.017464160919189453, 0.01761627197265625, 0.017834901809692383, 0.017675161361694336, 0.017667055130004883, 0.015717267990112305, 0.01622486114501953, 0.01700282096862793, 0.017875194549560547, 0.019533157348632812, 0.017794370651245117, 0.017199039459228516, 0.018090009689331055, 0.017589807510375977, 0.015639066696166992, 0.01788187026977539, 0.017183542251586914, 0.01925039291381836, 0.016158103942871094, 0.01817488670349121, 0.017919063568115234, 0.01781940460205078, 0.01759791374206543, 0.015894651412963867, 0.016355037689208984, 0.015380859375, 0.0166473388671875, 0.017713546752929688, 0.01780223846435547, 0.01756882667541504, 0.015947580337524414, 0.022091388702392578, 0.018876075744628906, 0.01765751838684082, 0.018065929412841797, 0.017934322357177734, 0.015373706817626953, 0.01793384552001953, 0.01732635498046875, 0.016811132431030273, 0.015807628631591797, 0.017053842544555664, 0.017864704132080078, 0.01743030548095703, 0.017186403274536133, 0.01714801788330078, 0.017838001251220703, 0.018172502517700195, 0.017585277557373047, 0.015873432159423828, 0.0171661376953125, 0.01595330238342285, 0.015509843826293945, 0.016462326049804688, 0.01984691619873047, 0.019541025161743164, 0.01820659637451172, 0.014963865280151367, 0.01619696617126465, 0.014244318008422852, 0.01440286636352539, 0.013501405715942383, 0.015439271926879883, 0.01334381103515625, 0.015528678894042969, 0.01557016372680664, 0.01780414581298828, 0.017776966094970703, 0.018182992935180664, 0.01799774169921875, 0.017140865325927734, 0.017451047897338867, 0.017318248748779297, 0.01674675941467285, 0.017020702362060547, 0.017901897430419922, 0.01565408706665039, 0.01808619499206543, 0.01817035675048828, 0.01791667938232422, 0.01685357093811035, 0.017760038375854492, 0.01644730567932129, 0.015861988067626953, 0.01598644256591797, 0.015776395797729492, 0.01582932472229004, 0.01468968391418457, 0.01505422592163086, 0.014900922775268555, 0.015316009521484375, 0.015610218048095703, 0.015353202819824219, 0.015646934509277344, 0.01566004753112793, 0.015456914901733398, 0.015995264053344727, 0.015011787414550781, 0.01427316665649414, 0.015952110290527344, 0.015352249145507812, 0.015909671783447266, 0.015063047409057617, 0.016309261322021484, 0.015422344207763672, 0.015612363815307617, 0.014358758926391602, 0.015366077423095703, 0.01587677001953125, 0.01597142219543457, 0.0157625675201416, 0.01688218116760254, 0.016648054122924805, 0.017038583755493164, 0.016144752502441406, 0.017049074172973633, 0.01752018928527832, 0.017495155334472656, 0.017350196838378906, 0.017641067504882812, 0.01773977279663086, 0.017444610595703125, 0.017609357833862305, 0.01708984375, 0.017891645431518555, 0.017515897750854492, 0.017910242080688477, 0.01607823371887207, 0.016503095626831055, 0.016156911849975586, 0.01692509651184082, 0.017625808715820312, 0.017259597778320312, 0.01746344566345215, 0.01534271240234375, 0.01750493049621582, 0.01796126365661621, 0.01739192008972168, 0.015736103057861328, 0.016402006149291992, 0.016367435455322266, 0.017157793045043945, 0.01787734031677246, 0.015761375427246094, 0.015015125274658203, 0.017707347869873047, 0.01790475845336914, 0.017740488052368164, 0.01814436912536621, 0.017906665802001953, 0.016312599182128906, 0.016948699951171875, 0.01787710189819336, 0.01801156997680664, 0.01630854606628418, 0.017759323120117188, 0.0170135498046875, 0.01695847511291504, 0.018040895462036133, 0.017263174057006836, 0.016329050064086914, 0.016524553298950195, 0.017057180404663086, 0.01742243766784668, 0.01600503921508789, 0.017731904983520508, 0.017729997634887695, 0.01622295379638672, 0.01746368408203125, 0.017338275909423828, 0.017693042755126953, 0.017891407012939453, 0.017788171768188477, 0.01600503921508789, 0.017910003662109375, 0.01745319366455078, 0.017087221145629883, 0.01676654815673828, 0.01711416244506836, 0.016971826553344727, 0.016945600509643555, 0.0159759521484375, 0.0177915096282959, 0.018075942993164062, 0.015926837921142578, 0.01686692237854004, 0.01738119125366211, 0.015885114669799805, 0.017850637435913086, 0.015379190444946289, 0.01666736602783203, 0.01593017578125, 0.01758265495300293, 0.016756534576416016, 0.015889406204223633, 0.017586946487426758, 0.01880049705505371, 0.01742696762084961, 0.01746988296508789, 0.017233848571777344, 0.0180814266204834, 0.017434120178222656, 0.01786327362060547, 0.016007661819458008, 0.017805814743041992, 0.017783403396606445, 0.0194091796875, 0.019303321838378906, 0.017524242401123047, 0.017505884170532227, 0.017351150512695312, 0.017837047576904297, 0.017063617706298828, 0.01813030242919922, 0.017650604248046875, 0.016300201416015625, 0.017741680145263672, 0.01792740821838379, 0.017363786697387695, 0.017389535903930664, 0.01650071144104004, 0.016950607299804688, 0.01736760139465332, 0.017667293548583984, 0.017328500747680664, 0.01606273651123047, 0.01692795753479004, 0.016271114349365234, 0.016779184341430664, 0.015937328338623047, 0.015920639038085938, 0.01610565185546875, 0.015942811965942383, 0.01571059226989746, 0.016084671020507812, 0.016320228576660156, 0.015716552734375, 0.016099929809570312, 0.016107559204101562, 0.013185501098632812, 0.014698266983032227, 0.014125585556030273, 0.016188859939575195, 0.0161588191986084, 0.01613759994506836, 0.016086339950561523, 0.013699054718017578, 0.01402592658996582, 0.013157367706298828, 0.014867544174194336, 0.013933420181274414, 0.015059709548950195, 0.013842582702636719, 0.016176939010620117, 0.01633763313293457, 0.016010046005249023, 0.01420140266418457, 0.01546025276184082, 0.013458728790283203, 0.01574540138244629, 0.015455245971679688, 0.016452789306640625, 0.015204906463623047, 0.016252517700195312, 0.01617884635925293, 0.014403104782104492, 0.01540064811706543, 0.01397085189819336, 0.014148712158203125, 0.013924837112426758, 0.016097307205200195, 0.016111373901367188, 0.01618814468383789, 0.015766620635986328, 0.015177488327026367, 0.016070127487182617, 0.01573801040649414, 0.01612377166748047, 0.016085147857666016, 0.015655517578125, 0.01616525650024414, 0.016068220138549805, 0.014165163040161133, 0.015100955963134766, 0.01589226722717285, 0.016355037689208984, 0.015114068984985352, 0.014581918716430664, 0.014247417449951172, 0.014698028564453125, 0.01618504524230957, 0.016040563583374023, 0.016062021255493164, 0.016132593154907227, 0.01577281951904297, 0.01598381996154785, 0.01613020896911621, 0.01618027687072754, 0.014974832534790039, 0.014179468154907227, 0.014303207397460938, 0.014968633651733398, 0.015717267990112305, 0.01623368263244629, 0.016179561614990234, 0.015758037567138672, 0.016230344772338867, 0.01616978645324707, 0.014745950698852539, 0.01512455940246582, 0.015819072723388672, 0.01643967628479004, 0.014551877975463867, 0.01483464241027832, 0.016219139099121094, 0.015201807022094727, 0.01621723175048828, 0.01587224006652832, 0.016143083572387695, 0.015389442443847656, 0.016064167022705078, 0.016344547271728516, 0.016178607940673828, 0.016854524612426758, 0.016193628311157227, 0.01596689224243164, 0.016084671020507812, 0.015468835830688477, 0.01634526252746582, 0.015878677368164062, 0.01581549644470215, 0.015963315963745117, 0.01590561866760254, 0.015151262283325195, 0.016089677810668945, 0.016163110733032227, 0.015883684158325195, 0.015998125076293945, 0.015888452529907227, 0.015972137451171875, 0.01415562629699707, 0.01424860954284668, 0.01298213005065918, 0.014800786972045898, 0.013370037078857422, 0.014872074127197266, 0.014490365982055664, 0.016058921813964844, 0.01423192024230957, 0.014153480529785156, 0.014427423477172852, 0.014215707778930664, 0.014824867248535156, 0.014463663101196289, 0.01611495018005371, 0.01618218421936035, 0.015868663787841797, 0.01614522933959961, 0.01507258415222168, 0.014877080917358398, 0.016336441040039062, 0.014098405838012695, 0.014418363571166992, 0.014621257781982422, 0.016138792037963867, 0.016053199768066406, 0.014946460723876953, 0.014115571975708008, 0.016249895095825195, 0.01621389389038086, 0.01621556282043457, 0.016076087951660156, 0.013964414596557617, 0.014837980270385742, 0.0161592960357666, 0.01621532440185547, 0.01741480827331543, 0.01876664161682129, 0.017534494400024414, 0.017362117767333984, 0.01793360710144043, 0.017041921615600586, 0.01729130744934082, 0.016638755798339844, 0.01866888999938965, 0.017435312271118164, 0.017683029174804688, 0.017306089401245117, 0.016859769821166992, 0.018300294876098633, 0.01764988899230957, 0.018687725067138672, 0.015760421752929688]
len = len(tb_list)
x1, x2 = 0, 0
for i in range(0, len//2):
    x1 += tb_list[i]

for i in range(len//2, len):
    x2 += tb_list[i]
print(x1)
print(x2)