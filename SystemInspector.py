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
    
    def __init__(self,extra_attributes={},extra_attr_names=[]):
        self.attr_names = ['PLATFORM','PYTHON_VERSION','INSTALLED_PYTHON_MODULES']
        self.attributes = {}
        self.add_attribute('PLATFORM', sys.platform)
        self.add_attribute('PYTHON_VERSION', sys.version)
        if os.path.isdir('.git'):
            self.attr_names.append('GIT_HASH')
            self.add_attribute('GIT_HASH', subprocess.check_output(
            ['git', 'log', '--pretty=format:"%H"', '-n', '1']))
        if os.path.isdir('.svn'):
            self.attr_names.append('SUBVERSION')
            self.add_attribute('SUBVERSION', True)
        if os.path.isdir('.hg'):
            self.attr_names.append('MERCURIAL')
            self.add_attribute('MERCURIAL', True)
        self.add_attribute('INSTALLED_PYTHON_MODULES', sys.modules.keys())
        for attr in extra_attr_names:
            self.attr_names.append(attr)
            self.add_attribute(attr,extra_attributes[attr])
        
    def add_attribute(self,key,value):
        self.attributes[key] = value
            
    def write_to_file(self,filename='system_info.txt'):
        fout = open(filename, 'w')
        for attr in self.attr_names:
            st = attr + ': ' + str(self.attributes[attr]) + '\n'
            fout.write(st)
        fout.close()
        
    
    
    
    