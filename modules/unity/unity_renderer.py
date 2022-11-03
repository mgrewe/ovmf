import json, os
from pathlib import Path
from subprocess import Popen
from multiprocessing import Value

from lib.module_base import ProcessBase


class Proc(ProcessBase):
	def start(self, *args, **kwargs):
		self.renderer_pid = Value('i', -1)
		super().start(*args, **kwargs)

	def main(self):
		config = self.config

		dir = Path(__file__).resolve().parents[2]
		with open(dir / 'config/contrib.json') as handle:
			executable_path = Path(json.loads(handle.read())['unity_renderer_executable'])
			if not executable_path.is_absolute():
				executable_path = dir / executable_path

		cmd = [str(executable_path)]
		cmd += ['-sender_host', str(config['address'])]
		cmd += ['-tracker_host', str(list(config['receive'].values())[0])]
		cmd += ['-control_commands_host', str(config['control_commands'])]
		cmd += ['-show_screen', str(config['show_screen'])]
		cmd += ['-screen-width', str(config['screen_width'])]
		cmd += ['-screen-height', str(config['screen_height'])]
		cmd += ['-pipeline', config['pipeline']]
		cmd += ['-logfile', f'logs/{config["name"]}.txt']

		print("Calling: ", cmd)
		renderer_process = Popen(cmd)
		self.renderer_pid.value = renderer_process.pid
		renderer_process.wait()
		self.renderer_pid.value = -1

	def __del__(self):
		if self.renderer_pid.value > -1:
			os.kill(self.renderer_pid.value, 9)

Module = Proc(None)
