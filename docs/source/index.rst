.. PyOma documentation master file, created by
   sphinx-quickstart on Mon Jun 26 18:56:43 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Bienvenido a la documentacion de PyOma
=================================================================
Breve Introducción
------------------
Pyoma es una aplicación destinada al control del ST-1461 de Princeton Instruments (OMAIII). 
 
Actuamente e encuentra en desarrollo lo que sera la versión final de la misma. Estan en uso en el ambito del laboratorio 
de Física del Plasma del Instituto de Física Rosario, versiones beta que cumplen funciones minimas con algunos "bugs". 

El modelo *ST-1461 de Princeton Instrument* es un dispositivo de escritorio diseñado para adquirir datos desde un 
detector de luz. Los datos son almacenados en la memoria interna del equipo y pueden ser capturados por una computadora externa.
Bajo instrucciones del usuario la computadora no solo accede a los datos en el dispositivo sin no que también controla todo el 
proceso de adquisición. 

Este control se realiza a través de una serie de comandos que deben ser enviados al dispositivo. El ST-1461 en si no realiza ningún 
análisis sobre los datos que recibe desde e sensor de luz, el mismo debe ser realizado por la computadora externa y el software 
utilizado en la misma. El equipo no puede ser controlado de forma directa por el usuario dado que no presenta ningun tipo de 
interruptor o mando físico que permita su operación salvo el de encendido. La función que cumple es basicamente la de  
intermediario entre la computadora y el detector.

Debido a que el dispositivo es de los años 80' no se cuenta con un software de adquisición de datos que sea compatible con los
sistemas informáticos modernos. Para poder afrontar este inconveniente se decide desarrolar una aplicación que permita la operacion
básica del equipo a traves de su interface de comunicación RS232.

.. toctree::
   :maxdepth: 2
   :hidden:
   
   intro
   screenshots
   use
	

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
