import matplotlib.pyplot as plt
import scipy.optimize as sc
import sympy as sym
import numpy as np
import math
import csv
import cv2
import os

#動画ファイル
def allwedFile(filename):
    EXTENSIONS = set(['avi', 'mp4', 'mkv', 'mov', 'flv', 'wmv', 'webm', 'ogv'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONS

#動画のフレーム数とFPSを取得
def getFinalFrameNumber(Path):
    cap = cv2.VideoCapture(Path)
    count, fps = cap.get(cv2.CAP_PROP_FRAME_COUNT), cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return int(count), fps

#第1フレームをstaticフォルダに保存
def saveFF(uploadPath, origname, seFrame):
    cap = cv2.VideoCapture(uploadPath)
    cap.set(cv2.CAP_PROP_POS_FRAMES, seFrame[0])
    success, img = cap.read()
    if not success:
        return ""
    cap.release()
    savePath = os.path.join("./AppFile/static/FirstFrame", origname+"_FF.jpg")
    cv2.imwrite(savePath, img)
    return os.path.join("./static/FirstFrame/", origname+"_FF.jpg")

#基準線の長さ(画素単位)を計算
def getLength(l:dict):
    return math.sqrt( (l['line_ex']-l['line_sx'])**2 + (l["line_ey"]-l['line_sy'])**2 )

#単位mmに統一
def setUnit(m, u):
    unit_dect = {
        "milli_meter" : 1, 
        "centi_meter" : 10, 
        "metre" : 1000, 
    }
    return int(m) * unit_dect[u]
"""
#追跡物体の平均的なBGR値を取得
def getObjectColor(img, bbox):
    x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
    x2 += x1
    y2 += y1
    b, g, r = img[y1:y2, x1:x2, 0], img[y1:y2, x1:x2, 1], img[y1:y2, x1:x2, 2]
    mb, mg, mr = float(np.median(b)), float(np.median(g)), float(np.median(r))
    b, g, r = b[abs(b-mb)<9], g[abs(g-mg)<9], r[abs(r-mr)<9]
    return [float(np.mean(b)), float(np.mean(g)), float(np.mean(r))]

#二値化
def treatColor(img, color):
    img = np.where(img-np.array(color)<9, 255, 0)
    img = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    _, img = cv2.threshold(img, 250, 255, cv2.THRESH_BINARY)
    img = cv2.medianBlur(img, 7)
    img = np.stack([img, img, img], axis=2)
    return img
"""

#物体を追跡して座標[m]を取得、散布図を保存
def trackObject(uploadPath, params, bbox, rate, savePath, offset, seFrame):
    cap = cv2.VideoCapture(uploadPath)
    cap.set(cv2.CAP_PROP_POS_FRAMES, seFrame[0])
    tracker = cv2.TrackerDaSiamRPN_create(params)
    success, img = cap.read()
    #color = getObjectColor(img, bbox)
    #Bimg = treatColor(img, color)
    #tracker.init(Bimg, bbox)
    #二値化の処理を削除
    tracker.init(img, bbox)

    WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    FPS = cap.get(cv2.CAP_PROP_FPS)
    x = []
    y = []
    
    frame = cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), (0, 0, 255), thickness=2)
    #fourcc = cv2.VideoWriter_fourcc('m','p','4', 'v')
    #fourcc = cv2.VideoWriter_fourcc(*"X264")
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    video  = cv2.VideoWriter('./AppFile/static/outfile/video.mp4', fourcc, float(FPS), (WIDTH, HEIGHT))

    cap.set(cv2.CAP_PROP_POS_FRAMES, seFrame[0])
    while True:
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == seFrame[1]:
            break
        #color = getObjectColor(img, bbox)
        success, img = cap.read()
        if not success:
            return [], [], []
        #Bimg = treatColor(img, color)
        #success, bbox = tracker.update(Bimg)
        success, bbox = tracker.update(img)
        if not success:
            return [], [], []

        x.append(int(bbox[0]+bbox[2]/2))
        y.append(int(bbox[1]+bbox[3]/2))

        #追跡動画の作成
        frame = cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), (0, 0, 255), thickness=2)
        video.write(frame)
    
    cap.release()
    video.release()

    #y座標を上基準からした基準に変換
    y = [HEIGHT-y[i] for i in range(len(y))]

    #時刻のリストを作成
    t = [a*(1/FPS) for a in range(len(x))]

    #進行方向に応じて符号を変換
    if offset['FD'][0] == 'left':
        x = [-x[i] for i in range(len(x))]
    if offset['FD'][1] == 'downward':
        y = [-y[i] for i in range(len(y))]
    
    #pix/mmを計算
    ppmm = 1.0/rate

    #設定した初期位置を原点とした座標[pix]に変換
    x = [int(xi - x[0] + offset['IP'][0]*ppmm) for xi in x]
    y = [int(yi - y[0] + offset['IP'][1]*ppmm) for yi in y]

    #mm/pix -> m/pix
    rate /= 1000.0

    #初期位置[m]を設定
    x_m = [xi * rate for xi in x]
    y_m = [yi * rate for yi in y]
    #xdef = x[0]*rate - offset['IP'][0]
    #ydef = y[0]*rate - offset['IP'][1]
    #x_m = [xi*rate - xdef for xi in x]
    #y_m = [yi*rate - ydef for yi in y]

    #散布図を作成
    plt.clf()
    plt.title("x-t Scatter")
    plt.xlabel("time [s]")
    plt.ylabel("X Position [m]")
    plt.scatter(t, x_m, s=5)
    plt.savefig(savePath+"_Xscatter.jpg", format="jpg", dpi=300)

    plt.clf()
    plt.title("y-t Scatter")
    plt.xlabel("time [s]")
    plt.ylabel("Y Position [m]")
    plt.scatter(t, y_m, s=5)
    plt.savefig(savePath+"_Yscatter.jpg", format="jpg", dpi=300)
    plt.clf()

    return t, x, y

