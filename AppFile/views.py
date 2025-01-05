import os
from flask import render_template as retmp, request, session as ss, jsonify, redirect
from flask_session import Session
from AppFile import app, params, defs

#ホーム画面の表示
@app.get('/')
def home():
    #IDの発効
    ss['ID'] = "hex: {:04x}".format(app.config['ID'])[5:]
    app.config['ID'] += 1

    return retmp(app.config['HTML_HOME'])

#アップロード画面の表示
@app.get("/upload")
def upload():
    return retmp(app.config['HTML_UPLO'])

#動画の保存
@app.route("/upload/done", methods=["GET", "POST"])
def upload_done():
    if request.method == "POST":
        video = request.files['video']
        if video.name == '':
            em = "There is no file name."
            return retmp(app.config['HTML_ERRO'], Message=em)
        
        if video and defs.allwedFile(video.filename):
            FileFormat = str(os.path.splitext(video.filename)[1])
            filename = ss['ID'] + FileFormat

        ss['uPath'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(ss['uPath'])
        return redirect("/upload/done")
    
    return redirect("/trimming")

#フレーム番号の設定
@app.get('/trimming')
def trimming():
    FFN, f = defs.getFinalFrameNumber(ss['uPath'])
    vp = "." + ss['uPath'][app.config['HTML_INDEX']:]
    return retmp(app.config['HTML_SSE'], VPath=vp, FFN=FFN, FPS=f)

#初期・最終フレーム保存
@app.route("/trimming/done", methods=["GET", "POST"])
def trimming_done():
    if request.method == "POST":
        ss['SEFrame'] = [int(request.form['sfNum'])-1, int(request.form['efNum'])-1]
        return redirect("/trimming/done")
    return redirect("/set")

#初期フレームの画像を保存（追跡物体の選択用）
@app.get('/set')
def select():
    FFPath = defs.saveFF(ss['uPath'], ss['ID'], ss['SEFrame'])
    if FFPath == "":
        em = "This video has no frame."
        return retmp(app.config['HTML_ERRO'], Message=em)
    else:
        return retmp(app.config['HTML_SET'], FFPath=FFPath)

#基準線・矩形の範囲保存
@app.post('/setPoint')
def setPoint():
    if request.json['type'] == "line":
        ss['length'] = defs.getLength(request.json['params'])
    elif request.json['type'] == "rect":
        rect = request.json['params']
        left = int(rect['left'])
        top = int(rect['top'])
        width = int(rect['width'])
        height = int(rect['height'])
        ss['bbox'] = [left, top, width, height]

    return jsonify({"message": "Image Processed successfully"})

#設定の保存
@app.route('/set/done', methods=["GET", "POST"])
def set_done():
    if request.method == "POST":
        length = request.form['length']
        unit = request.form['unit']
        length_mm = defs.setUnit(length, unit)
        ss['rate'] = float(length_mm) / float(ss['length'])

        XFD, YFD = request.form['Xforward'], request.form['Yforward']
        XIP = defs.setUnit(request.form['XIP'], request.form['XIPunit'])
        YIP = defs.setUnit(request.form['YIP'], request.form['YIPunit'])
        IV = {'0':False, '1':True}
        XIV = IV[request.form["XIV"]]
        YIV = IV[request.form["YIV"]]
        ss['offset'] = {
            'FD' : [XFD, YFD], 
            'IP' : [XIP, YIP], 
            'IV' : [XIV, YIV], 
        }
        return redirect("/set/done")
    return redirect("/track")

#物体追跡
@app.get("/track")
def set_track():
    global params
    scaPath = app.config['SCATTER_FOLDER']

    sp = os.path.join(scaPath, ss['ID'])
    t, x, y = defs.trackObject(ss['uPath'], params, ss['bbox'], ss['rate'], sp, ss['offset'], ss['SEFrame'])

    os.remove(ss['uPath'])
    os.remove(os.path.join("./AppFile/static/FirstFrame", ss['ID']+"_FF.jpg"))

    if len(t) == 0:
        em = "This video has no image."
        return retmp(app.config['HTML_ERRO'], em)

    ss['t'], ss['x'], ss['y'] = t, x, y
    return redirect("result")

#近似方法の変更
@app.get("/changeMethod")
def changeMethod():
    ScatterPath = {
        'XSP' : './static/scatters/'+ss['ID']+'_Xscatter.jpg', 
        'YSP' : './static/scatters/'+ss['ID']+'_Yscatter.jpg', 
    }
    return retmp(app.config['HTML_APPR'], Path=ScatterPath) 

#結果表示
@app.route("/result", methods=["POST", "GET"])
def track_result():
    if request.method == "GET":
        #最適な近似式を選択する関数を作成
        xm = defs.serchOptimalForm(ss['x'])
        ym = defs.serchOptimalForm(ss['y'])
    elif request.method == "POST":
        xm = request.form['x_appr_method']
        ym = request.form['y_appr_method']

    Formula, Path, CSV = defs.makeGraph(xm, ym, ss['t'], ss['x'], ss['y'], ss['ID'], ss['offset'], ss['rate']/1000.0)
    return retmp(app.config['HTML_RE'], Formula=Formula, Path=Path, VPath="./static/outfile/video.mp4", CSV=CSV)