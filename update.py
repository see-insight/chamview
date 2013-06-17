#!/usr/bin/env python
#
#
#   Created by Aaron Beckett 06/17/2013
#

import os
import subprocess

subprocess.call(['git','pull','--all'])
if not os.path.isfile(os.getcwd()+os.path.sep+'.gitmodules'):
    subprocess.call(['git','submodule','init'])
subprocess.call(['git','submodule','update'])
