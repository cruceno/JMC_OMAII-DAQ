Software de adquisicion de datos para ST-1461 (OMA III) 
-------------------------------------------------------

The Model 1461 Detector  Interface is a desktop size device designed to acquire data from a light detector.
The data is stored in  the 1461's memory and can be read by an external "host" computer.
Under command of  the user, the external computer not only accepts data from the 1461, 
but it  also controls the  entire  data acquisition process. 

This control is maintained by means of a  set of special commands that  the Model 1461 interprets and executes. 
The 1461 itself does not analyze the data it  receives; it is up to the host computer and  its software to perform this task. 
The Model 1461 has no user controls, other than a power switch. Likewise, it  does not  directly present  information to  the  operator, aside  from that given by its six status lights. 
It  functions,  basically, as an interface between the computer and  the  detector. 
In  addition,  it  serves as the power source for the detector and the detector controller. 

.. automodule:: pyoma.instrument.oma
   :members: