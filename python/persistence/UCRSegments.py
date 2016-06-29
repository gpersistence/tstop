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

def gen_windows(data, window_size, window_stride):
    return [[x for x in data[window_start:window_start+window_size]] \
            for window_start in range(0, len(data) - window_size + 1, window_stride) ]

def gen_segments(data_fd, sample_count, filename, learning, config) :
    segments = []
    for line in data_fd :
        if ',' in line :
            split_char = ','
        else :
            split_char = ' '
        data = [float(num) for num in line.split(split_char) if num != '']
        segments.append(Segment(windows=gen_windows(data[1:], 
                                                    config.window_size if config.window_size != -1 else len(data)-1, 
                                                    config.window_stride), 
                                     segment_start=sample_count, 
                                     segment_size=len(data)-1,
                                     window_stride=config.window_stride,
                                     window_size=config.window_size if config.window_size != -1 else len(data)-1,
                                     labels=dict([(str(data[0]), len(data)-1)]),
                                     filename=filename,
                                     learning=learning))
        sample_count = sample_count + len(data) - 1
    return sample_count, segments


class UCRSegments(Segments):
    def __init__(self, config) :
        super(self.__class__, self).__init__(config)
        self.segments = []
        sample_count = 0
        # We've been passed a pair of datasets, one to train one to test
        if (isinstance(self.config.data_file, list) and len(self.config.data_file) == 2) :
            with open(self.config.data_file[0], 'r') as data :
                (sample_count, segments) = gen_segments(data, sample_count, self.config.data_file[0], 'train', self.config)
                self.segments.extend(segments)
            with open(self.config.data_file[1], 'r') as data :
                (sample_count, segments) = gen_segments(data, sample_count, self.config.data_file[1], 'test', self.config)
                self.segments.extend(segments)
        else :
            with open(self.config.data_file, 'r') as data :
                (sample_count, segments) = gen_segments(data, sample_count, self.config.data_file, None, self.config)
                self.segments.extend(segments)
        if self.config.window_size == -1 :
            self.config.window_size = len(self.segments[0].windows[0])
        self.config.segment_size = self.segments[0].segment_size
        self.config.segment_stride = self.segments[0].segment_size


    @staticmethod
    def get_segment_filename(config, gz=True):
        if (isinstance(config.data_file, list)):
            (filename, ext) = os.path.splitext(os.path.basename(config.data_file[0]))
            if filename.rfind('_TRAIN') != -1 :
                filename = filename[0:filename.rfind('_TRAIN')]
        else :
            (filename, ext) = os.path.splitext(os.path.basename(config.data_file))
        return "%s/%s-win-%s-%s-UCRSegments.json%s" % \
            (config.out_directory, filename, config.window_size,
             config.window_stride, ".gz" if gz else "")
