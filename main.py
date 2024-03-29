import os
import sys
from io import BytesIO

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication

from ai_module import ali_nls
from core import wsa_server
from gui import flask_server
from gui.window import MainWindow

from utils import util
from utils import config_util
from scheduler.thread_manager import MyThread
from core.content_db import Content_Db
import sys
sys.setrecursionlimit(sys.getrecursionlimit() * 5)

SAMPLES_PATH = "data/samples"

def __clear_samples():
    if not os.path.exists(SAMPLES_PATH):
        os.mkdir(SAMPLES_PATH)
    for file_name in os.listdir(SAMPLES_PATH):
        if file_name.startswith('sample-'):
            os.remove(SAMPLES_PATH + '/' + file_name)

def __clear_songs():
    if not os.path.exists("./songs"):
        os.mkdir("./songs")
    for file_name in os.listdir('./songs'):
        if file_name.endswith('.mp3'):
            os.remove('./songs/' + file_name)

if __name__ == '__main__':
    if sys.version_info < (3, 10):
        raise ImportError("Python版本必须大于等于 3.10!")

    # 1. 清除之前的缓存
    __clear_samples()
    __clear_songs()
    util.clear_log()

    # 2. 加载配置文件信息 
    config_util.load_config()

    # 3. 初始化数据库信息 用于存放聊天记录
    dbstatus = os.path.exists("fay.db")
    if(dbstatus == False):
         contentdb = Content_Db()
         contentdb.init_db()     

    # 4. 启动STT（ASR）
    #Edit by xszyo  u in 20230516:增加本地asr后，aliyun调成可选配置
    if config_util.ASR_mode == "ali":
        ali_nls.start()

    # 5. 启动控制器后端（使用WebAPI)
    flask_server.start()

    # 6. 启动GUI与数字人通信（使用WebSocket）
    ws_server = wsa_server.new_instance(port=10002)
    ws_server.start_server()
    web_ws_server = wsa_server.new_web_instance(port=10003)
    web_ws_server.start_server()

    # 7. 使用Qt展示页面
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    win = MainWindow()
    win.show()
    app.exit(app.exec_())

    
