#!/usr/bin/env python
'''Child module of SystemInspector that gathers usefule information
from the Chamview program.

Information:
    number of point kinds
    total number of points
    number of points modified
    total number of frames
    number of frames modified
    image directory
    predictors used
    chooser used
    preprocessor used
'''

import os, sys
import SystemInspector

class ChamviewInspector(SystemInspector):
    
    def __init__(self,command):
        self.chamattr = {}
        SystemInspector.__init__(command)
    
    def get_points_data(self):
        inspector.attributes['DATA_POINTS_MODIFIED'] = 0
        
    def get_frame_data(self):
        inspector.attributes['DATA_FRAMES_MODIFIED'] = 0
        
    def get_image_directory(self):
        inspector.attributes['IMAGE_DIRECTORY'] = '/'
        
    def get_predictors_used(self):
        inspector.attributes['PREDICTORS_USED'] = [1,2]
    
    def get_chooser_used(self):
        inspector.attributes['CHOOSER_USED'] = 'basicGui'
        
    def get_preprocessor_used(self):
        inspector.attributes['PREPROCESSOR_USED'] = ''
        
    def collect_data(self):
        #Get all the information
        self.get_points_data()
        self.get_frame_data()
        self.get_image_directory()
        self.get_predictors_used()
        self.get_chooser_used()
        self.get_preprocessor_used()
        
        
    def write_to_file(self,filename='system_info.txt'):
        fout = open(filename, 'w')
        for attr in self.chamattr:
            st = attr + ': ' + str(self.chamattr[attr]) + '\n'
            fout.write(st)
        fout.close()
        SystemInspector.write_to_file(self,filename)
        

if __name__ == '__main__':
    args = sys.argv[sys.argv.index('chamviewInspector.py')+1:]
    args = ' '.join(args)
    inspector = ChamviewInspector(args)
    inspector.call_command()
    inspector.write_to_file()

