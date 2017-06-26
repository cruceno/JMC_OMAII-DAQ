# -*- coding: utf-8 -*-
'''
Created on 13 abr. 2017

@author: javit
'''

from PyQt4.QtGui import QSplashScreen, QFontDatabase, QFont, QLabel, QProgressBar

QFontDatabase.addApplicationFont("./fonts/EXO2REGULAR.TTF")


class SplashScreen(QSplashScreen):
    ''' Splash con logos mostrado al inicio de la aplicacion '''

    def __init__(self, pixmap):
        super(SplashScreen, self).__init__(pixmap)

        self._title = QLabel(self)
        self._title.setGeometry(50 * self.width() / 100,
                                20 * self.height() / 100,
                                50 * self.width() / 100,
                                11 * self.height() / 100
                                )
        self._title.setStyleSheet('QLabel { color : rgb(191,180,110); }')
        font = QFont('Exo 2')
        font.setPixelSize(36)
        font.setBold(True)
        font.setItalic(True)
        self._title.setFont(font)

        font = QFont('Exo 2')
        font.setPixelSize(16)
        font.setBold(False)
        font.setItalic(True)
        self.setFont(font)

        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(self.width() / 10,
                                     8 * self.height() / 10,
                                     8 * self.width() / 10,
                                     self.height() / 30)

    def setTitle(self, title):

        self._title.setText(title)

    def moveTitle(self, x1, y1, w, h):

        self._title.setGeometry(x1, y1, w, h)

    def mousePressEvent(self, event):
        pass
