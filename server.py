import glob
import os
from AppFile import app

if __name__ == '__main__':
    #delete tmp files
    kinds = ["UploadFiles", "FirstFrame", "scatters", "graphs"]
    sss = (glob.glob(".\\flask_session\*"))
    for ss in sss:
        os.remove(ss)
    for kind in kinds:
        files = glob.glob(".\AppFile\static\\"+kind+"\*")
        for file in files:
            os.remove(file)

    #startup
    app.run(host="0.0.0.0", port=8000, debug=True)