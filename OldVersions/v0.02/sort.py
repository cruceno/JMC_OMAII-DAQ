'''
Created on 04/11/2011

@author: Javier Cruceno
'''
import os, sys, glob
import numpy as np
from PyQt4 import QtCore, QtGui, uic
from matplotlib.colors import NP_CLIP_OUT

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
    def on_tlb_open_clicked( self ):
        self.le_path.setText( QtGui.QFileDialog.getExistingDirectory( self, 'Open Folder' ) )

    @QtCore.pyqtSlot()
    def on_btn_sort_clicked( self ):
        self.lb_status.setText( 'Iniciado' )
        dir = str( self.le_path.text() ) + '\\'
        patron = dir + '*.OMAIII'
#        print patron
        archivos = filter( os.path.isfile, glob.glob( patron ) )
        espectros = []
        for espectro in archivos:
            self.lb_status.setText( ' Listando Espectros' )
            file = str( espectro )
            if not os.path.isdir( file ):
#                print file
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

    def preparar_datos( self, element, data, data_background, backgrounds ):
        self.lb_status.setText( ' Preparando datos' )
        for back in backgrounds:
            if back.exposuretime == element.exposuretime:
                background = back
                break
        background_y = np.genfromtxt( background.name, skiprows = 7, usecols = 1, delimiter = '\t', dtype = None )
        y = np.genfromtxt( element.name, skiprows = 7, usecols = 1, delimiter = '\t', dtype = None )
        i = 0
        for line in data:

            if i == 0:
                data[0] = line.rstrip( '\n' ) + '\t' + element.exposuretime
                data_background[0] = data_background[0].rstrip( '\n' ) + '\t' + background.exposuretime
            elif i == 1:
                data[1] = line.rstrip( '\n' ) + '\t' + element.scansnumber
                data_background[1] = data_background[1].rstrip( '\n' ) + '\t' + background.scansnumber
            elif i == 2:
                data[2] = line.rstrip( '\n' ) + '\t' + element.ignoredscans
                data_background[2] = data_background[2].rstrip( '\n' ) + '\t' + background.ignoredscans
            elif i == 3:
                data[3] = line.rstrip( '\n' ) + '\t' + element.damode
                data_background[3] = data_background[3].rstrip( '\n' ) + '\t' + background.damode
            elif i == 4:
                data[4] = line.rstrip( '\n' ) + '\t' + element.detectortemp
                data_background[4] = data_background[4].rstrip( '\n' ) + '\t' + background.detectortemp
            elif i == 5:
                data[5] = line.rstrip( '\n' ) + '\t' + element.red
                data_background[5] = data_background[5].rstrip( '\n' ) + '\t' + background.red
            elif i == 6:
                data[6] = line.rstrip( '\n' ) + '\t' + element.counter
                data_background[6] = data_background[6].rstrip( '\n' ) + '\t' + background.counter
            elif i == 7:
                data[7] = line.rstrip( '\n' ) + '\t' + os.path.basename( element.name ) + '\n'
                data_background[7] = data_background[7].rstrip( '\n' ) + '\t' + os.path.basename( background.name ) + '\n'
            else:
                i2 = i - 8
                data[i] = line.rstrip( '\n' ) + '\t' + str( y[i2] ) + '\n'
                data_background[i] = data_background[i].rstrip( '\n' ) + '\t' + str( background_y[i2] ) + '\n'
            i = i + 1
#            print i

        return data, data_background

    def primera_columna( self, filename ):
        self.lb_status.setText( 'Imprimiendo priemra columna' )
        background_filename = os.path.splitext( filename )[0] + '_Backgrounds' + os.path.splitext( filename )[1]

        fsock = open( filename, 'w' )
        fsock_back = open( background_filename, 'w' )

        # Escritura de la primera columna del archivo
        x = np.arange( 1, 1025, 1 )
        fsock.write( '/* Tiempo de exposicion:\n/* Numero de Scans\n/* Scans Ignorados\n/* Modo de Adquiquisicion\n/* Temperatura del detector\n/*Red\n/*Posicion del Contador\n/*Archivo:\n' )
        for i in np.nditer( x ):
            line = str( i ) + '\n'
            fsock.write( line )
        fsock.close()
        fsock = open( filename, 'r' )
        data = fsock.readlines()
        fsock.close()

        # Escritura de la primera columna del archivo de backgrounds
        fsock_back.write( '/*Tiempo de exposicion:\n/*Numero de Scans\n/*Scans Ignorados\n/*Modo de Adquiquisicion\n/*Temperatura del detector\n/*Red\n/*Posicion del Contador\n/*Archivo:\n' )
        for i in np.nditer( x ):
            line = str( i ) + '\n'
            fsock_back.write( line )
        fsock_back.close()
        fsock_back = open( background_filename, 'r' )
        data_background = fsock_back.readlines()
        fsock_back.close()
        os.remove( background_filename )

        return data, data_background

    def sort_espectros( self, espectros ):
        self.lb_status.setText( 'Ordenando espectros' )
        posiciones = []
        current = None

        for espectro in espectros:
            if current != espectro.counter:
                if posiciones.count( espectro.counter ) == 0:
                    posiciones.append( espectro.counter )
                current = espectro.counter

#        print posiciones

#         Guardamos los backgrounds en una lista
        backgrounds = []
        for espectro in espectros:
            if int ( espectro.counter ) == 000:
                backgrounds.append( espectro )
        # print backgrounds
        for counter in posiciones:
            self.lb_status.setText( 'Guardando archivo' )
            # Archivos de salida
            filename = os.path.dirname( espectro.name ) + '\\E' + counter.rstrip( '\n' ) + '.txt'
            backgrounds_filename = os.path.dirname( espectro.name ) + '\\Backgrounds_E' + counter.rstrip( '\n' ) + '.txt'
            exp_time_file = os.path.dirname( espectro.name ) + '\\E_ExpTimes' + counter.rstrip( '\n' ) + '.txt'

#            print filename
            filtradas = []
            for espectro in espectros:
                if counter == espectro.counter:
                    filtradas.append( espectro )
            try:
                fsock = open( filename, 'r' )
                data = fsock.readlines()
                fsock.close()
            except:
                data, data_background = self.primera_columna( filename )
#            print filtradas
            fsock_exptime = open ( exp_time_file, 'w' )
            i = 1
            for element in sorted( filtradas, key = lambda espectro: espectro.name ):
                data, data_background = self.preparar_datos( element, data, data_background, backgrounds )
                line = str ( i ) + '\t' + str ( element.exposuretime )
                fsock_exptime.write( line )
                i += 1
            fsock_exptime.close()
            # Escribimos todos los datos en el archivo de espectros
            fsock = open( filename, 'w' )
            for line in data:
                fsock.write( str( line ) )
            fsock.close()

            # Escribimos todos los datos del archivo de backgrounds
            fsock = open( backgrounds_filename, 'w' )
            for line in data_background:
                fsock.write( str( line ) )
            fsock.close()
        self.lb_status.setText( 'Finalizado' )

def sort():
    app = QtGui.QApplication( sys.argv )
    Sort = SortDialog()
    Sort.show()
    sys.exit( app.exec_() )
sort()
