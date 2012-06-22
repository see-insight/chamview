import imagestack
from plugins import basepredictor
from plugins import basechooser
import imp
import os
import dircache


def load_plugins(path,expected_class):
    #plugin = [[]]
    file_list = dircache.listdir(path)
    for filename in file_list:
        mod_name,extension = os.path.splitext(os.path.split(filename)[-1])
        if extension != '.py' and extension != '.pyc': continue
        print filename
        mod = imp.load_source(filename,'')
        for cls in dir(module):
            print cls
            #instance = getattr(mod,'__init__')
            #plugin.append([instance,mod_name])
    #return plugin


load_plugins('plugins',basepredictor.BasePredictor)
