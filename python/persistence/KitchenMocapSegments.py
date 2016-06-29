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

class KitchenMocapSegments(Segments):
    """
    Segment generated from motion capture files from the Quality of
    Life Grand Challenge Data Collection main dataset

    Segment labels are gathered from the immediate parent in the
    pathnames of each data file in config.data_file

    e.g. for ['data/cmu-kitchen/S09/Salad/0006660160E3_02-02_17_30_37-time-synch.txt', 
              'data/cmu-kitchen/S50/Brownie/0006660160E3_11-04_16_39_33-time.txt']
         the labels are 'Salad' and 'Brownie'

    The data in each file consists of two header lines and a sequence
    of lines specifying to the accelerometer data at each time
    sample. The values in config.data_index are used as indices into
    each line for the values used in windows and segments.
    """
    def __init__(self, config) :
        super(self.__class__, self).__init__(config)
        self.config.label_index = None
        self.config.data_index = [int(i) for i in self.config.data_index]
        prefix = os.path.commonprefix([os.path.abspath(f) for f in self.config.data_file])
        self.segments = []
        for f in self.config.data_file :
            p = os.path.abspath(f)[len(prefix):] 
            label = p.split('/')[1]
            
            with open(f,'r') as data_file :
                # skip the first two lines
                data = []
                for line in itertools.islice(data_file, 2, None) :
                    line_data = []
                    for i in line.split()[0:-1] :
                        try :
                            line_data.append(float(i))
                        except ValueError as e :
                            line_data.append(i)
                    data.append(line_data)
                for segment_start in range(0, len(data) - self.config.segment_size + 1, 
                                           self.config.segment_stride) :
                    segment_end = segment_start + self.config.segment_size
                    
                    windows = [list(itertools.chain.from_iterable([[d[i] for i in self.config.data_index] 
                                                                   for d in data[window_start : (window_start + self.config.window_size)]]))
                               for window_start in range(segment_start, 
                                                         segment_end - self.config.window_size + 1, 
                                                         self.config.window_stride)]
                    self.segments.append(Segment(windows = windows,
                                                 segment_start = segment_start,
                                                 segment_size = self.config.segment_size,
                                                 window_stride = self.config.window_stride,
                                                 window_size = self.config.window_size,
                                                 labels = dict([(label,self.config.segment_size)]),
                                                 filename = p,
                                                 data_index = self.config.data_index,
                                                 label_index = self.config.label_index))
                print "File %s segments %s" % (p, len(self.segments))

    @staticmethod
    def get_segment_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 'window_size', 'window_stride']
        return get_filename(config, fields, 'KitchenMocapSegments', False)

