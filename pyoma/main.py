# -*- coding: utf-8 -*-
'''
Created on 22/09/2011

@author: Javier Cruceno
'''
# Importar librerias del sistema
import os
import sys
import time
# Imortar libreria para manejo de puertos serie
import serial

# Importar libreria para manejo de archivos de configuracion
from configobj import ConfigObj

# importar libreria para el manejo de datos numericos
import numpy as np

# Importar backends y librerias necesarias para graficar los datos
# Importar librerias de interfaz grafica
from PyQt4 import QtGui, QtCore
from pyoma.gui.mainwindow import Ui_OMAIII
from pyoma.instrument.oma import spectrum
from pyoma.worker.scan import Scanner
from pyoma.instrument.serialutil import scan_serial_ports

class OMAIIIuiAPP(QtGui.QMainWindow, Ui_OMAIII):
    """La ventana principal de la aplicacion."""

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        # Cargamos la interfaz grafica
        # Create a pixmap - not needed if you have your own.
        from pyoma.gui.splash import SplashScreen
        pixmap = QtGui.QPixmap('./gui/images/splash.png')
        self.splash = SplashScreen(pixmap)
        self.splash.setTitle('OMAIII DAQ')
        self.splash.show()
        self.splash.connect(self,
                   QtCore.SIGNAL('splashUpdate(QString, int)'),
                   self.splash.showMessage)
        self.setupUi(self)
        # Cargamos archivo de configuracion predeterminado
        # Estudiar caso en que el archivo de configuracion no exista
        self.config = ConfigObj('omaiii.ini')
        self.scaner = Scanner()

    def connect_thread(self):
        self.emit(QtCore.SIGNAL("splashUpdate(QString, int)"),
                  'Connect to thread . . .',
                  132)

        # Configurar subproceso encargado de la comunicacion con el OMA
        self.thread = QtCore.QThread()
        self.thread.started.connect(self.scaner.scan)
        self.connect(self.scaner, QtCore.SIGNAL("finished()"), self.thread.quit)
        # Conectar señales y funciones
        self.connect(self.scaner, QtCore.SIGNAL("scansignal(PyQt_PyObject)"), self.incoming_data)
        self.connect(self.scaner, QtCore.SIGNAL("msgsignal(PyQt_PyObject)"), self.change_messagge)
        self.connect(self.scaner, QtCore.SIGNAL("finished()"), self.update_ui)
        self.connect(self.scaner, QtCore.SIGNAL("terminated()"), self.update_ui)
        self.scaner.moveToThread(self.thread)

    def load_oma_scan_settings(self):

        scan_settings = self.config['scanSettings']
        self.le_exposuretime.setText(scan_settings['exposuretime'])
        self.le_detectortemp.setText(scan_settings['detectortemp'])
        self.le_damode.setText(scan_settings['damode'])
        self.le_scansnumber.setText(scan_settings['scannumber'])
        self.le_ignoredscans.setText(scan_settings['ignoredscans'])
        self.sp_loop.setValue(int(scan_settings['scansloop']))
        if scan_settings['background_action'] == 'save':
            self.rb_bkg_save_only.setChecked(True)
        elif scan_settings['background_action'] == 'auto':
            self.rb_bkg_auto.setChecked(True)
        elif scan_settings['background_action'] == 'plot':
            self.rb_bkg_plot.setChecked(True)
        self.rb_spectrum.setChecked(True)

    def get_serial_config(self):
        self.emit(QtCore.SIGNAL("splashUpdate(QString, int)"),
                  'Loading conected devices . . .',
                  132)
        
        # Obtener listado de puertos serie presentes en el equipo
        ports = scan_serial_ports(30, False)
        self.set_ui_serial_controls(ports)
        # Acceder a la configuracion guardada
        serialConfig = self.config['serialConfig']
        # Instanciar objeto serial
        self.ser = serial.Serial()

        if(serialConfig['port'] != '' and serialConfig['port'] in ports):
            self.ser.port = serialConfig['port']
            self.cbx_serial_port.setCurrentIndex(self.cbx_serial_port.findText(serialConfig['port']))
        else:
            self.ser.port = ports[0][1]
            self.cbx_serial_port.setCurrentIndex(self.cbx_serial_port.findText(self.ser.name))
        if(serialConfig['baudrate'] != '' and serialConfig['baudrate'] in self.ser.BAUDRATES):
            self.ser.baudrate = serialConfig['baudrate']
            self.cbx_serial_baudrates.setCurrentIndex(self.cbx_serial_baudrates.findData(serialConfig['baudrate']))
        else:
            self.cbx_serial_baudrates.setCurrentIndex(self.cbx_serial_baudrates.findData(self.ser.baudrate))
        if(serialConfig['parity'] != '' and serialConfig['parity'] in self.ser.PARITIES):
            self.ser.parity = serialConfig['parity']
            self.cbx_serial_parities.setCurrentIndex(self.cbx_serial_parities.findData(serialConfig['parity']))
        else:
            self.cbx_serial_parities.setCurrentIndex(self.cbx_serial_parities.findData(self.ser.parity))
        if(serialConfig['stopbits'] != '' and serialConfig['stopbits'] in self.ser.STOPBITS):
            self.ser.stopbits = serialConfig['stopbits']
            self.cbx_serial_stopbits.setCurrentIndex(self.cbx_serial_stopbits.findData(serialConfig['stopbits']))
        else:
            self.cbx_serial_stopbits.setCurrentIndex(self.cbx_serial_stopbits.findData(self.ser.stopbits))
        if(serialConfig['bytesize'] != '' and serialConfig['bytesize'] in self.ser.BYTESIZES):
            self.ser.byteSize = serialConfig['bytesize']
            self.cbx_serial_bytesizes.setCurrentIndex(self.cbx_serial_bytesizes.findData(serialConfig['bytesize']))
        else:
            self.cbx_serial_bytesizes.setCurrentIndex(self.cbx_serial_bytesizes.findData(self.ser.bytesize))
        self.sp_serial_timeout.setValue(int(serialConfig['timeout']))

    def load_plot_settings(self):
        self.emit(QtCore.SIGNAL("splashUpdate(QString, int)"),
                  'Load Plot Settings . . .',
                  132)
        plot_config = self.config['plotSettings']
        self.chk_show_grid_lines.setChecked(int(plot_config['grid']))
        self.chk_show_plot_toolbar.setChecked(int(plot_config['toolbar']))

    def load_output_fileconfig(self):
        self.emit(QtCore.SIGNAL("splashUpdate(QString, int)"),
                  'Load File Output Settings. . .',
                  132)
        output_file_cfg = self.config['fileFormat']
        self.cbx_file_separator.setCurrentIndex(self.cbx_file_separator.findText(output_file_cfg['column_sep']))
        self.le_file_comment_string.setText(output_file_cfg['comment_char'])
        self.le_basename.setText(output_file_cfg['basename'])

    def load_monochromathor_config(self):
        self.emit(QtCore.SIGNAL("splashUpdate(QString, int)"),
                  'Load Monochromator info . . .',
                  132)
        monochromatorConfig = self.config['monochromatorConfig']
        self.daq_sp_monochromator_counter.setValue(int(monochromatorConfig['counter']))
        index=self.daq_cbx_monochromator_grating.findData(monochromatorConfig['selected_grating'])
        self.daq_cbx_monochromator_grating.setCurrentIndex(index)
        self.le_monochromator_g1_lines.setText(monochromatorConfig['g1']['lines'])
        self.le_monochromator_g1_amplitude.setText(monochromatorConfig['g1']['amplitude'])
        self.le_monochromator_g1_resolution.setText(monochromatorConfig['g1']['resolution'])
        self.dsb_monochromator_g1_factor.setValue(float(monochromatorConfig['g1']['factor']))

        self.le_monochromator_g2_lines.setText(monochromatorConfig['g2']['lines'])
        self.le_monochromator_g2_amplitude.setText(monochromatorConfig['g2']['amplitude'])
        self.le_monochromator_g2_resolution.setText(monochromatorConfig['g2']['resolution'])
        self.dsb_monochromator_g2_factor.setValue(float(monochromatorConfig['g2']['factor']))

        self.le_monochromator_g3_lines.setText(monochromatorConfig['g3']['lines'])
        self.le_monochromator_g3_amplitude.setText(monochromatorConfig['g3']['amplitude'])
        self.le_monochromator_g3_resolution.setText(monochromatorConfig['g3']['resolution'])
        self.dsb_monochromator_g3_factor.setValue(float(monochromatorConfig['g3']['factor']))
    
    @QtCore.pyqtSlot()
    def on_daq_sp_monochromator_counter_valueChanged(self):
        self.config['monochromatorConfig']['counter']=self.daq_sp_monochromator_counter.value()
    @QtCore.pyqtSlot()
    def on_le_monochromator_g1_lines_editingFinished(self):
        self.config['monochromatorConfig']['g1']['lines']=self.le_monochromator_g1_lines.text()
    @QtCore.pyqtSlot()
    def on_le_monochromator_g1_amplitude_editingFinished(self):
        self.config['monochromatorConfig']['g1']['amplitude']=self.le_monochromator_g1_amplitude.text()
    @QtCore.pyqtSlot()
    def on_le_monochromator_g1_resolution_editingFinished(self):
        self.config['monochromatorConfig']['g1']['resolution']=self.le_monochromator_g1_resolution.text()
    @QtCore.pyqtSlot()
    def on_dsb_monochromator_g1_factor_valueChanged(self):
        self.config['monochromatorConfig']['g1']['factor']=self.dsb_monochromator_g1_factor.value()
    @QtCore.pyqtSlot()
    def on_le_monochromator_g2_lines_editingFinished(self):
        self.config['monochromatorConfig']['g2']['lines']=self.le_monochromator_g2_lines.text()
    @QtCore.pyqtSlot()
    def on_le_monochromator_g2_amplitude_editingFinished(self):
        self.config['monochromatorConfig']['g2']['amplitude']=self.le_monochromator_g2_amplitude.text()
    @QtCore.pyqtSlot()
    def on_le_monochromator_g2_resolution_editingFinished(self):
        self.config['monochromatorConfig']['g2']['resolution']=self.le_monochromator_g2_resolution.text()
    @QtCore.pyqtSlot()
    def on_dsb_monochromator_g2_factor_valueChanged(self):
        self.config['monochromatorConfig']['g2']['factor']=self.dsb_monochromator_g2_factor.value()
    @QtCore.pyqtSlot()
    def on_le_monochromator_g3_lines_editingFinished(self):
        self.config['monochromatorConfig']['g3']['lines']=self.le_monochromator_g3_lines.text()
    @QtCore.pyqtSlot()
    def on_le_monochromator_g3_amplitude_editingFinished(self):
        self.config['monochromatorConfig']['g3']['amplitude']=self.le_monochromator_g3_amplitude.text()
    @QtCore.pyqtSlot()
    def on_le_monochromator_g3_resolution_editingFinished(self):
        self.config['monochromatorConfig']['g3']['resolution']=self.le_monochromator_g3_resolution.text()
    @QtCore.pyqtSlot()
    def on_dsb_monochromator_g3_factor_valueChanged(self):
        self.config['monochromatorConfig']['g3']['factor']=self.dsb_monochromator_g3_factor.value() 
          
    def set_ui_serial_controls(self, ports=[]):

        ''' Esta funcion es la encargada de autocompletar la informacion necesaria
        en la interfaz grafica para la configuracion de la comunicacion por puerto serie
        '''
        from serial import SerialBase

        # Pasar listado de puertos serie disponibles a campo de seleccion en la interfaz gráfica
        for i in range(self.cbx_serial_port.count()):
            # Si hay algun item en el combobox removerlo
            self.cbx_serial_port.removeItem(i)
        for port in ports:
            # Agregar cada puerto serie disponible como item del combobox
            self.cbx_serial_port.addItem(port[1])

        # Listar configuraciones de baudrates posibles
        for i in range(self.cbx_serial_baudrates.count()):
            # Si hay algun item en el combobox removerlo
            self.cbx_serial_baudrates.removeItem(i)
        for baudrate in SerialBase.BAUDRATES:
            # Agregar configuraciones disponibles al campo de seleccion
            self.cbx_serial_baudrates.addItem(str(baudrate), baudrate)

        # Listar configuraciones de paridad posibles
        for i in range(self.cbx_serial_parities.count()):
            # Si hay algun item en el combobox removerlo
            self.cbx_serial_parities.removeItem(i)

        parities_texts = {'N': 'None', 'E': 'Even', 'O': 'Odd', 'M': 'Mark', 'S': 'Space'}
        for parity in SerialBase.PARITIES:
            # Agregar configuraciones disponibles al campo de seleccion
            self.cbx_serial_parities.addItem(parities_texts[parity], parity)

        # Listar configuraciones de stopbits posibles
        for i in range(self.cbx_serial_stopbits.count()):
            # Si hay algun item en el combobox removerlo
            self.cbx_serial_stopbits.removeItem(i)
        for stopbit in SerialBase.STOPBITS:
            # Agregar configuraciones disponibles al campo de seleccion
            self.cbx_serial_stopbits.addItem(str(stopbit), stopbit)

        # Listar configuraciones de bytsizes posibles
        for i in range(self.cbx_serial_bytesizes.count()):
            # Si hay algun item en el combobox removerlo
            self.cbx_serial_bytesizes.removeItem(i)
        for bytesize in SerialBase.BYTESIZES:
            # Agregar configuraciones disponibles al campo de seleccion
            self.cbx_serial_bytesizes.addItem(str(bytesize), bytesize)
            
    def Plotear(self, canvas):
        y=self.espectro.getSpec()
        canvas.axes.set_ylim(np.min(y) - np.min(y) * 20 / 100, np.max(y) + np.max(y) * 20 / 100)
        canvas.plotoma(self.espectro)
        self.statusBar().showMessage('Ploting...')
        
    @QtCore.pyqtSlot()
    def on_actionSave_triggered(self):
        self.espectro.toOmaFile(self.config['workspace'],
                                self.config['fileFormat']['column_sep'],
                                comments=self.config['fileFormat']['comment_char'],
                                )

    @QtCore.pyqtSlot()
    def on_cbx_serial_port_currentIndexChanged(self):
        port = self.cbx_serial_port.itemData(self.cbx_serial_port_currentIndex())
        self.config['serialConfig']['port'] = port
        self.ser.port(port)

    @QtCore.pyqtSlot()
    def on_cbx_serial_baudrates_currentIndexChanged(self):
        baudrate = self.cbx_serial_baudrates.itemData(self.cbx_serial_baudrates_currentIndex())
        self.config['serialConfig']['baudrate'] = baudrate
        self.ser.baudrate(baudrate)

    @QtCore.pyqtSlot()
    def on_cbx_serial_parities_currentIndexChanged(self):
        parity = self.cbx_serial_parities.itemData(self.cbx_serial_parities_currentIndex())
        self.config['serialConfig']['parity']=parity
        self.ser.parity(parity)

    @QtCore.pyqtSlot()
    def on_cbx_serial_bytesizes_currentIndexChanged(self):
        bytesize = self.cbx_serial_bytesizes.itemData(self.cbx_serial_bytesizes_currentIndex())
        self.config['serialConfig']['bytesize']=bytesize
        self.ser.bytesize(bytesize)

    @QtCore.pyqtSlot()
    def on_cbx_serial_stopbits_currentIndexChanged(self):
        stopbits=self.cbx_serial_stopbits.itemData(self.cbx_serial_stopbits_currentIndex())
        self.config['serialConfig']['stopbits']=stopbits
        self.ser.stopbits(stopbits)

    @QtCore.pyqtSlot()
    def update_ui(self):
        self.btn_run.setEnabled(True)

    @QtCore.pyqtSlot()
    def change_messagge(self, message):
        self.statusBar().showMessage(message, 5000)

    @QtCore.pyqtSlot()
    def on_le_exposuretime_editingFinished(self):
        self.btn_run.setEnabled(False)
        self.btn_update.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_le_damode_editingFinished(self):
        self.btn_run.setEnabled(False)
        self.btn_update.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_le_scansnumber_editingFinished(self):
        self.btn_run.setEnabled(False)
        self.btn_update.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_le_detectortemp_editingFinished(self):
        self.btn_run.setEnabled(False)
        self.btn_update.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_le_ignoredscans_editingFinished(self):
        self.btn_run.setEnabled(False)
        self.btn_update.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_tlb_basename_released(self):
        #TODO: add project directory check
        if os.path.isdir(self.config['workspace']):
            workdir = self.config['workspace']
        else:
            workdir = os.path.expanduser('~')
        fname = QtGui.QFileDialog.getSaveFileName(parent=self,
                                   caption='Select File Basename',
                                   directory=workdir,
                                   filter="OMA Files(*.oma)"
                                   )
        if fname:
            self.le_basename.setText(fname)

    @QtCore.pyqtSlot()
    def on_tlb_fo_bkg_released(self):
        #TODO: add project directory check
        if os.path.isdir(self.config['workspace']):
            workdir = self.config['workspace']
        else:
            workdir = os.path.expanduser('~')
        self.le_bkg.setText(QtGui.QFileDialog.getOpenFileName(self,
                                            directory=workdir,
                                            caption='Open Background File',
                                            filter="OMA Files(*.oma)")
                            )

    def disable_controls(self):
        self.toolBox_daq.setEnabled(False)

    @QtCore.pyqtSlot()
    def on_btn_run_pressed(self):
        """Proceso de Scan"""
        self.btn_run.setEnabled(False)
        self.disable_controls()
        self.scaner.scan(self.ser, self.sp_loop.value())

    @QtCore.pyqtSlot()
    def incoming_data(self, espectro):
        
        if self.rb_background.checkState():
            spec_type='bkg'
        else:
            spec_type='spec'
            
        fname = self.le_basename.text()+time.strftime('%Y%m%d%H%M%S')
        selected_grating=self.daq_cbx_monochromator_grating.itemData(self.daq_cbx_monochromator_grating.currentIndex())
        self.espectro.fname=fname
        self.espectro = spectrum( y=espectro,
                                  fname=fname,
                                  time=time.strftime('%c'),
                                  exptime=self.le_exposuretime.text(),
                                  damode=self.le_damode.text(),
                                  dtemp=self.le_detectortemp.text(),
                                  snumber=self.le_scansnumber.text(),
                                  iscans=self.le_ignoredscans.text(),
                                  monochromator_model='Jarrel Ash',
                                  grating_info=self.config['monochromatorConfi'][selected_grating],
                                  monochromator_counter=self.config['monochromatorConfig']['counter'],
                                  spec_type=spec_type,
                                  )

        if self.espectro.spec_type == 'spec':
            if self.le_bkg.text() == '':
                #TODO: add project directory check
                if os.path.isdir(self.config['workspace']):
                    workdir = self.config['workspace']
                else:
                    workdir = os.path.expanduser('~')
                self.le_bkg.setText(QtGui.QFileDialog.getOpenFileName(parent=self,
                                                                      caption='Open Background File',
                                                                      directory=workdir,
                                                                      filter="OMA Files(*.oma)"
                                                                      )
                                    )
            bkg_path = str(self.le_bkg.text())
            
            if os.path.isfile(bkg_path):
                self.espectro.setBackground(bkg_path)
                
            if self.chk_autosave.checkState():
                self.espectro.toOmaFile(self.config['workspace'],
                                        self.config['fileFormat']['column_sep'],
                                        comments=self.config['fileFormat']['comment_char'],
                                        )
                self.on_btn_check_clicked()
            
            self.Plotear(self.espectro.y, self.daq_maincanvas)
            
    @QtCore.pyqtSlot()
    def on_btn_stop_clicked(self):
        """Abortar Scan"""
        self.scaner.exiting = True
        self.scaner.terminate()

    @QtCore.pyqtSlot()
    def on_btn_check_clicked(self):
        self.ser.close()
        self.ser.open()
        """Consultar Parametros de Scan"""
        self.ser.write('ET\r\n')
        ET = self.ser.readline().rstrip('\r\n')

        if self.ser.read() == '*':
            self.le_exposuretime.setText(ET)

        self.ser.write('DT\r\n')
        DT = self.ser.readline().rstrip('\r\n')

        if self.ser.read() == '*':
            self.le_detectortemp.setText(DT)

        self.ser.write('DA\r\n')
        DA = self.ser.readline().rstrip('\r\n')

        if self.ser.read() == '*':
            self.le_damode.setText(DA)

        self.ser.close()

    @QtCore.pyqtSlot()
    def on_btn_update_clicked(self):
        """Update Scan Sequence Settings"""
        self.ser.close()
        self.ser.open()
        
        ET = 'ET ' + self.le_exposuretime.text() + '\r\n'
        self.config['scanSettings']['exposuretime']=ET
        self.ser.write(ET)

        if self.ser.read() == '*':
            pass

        DT = 'DT ' + self.le_detectortemp.text() + '\r\n'
        self.config['scanSettings']['detectortemp'] = DT
        self.ser.write(DT)

        if self.ser.read() == '*':
            pass

        DA = 'DA ' + self.le_damode.text() + '\r\n'
        self.config['scanSettings']['damode'] = DA
        self.ser.write(DA)

        if self.ser.read() == '*':
            pass
        
        I = 'I ' + self.le_scansnumber.text() + '\r\n'
        self.config['scanSettings']['scannumber']=I

        self.ser.write(I)

        if self.ser.read() == '*':
            pass

        K = 'K ' + self.le_ignoredscans.text() + '\r\n'
        self.config['scanSettings']['ignoredscans']=K
        self.ser.write(K)

        if self.ser.read() == '*':
            pass

        self.btn_run.setEnabled(True)
        self.btn_update.setEnabled(False)

    @QtCore.pyqtSlot()
    def on_btn_sustractbkg_pressed(self):
        self.daq_maincanvas.plotoma(self.espectro, substract_bkg=True )
    
    @QtCore.pyqtSlot() 
    def on_save_project_pressed(self):
        workdir=os.path.expanduser('~')
        dirname = QtGui.QFileDialog.getExistingDirectory(self,
                                                         'Select Project Folder',
                                                         workdir,
                                                         QtGui.QFileDialog.ShowDirsOnly
                                                         )
        if os.path.isdir(dirname):
            fname=dirname+'/.omaproject'
            self.config['workspace']=dirname
            self.config.filename=fname
            self.config.write()
            self.config.reload()
            self.maintabs.setTabEnabled(1,True)
            self.maintabs.setTabEnabled(2,True)
        
        else:
            message="Please select a valid omaproject directory"
            self.change_messagge(message)
            self.maintabs.setTabEnabled(1,False)
            self.maintabs.setTabEnabled(2,False)
            
    @QtCore.pyqtSlot()        
    def on_load_project_pressed(self):
        workdir=os.path.expanduser('~')
        dirname = QtGui.QFileDialog.getExistingDirectory(self,
                                                         'Select Project Folder',
                                                         workdir,
                                                         QtGui.QFileDialog.ShowDirsOnly
                                                         )
        fname=dirname+'/.omaproject'
        if os.path.isfile(fname):
            self.config.filename=fname
            self.config.reload()
            self.maintabs.setTabEnabled(1,True)
            self.maintabs.setTabEnabled(2,True)
            
        else:
            message="Please select a valid omaproject directory"
            self.change_messagge(message)
            self.maintabs.setTabEnabled(1,False)
            self.maintabs.setTabEnabled(2,False)
                       
    def get_status(self):
        """Obtener configuracion y estado del OMA"""
        self.ser.close()
        self.ser.open()
        self.ser.write('ID\r\n')
        status = self.ser.readline().rstrip('\r\n')
        self.ser.read()
        self.ser.close()
        sys.stdout.write(status)
        if status == 1461:
            self.statusBar().showMessage('Ready')


def main():
    app = QtGui.QApplication(sys.argv)
    app.processEvents()
    DAQ = OMAIIIuiAPP()
    for i in range(0, 101):
        DAQ.splash.progressBar.setValue(i)
        # Do something which takes some time.
        t = time.time()
        if i == 10:
            DAQ.get_serial_config()
        if i == 20:
            DAQ.load_plot_settings()
        if i == 30:
            DAQ.load_oma_scan_settings()
        if i == 40:
            DAQ.load_output_fileconfig()
        if i == 60:
            DAQ.load_monochromathor_config()
        if i == 80:
            DAQ.connect_thread()
        while time.time() < t + 0.03:
            app.processEvents()
    DAQ.show()
    DAQ.splash.finish(DAQ)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
