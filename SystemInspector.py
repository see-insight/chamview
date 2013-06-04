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
    
    def __init__(self,extra_attributes):
        self.attributes = {}
        self.add_attribute('PLATFORM', sys.platform)
        self.add_attribute('PYTHON_VERSION', sys.version)
        if os.path.isdir('.git'):
            self.add_attribute('GIT_HASH', subprocess.check_output(
            ['git', 'log', '--pretty=format:"%H"', '-n', '1']))
        if os.path.isdir('.svn'):
            self.add_attribute('SUBVERSION', True)
        if os.path.isdir('.hg'):
            self.add_attribute('MERCURIAL', True)
        self.add_attribute('INSTALLED_PYTHON_MODULES', sys.modules.keys())
        for key, value in extra_attributes:
            self.add_attribute(key,value)
        
    def add_attribute(self,key,value):
        self.attributes[key] = value
            
    def write_to_file(self,filename='system_info.txt'):
        fout = open(filename, 'w')
        for attr in self.attributes:
            st = attr + ': ' + str(self.attributes[attr]) + '\n'
            fout.write(st)
        fout.close()
        
    
    
    
    