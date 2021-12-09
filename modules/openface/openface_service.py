import sys
import json
import argparse
from pathlib import Path
from subprocess import call
sys.path.append(str(Path(__file__).resolve().parents[2]))
from lib.connection import getAddress


'''
 Openface FeatureExtractionService parameters:
		-scale %d		- Internally scale images for landmark detection. Recommended for larger images (optimum is about 800-1000pxl height).
		-wait 			- Wait for receivers to connect. Will connect to image source publisher before a receiver is connected.
		-net-timeout	- Timeout in msec for receiving socket.
		-net-out		- Address of landmark output socket [automatically set from modules.json by openface.py].
		-net-in			- Address of image source publisher to receive from [automatically set from pipelines by openface.py].
							  [Openface default parameters like '-device'/'-f'/'-fdir' do still exist and can be used instead of '-net-in']
'''


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--pipeline', required=True)
	args, _ = parser.parse_known_args()
	params = sys.argv[1:]
	try:
		i = params.index('-p')
	except:
		i = params.index('--pipeline')
	del params[i:i+2]

	dir = Path(__file__).resolve().parents[2]
	with open(dir / 'config/contrib.json') as handle:
		handle = json.loads(handle.read())
		executable_path = dir / handle['openface_executable']
	host, publishers = getAddress('openface_service', args.pipeline)

	cmd = [str(executable_path)]
	if host is not None:
		cmd += ['-net-out', host]
	if publishers is not None:
		for k, v in publishers.items():
			cmd += ['-net-in', v[1]]
	for p in params:
		cmd += [p]

	print('Calling: ', cmd)
	call(cmd)
