from lib.module_base import ModuleBase, ProcessBase
import json
from auxiliary import get_time_ms


class JSONDiskReader(ModuleBase):

    _last_frame = None
    _current_frame = 0
    _delay = None
    _data = {}
    _delay = 0.0
    _current_json = None

    def __init__(self, config,  **kwargs):

        super().__init__(config,**kwargs)

        print("Parsing JSON files:",config['json_filenames'])
        for name, filename in config['json_filenames'].items():
            with open(filename,'r') as fp:
                self._data[name] = json.load(fp)
            print("Read", len(self._data[name]),"frames from",filename)

        if len(self._data):
            self._current_json = list(self._data.keys())[0]
            print("Setting json to:", self._current_json)
            self._current_frame = self.get_num_frames()

        if 'fps' in config:
            self._delay = 1.0 / float(config['fps'])


    def get_num_frames(self):
        return 0 if self._current_json is None else len(self._data[self._current_json])

    def process_control_commands(self, update, receiver_channel = ''):
        if not update:
            return
        
        if 'json_disk_reader_play' in update:
            if update['json_disk_reader_play'] in self._data.keys():
                self._current_json = update['json_disk_reader_play']
                self._current_frame = 0
                print("Playing",update['json_disk_reader_play'])
            else:
                print(update['json_disk_reader_play'],"not found in json files")

        if 'json_disk_reader_fps' in update:
            self._delay = 1.0 / float(update['json_disk_reader_fps'])
            print("FPS",update['json_disk_reader_fps'])

    def process(self, data, image, receiver_channel):

        if self._current_json is None:
            return data, image

        if not self.config['auto_replay'] and self._current_frame == self.get_num_frames():
            return data, image

        current_time = get_time_ms() / 1000

        if self._last_frame is not None and current_time < (self._last_frame + self._delay):
            return data, image
                   
        self._current_frame = self._current_frame % self.get_num_frames()
        data = self._data[self._current_json][str(self._current_frame)]

        self._current_frame += 1
        self._last_frame = current_time

        return data, None



Module = ProcessBase(JSONDiskReader)



