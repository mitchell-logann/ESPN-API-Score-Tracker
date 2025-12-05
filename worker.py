from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import json

class Worker(QObject):
    data_fetched = pyqtSignal(dict)
    error = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, url, interval = 10):
        super().__init__()
        self.url = url
        self.interval = interval
        
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.handleReply)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch)
        self.timer.setInterval(self.interval * 1000)
        
    def start(self):
        self.fetch()
        self.timer.start()
        
    def stop(self):
        self.timer.stop()
    
    def fetch(self):
        request = QNetworkRequest(QUrl(self.url))
        self.manager.get(request)
        
    def handleReply(self, reply):
        if reply.error():
            self.error.emit(reply.errorString())
            return
    
        raw = reply.readAll().data().decode()
        try:
            data = json.loads(raw)
            self.data_fetched.emit(data)
        except Exception as e:
            self.error.emit(str(e))