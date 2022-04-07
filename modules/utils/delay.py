from lib.module_base import ModuleBase, ProcessBase
import numpy as np

class Delay(ModuleBase):

    buffer = dict()

    def process_control_commands(self, data, receiver_channel = ''):
        if data is not None:
            if 'delay_sec' in data:
                self.config['delay_sec'] = data['delay_sec']

    def process(self, data, image, receiver_channel = ''):
        
        if data is not None and 'timestamp' in data:
            ts = data['timestamp']
            self.buffer[ts] = data
            delayed_data = self.get_delayed_package(data['timestamp'])
            self.clean_buffer(data['timestamp'])

            return delayed_data, image

        return data, image

    def clean_buffer(self, now):
        buffer = self.buffer
        keys = sorted(buffer.keys())
        # Determine buffer size from delay, i.e., double it
        while (keys[0] < (now - self.config['delay_sec'] * 1000 * 2)):
            del buffer[keys[0]]
            del keys[0]

    def find_nearest(self, array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx]

    def get_nearest_timestamp(self, delay):
        buffer = self.buffer
        if len(buffer) == 0:
            return None
        keys = sorted(buffer.keys())
        nn_time = self.find_nearest(np.array(keys), delay)
        return nn_time

    def get_delayed_package(self, now):
        delayed_ts = self.get_nearest_timestamp(now - self.config['delay_sec'] * 1000)
        if delayed_ts is None:
            print(now, ": no packages yet...")
            return
        return self.buffer[delayed_ts]

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

Module = ProcessBase(Delay)
