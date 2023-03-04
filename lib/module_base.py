import time, os, sys, json
from pathlib import Path
import traceback
from contextlib import contextmanager
from multiprocessing import Process

dir = Path(__file__).resolve().parents[1]
if not str(dir) in sys.path:
    sys.path.append(str(dir))
from lib.connection import Sender, Receiver
import lib.auxiliary as aux



class ModuleBase():

    poll_timeout = 0
    module_measurement = True

    def __init__(self, config):
        '''
        Base class for a processing filter within the virtual mirror pipeline. The filter function can be implemented by overwriting the process function.
        
        Typically, the packages are forwarded though the pipeline as specified by the pipelines config file using socket connections such that every filter is started in its own process. However, by creating the objects and calling the processing function explicitly, the socket mechanism can be bypassed. To this end, socket creation and connection can be skipped.

        sockets determines if this module is using communication via sockets.

        queue_size determines the size of the receiver's queue sizes

        drop_images_before_processing causes incoming images to be dropped before processing for performance reasons
        '''
        self.config = config
        self.use_sockets = config['use_sockets']
        if self.use_sockets:
            self.receiver = None
            try:
                self.receiver = dict()
                for type, address in config['receive'].items():
                    self.receiver[type] = Receiver(address=address, type=type, queue_size = config['queue_size'])[type]
            except RuntimeError as e:
                print(e)
            except KeyError:
                pass
            try:
                self.control_command_receiver = Receiver(address = config['control_commands'], type='control_cmds', queue_size=0)['control_cmds']
            except RuntimeError as e:
                self.control_command_receiver = None
                print(e)
            try:
                self.sender = Sender(address = config['address'])
            except RuntimeError as e:
                self.sender = None
                print(e)
        else:
            self.receiver = None
            self.sender = None
            self.control_command_receiver = None
        
    def process(self, data, image, receiver_channel = ''):
        '''
        data contains the received dict.
        receiver_channel contains the name of the channel over which data was received. 
        '''
        return data, image

    def process_control_commands(self, data, receiver_channel = ''):
        '''
        data contains the received dict.
        receiver_channel contains the name of the channel over which data was received. 
        '''
        pass
        

    def add_time_measurement(self, data, start_time, end_time, modulename = None):
        if data is None:
            data = {}
        if modulename is None:
            modulename = str(type(self).__name__)
        if 'time_statistics' not in data.keys():
            data['time_statistics'] = {}
        if modulename not in data['time_statistics'].keys():
            data['time_statistics'][modulename]= {}
                
        # separated time_statistics for processing time and time for the whole process
        data['time_statistics'][modulename]["start_time"] = start_time
        data['time_statistics'][modulename]["end_time"] = end_time

    def process_and_measure(self, data, image, channel_name):
        start_time = aux.get_time_ms()

        data, image = self.process(data, image, channel_name)

        end_time = aux.get_time_ms()

        if (self.module_measurement):
            self.add_time_measurement(data, start_time, end_time)

        return data, image

    def update(self):

        if not self.use_sockets:
            return
            
        # Process controll commands
        data, _  = self.control_command_receiver.receive(block = False)
        while data is not None:
            print("Contol command received: " + str(data))
            self.process_control_commands(data, 'control_commands')
            data, _  = self.control_command_receiver.receive(block = False)

        # Process normal packages
        if self.receiver is not None and len(self.receiver):
            # We have receivers
            for channel_name, receiver in self.receiver.items():
                data, image = receiver.receive(block = False)
                #data, image = receiver.poll(timeout = 0.03, sleep_per_retry = 0.001)
                if data:
                    data, image = self.process_and_measure(data, image, channel_name)
                if data and self.sender:
                    self.sender.send(data, image)
        elif self.sender:
            # We don't have receiver but sender
            data, image = self.process_and_measure(None, None, '')
            if data:
                self.sender.send(data, image if self.config['send_image'] else None)

    def run(self, sleep_time = 0.0005):
        if not self.use_sockets:
            raise RuntimeError("This filter was created without sockets.")
        while True:
            self.update()
            time.sleep(sleep_time)

    def finalize(self):
        pass



def loadConfig(pipeline=None, module=None):
    with open(dir / 'config/modules.json') as f:
        global_config = json.load(f)
    if pipeline:
        pf = dir / f'config/pipelines/{pipeline}.json'
        if not pf.exists():
            raise Exception(f"pipeline '{pipeline}' does not exist")
        with open(pf) as f:
            local_config = json.load(f)
    else:
        local_config = {}
    for m in global_config.keys():
        tmp_config = local_config.get(m, {})
        tmp_config['pipeline'] = pipeline
        tmp_config['name'] = m
        tmp_config['control_commands'] = global_config["control_commands"]['address']
        if not 'send_image' in tmp_config:
            tmp_config['send_image'] = True
        if m == module:
            local_config[m] = tmp_config
    if module:
        return {**global_config[module], **local_config.get(module, {})}
    else:
        return global_config, local_config


# source: https://stackoverflow.com/a/22434262
@contextmanager
def output_redirected(source, target):
    source.write = lambda z: os.write(source.fileno(),z.encode() if hasattr(z,'encode') else z) # windows fix, source: https://www.tutorialguruji.com/python/dup2-and-pipe-shenanigans-with-python-and-windows/amp/
    stdout_fd = source.fileno()
    # copy stdout_fd before it is overwritten
    with os.fdopen(os.dup(stdout_fd), 'wb') as copied: 
        source.flush()  # flush library buffers that dup2 knows nothing about
        os.dup2(target.fileno(), stdout_fd)
        try:
            yield source # allow code to be run with the redirected stdout
        finally:
            # restore stdout to its previous value
            source.flush()
            os.dup2(copied.fileno(), stdout_fd)


class ProcessBase(Process):
    """
    Base class for pipeline module starter. Used to launch modul by start script.
    """
    def __init__(self, Cls, *args, **kwargs):
        self.Cls = Cls
        self.args = args
        self.kwargs = kwargs

    def start(self, config):
        self.config = config
        super().__init__(name=config['name'], daemon=True)
        super().start()

    def main(self):
        m = self.Cls(self.config, *self.args, **self.kwargs)
        m.run()

    def run(self):
        Path('logs').mkdir(parents=True, exist_ok=True)
        with output_redirected(sys.stdout, open(f'logs/{self.name}.txt', 'w', encoding='utf-8')), output_redirected(sys.stderr, sys.stdout):
            try:
                self.main()
            except:
                print("\n\n##### Unhandled Exception #####\n")
                print(traceback.format_exc(), flush=True)
