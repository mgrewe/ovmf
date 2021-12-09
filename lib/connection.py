import sys
import json
import time
import argparse
import pathlib as pl
import threading
import queue
import numpy as np
import zmq
import cv2
sys.path.append(str(pl.Path(__file__).resolve().parents[0]))

# The threshold of pixels before images are compressed as jpeg before passing them between pocesses, -1 dactivates compression
#NO_OF_PIX_BEFORE_USING_JPEG_COMPRESSION = 3 * 640 * 480
NO_OF_PIX_BEFORE_USING_JPEG_COMPRESSION = -1


def Receiver(address=None, type='data_type', queue_size=1):
	""" creates a dict of receivers data_type and address string
	queue_size defines how many unread messages are kept before droping some. value of 0 means no limit (better do not do this).
	"""
	if address is None:
		raise RuntimeError("no host address provided")
	publishers = {type: ['module', address]}
	context = zmq.Context()
	socks = dict()
	if publishers:
		for k, v in publishers.items():
			socks[k] = _Receiver(context, v[1], queue_size)
			print(f"receive {k} from {v[0]} ({v[1]})")
	return socks

class _Receiver:
	def __init__(self, context, host, queue_size):
		self.sock = context.socket(zmq.SUB)
		self.sock.setsockopt(zmq.LINGER, 500)
		self.sock.setsockopt(zmq.RCVHWM, queue_size)
		self.sock.setsockopt(zmq.SUBSCRIBE, b"")
		self.sock.connect(host)
		self.queue = queue.Queue(maxsize=queue_size)
		def recv_func():
			while True:
				msg = self.sock.recv_multipart(copy = False)
				data = json.loads(msg[0].bytes)
				if len(msg) == 1:
					image = None
				else:
					if 'image_compressed' in data and data["image_compressed"] == 1:
						image = cv2.imdecode(np.frombuffer(msg[1].buffer, np.uint8), cv2.IMREAD_UNCHANGED)
					else:
						image = np.frombuffer(msg[1].buffer, np.uint8).reshape(data['image_shape'])
				try:
					self.queue.put_nowait((data, image))
				except queue.Full:
					try:
						self.queue.get()
					except queue.Empty:
						pass
					self.queue.put((data, image))
		self.thread = threading.Thread(target=recv_func)
		self.thread.daemon = True
		self.thread.start()

	def receive(self, block=True):
		""" receives a dict (and image) from sender """
		try:
			data, image = self.queue.get(block=block)
		except queue.Empty:
			data, image = (None, None)
		return (data, image)

	def poll(self, timeout=0.04, sleep_per_retry=0.001):
		""" poll for incomeing messages till one is received or timeout (in secounds) is hit """
		first_run = True
		start = time.monotonic()
		while (start + timeout > time.monotonic() or first_run):
			first_run = False
			data, image = self.receive(False)
			if data is None:
				time.sleep(sleep_per_retry)
			else:
				return (data, image)
		return (None, None)


def Sender (address=None):
	""" creates a sender by address string.
	"""
	if address is None:
		raise RuntimeError("no host address provided")
	
	if address:
		return _Sender(address)
	else:
		return None

class _Sender:
	def __init__(self, address):
		""" creates a sender by address string """
		self.subscribers = 0

		self.context = zmq.Context()
		self.sock = self.context.socket(zmq.XPUB)
		self.sock.setsockopt(zmq.LINGER, 500)
		self.sock.bind(address)
		print("sender established at " + address)

	def hasReceiver(self):
		""" returns whether there is at least one subscriber connected """
		try:
			data = self.sock.recv(flags=zmq.NOBLOCK)
			if data[0] == 1:		# subscriber connected
				self.subscribers += 1
			elif data[0] == 0:	# subscriber disconnected
				self.subscribers -= 1
		except zmq.ZMQError:
			pass
		return self.subscribers > 0

	def send(self, msg=dict({}), img=None):
		""" sends a dict (and image) to receiver """
		if img is None:
			self.sock.send_json(msg)
		else:
			msg["image_shape"] = img.shape
			if NO_OF_PIX_BEFORE_USING_JPEG_COMPRESSION < 0 or np.prod(img.shape) <= NO_OF_PIX_BEFORE_USING_JPEG_COMPRESSION:
				msg["image_compressed"] = 0
				image_in_bytes = img.tobytes()
			else:
				msg["image_compressed"] = 1
				_, image_in_bytes = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 25])

			self.sock.send_json(msg, flags=zmq.SNDMORE)
			self.sock.send(image_in_bytes, copy = False)
