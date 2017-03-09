# -*- coding: utf-8 -*-
'''
Created on 22/09/2011
Corregir guardado de tiempo de exposicion para evitar errores
@author: Solar
'''
from PyQt4 import QtCore, QtGui, uic
import os, sys, serial, time, sort
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
global counter

class Lienzo( FigureCanvas ):

    def __init__( self, parent, y ):
        # Se instancia el objeto figure
        self.fig = Figure()
        # Se define la grafica en coordenadas polares
        self.axes = self.fig.add_subplot( 111 )
                # Se define el limite del eje X
        x = np.arange( 1, 1025, 1 )
        self.axes.plot( x, y )
        self.axes.set_xlim( [1, 1024] )

        # Se define una grilla
        self.axes.grid( True )
        # Se crea una etiqueta en el eje Y
        self.axes.set_ylabel( 'Counts' )
        self.axes.set_xlabel( '' )

        # se inicializa FigureCanvas
        FigureCanvas.__init__( self, self.fig )
        # se define el widget padre
        self.setParent( parent )
        # se define el widget como expandible
        FigureCanvas.setSizePolicy( self,
                QtGui.QSizePolicy.Expanding,
                QtGui.QSizePolicy.Expanding )
        # se notifica al sistema de la actualizacion
        # de la politica
        FigureCanvas.updateGeometry( self )
        self.fig.canvas.draw()

