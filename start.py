#!/usr/bin/env python3

import sys, mmap
import queue, time
import importlib
from pathlib import Path
from threading import Thread
from argparse import ArgumentParser

dir = Path(__file__).resolve().parents[1]
if not str(dir) in sys.path:
    sys.path.append(str(dir))
from lib.module_base import loadConfig


PROTOCOL = 'tcp'
HOST = '127.0.0.1'
STARTING_PORT = 5555


class KeyboardThread(Thread):
	def __init__(self, name='keyboard-input-thread'):
		self.last_input = queue.Queue(3)
		super().__init__(name=name)
		self.daemon = True
		self.start()

	def run(self):
		while True:
			inp = sys.stdin.readline()
			try:
				self.last_input.put_nowait(inp)
			except queue.Full:
				try:
					self.last_input.get()
				except queue.Empty:
					pass
				self.last_input.put(inp)

	def get_line(self, block=True):
		try:
			return self.last_input.get(block=block)
		except queue.Empty:
			return None


class ZIB_Pipeline:
	def __init__(self, pipeline):
		"""prepare pipeline startup and read configs"""
		self.modules_started = {}
		self.pipeline = pipeline
		self.global_config, self.local_config = loadConfig(pipeline)
		self.log = None

	def start(self):
		"""start all modules as defined by this pipeline"""
		next_port = STARTING_PORT

		# find starting modules and add to waiting list
		modules = list(self.local_config.items())
		modules_waiting = dict()
		nm = int(len(self.local_config)) ** 2 + 1
		while len(modules):
			m, c = modules.pop(0)
			if 'receive' in c:
				for n in c['receive'].values():
					modules.append([n, self.local_config[n]])
			else:
				modules_waiting[m] = c
			nm -= 1
			if nm == 0:
				raise RecursionError("Check pipeline configuration, there may be a loop!")

		# begin starting modules in waiting list
		while len(modules_waiting):
			# prepare config for this module
			module, config = list(modules_waiting.items())[0]
			del modules_waiting[module]
			if module in self.modules_started:
				return
			try:
				global_config = self.global_config[module]
			except:
				raise NameError(f"Module {module} does not exist in global config!")
			if 'receive' in config:
				recv = dict()
				for t, n in config['receive'].items():
					if n in self.modules_started:
						recv[t] = self.modules_started[n]['address']
					else:
						modules_waiting[module] = config
						recv = dict()
				if len(recv) == 0:
					continue
				config['receive'] = recv
			config = {**global_config, **config}
			config['pipeline'] = self.pipeline
			config['name'] = module
			if not 'address' in config:
				config['address'] = f"{PROTOCOL}://{HOST}:{next_port}"
			if not 'send_image' in config:
				config['send_image'] = True
			config['control_commands'] = self.global_config["control_commands"]['address']
			next_port += 1

			# start this module
			print('# started', module)
			module_path = config['file'][:-3].replace('/', '.')
			module_code = importlib.import_module(module_path)
			proc = module_code.Module
			proc.start(config)
			config['process'] = proc
			self.modules_started[module] = config

			# add child modules to waiting list
			for m, c in self.local_config.items():
				if 'receive' in c:
					for n in c['receive'].values():
						if n == module:
							modules_waiting[m] = c

	@property
	def running(self):
		return len(self.modules_started) > 0

	def openLog(self, module):
		self.log = open(f"logs/{self.modules_started[module]['name']}.txt", 'r+')
#		print("\033c", end="") # clear screen
		print(f"\n\n#####################\n# {self.modules_started[module]['name']}\n#####################\n")

	def checkModules(self):
		for m in list(self.modules_started.keys()):
			if not self.modules_started[m]['process'].is_alive():
				self.openLog(m)
				fm = mmap.mmap(self.log.fileno(), 0, access=mmap.ACCESS_READ)
				i = fm.find('\n\n##### Unhandled Exception #####\n'.encode())
				if i != -1:
					print(fm[i+2:].decode())
					self.stop()
					break
				print('module terminated')
				self.log = None
				del self.modules_started[m]

	def stop(self):
		self.modules_started = {}


if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('-p', '--pipeline', required=True)
	args, _ = parser.parse_known_args()

	pipeline = ZIB_Pipeline(args.pipeline)
	pipeline.start()

	keyboard = KeyboardThread()
	curr_mod = -1
	print('#####  press n + return to switch output  #####  press q + return to quit  #####')

	while pipeline.running:
		time.sleep(0.01)
		pipeline.checkModules()
		k = keyboard.get_line(block=False)
		if k:
			if 'q' in k.lower():
				pipeline.stop()
			elif 'n' in k.lower():
				modules = list(pipeline.modules_started.keys())
				curr_mod = (curr_mod + 1) % len(modules)
				pipeline.openLog(modules[curr_mod])
		if pipeline.log:
			for i in range(20):
				t = pipeline.log.readline()
				if len(t):
					print(t, end='')
				else:
					break
	pipeline.stop()
	