#TSTOP
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import time
import sys
import json
import csv
import itertools
import argparse

from Datatypes.Segments import Segments, Segment
from Datatypes.Configuration import get_filename

class BirdSoundsSegments(Segments):
    """ 
    Segment class created for parsing mfcc files generated from the audio files at http://www.xeno-canto.org
    File paths supply our category labels, using the immediate parent of the mfcc file
    e.g. if config.data_file is [ 'data/new_bird_sounds/Colibri-thalassinus/0082.mfcc', 
                                  'data/new_bird_sounds/Cyanocorax-yncas/0066.mfcc' ] 
    then there are two labels, 'Colibri-thalassinus' and 'Cyanocorax-yncas'
    The data format of the mfcc files are simply one floating point number per line, 
    which are then translated to segments and windows.
    """
    def __init__(self, config) :
        super(self.__class__, self).__init__(config)
        self.config.label_index = None
        self.config.data_index = 0
        prefix = os.path.commonprefix([os.path.abspath(f) for f in self.config.data_file])
        self.segments = []
        for f in self.config.data_file :
            p = os.path.abspath(f)[len(prefix):] 
            (label, filename) = p.split('/')
            with open(f,'r') as data_file :
                data = [float(line.strip()) for line in data_file]
            for segment_start in range(0, len(data) - self.config.segment_size + 1, self.config.segment_stride) :
                segment_end = segment_start + self.config.segment_size
                windows = []
                for window_start in range(segment_start, segment_end - self.config.window_size + 1, self.config.window_stride):
                    window_end = window_start + self.config.window_size
                    windows.append(data[window_start:window_end])
                labels = dict([(label,self.config.segment_size)])
                self.segments.append(Segment(windows = windows,
                                             segment_start = segment_start,
                                             segment_size = self.config.segment_size,
                                             window_stride = self.config.window_stride,
                                             window_size = self.config.window_size,
                                             labels = labels,
                                             filename = p,
                                             data_index = self.config.data_index,
                                             label_index = self.config.label_index))
        # Strip out trailing '/'
        self.config.data_file = prefix[0:-1]

    @staticmethod
    def get_segment_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 'window_size', 'window_stride']
        return get_filename(config, fields, 'BirdSoundsSegments', gz)

