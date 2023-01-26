'''
	This script opens an instance of the eevee-based display module
'''

import json, sys, os
from pathlib import Path
from subprocess import Popen
from multiprocessing import Value

from lib.module_base import ProcessBase


class Proc(ProcessBase):
	def start(self, *args, **kwargs):
		self.blender_pid = Value('i', -1)
		super().start(*args, **kwargs)

	def main(self):
		config = self.config

		if config['blend'] == '' or config['init'] == '':
			raise Exception("parameter 'blend' or 'init' not specified")

		dir = Path(__file__).resolve().parents[2]
		with open(dir / 'config/contrib.json') as handle:
			executable_path = Path(json.loads(handle.read())['blender_renderer_executable'])
			if not executable_path.is_absolute():
				executable_path = dir / executable_path

		cmd = [str(executable_path)]
		cmd += [str(config['blend'])]
		cmd += ['--python', str(config['init'])]
		cmd += ['--', '-p', config['pipeline'], '-c', json.dumps(config)]

		print("Calling: ", cmd)
		blender_process = Popen(cmd)
		self.blender_pid.value = blender_process.pid
		blender_process.wait()
		self.blender_pid.value = -1

	def __del__(self):
		if self.blender_pid.value > -1:
			os.kill(self.blender_pid.value, 9)

Module = Proc(None)