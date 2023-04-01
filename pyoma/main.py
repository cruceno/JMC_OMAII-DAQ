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
from PySide6 import QtGui, QtCore, QtWidgets
from pyoma.gui.main_app import MainApp
from pyoma.instrument.oma import spectrum
from pyoma.ploter.qtmatplotlib import cursor
from pyoma.worker.scan import Scanner
from pyoma.instrument.serialutil import scan_serial_ports


class OMAIIIuiAPP(QtWidgets.QMainWindow, MainApp):

    """La ventana principal de la aplicacion."""

    def __init__(self):
        super(OMAIIIuiAPP, self).__init__()
        # Cargamos la interfaz grafica
        self.setupUi(self)

        self.cbx_serial_port.activated.connect(self.on_cbx_serial_port_activated)
        self.cbx_serial_baudrates.activated.connect(self.on_cbx_serial_baudrates_activated)
        self.cbx_serial_stopbits.activated.connect(self.on_cbx_serial_stopbits_activated)
        self.cbx_serial_bytesizes.activated.connect(self.on_cbx_serial_bytesizes_activated)
        self.cbx_serial_parities.activated.connect(self.on_cbx_serial_parities_activated)
        # Cargamos archivo de configuracion predeterminado
        # Estudiar caso en que el archivo de configuracion no exista
        self.config = ConfigObj('pyoma/omaiii.ini')
        self.scaner = Scanner()
        # Instanciar objeto serial
        self.ser = serial.Serial()

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
        self.connect(self.scaner, QtCore.SIGNAL("msgsignal(PyQt_PyObject)"), self.update_log_monitor)
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
        # Acceder a la configuracion guardada
        serialConfig = self.config['serialConfig']

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
        self.ser.timeout = self.sp_serial_timeout.value()

        if serialConfig['port'] != '' and self.cbx_serial_port.findText(serialConfig['port']) > -1:
            self.ser.port = serialConfig['port']
            try:
                with self.ser as s:
                    self.update_log_monitor(str(s.port))
                    self.update_log_monitor(str(s.get_settings()))
                    self.cbx_serial_port.setCurrentIndex(self.cbx_serial_port.findText(serialConfig['port']))
            except IOError as e:
                self.update_log_monitor('El puerto en el archivo de configuracion no esta disponible')
                self.update_log_monitor(str(e))
                self.update_log_monitor('Seleccionando primer puerto disponible')
                self.ser.port = self.cbx_serial_port.itemText(self.cbx_serial_port.currentIndex())
                self.config['serialConfig']['port'] = self.ser.port
                try:
                    with self.ser as s:
                        s.close()
                        s.open()
                        self.update_log_monitor(str(s.port))
                        self.update_log_monitor(str(s.get_settings()))
                        s.close()
                except IOError as e:
                    self.update_log_monitor("La configuracion del puerto serie requiere atencion")
                    self.update_log_monitor(str(e))
        else:
            self.update_log_monitor('Seleccionando primer puerto disponible')
            self.ser.port = self.cbx_serial_port.itemText(self.cbx_serial_port.currentIndex())
            self.config['serialConfig']['port'] = self.ser.port
            try:
                with self.ser as s:
                    s.close()
                    s.open()
                    self.update_log_monitor(str(s.port))
                    self.update_log_monitor(str(s.get_settings()))
                    s.close()

            except IOError as e:
                self.update_log_monitor("La configuracion del puerto serie requiere atencion")
                self.update_log_monitor(str(e))

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
        index = self.daq_cbx_monochromator_grating.findData(monochromatorConfig['selected_grating'])
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

    @QtCore.Slot()
    def on_daq_sp_monochromator_counter_valueChanged(self):
        self.config['monochromatorConfig']['counter'] = self.daq_sp_monochromator_counter.value()

    @QtCore.Slot()
    def on_le_monochromator_g1_lines_editingFinished(self):
        self.config['monochromatorConfig']['g1']['lines'] = self.le_monochromator_g1_lines.text()

    @QtCore.Slot()
    def on_le_monochromator_g1_amplitude_editingFinished(self):
        self.config['monochromatorConfig']['g1']['amplitude'] = self.le_monochromator_g1_amplitude.text()

    @QtCore.Slot()
    def on_le_monochromator_g1_resolution_editingFinished(self):
        self.config['monochromatorConfig']['g1']['resolution'] = self.le_monochromator_g1_resolution.text()

    @QtCore.Slot()
    def on_dsb_monochromator_g1_factor_valueChanged(self):
        self.config['monochromatorConfig']['g1']['factor'] = self.dsb_monochromator_g1_factor.value()

    @QtCore.Slot()
    def on_le_monochromator_g2_lines_editingFinished(self):
        self.config['monochromatorConfig']['g2']['lines'] = self.le_monochromator_g2_lines.text()

    @QtCore.Slot()
    def on_le_monochromator_g2_amplitude_editingFinished(self):
        self.config['monochromatorConfig']['g2']['amplitude'] = self.le_monochromator_g2_amplitude.text()

    @QtCore.Slot()
    def on_le_monochromator_g2_resolution_editingFinished(self):
        self.config['monochromatorConfig']['g2']['resolution'] = self.le_monochromator_g2_resolution.text()

    @QtCore.Slot()
    def on_dsb_monochromator_g2_factor_valueChanged(self):
        self.config['monochromatorConfig']['g2']['factor'] = self.dsb_monochromator_g2_factor.value()

    @QtCore.Slot()
    def on_le_monochromator_g3_lines_editingFinished(self):
        self.config['monochromatorConfig']['g3']['lines'] = self.le_monochromator_g3_lines.text()

    @QtCore.Slot()
    def on_le_monochromator_g3_amplitude_editingFinished(self):
        self.config['monochromatorConfig']['g3']['amplitude'] = self.le_monochromator_g3_amplitude.text()

    @QtCore.Slot()
    def on_le_monochromator_g3_resolution_editingFinished(self):
        self.config['monochromatorConfig']['g3']['resolution'] = self.le_monochromator_g3_resolution.text()

    @QtCore.Slot()
    def on_dsb_monochromator_g3_factor_valueChanged(self):
        self.config['monochromatorConfig']['g3']['factor'] = self.dsb_monochromator_g3_factor.value()

    def set_ui_serial_controls(self):

        ''' Esta funcion es la encargada de autocompletar la informacion necesaria
        en la interfaz grafica para la configuracion de la comunicacion por puerto serie
        '''
        from serial import SerialBase
        ports = scan_serial_ports(20, False)
        # Pasar listado de puertos serie disponibles a campo de seleccion en la interfaz gráfica
        for i in range(self.cbx_serial_port.count()):
            # Si hay algun item en el combobox removerlo
            self.cbx_serial_port.removeItem(i)
        for port in ports:
            # Agregar cada puerto serie disponible como item del combobox
            self.cbx_serial_port.addItem(port[1], port[1])

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

    def get_cursors(self, lw):
        items = []
        for x in range(lw.count()):
            items.append(lw.item(x))
        return items

    @QtCore.Slot()
    def on_da_plot_cursors_add_pressed(self):
        data = self.da_le_cursor.text().split(':')
        cur = cursor()
        cur.setText(data[0])
        cur.x = float(data[1])
        cur.color = data[2]
        self.da_plot_cursors_list.addItem(cur)

    @QtCore.Slot()
    def on_daq_plot_cursor_add_pressed(self):
        data = self.daq_le_cursor.text().split(':')
        cur = cursor()
        cur.setText(data[0])
        cur.x = float(data[1])
        cur.color = data[2]
        self.daq_plot_cursor_list.addItem(cur)

    @QtCore.Slot()
    def on_da_plot_cursors_remove_pressed(self):
        self.da_plot_cursors_list.takeItem(self.da_plot_cursors_list.currentRow())

    @QtCore.Slot()
    def on_daq_plot_cursor_remove_pressed(self):
        self.daq_plot_cursor_list.takeItem(self.daq_plot_cursor_list.currentRow())

    @QtCore.Slot()
    def on_da_list_files_itemSelectionChanged(self):
        specs = self.da_list_files.selectedItems()
        self.da_maincanvas.axes.cla()
        self.da_maincanvas.cursors = self.get_cursors(self.da_plot_cursors_list)
        self.da_maincanvas.multiplot(specs, self.da_chk_subst_bkg.isChecked())
        spec_info = ''
        for spec in specs:
            spec_info += spec.getSpecHeader()
            spec_info += "\n------------------------------------------------------------\n"
        if spec_info:
            self.pte_da_spec_info.setPlainText(spec_info)

    def Plotear(self, canvas):
        canvas.cursors = self.get_cursors(self.daq_plot_cursor_list)
        y = self.espectro.getSpec()
        canvas.axes.set_ylim(np.min(y) - np.min(y) * 20 / 100, np.max(y) + np.max(y) * 20 / 100)
        canvas.plotoma(self.espectro,
                       False if self.sp_loop.value() != 0 else self.rb_bkg_plot.isChecked(),
                       False if self.sp_loop.value() != 0 else self.rb_bkg_auto.isChecked())

        self.update_log_monitor('Ploting...')

    @QtCore.Slot()
    def on_actionSave_triggered(self):
        self.espectro.toOmaFile(self.config['workspace'],
                                self.cbx_file_separator.itemData(self.cbx_file_separator.currentIndex()),
                                comments=self.le_file_comment_string.text(),
                                )

    @QtCore.Slot()
    def on_cbx_serial_port_activated(self):
        index = self.cbx_serial_port.currentIndex()
        port = self.cbx_serial_port.itemData(index)
        print(port)
        self.config['serialConfig']['port'] = port
        self.ser.port = port
        try:
            with self.ser as s:
                s.close()
                s.open()
                self.update_log_monitor(s.name)
                self.update_log_monitor(str(s.get_settings()))
                s.close()
        except IOError as e:
            self.update_log_monitor("La configuracion del puerto serie requiere atencion")
            self.update_log_monitor(str(e))

    @QtCore.Slot()
    def on_cbx_serial_baudrates_activated(self):
        index = self.cbx_serial_baudrates.currentIndex()
        baudrate = self.cbx_serial_baudrates.itemData(index)
        self.config['serialConfig']['baudrate'] = baudrate
        self.ser.baudrate = baudrate
        try:
            with self.ser as s:
                s.close()
                s.open()
                self.update_log_monitor(s.name)
                self.update_log_monitor(str(s.get_settings()))
                s.close()
        except IOError as e:
            self.update_log_monitor("La configuracion del puerto serie requiere atencion")
            self.update_log_monitor(str(e))

    @QtCore.Slot()
    def on_cbx_serial_parities_activated(self):
        index = self.cbx_serial_parities.currentIndex()
        parity = self.cbx_serial_parities.itemData(index)
        self.config['serialConfig']['parity'] = parity
        self.ser.parity = parity

        try:
            with self.ser as s:
                s.close()
                s.open()
                self.update_log_monitor(s.name)
                self.update_log_monitor(str(s.get_settings()))
                s.close()
        except IOError as e:
            self.update_log_monitor("La configuracion del puerto serie requiere atencion")
            self.update_log_monitor(str(e))

    @QtCore.Slot()
    def on_cbx_serial_bytesizes_activated(self):
        index = self.cbx_serial_bytesizes.currentIndex()
        bytesize = self.cbx_serial_bytesizes.itemData(index)
        self.config['serialConfig']['bytesize'] = bytesize
        self.ser.bytesize = bytesize
        try:
            with self.ser as s:
                self.update_log_monitor(s.name)
                self.update_log_monitor(str(s.get_settings()))
        except IOError as e:
            self.update_log_monitor("La configuracion del puerto serie requiere atencion")
            self.update_log_monitor(str(e))

    @QtCore.Slot()
    def on_cbx_serial_stopbits_activated(self):
        index = self.cbx_serial_stopbits.currentIndex()
        stopbits = self.cbx_serial_stopbits.itemData(index)
        self.config['serialConfig']['stopbits'] = stopbits
        self.ser.stopbits = stopbits
        try:
            with self.ser as s:
                self.update_log_monitor(s.name)
                self.update_log_monitor(str(s.get_settings()))
        except IOError as e:
            self.update_log_monitor("La configuracion del puerto serie requiere atencion")
            self.update_log_monitor(str(e))

    @QtCore.Slot()
    def update_ui(self):
        self.btn_run.setEnabled(True)

    @QtCore.Slot()
    def change_messagge(self, message):
        self.statusBar().showMessage(message, 5000)

    @QtCore.Slot()
    def on_le_exposuretime_editingFinished(self):
        self.btn_run.setEnabled(False)
        self.btn_update.setEnabled(True)

    @QtCore.Slot()
    def on_le_damode_editingFinished(self):
        self.btn_run.setEnabled(False)
        self.btn_update.setEnabled(True)

    @QtCore.Slot()
    def on_le_scansnumber_editingFinished(self):
        self.btn_run.setEnabled(False)
        self.btn_update.setEnabled(True)

    @QtCore.Slot()
    def on_le_detectortemp_editingFinished(self):
        self.btn_run.setEnabled(False)
        self.btn_update.setEnabled(True)

    @QtCore.Slot()
    def on_le_ignoredscans_editingFinished(self):
        self.btn_run.setEnabled(False)
        self.btn_update.setEnabled(True)

    @QtCore.Slot()
    def on_tlb_basename_released(self):

        if os.path.isdir(self.config['workspace']):
            workdir = self.config['workspace']
        else:
            workdir = os.path.expanduser('~')
        fname = QtWidgets.QFileDialog.getSaveFileName(parent=self,
                                                  caption='Select File Basename',
                                                  directory=workdir,
                                                  filter="OMA Files(*.oma)"
                                                  )
        if fname:
            self.le_basename.setText(fname)

    @QtCore.Slot()
    def on_tlb_fo_bkg_released(self):
        if os.path.isdir(self.config['workspace']):
            workdir = self.config['workspace']
        else:
            workdir = os.path.expanduser('~')
        self.le_bkg.setText(QtWidgets.QFileDialog.getOpenFileName(self,
                                                              directory=workdir,
                                                              caption='Open Background File',
                                                              filter="OMA Files(*.bkg)")
                            )

    def disable_controls(self):
        self.toolBox_daq.setEnabled(False)
        self.gb_monochromator.setEnabled(False)

    def enable_controls(self):
        self.toolBox_daq.setEnabled(True)
        self.btn_run.setText('RUN')
        self.btn_run.setEnabled(True)
        self.gb_monochromator.setEnabled(True)

    @QtCore.Slot()
    def update_log_monitor(self, text):
        self.pte_daq_monitor.appendPlainText(text)

    @QtCore.Slot()
    def on_btn_run_pressed(self):

        """Proceso de Scan"""
        if self.btn_run.text() == "RUN":
            self.btn_run.setEnabled(False)
            self.disable_controls()
            self.scaner.scan(self.ser, self.sp_loop.value())
            self.btn_run.setText('STOP')
            self.btn_run.setEnabled(True)
        elif self.btn_run.text() == 'STOP':
            self.btn_run.setEnabled(False)
            self.scaner.exiting = True
            while self.scaner.isRunning():
                continue
            self.enable_controls()

    @QtCore.Slot()
    def incoming_data(self, spec):
        self.update_log_monitor('Processing incoming data')
        if self.rb_background.isChecked():
            spec_type = 'bkg'
        else:
            spec_type = 'spec'

        fname = self.le_basename.text() + time.strftime('%Y%m%d%H%M%S')
        selected_grating = self.daq_cbx_monochromator_grating.itemData(self.daq_cbx_monochromator_grating.currentIndex())
        self.espectro = spectrum(y=spec,
                                 fname=fname,
                                 time=time.strftime('%c'),
                                 exptime=self.le_exposuretime.text(),
                                 damode=self.le_damode.text(),
                                 dtemp=self.le_detectortemp.text(),
                                 snumber=self.le_scansnumber.text(),
                                 iscans=self.le_ignoredscans.text(),
                                 monochromator_model='Jarrel Ash',
                                 grating_info=self.config['monochromatorConfig'][selected_grating],
                                 monochromator_counter=self.config['monochromatorConfig']['counter'],
                                 spec_type=spec_type
                                 )

        if os.path.isdir(self.config['workspace']):
            workdir = self.config['workspace']
        else:
            workdir = os.path.expanduser('~')

        if spec_type == 'spec':
            if os.path.isfile(self.le_bkg.text()):
                bkg_path = str(self.le_bkg.text())
                self.update_log_monitor('Adding background information')
                self.espectro.setBackground(bkg_path)
            else:
                if self.sp_loop.value()!=0:
                    self.le_bkg.setText(QtWidgets.QFileDialog.getOpenFileName(parent=self,
                                                                          caption='Open Background File',
                                                                          directory=workdir,
                                                                          filter="OMA Files(*.bkg)"
                                                                          )
                                        )

                    bkg_path = str(self.le_bkg.text())

                    if os.path.isfile(bkg_path):
                        self.update_log_monitor('Adding background information')
                        self.espectro.setBackground(bkg_path)
                        self.update_log_monitor('Adding background information')
                    else:
                        self.update_log_monitor('Continue without background infomation ')
        if self.chk_autosave.isChecked():
            if self.sp_loop.value() != 0:
                self.update_log_monitor('Autosave enabled. Saving data on' + self.config['workspace'])
                self.espectro.toOmaFile(self.config['workspace'],
                                        self.cbx_file_separator.itemData(self.cbx_file_separator.currentIndex()),
                                        comments=self.le_file_comment_string.text(),
                                        )
                self.on_btn_check_clicked()

        self.Plotear(self.daq_maincanvas)
        self.load_project_oma_specs(self.config['workspace'])
        if self.sp_loop.value() != 0:
            self.enable_controls()
            self.update_log_monitor('Done.')

    @QtCore.Slot()
    def on_btn_check_clicked(self):
        """Consultar Parametros de Scan"""
        try:
            with self.ser as s:
                s.close()
                s.open()
                s.write(b'ET\r\n')
                ET = s.readline().decode().rstrip('\r\n')
                if s.read() == b'*':
                    self.le_exposuretime.setText(ET)

                s.write(b'DT\r\n')
                DT = s.readline().decode().rstrip('\r\n')

                if s.read() == b'*':
                    self.le_detectortemp.setText(DT)

                s.write(b'DA\r\n')
                DA = s.readline().decode().rstrip('\r\n')

                if s.read() == b'*':
                    self.le_damode.setText(DA)

                s.write(b'I\r\n')
                I = s.readline().decode().rstrip('\r\n')

                if s.read() == b'*':
                    self.le_scansnumber.setText(I)
                s.close()

        except IOError as e:
            self.update_log_monitor("La configuracion del puerto serie requiere atencion")
            self.update_log_monitor(str(e))

    @QtCore.Slot()
    def on_btn_update_clicked(self):
        """Update Scan Sequence Settings"""
        try:
            with self.ser as s:
                s.close()
                s.open()
                ET = 'ET ' + self.le_exposuretime.text() 
                self.config['scanSettings']['exposuretime'] = ET
                ET = ET + '\r\n'
                s.write(ET.encode())

                if s.read() == b'*':
                    pass

                DT = 'DT ' + self.le_detectortemp.text()
                self.config['scanSettings']['detectortemp'] = DT
                DT = DT + '\r\n'
                s.write(DT.encode())
                if s.read() == b'*':
                    pass
                DA = 'DA ' + self.le_damode.text() 
                self.config['scanSettings']['damode'] = DA
                DA = DA + '\r\n'
                s.write(DA.encode())
                if s.read() == b'*':
                    pass
                I = 'I ' + self.le_scansnumber.text()
                self.config['scanSettings']['scannumber'] = I
                I = I + '\r\n'
                s.write(I.encode())
                if s.read() == b'*':
                    pass
                K = 'K ' + self.le_ignoredscans.text()
                self.config['scanSettings']['ignoredscans'] = K
                K = K + '\r\n'
                s.write(K.encode())
                if s.read() == b'*':
                    pass
                s.close()
                self.btn_run.setEnabled(True)
                self.btn_update.setEnabled(False)
        except(IOError):
            self.update_log_monitor("La configuracion del puerto serie requiere atencion")
            self.update_log_monitor(str(self.ser.SerialEcxeption()))

    @QtCore.Slot()
    def on_pb_subst_bkg_pressed(self):
        try:
            self.daq_maincanvas.plotoma(self.espectro, substract_bkg=True)
        except(AttributeError):
            self.update_log_monitor("Debe tomar un espectro primero")

    @QtCore.Slot()
    def on_save_project_pressed(self):
        workdir = os.path.expanduser('~')
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                         'Select Project Folder',
                                                         workdir,
                                                         QtWidgets.QFileDialog.ShowDirsOnly
                                                         )
        if os.path.isdir(dirname):
            fname = dirname + '/.omaproject'
            self.config['workspace'] = dirname
            self.config.filename = fname
            self.config.write()
            self.config.reload()
            self.maintabs.setTabEnabled(1, True)
            self.maintabs.setTabEnabled(2, True)

        else:
            message = "Please select a valid omaproject directory"
            self.change_messagge(message)
            self.update_log_monitor(message)
            self.maintabs.setTabEnabled(1, False)
            self.maintabs.setTabEnabled(2, False)

    def load_project_oma_specs(self, project_path):

        import glob
        patron = project_path + os.sep + '*.oma'
        fileList = list(filter(os.path.isfile, glob.glob(patron)))
        fileList.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))

        self.da_list_files.clear()
        for file in fileList:
            OmaListItem = spectrum()
            OmaListItem.setText(os.path.basename(file))
            OmaListItem.fromOmaFile(file)
            self.da_list_files.addItem(OmaListItem)

    @QtCore.Slot()
    def on_load_project_pressed(self):
        workdir = os.path.expanduser('~')
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                         'Select Project Folder',
                                                         workdir,
                                                         QtWidgets.QFileDialog.ShowDirsOnly
                                                         )
        fname = dirname + '/.omaproject'
        if os.path.isfile(fname):
            self.config['workspace'] = dirname
            self.config.filename = fname
            self.config.reload()
#            print(self.config)
            self.load_monochromathor_config()
            self.load_oma_scan_settings()
            self.load_output_fileconfig()
            self.get_serial_config()
            self.load_project_oma_specs(dirname)
            self.maintabs.setTabEnabled(1, True)
            self.maintabs.setTabEnabled(2, True)

        else:
            message = "Please select a valid omaproject directory"
            self.change_messagge(message)
            self.update_log_monitor(message)
            self.maintabs.setTabEnabled(1, False)
            self.maintabs.setTabEnabled(2, False)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.processEvents()
    DAQ = OMAIIIuiAPP()
    for i in range(0, 101):
        DAQ.splash.progressBar.setValue(i)
        # Do something which takes some time.
        t = time.time()
        if i == 10:
            DAQ.set_ui_serial_controls()
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
