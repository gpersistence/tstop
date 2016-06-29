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
from Datatypes.Configuration import get_filename
from Datatypes.Segments import Segments, Segment
import os


class PAMAPSegments(Segments):
    """
    Segments generated from the Physical Activity Monitoring Data Set from 
    https://archive.ics.uci.edu/ml/datasets/PAMAP2+Physical+Activity+Monitoring
    
    Labels are derived from the second value in each line of the file,
    followed by a heart rate and readings from three inertial
    measurement units (that sporadically have dropped values). The
    values in config.data_index correspond to the index of the data
    values used for segments and windows. In the event of a dropped
    value, indicated by NaN in the file, we carry over the previous
    data value.
    """
    def __init__(self, config) :
        config.label_index = 1
        super(self.__class__, self).__init__(config)
        if isinstance(self.config.data_file, list) :
            self.config.data_file = self.config.data_file[0]
        if not isinstance(self.config.data_index, list) :
            self.config.data_index = [self.config.data_index]
        with open(self.config.data_file, 'r') as data_file :
            data_reader = csv.reader(data_file, delimiter=' ')
            full_data = [line for line in data_reader]

        # carry over previous values for any NaNs
        prev_line = full_data[0]
        line_range = range(len(prev_line))
        for line in full_data[1:] :
            for (l0, l1, i) in zip(prev_line, line, line_range) :
                if l1 == "NaN" :
                    line[i] = l0
            prev_line = line
        label_set = set([d[self.config.label_index] for d in full_data])

        if self.config.window_size == -1 :
            self.config.window_size = self.config.segment_size
        self.segments = []
        for segment_start in range(0, len(full_data) - self.config.segment_size + 1, self.config.segment_stride) :
            segment_end = segment_start + self.config.segment_size
            windows = []
            # if the data_index has more than one entry, interleave the results.
            # e.g. if data_index is [1,2] it's [(x_0, label), (y_0, label), (x_1, label), (y_1, label)...]
            for window_start in range(segment_start, segment_end - self.config.window_size + 1, self.config.window_stride):
                window_end = window_start + self.config.window_size
                windows.append(list(itertools.chain(*itertools.izip(*[[float(d[i]) for d in full_data[window_start:window_end]] \
                                                                      for i in self.config.data_index]))))
            
            labels = [d[self.config.label_index] for d in full_data[segment_start:segment_end]]
            label_dict = dict([(str(l), len([d for d in labels if d == l])) for l in list(set(labels))])
            segment = Segment(windows=windows,
                              segment_start=segment_start,
                              segment_size=self.config.segment_size,
                              window_stride=self.config.window_stride,
                              window_size=self.config.window_size,
                              labels=label_dict,
                              filename=self.config.data_file,
                              data_index = self.config.data_index,
                              label_index = self.config.label_index)
            self.segments.append(segment)
    
    @staticmethod
    def get_segment_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 'window_size', 'window_stride']
        return get_filename(config, fields, 'PAMAPSegments', gz)

