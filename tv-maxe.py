#!/usr/bin/env python3
import sys
import os
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QIcon, QPixmap

import icons_rc
from listManager import ListManager
from videoManager import VideoManager
from mediaProxy import MediaProxy
from tvmxutils import PLAYERSTATE_STOPPED, PLAYERSTATE_PLAYING
from tvmxutils import PLAYERSTATE_PAUSED


class TVMaxe(QtWidgets.QMainWindow):
    def __init__(self):
        super(TVMaxe, self).__init__()
        self.window = uic.loadUi('mainWindow.ui', self)
        self.listManager = ListManager(self.window.channelListWidget)
        self.videoManager = VideoManager(self.videoWindow)
        self.videoManager.stateChanged.connect(self.playerStateChanged)
        self.mediaProxy = MediaProxy(self)
        self.listManager.playUrl.connect(self.playUrl)
        self.mediaProxy.playReady.connect(self.playVideo)
        self.mediaProxy.bufferProgress.connect(self.updateProgress)

        # configure the UI
        self.window.statusbar.hide()
        self.window.bottomLayout.addWidget(QtWidgets.QSizeGrip(self.window))
        self.window.progressBar.hide()
        self.window.playPauseBtn.clicked.connect(self.playPause)
        self.window.stopBtn.clicked.connect(self.stop)
        self.window.fullscreenBtn.clicked.connect(self.switchFullscreen)
        self.window.volumeSlider.valueChanged.connect(
            self.videoManager.setVolume)
        self.window.splitter.setSizes([229, 475])
        self.window.splitter.setStretchFactor(1, 1)
        self.window.show()

        self.downloadChannelLists()

    def downloadChannelLists(self):
        self.listManager.getChannelLists()

    def playUrl(self, qurl):
        self.stop()
        url = qurl.toString()
        self.window.progressBar.show()
        self.window.progressBar.setValue(0)
        self.window.progressBar.setFormat("Loading...")
        self.mediaProxy.play(url)

    def updateProgress(self, p):
        if self.videoManager.mediaPlayer.state() == PLAYERSTATE_STOPPED:
            if p > 0:
                self.window.progressBar.show()
                self.window.progressBar.setValue(p)
                self.window.progressBar.setFormat("Loading: %p%")
        else:
            self.window.progressBar.hide()

    def playerStateChanged(self, state):
        if state == PLAYERSTATE_PLAYING:
            self.window.progressBar.hide()
            self.window.playPauseBtn.setIcon(
                QIcon(QPixmap(":/ico/icons/media-playback-pause.png")))
        elif state == PLAYERSTATE_STOPPED:
            self.window.playPauseBtn.setIcon(
                QIcon(QPixmap(":/ico/icons/media-playback-start.png")))
        elif state == PLAYERSTATE_PAUSED:
            self.window.playPauseBtn.setIcon(
                QIcon(QPixmap(":/ico/icons/media-playback-start.png")))

    def playVideo(self, url):
        if self.videoManager.mediaPlayer.state() == PLAYERSTATE_STOPPED:
            self.videoManager.playVideo(url)
            self.videoManager.setVolume(self.window.volumeSlider.value())

    def playPause(self):
        if self.videoManager.mediaPlayer.state() == PLAYERSTATE_PLAYING:
            self.videoManager.pauseVideo()
        else:
            self.videoManager.unpauseVideo()

    def stop(self):
        self.videoManager.stopVideo()
        self.mediaProxy.stop()

    def switchFullscreen(self, event=None):
        self.videoManager.switchFullscreen(event)

    def closeEvent(self, event):
        self.stop()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    app = QtWidgets.QApplication(sys.argv)
    tvmaxe = TVMaxe()
    sys.exit(app.exec_())
