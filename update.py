#!/usr/bin/env python
#
#
#   Created by Aaron Beckett 06/17/2013
#

import subprocess

subprocess.call(['git','pull','--all'])
subprocess.call(['git','submodule','init'])
subprocess.call(['git','submodule','update'])
