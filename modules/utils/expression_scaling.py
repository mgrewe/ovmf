from lib.module_base import ModuleBase, ProcessBase


class ExpressionScaling(ModuleBase):

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.au_scale = config['expressionscaling_au_scale']


    def process(self, data, image, receiver_channel):
        if 'au' in data.keys():
            for key, value in data['au'].items():
                data['au'][key] = self.au_scale * value
        return data, image


    def process_control_commands(self, update, receiver_channel):
        if 'expressionscaling_au_scale' in update:
            self.au_scale = float(update['expressionscaling_au_scale'])
        

Module = ProcessBase(ExpressionScaling)
