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


import time
import sys
import json
import csv
import itertools
import argparse
from Datatypes.Segments import Segments,Segment
from Datatypes.Configuration import get_filename
import os
class WalkingSegments(Segments):
    """
    Segments generated from the User Identification From Walking Activity 
    https://archive.ics.uci.edu/ml/datasets/User+Identification+From+Walking+Activity
    
    Each data file corresponds to a separate individual, so the file name is used as our classification label.
    Each datapoint is read from the elements of each line, corresponding to the indices listed in config.data_index
    """
    def __init__(self, config) :
        super(self.__class__, self).__init__(config)
        self.segments = []
        if not isinstance(self.config.data_file, list) :
            self.config.data_file = [self.config.data_file]
        if self.config.window_size == -1 :
            self.config.window_size = self.config.segment_size
        for filename in self.config.data_file :
            with open(filename, 'r') as data_file :
                data_reader = csv.reader(data_file, delimiter=',')
                data = [[line[i] for i in self.config.data_index] for line in data_reader]
            for segment_start in range(0, len(data) - self.config.segment_size + 1, self.config.segment_stride) :
                segment_end = segment_start + self.config.segment_size
                self.segments.append( Segment(windows = [[float(item) for sublist in data[window_start:(window_start + self.config.window_size)] for item in sublist] 
                                                 for window_start in range(segment_start, segment_end - self.config.window_size + 1, self.config.window_stride)],
                                      segment_start=segment_start,
                                      segment_size=self.config.segment_size,
                                      window_stride=self.config.window_stride,
                                      window_size=self.config.window_size,
                                      labels=dict([(filename.split('/')[-1], segment_end - segment_start)]),
                                      filename=filename,
                                      data_index=self.config.data_index,
                                      label_index=self.config.label_index))
    
    @staticmethod
    def get_segment_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 'window_size', 'window_stride']
        return get_filename(config, fields, 'WalkingSegments', gz)

