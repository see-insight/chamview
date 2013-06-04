#!/usr/bin/env python
'''Program for getting system information.

Included information:
    operating system
    git hash of project if applicable
    python version
    installed python modules
    total time target program ran
'''

import os, sys
import subprocess

class SystemInspector:
    
    def __init__(self,command):
        self.attributes = {}
        self.command = command
        self.attributes['PLATFORM'] = sys.platform
        self.attributes['PYTHON_VERSION'] = sys.version
        if os.path.isdir('.git'):
            self.attributes['GIT_HASH'] = subprocess.check_output(['git', 'describe'])
        if os.path.isdir('.svn'):
            self.attributes['SUBVERSION'] = True
        if os.path.isdir('.hg'):
            self.attributes['MERCURIAL'] = True
        self.attributes['INSTALLED_PYTHON_MODULES'] = sys.modules.keys()
        
    def call_command(self):
        self.attribute['EXIT_STATUS'] = subprocess.call(self.command.split())
            
    def write_to_file(self,filename='system_info.txt'):
        fout = open(filename, 'a')
        for attr in self.attributes:
            st = attr + ': ' + str(self.attributes[attr]) + '\n'
            fout.write(st)
        fout.close()
        
if __name__ == '__main__':
    args = sys.argv[sys.argv.index('SystemInspector.py')+1:]
    args = ' '.join(args)
    inspector = SystemInspector(args)
    inspector.call_command()
    inspector.write_to_file()
    
    