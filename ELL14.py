#!/usr/bin/python3 -u

from ast import Num
from gzip import READ
from tango import AttrWriteType, DevState, DebugIt
from tango.server import Device, attribute, command, device_property

from thorlabs_elliptec import ELLx, ELLError, ELLStatus, list_devices


class ELL14(Device):
    """ELL14
    This controls an  ELL14 - Rotation Mount
    """
    
    Port = device_property(dtype='str')
    Address = device_property(dtype='int')
    
    

    
    position = attribute(
        min_value = 0.0,
        max_value = 360.0,
        dtype='float',
        access=AttrWriteType.READ_WRITE,
        label="Position",
        unit="degree",
        format="%6.3f",
        doc = 'absolute position in degrees'
    )
    numOperations = attribute(
        min_value = 0,
        max_warning = 10000,
        dtype='int',
        label = "number of Movements",
        format = "%5.0f",
        doc= "number of movements since last Swipe operation",
        #hw_memorized = True,
        #access=AttrWriteType.READ_WRITE
        )
    
    
    #numOperations=0   

    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.INIT)
        self.counter = 0
        try:
            self.stage = ELLx(serial_port=self.Port)
            self.info_stream('Connected to Port {:s}'.format(self.Port))
            self.set_state(DevState.ON)
        except:
            self.error_stream('Cannot connect on Port {:s}'.format(self.Port))
            self.set_state(DevState.FAULT)

    def always_executed_hook(self):
        info = ""
        if self.counter > 10000:
            info = "PLEASE EXECUTE SWIPE OPERATION!!!"
        if self.stage.is_moving():
            self.set_state(DevState.MOVING)
            info += "\nThe divice Status is MOVING"
        else:
            self.set_state(DevState.ON)
            info += "\nThe divice Status is ON"
        self.set_status(info)


    def read_position(self):
        self.position = self.stage.get_position()
        return self.position

    


    @DebugIt()
    def write_position(self, value):
        self.stage.move_absolute(value)
        self.set_state(DevState.MOVING)
        self.counter +=1

    def read_numOperations(self):
        
        return self.counter

    

    @command()
    def Homing(self):        
        self.stage.home()
        self.set_state(DevState.MOVING)
        self.counter +=1
    
    @command()
    def Swipe(self):
        self.stage.move_relative(270.)
        self.stage.move_relative(-540.)
        self.stage.move_relative(270.)
        self.counter = 0


# start the server
if __name__ == '__main__':
    ELL14.run_server()
