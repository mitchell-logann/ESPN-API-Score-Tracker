from os import name
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from worker import Worker
from db import initDB, saveFavorite, getFavorite, removeFavorite
import api
from sports import SPORTS
from notify import showAlert
import json
from PyQt5 import sip
import pickle

class GameItemWidget(QWidget):
    def __init__(self, name, scoreSTR, logos=[],isFavorite=False, logo_cache={}, eventID = None):
        super().__init__()
        self.isFavorite = isFavorite
        self.name = name
        self.logo_urls = logos
        self.logo_cache = logo_cache
        self.eventID = eventID
        
        layout = QHBoxLayout()
        layout.setContentsMargins(5,5,5,5)
        self.setLayout(layout)
        
        
        self.leftLogoLabel = QLabel()
        self.leftLogoLabel.setFixedSize(40,40)
        layout.addWidget(self.leftLogoLabel)
        
        self.rightLogoLabel = QLabel()
        self.rightLogoLabel.setFixedSize(40,40)
        layout.addWidget(self.rightLogoLabel)
        
        self.textLabel = QLabel(scoreSTR)
        layout.addWidget(self.textLabel)
        layout.addStretch()
        
        if logos:
            if logos[0] in self.logo_cache:
                self.leftLogoLabel.setPixmap(self.logo_cache[logos[0]])
            if len(logos) > 1 and logos[1] in self.logo_cache:
                self.rightLogoLabel.setPixmap(self.logo_cache[logos[1]])
           
        self.updateBackground()     
        
    def setFavorite(self, fav: bool):
        self.isFavorite = fav
        self.updateBackground()
            
    def updateBackground(self):
        if self.isFavorite:
            self.setStyleSheet("background-color: #FFFACD; border: 1px solid #FFD700;")
        else:
            self.setStyleSheet("")

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ESPN Score Tracker")
        self.resize(900, 600)
        
        self.logo_cache = {}
        self.pendingLogoItems = {}
        self.previousScores = {}
        self.user_id = 1 # Placeholder user ID'
        self.gameWidgets = {}
        
        self.settings = QSettings("User", "ESPNScoreTracker")
        self.currentLeague = self.settings.value("last_league", "NFL")
        
        self.network = QNetworkAccessManager()
        self.network.finished.connect(self.onNetworkReply)
        
        self.imageManager = QNetworkAccessManager()
        self.imageManager.finished.connect(self.handleLogoDownloaded)
        
        initDB()
        self.currentLeague = "NFL"
        self.worker = None
        
        self.setupUI()
        self.loadGames()
    
    def setupUI(self):
        central = QWidget()
        layout = QVBoxLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)
        
        leagueLayout = QHBoxLayout()
        self.leagueDropdown = QComboBox()
        for league in SPORTS.keys():
            self.leagueDropdown.addItem(league)
            
        self.leagueDropdown.currentTextChanged.connect(self.changeLeague)
        
        leagueLayout.addWidget(QLabel("Select League:"))
        leagueLayout.addWidget(self.leagueDropdown)
        layout.addLayout(leagueLayout)
        
        exitButton = QPushButton("Exit")
        exitButton.clicked.connect(self.exitApp)
        leagueLayout.addWidget(exitButton)
        layout.addLayout(leagueLayout)
        
        menubar = QMenuBar()
        settingsMenu = menubar.addMenu("Settings")
        aboutAction = QAction("About", self)
        aboutAction.triggered.connect(self.showAbout)
        settingsMenu.addAction(aboutAction)
        layout.setMenuBar(menubar)
        
        self.listWidget = QListWidget()
        self.listWidget.itemClicked.connect(self.toggleFavorite)
        layout.addWidget(self.listWidget)
        
    def exitApp(self):
        self.settings.setValue("last_league", self.currentLeague)
        self.settings.setValue("geometry", self.saveGeometry())
        serializableCache = {}
        
        for url, pix in self.logo_cache.items():
            ba = QByteArray()
            buffer = QBuffer(ba)
            buffer.open(QIODevice.WriteOnly)
            pix.save(buffer, "PNG")
            serializableCache[url] = bytes(ba)
            
        with open("logo_cache.pkl", "wb") as f:
            pickle.dump(serializableCache, f)
        with open("previous_scores.pkl", "wb") as f:
            pickle.dump(self.previousScores, f)
        
        self.settings.sync()
        self.close()
    
    def changeLeague(self, league):
        self.currentLeague = league
        if self.worker:
            self.worker.stop()
            self.worker.deleteLater()
            self.worker = None
        
        for name, widget in list(self.gameWidgets.items()):
            try:
                for i in range(self.listWidget.count()):
                    item = self.listWidget.item(i)
                    if self.listWidget.itemWidget(item) is widget:
                        self.listWidget.takeItem(i)
                        break
            except Exception:
                pass
            try:
                widget.deleteLater()
            except Exception:
                pass
            
        self.gameWidgets.clear()
        self.pendingLogoItems.clear()
        self.previousScores.clear()
        self.loadGames()
        
    def loadGames(self):
        if self.worker is not None:
            self.worker.stop()
            self.worker.deleteLater()
            self.worker = None
            
        
        sport, league = SPORTS[self.currentLeague]
        url = f"{api.BASE}/{sport}/{league}/scoreboard"
        
        self.worker = Worker(url, interval=10)
    
        self.worker.data_fetched.connect(self.displayGames)
        self.worker.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
        
        self.worker.start()
        
    def onNetworkReply(self, reply):
        data = reply.readAll().data().decode()
        try:
            jsonData = json.loads(data)
            self.displayGames(jsonData)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        
    def displayGames(self, data):
        favorites = set(getFavorite(self.user_id) or [])
        
        events = data.get("events", [])
        visibleGames = set(self.gameWidgets.keys())
        
        for event in events:
            name = event.get("shortName", "Game")
            competitions = event.get("competitions", [])
            competitors = competitions[0].get("competitors", []) if competitions else []
            
            scoreSTR = ""
            logos = []
            teamIDS = []
            for team in competitors:
                teamOBJ = team.get("team", {})
                teamID = teamOBJ.get("id", None)
                if teamID:
                    teamIDS.append(teamID)
                teamName = teamOBJ.get("displayName", teamOBJ.get("name", "Team"))
                teamScore = team.get("score", "0")
                scoreSTR += f"{teamName}: {teamScore}  "
                logo_url = teamOBJ.get("logo", "") or ""
                if logo_url:
                    logos.append(logo_url)
            scoreSTR = scoreSTR.strip()
            eventID = "-".join(teamIDS) if teamIDS else name
            
            status = competitions[0].get("status", {}).get("displayClock", "")
            period = competitions[0].get("status", {}).get("period", "")
            if status:
                scoreSTR += f" | {status} Q{period}"
            
            
            previousScore = self.previousScores.get(name)
            if previousScore and previousScore != scoreSTR:
                showAlert(self, "Score Update", f"Score changed for {name}!\nNew Score: {scoreSTR}")
            
            self.previousScores[name] = scoreSTR

            isFav = eventID in favorites
            
            widget = self.gameWidgets.get(name)
            if widget is None or sip.isdeleted(widget):
                widget = GameItemWidget(name, scoreSTR, logos=logos, isFavorite=isFav, logo_cache=self.logo_cache, eventID=eventID)
                item = QListWidgetItem()
                self.listWidget.addItem(item)
                item.setSizeHint(widget.sizeHint())
                self.listWidget.setItemWidget(item, widget)
                self.gameWidgets[name] = widget
            else:
                try:
                    widget.textLabel.setText(scoreSTR)
                except RuntimeError:
                    widget = GameItemWidget(name, scoreSTR, logos=logos, isFavorite=name in favorites, logo_cache=self.logo_cache)
                    for i in range(self.listWidget.count()):
                        item = self.listWidget.item(i)
                        if self.listWidget.itemWidget(item) is widget:
                            item.setSizeHint(widget.sizeHint())
                            self.listWidget.setItemWidget(item, widget)
                            break

            for logo_url in logos:
                if logo_url not in self.logo_cache:
                    lst = self.pendingLogoItems.get(logo_url, [])
                    if widget not in lst:
                        lst.append(widget)
                    request = QNetworkRequest(QUrl(logo_url))
                    self.imageManager.get(request)
            visibleGames.discard(name)
        for oldName in list(visibleGames):
            oldWidget = self.gameWidgets.pop(oldName, None)
            if oldWidget:
                for i in range(self.listWidget.count()):
                    item = self.listWidget.item(i)
                    if self.listWidget.itemWidget(item) is oldWidget:
                        self.listWidget.takeItem(i)
                        break
                try:
                    oldWidget.deleteLater()
                except Exception:
                    pass
            for url, widgets in list(self.pendingLogoItems.items()):
                try:
                    self.pendingLogoItems[url] = [w for w in widgets if w is not oldWidget]
                    if not self.pendingLogoItems[url]:
                        self.pendingLogoItems.pop(url, None)
                except Exception:
                    pass
            
    def toggleFavorite(self, item):
        widget = self.listWidget.itemWidget(item)
        if not widget:
            return
        eventID = widget.eventID
        if not eventID:
            return
        favorites = set(getFavorite(self.user_id) or [])
        if eventID in favorites:
            removeFavorite(self.user_id, eventID)
            widget.setFavorite(False)
            showAlert(self, "Favorite Removed", f"{eventID} removed from favorites.")
        else:
            saveFavorite(self.user_id, eventID)
            widget.setFavorite(True)
            showAlert(self, "Favorite Added", f"{eventID} added to favorites.")
    
    def showAbout(self):
        QMessageBox.information(self, "About", "ESPN Score Tracker\nDeveloped with PyQt5")   

    def handleLogoDownloaded(self, reply):
        if reply.error():
            reply.deleteLater()
            return
        
        url = reply.request().url().toString()
        data = reply.readAll()
        pix = QPixmap()
        if not pix.loadFromData(data):
            reply.deleteLater()
            return
        
        pix = pix.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        urlSTR = reply.url().toString()
        self.logo_cache[urlSTR] = pix
        
        items = self.pendingLogoItems.pop(urlSTR, [])
        for item in items:
            if item and not sip.isdeleted(item):
                if len(item.logo_urls) > 0 and item.logo_urls[0] == urlSTR:
                        item.leftLogoLabel.setPixmap(pix)
                if len(item.logo_urls) > 1 and item.logo_urls[1] == urlSTR:
                    item.rightLogoLabel.setPixmap(pix)
        
        reply.deleteLater()
        
        
if __name__ == "__main__":
    initDB()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
            