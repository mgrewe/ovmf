from lib.module_base import ModuleBase, ProcessBase
import auxiliary
import numpy as np

class Delay(ModuleBase):

    psychopy_receiver = None
    buffer_size = 30 * 5
    buffer = dict()
    delay_in_ms = 0

    def process_control_commands(self, data, receiver_channel = ''):
        if data is not None:
            if 'delay' in data:
                self.delay_in_ms = data['delay']

    def process(self, data, image, receiver_channel = ''):
        
        if data is not None and 'timestamp' in data:
            ts = data['timestamp']
            self.buffer[ts] = data
            self.clean_buffer()

        # what is the reference time? 
        # changed from:
        #   now = int(time.clock_gettime(time.CLOCK_MONOTONIC)*1000)
        # to 
        # timestamp in data

        return self.get_delayed_package(data['timestamp']), image

    def clean_buffer(self):
        buffer = self.buffer
        keys = sorted(buffer.keys())
        while (len(buffer) > self.buffer_size):
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
        delayed_ts = self.get_nearest_timestamp(now - self.delay_in_ms)
        if delayed_ts is None:
            print(now, ": no packages yet...")
            return
        return self.buffer[delayed_ts]

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

Module = ProcessBase(Delay)
