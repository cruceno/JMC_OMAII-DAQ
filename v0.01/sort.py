'''
Created on 04/11/2011

@author: Solar
'''
import os, sys
import numpy as np
from PyQt4 import QtCore, QtGui, uic



class Espectro( object ):
    def __init__( self, file, exposuretime, scansnumber, ignoredscans, damode, detectortemp, counter, red ):
        self.name = file
        self.exposuretime = exposuretime
        self.scansnumber = scansnumber
        self.ignoredscans = ignoredscans
        self.damode = damode
        self.detectortemp = detectortemp
        self.counter = counter
        self.red = red
    def __repr__( self ):
        return repr( ( self.name, self.counter, self.red ) )

class SortDialog ( QtGui.QDialog ):
    def __init__( self ):
        QtGui.QDialog.__init__( self )
                # Cargamos la interfaz desde el archivo .ui
        uifile = os.path.join( 
             os.path.abspath( 
                 os.path.dirname( __file__ ) ), 'sort.ui' )
        uic.loadUi( uifile, self )

    @QtCore.pyqtSlot()
    def on_tlb_open_pressed( self ):
        self.le_path.setText( QtGui.QFileDialog.getExistingDirectory( self, 'Open Folder' ) )

    @QtCore.pyqtSlot()
    def on_tlb_save_pressed( self ):
        self.le_save_path.setText( QtGui.QFileDialog.getSaveFileName( self, 'Save File', os.path.pardir ) )
    @QtCore.pyqtSlot()
    def on_btn_sort_pressed( self ):
        archivos = os.listdir( self.le_path.text() )
        espectros = []
        for espectro in archivos:

            file = self.le_path.text() + '\\' + str( espectro )
            if not os.path.isdir( file ):
                print file
                fsock = open ( file, 'r' )
                exposuretime = fsock.readline()
                scansnumber = fsock.readline()
                ignoredscans = fsock.readline()
                damode = fsock.readline()
                detectortemp = fsock.readline()
                red = fsock.readline()
                counter = fsock.readline()
                fsock.close()
                espectros.append( Espectro( str( file ), exposuretime, scansnumber, ignoredscans, damode, detectortemp, counter, red ) )
        self.sort_espectros( espectros )

    def preparar_datos( self, element, data ):
        print 'preparando datos'
        y = np.genfromtxt( element.name, skiprows = 3, usecols = 1, delimiter = '\t', dtype = None )
        i = 0
        for line in data:
            if i == 0:
                data[0] = data[0].rstrip( '\n' ) + '\t' + element.exposuretime
            elif i == 1:
                data[1] = data[1].rstrip( '\n' ) + '\t' + element.scansnumber
            elif i == 2:
                data[2] = data[2].rstrip( '\n' ) + '\t' + element.ignoredscans
            elif i == 3:
                data[3] = data[3].rstrip( '\n' ) + '\t' + element.damode
            elif i == 4:
                data[4] = data[4].rstrip( '\n' ) + '\t' + element.detectortemp
            elif i == 5:
                data[5] = data[5].rstrip( '\n' ) + '\t' + element.red
            elif i == 6:
                data[6] = data[6].rstrip( '\n' ) + '\t' + element.counter
            else:
                i2 = i - 7
                data[i] = data[i].rstrip( '\n' ) + '\t' + str( y[i2] ) + '\n'
            i = i + 1
        return data

    def sort_espectros( self, espectros ):
        print 'ordenando espectros'
        fsock = open( str( self.le_save_path.text() ), 'w' )
        x = np.arange( 1, 1024, 1 )
        fsock.write( 'Tiempo de exposicion:\nNumero de Scans\nScans Ignorados\nModo de Adquiquisicion\nTemperatura del detector\nPosicion del Contador\nRed\n' )
        for i in np.nditer( x ):
            line = str( i ) + '\n'
            fsock.write( line )
        fsock.close()
        fichero = open( str( self.le_save_path.text() ), 'r' )
        data = fichero.readlines()
        fichero.close()

        if self.rb_exp_time.isChecked():
            for element in sorted( espectros, key = lambda espectro: espectro.exposuretime ):
                data = self.preparar_datos( element, data )
        elif self.rb_counter.isChecked():
            for element in sorted( espectros, key = lambda espectro: espectro.counter ):
                data = self.preparar_datos( element, data )
        elif self.rb_red.isChecked():
            for element in sorted( espectros, key = lambda espectro: espectro.red ):
                data = self.preparar_datos( element, data )

        #Escribimos todos los datos en el archivo
        fsock = open( str( self.le_save_path.text() ), 'w' )
        print 'guardando archivo'
        for line in data:
            fsock.write( str( line ) )
        fsock.close()

def sort():
    app = QtGui.QApplication( sys.argv )
    Sort = SortDialog()
    Sort.show()
    sys.exit( app.exec_() )
