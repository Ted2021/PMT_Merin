import uproot
import numpy as np



def AnaSingleWF(file, Gain = "H",tree_s = "Treesource_0", tree_d = "Treedark_0"):

    #取得するbranch(HGの時は、wform1,0を使用し、LGの時は、wform3,2を使用する)
    #※基本的にSingePhe測定はHGで行う
    if Gain == "H":
        wform_pos = "wform1"
        wform_neg = "wform0"
        #1p.e.のピーク波高値の範囲(7dyPMTの場合 ※あくまで経験から設定)
        thres_min = 4.0
        thres_max = 20.0

    elif Gain == "L":
        wform_pos = "wform3"
        wform_neg = "wform2"
        #1p.e.のピーク波高値の範囲(7dyPMTの場合 ※あくまで経験から設定)
        thres_min = 0.3
        thres_max = 0.6

    #SourceとDarkの差動電圧をとる
    tr_s = uproot.open(file)[tree_s]
    wf_p = tr_s.arrays(wform_pos, library="np")[wform_pos]
    wf_n = tr_s.arrays(wform_neg, library="np")[wform_neg]
    tr_d = uproot.open(file)[tree_d]
    wf_p_d = tr_d.arrays(wform_pos, library="np")[wform_pos]
    wf_n_d = tr_d.arrays(wform_neg, library="np")[wform_neg]

    wf = wf_p - wf_n
    wf_d = wf_p_d - wf_n_d
    avg = np.average(wf,axis=0)
    avf_d = np.average(wf_d,axis=0)        #Darkの平均波形を取り、ベースラインとする

    peak = np.argmax(avg)     #Sourceのピーク位置を取得
    cell_bind = np.max(wf[:,peak-4:peak+4]-avf_d[peak-4:peak+4], axis=1)     #各イベントピークの前後4cellだけ取り出し、その波高の最大値を取得

    #各イベントで1p.e.の波高値の範囲に入っているか探査する
    single_phe = []
    for i in range(len(cell_bind)):
        if cell_bind[i] >= thres_min and cell_bind[i] < thres_max:
            single_phe.append(i)
    
    print("1p.e. evnet num => {0} events".format(len(single_phe)))
    print("1p.e. Probability of occurrence => {0} p.e.".format(len(single_phe)/len(cell_bind)))


    return len(single_phe), len(single_phe)/len(cell_bind), avg - avf_d, cell_bind