from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

class WebEngineView(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.setUrl(QUrl("https://melvoridle.com/"))
