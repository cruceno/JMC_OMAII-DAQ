'''
Created on 1 jun. 2017

@author: javier
'''
import numpy as np
from os import path


class OMAIII:

    """ Biblioteca de comandos """
    def __init__(self):
        pass

    def send(self, command_str):
        serial_str = command_str+'\r\n'
        self.ser.write(serial_str)

    def read(self, curve_bytes):
        self.ser.read(curve_bytes)

    def check_serial_conn(self, port, serial_settings):
        '''
        Comprueba si el OMAIII esta conectado en el puerto serie

        '''
        import serial
        try:
            ser = serial.Serial(port=port,
                                baudrate=9600,
                                parity=serial.PARITY_NONE,
                                stopbits=1,
                                bytesize=8,
                                timeout=2)
            ser.close()
            ser.open()
            ser.write('ID')

            oma_id = ser.readline()

            if oma_id == '1461':
                self.ser = ser
                return True
            else:
                return False

        except:
            error = serial.SerialException()
            return error

    def ID(self):
         
        """
        R/O
        Especifica el OMA en uso, Devuelve: 1461
        """
        pass
         
    def DM(self):
         
        """
        R/O
        Especifica el detector en uso, Devuelve 1462 o 1463 
        """
     
    def VER(self):
         
        """
        R/O
        Devuelve version del software usado por el sistema
        """
     
    def CL(self):
         
        """
        R/O 
        Indica el estado del cooler utilizado en el detector 
        Devuelve: 1 si el cooler esta blooqueado
                  0 si el cooler esta desbloqueado
        """

    def DLEN(self):
        """
        R/O 
        Especifica la longitu del detector utilizado 
        """
    def ERR(self):

        """
        R/O 
        Devuelve un codigo de error que corresponde al ultimo comando
        operado por el OMA III
        CODE                        ERROR
         0            No se genero ningun error en la ultima ejecucion
         2            No se reconoce el comando o se a enviado un parametro
                       en un comando que no lo requiere
         3            se a enviado un parametro fera del rango aceptable
         6            Se a enviado un operador no numerico como parametro
         7            Error en la separacion de comandos compuestos
        """

    def MINET(self):
        """
        
        R/O
        Devuelve el tiempo de exposicion minimo, en segundos,
        para la configuracion actual
        
        """

    def MAXMEM(self):
         
        """
        R/O
        Devuelve un numero que representa el maximo numero de memorias disponbles 
        para el almacenamiento de datos
        """
         
    def ADP (self):
         
        """
        R/O 
        Indica la presicion usada por el convertidor Analogo-Digital
        Devuelve: 0, si esta unstalando un convertidor de 12 bits
                  1, si esta utilizando un convertidor de 14 bits
        """
        
    def DT (self, n):
         
        """
        R/W
        Tempeatura del detector: si 'n' es omitido el comando devolvera la temperatura, en grados centigrados,
        a la que se encuentra seteado el sistema de enfriamiento del detector.
        Si 'n' es incluido se configurara el sistema de enfriamiento para el valor especificado por 'n',
        'n' debe ser un numero entero.
        Para el detector 1462 el unico valo valor admitido para 'n' es '5' cuialquier otro valor seleccionara
        el ajuste manual del sistema de enfriamiento
        """
    
    def ET (self, n):
         
        """
        R/W
        Tiempo de Exposición: Si 'n' es omitido el comando devolvera el tiempo, en segundos,
        en que la luz sera captada por el detector.
        Si 'n' es especificado se ajustara el tiempo de exposicion del detector al valor de 'n',
        el maximo valor admitido es 14400
        """
    
    def FREQ (self, n):
         
        """
        R/W
        Frecuencia de la linea electrica: Si 'n' es omitido este comando leer la frecuencia
        de la linea (50/60 Hz) para la que esta configurado el sistema.
        Si 'n' es definido [50|60] se ajustara la configuracion del sistema al valor sekeccionado
        """
         
    def TRIGON (self):
         
        """
        TRIG.ON
         
        """
        pass
     
    def TRIGOFF (self):
         
        """
        TRIG.OFF
        """
        pass
     
    def SYNC (self):
         
        """
        Estado de sincronización
        """
         
    def NS (self):
         
        """
        Sincronización normal
        """
        pass
     
    def LS (self):
        
        """
        Sincronización con la linea
        """
        pass

    def DA(self, n):

        """
        R/W
        Modo de adquisicion de datos: si 'n' es omitido este comano devolvera el modo de adquisicion de datos
        que se esta utilizando.
        Si si el valor de 'n' es definido se ajustara el modo de adquisicion de datos a ese valor.
        (Ver Data Adquisitions Mode Section XVIII 1461's manual)
        """
    def RUN(self):

        """
        W/O
        Este comando inicia inmediatamente la adquisicion de datos, utilizando el modo de adquisicion
        de datos que este seleccionado en ese momento. 
        """

    def I (self, n):

        """
        W/O
        Contador de Scans
        """

    def J (self, n):

        """
        W/O
        Contador de Memoria
        """

    def K(self, n):

        """
        W/O
        Scans Ignorados
        """

    def CLR(self, n):

        """
        W/O
        Borra el contenido de la memoria especificada por 'n'
        """
         
    def CLRALL(self):
         
        """
        W/O
        Borra el contenido de todas las memorias del 1461
        """
         
    def MEM (self,n):
         
        """
        R/W
        Si 'n' es omitido el comando devolvera un entero como puntero que indica que memoria se esta utilizando actualmente,
        para el almacenamiento de datos
        Si se indica un valor para 'n' el comando movera el puntero a esa posicion de almacenamiento
        """
     
    def ADD (self, n1, n2):
         
        """
        Suma las curvas almacenadas en las memorias 'n1' y 'n2' el resultado es almacenado en 'n2'
        """
        
    def SUB(self, n1, n2):

        """
        Realiza la sustraccion entre las curvas almacenadas en 'n1' y 'n2' y almacena el resultado en 'n2'
        """

    def PTS(self):

        """
        R/O
        Devuelve el numero de puntos necesarios para almacenar una curva en memoria. 
        El numero develto por este comando varia segun el modo de adquisicion de dator utilizado.
        """

    def BYTES(self):

        """
        R/O
        Devuelve el numero de bytes necesarios para almacenar una curva en memoria-
        El valor devuelto por este comando es equivalente al de PTS() multiplicado por 2,
        o por 4 si se esta utilizando doble presición.
        """
         
    def DP(self):
        """
        R/O
        Presicion de datos: este comando indica la presicion de datos que se esta utilizando,
        la misma es seleccionada al momento de elegir un modo de adquisicion de datos
        """

    def DC(self, n1, n2, n3):
        """
        Volcado de Curva: Este comando envia al host (PC) los datos almacenaos en una deterinada 
        memoria del 1461. cada dato estara separado del siguiente mediate el separador designado con el comando DD
        la coma es el separador por defecto.

        n1= numero de memoria de la que se volcaran los datos
        n2= numero del primer canal a ser volvcado
        n3= numero de canales a ser volcados 
        Ejemplo DC(1, 1, 1024) enviara a la computadora los datos almacenados en la memoria 1, 
        desde el pixel 1 al pixel 1024
        """

    def BD(self, n1, n2, n3):

        """
        * Deprecated 
        Volcado Binario de Curva: Basicamente cumple la misma funcion que DC solo que en este caso 
        los datos seran enviados en forma binaria. en este caso no se enviara el separador por lo que el
        usuario debera conocer cual es la presicion de los datos al momento de recibirlos.

        n1= numero de memoria de la que se volcaran los datos
        n2= numero del primer canal a ser volvcado
        n3= numero de canales a ser volcados 
        Ejemplo DC(1, 1, 1024) enviara a la computadora los datos almacenados en la memoria 1, 
        desde el pixel 1 al pixel 1024
        """
         
    def DD(self, n):
        
        """
        Delimitador: Si 'n' es omitido el comando devolvera el caracter que esta siendo utilizado como delimitador,
        en el caso de que se 'n' tome un valor este sera seteado como nuevo delimitador entre los datos.
        """


