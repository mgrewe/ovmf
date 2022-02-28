from lib.module_base import ModuleBase, ProcessBase


class MyModuleClass(ModuleBase):
    def __init__(self, config, **kwargs):
        # constructor overload is optional - remove if not needed
        super().__init__(config, **kwargs)
        # do setup stuff
        print(self.config) #access config when needed


    def process(self, data, image, receiver_channel):
        # image may be None, better check before using!

        # do process stuff - your code goes here!

        return data, image


    def process_control_commands(self, update, receiver_channel = ''):
        # update contains a dict of parameters sent via the OVMF interface

        # do process stuff - your code goes here!
        pass

Module = ProcessBase(MyModuleClass)
