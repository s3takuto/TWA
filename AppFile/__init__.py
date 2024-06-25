from flask import Flask
import cv2

app = Flask(__name__)
app.config.from_object('AppFile.config')

params = cv2.TrackerDaSiamRPN_Params()
params.model = "./AppFile/model/DasiamRPN/dasiamrpn_model.onnx"
params.kernel_r1 = "./AppFile/model/DasiamRPN/dasiamrpn_kernel_r1.onnx"
params.kernel_cls1 = "./AppFile/model/DasiamRPN/dasiamrpn_kernel_cls1.onnx"

from AppFile import views