class Main( QtGui.QMainWindow ):
    """La ventana principal de la aplicacion."""

    def __init__( self ):
        QtGui.QMainWindow.__init__( self )
        # Cargamos la interfaz desde el archivo .ui
        uifile = os.path.join( 
             os.path.abspath( 
                 os.path.dirname( __file__ ) ), 'main.ui' )
        uic.loadUi( uifile, self )

        self.actionQuit.triggered.connect( QtGui.qApp.quit )
        self.actionSort.triggered.connect( sort.sort() )

        self.ser = serial.Serial( port = 'COM18',
                                  baudrate = 9600,
                                  parity = serial.PARITY_NONE,
                                  stopbits = 1,
                                  bytesize = 8,
                                  timeout = 2 )

        self.qmc = False

    def Plotear( self, y ):
        self.statusBar().showMessage( 'Ploting...' )
        if not self.qmc:
            self.vbl = QtGui.QVBoxLayout( self.Plot )
            # Se instancia el Lienzo con la grafica de Matplotlib
            if self.chk_autobkgsus.checkState():
                if self.le_selectedbkg.text() == '':
                    self.le_selectedbkg.setText( QtGui.QFileDialog.getOpenFileName( parent = None, caption = 'Open Background File' ) )
                else:
                    background = np.genfromtxt( str( self.le_selectedbkg.text() ), skiprows = 7, useecols = 1, delimiter = '\t' )
                    y = y - background
            self.qmc = Lienzo( self.Plot, y )
            # se instancia la barra de navegacion
            self.ntb = NavigationToolbar( self.qmc, self.Plot )
            # se empaqueta el lienzo y
            # la barra de navegacion en el vbox
            self.vbl.insertWidget( 0, self.qmc )
            self.vbl.insertWidget( 1, self.ntb )
        else:
            QtGui.QLayout.removeWidget( self.vbl, self.qmc )
            QtGui.QLayout.removeWidget( self.vbl, self.ntb )
            if self.chk_autobkgsus.checkState():
                if self.le_selectedbkg.text() == '':
                    self.le_selectedbkg.setText( QtGui.QFileDialog.getOpenFileName( parent = None, caption = 'Open Background File' ) )
                else:
                    background = np.genfromtxt( str( self.le_selectedbkg.text() ), skiprows = 7, usecols = 1, delimiter = '\t' )
                    y = y - background
            self.qmc = Lienzo( self.Plot, y )
            # se instancia la barra de navegacion
            self.ntb = NavigationToolbar( self.qmc, self.Plot )
            # se empaqueta el lienzo y
            # la barra de navegacion en el vbox
            self.vbl.insertWidget( 0, self.qmc )
            self.vbl.insertWidget( 1, self.ntb )
        if np.max( y ) >= 4096 :
            self.statusBar().showMessage( 'SATURATED AT' + str( np.argmax( y ) ) )
        else:
            self.statusBar().showMessage( 'Ready...' )

    @QtCore.pyqtSlot()
    def on_le_exposuretime_editingFinished( self ):
        self.btn_run.setEnabled( False )
        self.btn_update.setEnabled( True )

    @QtCore.pyqtSlot()
    def on_le_damode_editingFinished( self ):
        self.btn_run.setEnabled( False )
        self.btn_update.setEnabled( True )

    @QtCore.pyqtSlot()
    def on_le_scansnumber_editingFinished( self ):
        self.btn_run.setEnabled( False )
        self.btn_update.setEnabled( True )

    @QtCore.pyqtSlot()
    def on_le_detectortemp_editingFinished( self ):
        self.btn_run.setEnabled( False )
        self.btn_update.setEnabled( True )

    @QtCore.pyqtSlot()
    def on_le_ignoredscans_editingFinished( self ):
        self.btn_run.setEnabled( False )
        self.btn_update.setEnabled( True )

    @QtCore.pyqtSlot()
    def on_actionSave_triggered ( self ):
        filename = QtGui.QFileDialog.getSaveFileName( self, 'Save File', '.' )
        if filename:
            self.on_btn_check_clicked()
            header = self.le_exposuretime.text() + '\n'
            header = header + self.le_scansnumber.text() + '\n'
            header = header + self.le_ignoredscans.text() + '\n'
            header = header + self.le_damode.text() + '\n'
            header = header + self.le_detectortemp.text()
            header = header + '\n' + self.le_red.text() + '\n'
            header = header + self.le_counter.text() + '\n'
            filename = filename + '.OMAIII'
            fsock = open( filename, 'w' )
            fsock.write( header )
            x = np.arange( 1, 1025, 1 )
            index = 0
            for Value in np.nditer( x ):

                y = str( self.espectro[index] )
                x = str( Value )
                line = x + '\t' + y + '\n'
                fsock.write( line )
                index = index + 1
            fsock.close()

    @QtCore.pyqtSlot()
    def on_btn_run_pressed ( self ):
        """Proceso de Scan"""
        self.btn_run.setEnabled( False )
        while self.btn_run.isEnabled():
            print 'iniciando adquisicion'
            continue
        self.ser.close()

        if self.chk_continuous.checkState():
            self.ser.open()
            while self.chk_continuous.checkState():
                time.sleep( 5 )
                print 'run'
                self.ser.write( 'RUN\r\n' )
                while self.ser.read() != '*':
                    self.statusBar().showMessage( 'OMA Running...' )
                    continue

                self.ser.write( 'DC 1,1,1024\r\n' )
                while self.ser.inWaiting < 4096:
                    self.statusBar().showMessage( 'Reading Curve...' )
                    continue
                r = self.ser.readline().rstrip( '\r\n' )
                self.ser.close()
                self.espectro = np.fromstring( r, sep = ',' )
                self.espectro = np.arange( 1, 1025, 1 )
                self.Plotear( self.espectro )
                if self.chk_autosave.checkState():
                    counter = int( self.le_initvalue.text() )
                    if counter < 10:
                        file = self.le_basename.text() + '_000' + str( counter )
                    elif 9 < counter < 100:
                        file = self.le_basename.text() + '_00' + str( counter )
                    elif 99 < counter < 1000:
                        file = self.le_basename.text() + '_0' + str( counter )
                    else:
                        file = self.le_basename.text() + '_' + str( counter )

                    self.on_btn_check_clicked()
                    header = self.le_exposuretime.text() + '\n'
                    header = header + self.le_scansnumber.text() + '\n'
                    header = header + self.le_ignoredscans.text() + '\n'
                    header = header + self.le_damode.text() + '\n'
                    header = header + self.le_detectortemp.text()
                    header = header + '\n' + self.le_red.text() + '\n'
                    header = header + self.le_counter.text() + '\n'
                    file = file + 'OMAIII'
                    fsock = open( file, 'w' )
                    fsock.write( header )

                    x = np.arange( 1, 1025, 1 )
                    index = 0

                    for Value in np.nditer( x ):

                        y = str( self.espectro[index] )
                        x = str( Value )
                        line = x + '\t' + y + '\n'
                        fsock.write( line )
                        index = index + 1

                    fsock.close()
                    counter = int( counter ) + 1
                    self.le_initvalue.setText( str( counter ) )
        else:
            self.ser.open()
            self.ser.write( 'RUN\r\n' )
            self.statusBar().showMessage( 'OMA Running...' )
            while self.ser.read() != '*':
                continue

            self.ser.write( 'DC 1,1,1024\r\n' )
            self.statusBar().showMessage( 'Reading Curve...' )
            while self.ser.inWaiting < 4096:
                continue
            r = self.ser.readline().rstrip( '\r\n' )
            self.ser.close()
            self.espectro = np.fromstring( r, sep = ',' )
            self.Plotear( self.espectro )
            self.Plot.update()

        if self.chk_autosave.checkState():

            counter = int( self.le_initvalue.text() )
            if counter < 10:
                file = self.le_basename.text() + '_000' + str( counter )
            elif 9 < counter < 100:
                file = self.le_basename.text() + '_00' + str( counter )
            elif 99 < counter < 1000:
                file = self.le_basename.text() + '_0' + str( counter )
            else:
                file = self.le_basename.text() + '_' + str( counter )

            self.on_btn_check_clicked()
            header = self.le_exposuretime.text() + '\n'
            header = header + self.le_scansnumber.text() + '\n'
            header = header + self.le_ignoredscans.text() + '\n'
            header = header + self.le_damode.text() + '\n'
            header = header + self.le_detectortemp.text()
            header = header + '\n' + self.le_red.text() + '\n'
            header = header + self.le_counter.text() + '\n'
            file = file + 'OMAIII'
            fsock = open( file, 'w' )
            fsock.write( header )
            x = np.arange( 1, 1025, 1 )

            index = 0

            for Value in np.nditer( x ):

                y = str( self.espectro[index] )
                x = str( Value )
                line = x + '\t' + y + '\n'
                fsock.write( line )
                index = index + 1

            fsock.close()
            counter = int( counter ) + 1
            self.le_initvalue.setText( str( counter ) )
        self.btn_run.setEnabled( True )

    @QtCore.pyqtSlot()
    def on_btn_stop_clicked( self ):
        """Abortar Scan"""
        self.chk_continuous.setCheckState( QtCore.Qt.Unchecked )

    @QtCore.pyqtSlot()
    def on_btn_check_clicked( self ):
        self.ser.close()
        self.ser.open()
        """Consultar Parametros de Scan"""
        self.ser.write( 'ET\r\n' )
        ET = self.ser.readline().rstrip( '\r\n' )

        if self.ser.read() == '*':
            self.le_exposuretime.setText( ET )

        self.ser.write( 'DT\r\n' )
        DT = self.ser.readline().rstrip( '\r\n' )

        if self.ser.read() == '*':
            self.le_detectortemp.setText( DT )

        self.ser.write( 'DA\r\n' )
        DA = self.ser.readline().rstrip( '\r\n' )

        if self.ser.read() == '*':
            self.le_damode.setText( DA )

        self.ser.close()

    @QtCore.pyqtSlot()
    def on_btn_update_clicked( self ):
        """Update Scan Sequence Settings"""
        self.ser.close()
        self.ser.open()
        ET = 'ET ' + self.le_exposuretime.text() + '\r\n'
        self.ser.write( ET )

        if self.ser.read() == '*':
            pass

        DT = 'DT ' + self.le_detectortemp.text() + '\r\n'
        self.ser.write( DT )

        if self.ser.read() == '*':
            pass

        DA = 'DA ' + self.le_damode.text() + '\r\n'
        self.ser.write( DA )

        if self.ser.read() == '*':
            pass
        I = 'I ' + self.le_scansnumber.text() + '\r\n'
        self.ser.write( I )

        if self.ser.read() == '*':
            pass

        K = 'K ' + self.le_ignoredscans.text() + '\r\n'
        self.ser.write( K )

        if self.ser.read() == '*':
            pass

        self.btn_run.setEnabled( True )
        self.btn_update.setEnabled( False )

    @QtCore.pyqtSlot()
    def on_tlb_basename_pressed( self ):
        filename = QtGui.QFileDialog.getSaveFileName( self, 'Save File', os.path.pardir )
        if filename:
            self.le_basename.setText( filename )

    @QtCore.pyqtSlot()
    def on_tlb_selectbkg_pressed( self ):
        self.le_selectedbkg.setText( QtGui.QFileDialog.getOpenFileName( parent = None, caption = 'Open Background File' ) )

    @QtCore.pyqtSlot()
    def on_btn_sustractbkg_pressed( self ):
        if self.le_selectedbkg.text() == '':
            self.le_selectedbkg.setText( QtGui.QFileDialog.getOpenFileName( parent = None, caption = 'Open Background File' ) )
        else:
            background = np.genfromtxt( str( self.le_selectedbkg.text() ), skiprows = 7, usecols = 1, delimiter = '\t' )
            y = self.espectro - background
            self.Plotear( y )
    def get_config( self ):
        """Obtener configuracion y estado del OMA"""
        self.ser.close()
        self.ser.open()
        self.ser.write( 'ID\r\n' )
        status = self.ser.readline().rstrip( '\r\n' )
        self.ser.read()
        self.ser.close()
        print status
        if status == 1461:
            self.statusBar().showMessage( 'Ready' )


def main():
    app = QtGui.QApplication( sys.argv )
    OMAIII = Main()
    OMAIII.show()


    sys.exit( app.exec_() )

if __name__ == "__main__":
    main()
