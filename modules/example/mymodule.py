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


Module = ProcessBase(MyModuleClass)
