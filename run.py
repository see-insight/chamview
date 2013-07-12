#!/usr/bin/env python
#
# Created by Aaron Beckett June 13, 2013
# Editted by:
#   Aaron Beckett
#
#
'''Chamview Gui used by CLIWrapper to get user inputted options for Chamview.'''

import os, sys
from datetime import date
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from wrappers import cliwrapper
from wrappers import cligui
from wrappers import customWidgets
import vidshop

class ChamviewWrapper(cliwrapper.CLIWrapper):

    def __init__(self):
        command = 'python chamview.py'
        args = [('Image Directory', '-d:_dir_|*'),
                ('Video File', ':'),
                ('FPS', ':'),
                ('Start Time', ':'),
                ('End Time', ':'),
                ('Save Frames Directory', ':'),
                ('Open Existing Points File', '-p:_openfile_:Text File,*.txt'),
                ('Output Points File', '-o:_savefile_:Text File,*.txt'),
                ('Preprocessor', '-i:_menu_:'),
                ('Chooser', '-c:_menu_:BasicGui'),
                ('Store System Info in File', '-w:_savefile_:Text File,*.txt')]
        cliwrapper.CLIWrapper.__init__(self, command, args)

    def create_window(self):
        return ChamviewWindow(self.base_command, self.args, self.options)

class ChamviewWindow(cligui.OptionInputWindow):

    def fill_command(self):
        return QVBoxLayout()

    def fill_body(self):
        # Create boxes to add Widgets to
        self.body = QHBoxLayout()
        lbox = QVBoxLayout()
        rbox = QVBoxLayout()

        # Add Image Directory widget w/ frame grab potential
        label = QLabel('<b>Input Media</b>')
        lbox.addWidget(label)
        in_media = QFrame()
        in_media.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        group = QVBoxLayout()

        self.im_dir_checkbox = QRadioButton('Use Image Directory')
        image_dir = customWidgets.CollapsibleFrame(self.im_dir_checkbox)
        layout = QVBoxLayout()
        label = QLabel('Directory Containing Images')
        layout.addWidget(label)
        layout.addLayout(self.new_directory(self.options[0]))
        image_dir.setLayout(layout)
        self.im_dir_checkbox.setChecked(True)
        group.addWidget(self.im_dir_checkbox)
        group.addWidget(image_dir)

        if vidshop.ffmpeg_installed():
            self.vid_file_checkbox = QRadioButton('Grab Frames from Video')
            grab_frames = customWidgets.CollapsibleFrame(self.vid_file_checkbox)
            layout = QVBoxLayout()
            label = QLabel('Video File')
            layout.addWidget(label)
            layout.addLayout(self.new_file(self.options[1],'open','QuickTime Video (*.mov);;AVI Files (*.avi)'))
            label = QLabel('Frames Per Second')
            layout.addWidget(label)
            layout.addWidget(self.new_int(self.options[2], 1, 100))
            label = QLabel('Start Time (HH:MM:SS)')
            layout.addWidget(label)
            layout.addWidget(self.new_string(self.options[3]))
            label = QLabel('End Time (HH:MM:SS)')
            layout.addWidget(label)
            layout.addWidget(self.new_string(self.options[4]))
            label = QLabel('Directory to Save Frames In')
            layout.addWidget(label)
            save_dir = self.new_directory(self.options[5])
            today = date.today()
            DATE = str(today.year) + '_' + str(today.month) + '_' + str(today.day)
            widget = save_dir.itemAt(0).widget().setText('~/' + DATE + 'frames/')
            layout.addLayout(save_dir)
            grab_frames.setLayout(layout)
            self.vid_file_checkbox.setChecked(False)
            group.addWidget(self.vid_file_checkbox)
            group.addWidget(grab_frames)
        else:
            group.addStretch()
            label = QLabel('*** Install FFMPEG to enable video input ***')
            group.addWidget(label)

        in_media.setLayout(group)
        lbox.addWidget(in_media)

        # Add all other widgets
        arg_names = [x[0] for x in self.args]
        ignore_names = ['Image Directory',
                        'Video File',
                        'FPS',
                        'Start Time',
                        'End Time',
                        'Save Frames Directory']
        for opt in self.options:
            if opt[0] in ignore_names: continue
            i = arg_names.index(opt[0])
            blueprint, required = self.parse_arg(self.args[i][1])
            widget = self.make_widget(blueprint, required, opt)
            rbox.addWidget(widget)

        # Pack self.body
        lbox.addStretch()
        self.body.addLayout(lbox)
        self.body.addWidget(self.vert_line())
        self.body.addLayout(rbox)
        return self.body

    def apply(self):
        cligui.OptionInputWindow.apply(self)

        obj = self.options[0]
        opts =  self.result[2]

        if self.im_dir_checkbox.isChecked():
            opts.append([obj[0], obj[1], str(obj[2])])
        elif self.vid_file_checkbox.isChecked():
            if str(self.options[5][2]) == '':
                today = date.today()
                DATE = str(today.year) + '_' + str(today.month) + '_' + str(today.day)
                self.options[5][2].swap('~/' + DATE + 'frames/')
            vid = str(self.options[1][2])
            fps = int(self.options[2][2])
            begin_time = str(self.options[3][2])
            end_time = str(self.options[4][2])
            save_directory = str(self.options[5][2])
            vidshop.grab_frames(vid, fps, begin_time, end_time, save_directory)
            opts.append([obj[0], obj[1], str(self.options[5][2])])

        self.result = self.result[0], self.result[1], opts


def main():
    '''Open a ChamviewWrapper.'''
    os.chdir('../chamview')
    wrapper = ChamviewWrapper()
    wrapper.wrap()

if __name__ == '__main__':
    sys.exit(main())
