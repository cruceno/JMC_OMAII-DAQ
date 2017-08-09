'''
Created on 2 jun. 2017

@author: javier
'''
import sys
from serial import Serial


def scan_serial_ports(num_ports=20, verbose=True):
    '''Configuracion de puerto serie
    Parametros
    ----------
        num_ports: Cantidad de puertos series a escanear
        verbose: Muestra informacion del proceso
    '''
    # Lista de los dispositivos serie. Inicialmente vacia
    dispositivos_serie = []
    # num_ports =100
    if verbose:
        sys.stdout.write("Escanenado %d puertos serie:\n" % num_ports)

    # Escanear num_port posibles puertos serie
    for i in range(num_ports):

        if verbose:
            sys.stdout.write("puerto %d: \n" % i)
            sys.stdout.flush()
        if sys.platform == 'win32':
            try:
                # Abrir puerto serie

                    s = Serial("COM%d" % i)
                    if verbose:
                        sys.stdout.write("OK --> %s\n" % s.portstr)
                    # Si no hay errores, anadir el numero y nombre a la lista
                    dispositivos_serie.append((i, s.portstr))

                    # Cerrar puerto
                    s.close()
            # Si hay un error se ignora
            except:
                if verbose:
                    sys.stdout.write("COM: NO\n")

        if sys.platform.startswith('linux'):
            try:
                # Abrir puerto serie
                    s = Serial('/dev/ttyS' + str(i))
                    if verbose:
                        sys.stdout.write("OK --> %s\n" % s.portstr)
                    # Si no hay errores, anadir el numero y nombre a la lista
                    dispositivos_serie.append((i, s.portstr))
                    # Cerrar puerto
                    s.close()
            # Si hay un error se ignora
            except:
                if verbose:
                    sys.stdout.write("/dev/ttyS: NO\n")

            try:
                # Abrir puerto serie
                    s = Serial('/dev/ttyUSB' + str(i))
                    if verbose:
                        sys.stdout.write("OK --> %s\n" % s.portstr)
                    # Si no hay errores, anadir el numero y nombre a la lista
                    dispositivos_serie.append((i, s.portstr))
                    # Cerrar puerto
                    s.close()
            # Si hay un error se ignore
            except:
                if verbose:
                    sys.stdout.write("/dev/ttyUSB%s: NO\n" % i)
                pass
            try:
                # Abrir puerto serie
                    s = Serial('/dev/ttyACM' + str(i))
                    if verbose:
                        sys.stdout.write("OK --> %s \n" % s.portstr)
                    # Si no hay errores, anadir el numero y nombre a la lista
                    dispositivos_serie.append((i, s.portstr))
                    # Cerrar puerto
                    s.close()
            # Si hay un error se ignore
            except:
                if verbose:
                    sys.stdout.write("/dev/ttyACM: NO\n")
                pass
    # Devolver la lista de los dispositivos serie encontrados
    return dispositivos_serie

