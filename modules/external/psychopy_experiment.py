import sys
from pathlib import Path
# import modules.external.ovmf as ovmf
from lib.module_base import ProcessBase

class Proc(ProcessBase):
    def main(self):
        print(self.config['script'])
        exec(open(self.config['script']).read())

Module = Proc(None)


if __name__ == "__main__":
    Module.main()
