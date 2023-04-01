# Se importan los archivos generados por Pyside2-uic
from .mainwindow import Ui_OMAIII
from PySide6.QtGui import (QIcon, QPixmap, QFont)
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import SIGNAL, Slot
from pyoma.ploter.QtMatplotLibPlot import canvas, NavigationToolbar

class MainApp (Ui_OMAIII):

    def setupUi(self, app):

        super(MainApp, self).setupUi(self)
        # self.widgetPlot(self.fr_main_plot)
        # Create a pixmap - not needed if you have your own.
        from pyoma.gui.splash import SplashScreen
        pixmap = QPixmap('./pyoma/gui/images/splash.png')
        self.splash = SplashScreen(pixmap)
        self.splash.setTitle('OMAIII DAQ')
        self.splash.show()
        self.splash.connect(self,
                            SIGNAL('splashUpdate(QString, int)'),
                            self.splash.showMessage
                            )
        # app.lb_kn_force.setStyleSheet("color: rgb(85, 255, 127);")
        font = QFont()
        font.setFamily("Exo 2")
        font.setPointSize(12)
        font.setWeight(QFont.Weight.Thin)
        font.setBold(False)
        app.setFont(font)

        icon = QIcon()
        icon.addPixmap(QPixmap("./pyoma/gui/images/logo-symbol-64x64.png"),
                       QIcon.Normal,
                       QIcon.Off
                       )
        app.setWindowIcon(icon)


    def load_cbx_data(self):

        for value in range(1,6):

            self.cbx_median_rank.addItem("Rank {}".format(value), str(value))

        self.cbx_aver_class.addItem("Digital Filter", "OFF")
        self.cbx_aver_class.addItem("Advanced Filter", "ON")
        self.cbx_aver_type.addItem("Moving filter", "MOVing")
        self.cbx_aver_type.addItem("Repeating filter", "REPeat")

        self.cbx_main_speed.addItem("0.01", 0.01)
        self.cbx_main_speed.addItem("FAST", 0.1)
        self.cbx_main_speed.addItem("MEDIUM", 1)
        self.cbx_main_speed.addItem("2 NPLC", 2)
        self.cbx_main_speed.addItem("3 NPLC", 3)
        self.cbx_main_speed.addItem("4 NPLC", 4)
        self.cbx_main_speed.addItem("SLOW", 5)


        self.cbx_aux_speed.addItem("0.006", 0.006)
        self.cbx_aux_speed.addItem("0.02", 0.02)
        self.cbx_aux_speed.addItem("0.06", 0.06)
        self.cbx_aux_speed.addItem("0.2", 0.2)
        self.cbx_aux_speed.addItem("1", 1)
        self.cbx_aux_speed.addItem("2", 2)
        self.cbx_aux_speed.addItem("10", 10)
        self.cbx_aux_speed.addItem("100", 100)

        self.cbx_aux_range.addItem("AUTO", "AUTO")
        self.cbx_aux_range.addItem("0.1", 0.1)
        self.cbx_aux_range.addItem("1", 1)
        self.cbx_aux_range.addItem("10", 10)
        self.cbx_aux_range.addItem("100", 100)
        self.cbx_aux_range.addItem("1000", 1000)

    @staticmethod
    def get_cbx_data(cbx):
        return cbx.itemData(cbx.currentIndex())

    def splash_message(self, message):
        self.emit(SIGNAL("splashUpdate(QString, int)"),
                  message,
                  132)

    @Slot(str)
    def change_messagge(self, message, duration=1000):
        self.statusbar.showMessage(message, duration)


    @staticmethod
    def change_widget_text_color(widget, r=255, g=255, b=255, a=100):
        widget.setStyleSheet("color: rgb({},{},{},{});".format(r, g, b, a))


    @Slot()
    def print_to_pte(self, text):
        self.pte_console.appendPlainText(text)

    @staticmethod
    def widgetPlot(widget):
        widget.setLayout(QVBoxLayout())
        widget.canvas = canvas(widget)
        widget.toolbar = NavigationToolbar(widget.canvas, widget)
        widget.layout().addWidget(widget.toolbar)
        widget.layout().addWidget(widget.canvas)