#近似用の関数群
#定数関数
def constant_function(x, a):
    return a + 0*x
#一次関数
def linear_function(x, a, b):
    return a + b*x
#二次関数
def quadratic_function(x, a, b, c):
    return a + b*x + c*(x**2)
#Cos関数
def cosine_function(x, a, b, c, d):
    return a*np.cos(b*x - c) + d
#Sin関数
def sine_function(x, a, b, c, d):
    return a*np.sin(b*x - c) + d
#空気抵抗ありの関数（未完成）
def exp_and_linear_function(x, a):
    return a*x
    #return a*sym.exp(b*x) + c*x + d

#曲線回帰
def fitting(method, time, x, t):
    func_dict = {
        "CF" : constant_function, 
        "LF" : linear_function, 
        "QF" : quadratic_function, 
        "CosF" : cosine_function, 
        "SinF" : sine_function, 
        "ELF": exp_and_linear_function, 
    }

    if method=="CosF" or method=="SinF":
        nx = np.array(x)
        amp = 2*np.std(nx)
        fft_freq = np.fft.fftfreq(nx.size, d=time[1]-time[0])
        freqAmp = abs(np.fft.fft(nx)/int(nx.size/2))
        freq = abs(fft_freq[np.argmax(freqAmp[1:])+1])
        angFreq = 2*np.pi*freq
        phi = 0
        offset = np.mean(np.array(x))
        tri_p0 = [amp, angFreq, phi, offset]
        C, _ = sc.curve_fit(func_dict[method], time, x, p0=tri_p0)
    else:
        C, _ = sc.curve_fit(func_dict[method], time, x)

    if method == 'CF':
        return C[0] + 0*t
    elif method == 'LF':
        return C[0] + C[1]*t
    elif method == 'QF':
        return C[0] + C[1]*t + C[2]*(t**2)
    elif method == 'CosF':
        return C[0]*sym.cos(C[1]*t - C[2]) + C[3]
    elif method == 'SinF':
        return C[0]*sym.sin(C[1]*t - C[2]) + C[3]
    elif method == "ELF":
        return C[0]*t
        #return C[0]*sym.exp(C[1]*t) + C[2]*t + C[3]

#最適な回帰手法を選択
def serchOptimalForm(x):
    methods = {
        "CF" : constant_function, 
        "LF" : linear_function, 
        "QF" : quadratic_function, 
        "CosF" : cosine_function, 
        "SinF" : sine_function, 
    }
    def norm(x:np.ndarray)->np.ndarray:
        max = x.max()
        min = x.min()
        return (x-min) / (max-min)
    
    x = np.array(x)
    t = np.array([i for i in range(len(x))])
    x, t = norm(x), norm(t)

    def MSE(x1:np.ndarray, x2:np.ndarray)->float:
        return ((x1 - x2)**2).mean()
    
    for method in methods:
        C, _ = sc.curve_fit(methods[method], t, x)
        
        if method == "CF":
            x2 = np.full(x.size, C[0])
        elif method == "LF":
            x2 = C[0] + C[1]*t
        elif method == "QF":
            x2 = C[0] + C[1]*t + C[2]*(t**2)
        elif method == "CosF":
            x2 = C[0]*np.cos(C[1]*t - C[2]) + C[3]
            if abs(C[2]) < np.pi/4:
                method = "SinF"
        elif method == "SinF":
            x2 = C[0]*np.sin(C[1]*t - C[2]) + C[3]
            if abs(C[2]) > np.pi/4:
                method = "CosF"

        if MSE(x, x2) < 0.1:
            return method

    return "CF"

#グラフの保存
def saveGraph(f, t, time, path, title, label):
    plt.rcParams["font.size"] = 15
    plt.title(title)
    arr = [f.subs(t, time[i]) for i in range(len(time))]
    plt.plot(time, arr)
    plt.xlabel('time [s]')
    plt.ylabel(label)
    plt.savefig(path, format="jpg", dpi=300)
    plt.clf()

