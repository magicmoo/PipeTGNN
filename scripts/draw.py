import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# 示例数据
y1 = [0.7475054860115051, 0.8134389519691467, 0.8661423921585083, 0.8874474167823792, 0.8971476554870605, 0.9095746278762817, 0.9127955436706543, 0.9223772287368774, 0.9263902902603149, 0.9319685697555542, 0.9327609539031982, 0.9395160675048828, 0.9435553550720215, 0.9457331299781799, 0.9456814527511597, 0.9539593458175659, 0.9566447138786316, 0.9600701928138733, 0.961207389831543, 0.961219310760498, 0.9656267166137695, 0.9647637605667114, 0.9667479991912842, 0.9665465354919434, 0.9666349291801453, 0.9661250114440918, 0.9697049856185913, 0.9685212969779968, 0.9692920446395874, 0.96925950050354, 0.9692325592041016, 0.9702886343002319, 0.9715678691864014, 0.9699563980102539, 0.9709230661392212, 0.9713723659515381, 0.9734687209129333, 0.9715523719787598, 0.973697304725647, 0.9739593267440796, 0.9731742143630981, 0.9721323847770691, 0.9732493758201599, 0.9735063314437866, 0.9737027883529663, 0.9738204479217529, 0.9735777378082275, 0.974539041519165, 0.9744167327880859, 0.9742454290390015]
x1 = [3.1418166160583496, 5.964349985122681, 8.909375667572021, 11.288636922836304, 13.814565420150757, 16.387798309326172, 18.74594211578369, 21.174751043319702, 23.587980270385742, 25.96347427368164, 28.73765540122986, 31.12152075767517, 33.59225296974182, 35.94890904426575, 38.42287349700928, 40.71676826477051, 43.162076234817505, 45.54236888885498, 47.88604760169983, 50.27756857872009, 52.86811351776123, 55.64393067359924, 58.21916604042053, 60.844398975372314, 63.23027682304382, 65.55032873153687, 67.65184545516968, 70.18141078948975, 72.78098964691162, 75.18375730514526, 77.60484147071838, 79.87484216690063, 82.43501853942871, 85.46640682220459, 87.77140641212463, 90.07471346855164, 92.5238528251648, 94.95184659957886, 97.23625254631042, 99.52978777885437, 101.99144959449768, 104.27836513519287, 107.02782130241394, 109.38043904304504, 111.86252236366272, 114.28527355194092, 116.78659129142761, 119.50363254547119, 121.75080919265747, 124.2774076461792]
y2 = [0.7558175325393677, 0.8622879981994629, 0.9034221768379211, 0.9165529012680054, 0.9251185655593872, 0.9301984310150146, 0.933010995388031, 0.9371980428695679, 0.9408709406852722, 0.9434203505516052, 0.947674036026001, 0.9501987099647522, 0.9540358781814575, 0.9570292234420776, 0.9553890228271484, 0.960273265838623, 0.960282027721405, 0.9629701972007751, 0.9603040218353271, 0.9642537832260132, 0.9663869738578796, 0.9659578204154968, 0.9673120975494385, 0.9662883281707764, 0.9693182110786438, 0.9692651033401489, 0.9704564809799194, 0.9700431823730469, 0.9713132977485657, 0.9730026721954346, 0.9737147092819214, 0.9736224412918091, 0.9736305475234985, 0.9740866422653198, 0.9755397439002991, 0.9743759632110596, 0.9755541086196899, 0.9754674434661865, 0.9764336943626404, 0.9757048487663269, 0.9764087200164795, 0.9752940535545349, 0.9763912558555603, 0.9772237539291382, 0.9771835803985596, 0.9779213666915894, 0.9777145981788635, 0.9779038429260254, 0.9780591130256653, 0.9779865741729736]
x2 = [4.489468097686768, 6.737579584121704, 9.030954837799072, 11.11675214767456, 13.326087474822998, 15.838558197021484, 18.038270473480225, 20.526294231414795, 22.961153984069824, 25.249308586120605, 27.31272006034851, 29.453993320465088, 31.88307476043701, 34.21681571006775, 36.56238865852356, 38.74372935295105, 41.14835572242737, 43.367905139923096, 45.69597601890564, 47.98928737640381, 50.28965497016907, 52.430586099624634, 54.79670429229736, 57.00453734397888, 59.247867584228516, 61.40787601470947, 63.68410873413086, 65.96591639518738, 68.26850628852844, 70.52880048751831, 72.87509775161743, 74.97245264053345, 77.42430400848389, 79.88469552993774, 82.25410008430481, 84.49696898460388, 86.67784595489502, 88.9897792339325, 91.2790629863739, 93.65868401527405, 95.86388564109802, 97.92407703399658, 100.10039043426514, 102.20436191558838, 104.58959150314331, 106.50349688529968, 108.92674589157104, 111.53941893577576, 114.00113797187805, 116.18290042877197]

# x1 = [i for i in range(100)]
# x2 = [i for i in range(100)]
# y1 = savgol_filter(y1, window_length=15, polyorder=3)
# y2 = savgol_filter(y2, window_length=15, polyorder=3)

# 调用函数绘制折线图
plt.figure()
plt.plot(x1, y1, label='GNNFlow')
plt.plot(x2, y2, label='Pipeline')
plt.legend()
plt.xlabel('time(s)')
plt.ylabel('auc')

plt.savefig('./img/img.jpg')