class spectrum(object):

    def __init__(self,
                 x=np.arange(1, 1025, 1),
                 y=np.zeros_like(np.arange(1, 1025, 1)),
                 bkg=np.zeros_like(np.arange(1, 1025, 1)),
                 fname='omaspec',
                 time='',
                 exptime='',
                 damode='',
                 dtemp='',
                 snumber='',
                 iscans='',
                 monochromator_model='Jarrel Ash',
                 grating_info=[],
                 monochromator_counter='',
                 spec_type='spec',
                 ):

        self.spec_type=spec_type
        self.fname = fname
        self.time = time
        self.exptime = exptime
        self.damode = damode
        self.dtemp = dtemp
        self.snumber = snumber
        self.ignoredscans = iscans
        self.monochromator_model = monochromator_model
        self.grating_info = grating_info
        self.monochromator_counter = monochromator_counter
        if self.type == 'spec':
            self.bkg = bkg
        self.x = x
        self.y = y

    def getOmaSettings(self):

        ''' Returns a dict OMA Settings values for the spectrum
            Returns:
            -------
            oma_settings:
                dict_keys:
                ---------
                    extime: Time exposition used
                    damode: Data adquisition mode used
                    dtemp: Detector temerature
                    snumber: Number of scans
                    iscan: Ignored Scans

        '''
        oma_settings = {'exptime': self.exptime,
                        'damode': self.damode,
                        'dtemp': self.dtemp,
                        'snumber': self.snumber,
                        'iscans': self.iscans
                        }
        return oma_settings

    def getSpecHeader(self):

        not_print = ['x', 'y', 'bkg']
        header = []
        import collections
        odict = collections.OrderedDict(sorted(self.__dict__.items()))

        for key, v in odict.items():
            if key not in not_print:
                header.append("{key}={value}".format(key=key, value=v))

        return '\n'.join(header)
    
    def setBackground(self, fname, sep='\t', comments='/*', headerlines=11):
        self.bkg = np.genfromtxt(fname,
                                 delimiter=sep,
                                 skip_header=headerlines,
                                 usecols=1,
                                 )
        
    def getSpec(self, substract_bkg=True):
        if substract_bkg:
            return self.y - self.bkg
        else:
            return self.y
        
    def toOmaFile(self,
                  path_to_save=path.expanduser('~'),
                  delimiter='\t',
                  newline='\n',
                  comments='/*',
                  use_header=True):

        ''' Save data to oma file
        '''

        if path.isdir(path_to_save):
            fname = self.fname + '.oma'

        else:
            #TODO: add validation file rutine
            self.fname = path_to_save
            fname = self.fname + '.oma'

        if self.type == 'bkg':
            X = np.column_stack((self.x, self.y))
        else:
            X = np.column_stack((self.x, self.y, self.bkg))
        if use_header:
            header = self.getSpecHeader()
        else:
            header = ''
        #TODO: add error handle
        np.savetxt(fname, X, fmt='%10.0f', delimiter=delimiter, newline=newline, header=header, comments=comments)

    def validateOmaSpec(self):
        ''' Valida oma data '''
        #TODO: add validation for oma settings
        pass
    
    def fromOmaFile(self, fname, sep='\t', comments='/*', headerlines=11):
        ''' Load data from file'
        '''
        f = open(fname, 'r')
        for line in f.readlines()[:headerlines]:
            key, value = line.split("=")
            self.__setattr__(key.strip(comments), value.strip('\'\n'))
        f.close()

        if self.type=='spec':
            cols = (0,1,2)
        elif self.type == 'bkg':
            cols = (0,1)

        import ast
        self.grating_info = ast.literal_eval(self.grating_info)
        self.x, self.y, self.bkg = np.genfromtxt(fname,
                                                 delimiter=sep,
                                                 skip_header=headerlines,
                                                 usecols=cols,
                                                 unpack=True,
                                                 )

