'''
Created on 1 jun. 2017

@author: javier
'''
from PyQt4.QtCore import QThread, SIGNAL
from numpy import fromstring


class Scanner(QThread):

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.message = ''

    def scan(self, ser, stopAt):
        self.ser = ser
        self.stop = int(stopAt)
        self.start()

    def run(self):
        """Proceso de Scan"""
        if self.stop != 0:
            n = self.stop
        else:
            n = 1
        while not self.exiting and n > 0:
            # Abrir concexion de serie y enviamos el comando "RUN\r\n" que inicia el proceso de scan
            self.ser.close()
            self.ser.open()
            self.ser.write('RUN\r\n')
            # emitimos un mensaje que diga en que parte del proceso de scan nos encontramos
            self.message = 'OMA Running...'
            while self.ser.read() != '*':
                self.emit(SIGNAL("msgsignal(Qstring)"), self.message)
                continue
            # escribimos el comando que indica al oma que debe transferirnos los datos del espectro
            self.ser.write('DC 1,1,1024\r\n')
            # emitimos un mensaje que diga en que parte del proceso de scan nos encontramos
            self.message = 'Reading Curve...'
            while self.ser.inWaiting < 4096:
                self.emit(SIGNAL("msgsignal(Qstring)"), self.message)
                continue
            # leemos los datos del OMA y cerramos la conexion
            r = self.ser.readline().rstrip('\r\n')
            self.ser.close()
            # convertimos los datos(string) a ndarray para poder trabajar matematicamene y graficar los mismos
            self.espectro = fromstring(r, sep=',')
            # emitimos una señal en la que pasamos el espectro adquirido
            self.emit(SIGNAL("scansignal(PyQt_PyObject)"), self.espectro)
            if self.stop != 0:
                n -= 1
            else:
                pass

    def __del__(self):
        self.exiting = True
        self.wait()
