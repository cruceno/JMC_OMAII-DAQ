'''
Created on 6 abr. 2017

@author: cruce
'''

# Librerias para graficar en el ploter
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure


class canvas(FigureCanvas):

    def __init__(self, parent):
        # Se instancia el objeto figure
        self.fig = Figure()
        # Se define la grafica en coordenadas polares
        self.axes = self.fig.add_subplot(111)
        # Se define una grilla
        self.axes.grid(True)
        # se inicializa FigureCanvas
        FigureCanvas.__init__(self, self.fig)

        # se define el widget padre
        self.setParent(parent)
        self.fig.canvas.draw()

    def plotoma(self, espectro, plot_bkg=False, substract_bkg=False):
        x = espectro.x
        y = espectro.getSpec(substract_bkg)
        bkg = espectro.bkg
        
        # Dibujar Curva
        self.axes.plot(x, y, color='b')
        if plot_bkg:
            self.axes.plot(x, bkg, color='g')
        self.fig.canvas.draw()

        

class NavigationToolbar(NavigationToolbar):
    pass