#MathJax形式の数式を作成
def mathForm2str(s, u, fx):
    sfx = "\("
    symbol = {
        "m"     :   s, 
        "ms"    :   "v_{"+s+"}", 
        "mss"   :   "a_{"+s+"}",
    }
    sfx += symbol[u]
    sfx += "="
    fx = list(str(fx) + " ")
    isNumber = False

    for i in range(fx.__len__()):
        if fx[i].isdigit() and isNumber==False:
            head = i
            isNumber = True
        elif isNumber==True and not (fx[i].isdigit() or fx[i]=='.'):
            num = float(''.join(fx[head:i]))
            if not num == int(num):
                num = round(num, 3)
            else:
                num = int(num)
            num = list(str(num))
            for j in range(head+len(num), i):
                num += " "
            fx[head:i] = num
            isNumber = False

    fx = ''.join(fx)
    fx = fx.replace(' ', '')
    fx = fx.replace("**", '^')
    fx = fx.replace('*', " \ ")
    fx = fx.replace("cos", " \cos ")
    fx = fx.replace("sin", " \sin ")
    sfx += fx

    sfx += " \ "
    unit = {
        "m" : "[m]", 
        "ms" : "[m/s]", 
        "mss" : "[m/s^2]", 
    }
    sfx += unit[u]
    sfx += "\)"

    return sfx

#CSVファイルを作成
def makeCSV(t, x, y, origname):
    with open('.\AppFile\static\csv\\'+origname+'.csv', 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time [s]", "x [m]", "y [m]"])
        rows = [[t[i], x[i], y[i]] for i in range(len(t))]
        writer.writerows(rows)

        return "./static/csv/"+origname+".csv"

#各種グラフを作成
def makeGraph(xm, ym, time, x, y, origname, offset, rate):
    #pix -> m
    x = [xi*rate for xi in x]
    y = [yi*rate for yi in y]

    SavePath = "./AppFile/static/graphs/"
    t = sym.symbols('t')
    
    xt = fitting(xm, time, x, t)
    xt -= xt.subs(t, 0) - offset['IP'][0]/1000
    vxt = sym.diff(xt)
    if offset['IV'][0]:
        vxt -= vxt.subs(t, 0)
    axt = sym.diff(vxt)
    plt.scatter(time, x, s=5)
    xtPath = os.path.join(SavePath, origname+"_XT.jpg")
    vxPath = os.path.join(SavePath, origname+"_VxT.jpg")
    axPath = os.path.join(SavePath, origname+"_AxT.jpg")
    saveGraph(xt, t, time, xtPath, "X Position", "position [m]")
    saveGraph(vxt, t, time, vxPath, "X Velocity", "velocity [m/s]")
    saveGraph(axt, t, time, axPath, "X Acceleration", "acceleration [m/s^2]")

    yt = fitting(ym, time, y, t)
    yt -= yt.subs(t, 0) - offset['IP'][1]/1000
    vyt = sym.diff(yt)
    if offset['IV'][1]:
        vyt -= vyt.subs(t, 0)
    ayt = sym.diff(vyt)
    plt.scatter(time, y, s=5)
    ytPath = os.path.join(SavePath, origname+"_YT.jpg")
    vyPath = os.path.join(SavePath, origname+"_VyT.jpg")
    ayPath = os.path.join(SavePath, origname+"_AyT.jpg")
    saveGraph(yt, t, time, ytPath, "Y Position", "position [m]")
    saveGraph(vyt, t, time, vyPath, "Y Velocity", "velocity [m/s]")
    saveGraph(ayt, t, time, ayPath, "Y Acceleration", "acceleration [m/s^2]")

    #MSE計算
    x2 = np.array([xt.subs(t, ti) for ti in time])
    y2 = np.array([yt.subs(t, ti) for ti in time])
    MSEX = round(pow(np.array(x) - x2, 2).mean(), 3)
    MSEY = round(pow(np.array(y) - y2, 2).mean(), 3)
    MSEX = "\(MSE:"+ str(MSEX) +"\)"
    MSEY = "\(MSE:"+ str(MSEY) +"\)"

    xt = mathForm2str("x", "m", xt)
    vxt = mathForm2str("x", "ms", vxt)
    axt = mathForm2str("x", "mss", axt)
    yt = mathForm2str("y", "m", yt)
    vyt = mathForm2str("y", "ms", vyt)
    ayt = mathForm2str("y", "mss", ayt)

    SavePath = "./static/graphs/"
    formula = {
        "MSEX" : MSEX, 
        "MSEY" : MSEY, 
        'xt' : xt, 
        'vxt' : vxt, 
        'axt' : axt, 
        'yt' : yt, 
        'vyt' : vyt, 
        'ayt' : ayt
    }
    FilePath = {
        'xt' : os.path.join(SavePath, origname+"_XT.jpg"), 
        'yt' : os.path.join(SavePath, origname+"_YT.jpg"), 
        'vxt' : os.path.join(SavePath, origname+"_VxT.jpg"), 
        'vyt' : os.path.join(SavePath, origname+"_VyT.jpg"), 
        'axt' : os.path.join(SavePath, origname+"_AxT.jpg"), 
        'ayt' : os.path.join(SavePath, origname+"_AyT.jpg"), 
    }

    CSVPath = makeCSV(time, x, y, origname)

    return formula, FilePath, CSVPath