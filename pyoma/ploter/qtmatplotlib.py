'''
Created on 6 abr. 2017

@author: cruce
'''

# Librerias para graficar en el ploter
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
from PyQt4.Qt import QListWidgetItem


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
        self.cursors=[]

#     def axvlines(self, xs, **plot_kwargs):
#         import numpy as np
#         """
#         Draw vertical lines on plot
#         :param xs: A scalar, list, or 1D array of horizontal offsets
#         :param plot_kwargs: Keyword arguments to be passed to plot
# 
#         """
#         print (xs)
#         xs = np.array((xs, ) if np.isscalar(xs) else xs, copy=False)
#         lims = self.axes.get_ylim()
#         x_points = np.repeat(xs[:, None], repeats=3, axis=1).flatten()
#         y_points = np.repeat(np.array(lims + (np.nan, ))[None, :], repeats=len(xs), axis=0).flatten()
#         self.axes.plot(x_points, y_points, scaley = False, **plot_kwargs)

    def plotoma(self, espectro, plot_bkg=False, substract_bkg=False):

        self.axes.axes.cla()
        self.axes.grid(True)

        labels = []
        x = espectro.x
        y = espectro.getSpec(substract_bkg)
        labels.append(espectro.fname)
        bkg = espectro.bkg

        # Dibujar Curva
        self.axes.plot(x, y, color='b')
        if plot_bkg:

            self.axes.plot(x, bkg, color='g')
            labels.append('Background')

        self.axes.legend(labels, ncol=4, loc='upper center',
                         bbox_to_anchor=[0.5, 1.1],
                         columnspacing=1.0,
                         labelspacing=0.0,
                         handletextpad=0.0,
                         handlelength=1.5,
                         fancybox=True,
                         shadow=True)

        for c in self.cursors:
            self.axes.axvline(c.x, color=c.color)
        self.fig.canvas.draw()

    def multiplot(self, espectros=[], substract_bkg=False):

        self.axes.grid(True)
        if espectros:

            labels = []

            for spec in espectros:
                self.axes.plot(spec.x, spec.y - spec.bkg if substract_bkg else spec.y)
                labels.append(spec.fname)

            self.axes.legend(labels, ncol=4, loc='upper center',
                             bbox_to_anchor=[0.5, 1.1],
                             columnspacing=1.0,
                             labelspacing=0.0,
                             handletextpad=0.0,
                             handlelength=1.5,
                             fancybox=True,
                             shadow=True)

            for c in self.cursors:
                self.axes.axvline(c.x, color=c.color)

            self.fig.canvas.draw()


class cursor (QListWidgetItem):

    def __init__(self, text='', x=0, color='k'):
        QListWidgetItem.__init__(self)
        self.setText(text)
        self.x = x
        self.color = color


class NavigationToolbar(NavigationToolbar):
    pass
