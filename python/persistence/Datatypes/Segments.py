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
import importlib
import argparse
import multiprocessing
import os
from persistence.Datatypes.JSONObject import JSONObject, load_data, save_data, cond_get, cond_get_obj_list

class SegmentInfo(JSONObject):
    '''
    Strips out the "important" data to keep about segments to forward through computation
    SegmentInfo.fromJSONDict also works to instantiate from a Segment object
    '''

    fields = ['segment_start', 
              'labels', 
              'filename', 
              'learning',
              'window_size', 
              'data_index',
              'tau']

    def __init__(self, segment_start=0, labels=None,
                 filename=None, learning=None, window_size=None, data_index=None, tau=None):
        self.segment_start = segment_start
        self.labels = labels
        self.filename = filename
        self.learning = learning
        self.window_size = window_size
        self.data_index = data_index
        self.tau = tau

    @classmethod
    def fromJSONDict(cls, json):
        return cls(segment_start = cond_get(json, 'segment_start'),
                   labels        = cond_get(json, 'labels'),
                   filename      = cond_get(json, 'filename'),
                   learning      = cond_get(json, 'learning'),
                   window_size   = cond_get(json, 'window_size'),
                   data_index    = cond_get(json, 'data_index'),
                   tau           = cond_get(json, 'tau'))

    def max_label(self) :
        max_label = None
        if self.labels != None :
            max_freq = 0
            for (label, freq) in self.labels.items():
                if (freq > max_freq) :
                    max_label = label
                    max_freq = freq
        return max_label        

class Segment(JSONObject):
    fields = ['windows', 
              'segment_start', 
              'segment_size', 
              'window_stride', 
              'window_size', 
              'tau',
              'labels', 
              'filename', 
              'data_index', 
              'label_index',
              'learning']

    def __init__(self, windows=None, segment_start=0, segment_size=0,
                 window_stride=0, window_size=0, labels=None,
                 filename=None, data_index=0, label_index=0, learning=None, tau=None):
        self.windows = windows
        self.segment_start = segment_start
        self.segment_size = segment_size
        self.window_stride = window_stride
        self.window_size = window_size
        self.labels = labels
        self.filename = filename
        self.data_index = data_index
        self.label_index = label_index
        self.learning = learning
        self.tau = tau

    @classmethod
    def fromJSONDict(cls, json):
        return cls(windows       = cond_get(json, 'windows'),
                   segment_start = cond_get(json, 'segment_start'),
                   segment_size  = cond_get(json, 'segment_size'),
                   window_stride = cond_get(json, 'window_stride'),
                   window_size   = cond_get(json, 'window_size'),
                   labels        = cond_get(json, 'labels'),
                   filename      = cond_get(json, 'filename'),
                   data_index    = cond_get(json, 'data_index'),
                   label_index   = cond_get(json, 'label_index'),
                   learning      = cond_get(json, 'learning'),
                   tau           = cond_get(json, 'tau'))

    def toJSONDict(self):
        """
        Overriding here for when windows is 3-D
        """
        item_dict = dict()
        item_dict['windows']       = self.windows
        item_dict['segment_start'] = self.segment_start
        item_dict['segment_size']  = self.segment_size
        item_dict['window_stride'] = self.window_stride
        item_dict['window_size']   = self.window_size
        item_dict['labels']        = self.labels
        item_dict['filename']      = self.filename
        item_dict['data_index']    = self.data_index
        item_dict['label_index']   = self.label_index
        item_dict['learning']      = self.learning
        item_dict['tau']           = self.tau
        return item_dict

    def max_label(self) :
        max_label = None
        if self.labels != None :
            max_freq = 0
            for (label, freq) in self.labels.items():
                if (freq > max_freq) :
                    max_label = label
                    max_freq = freq
        return max_label

def max_label(labels) :
    if isinstance(labels, dict) :
        max_label = None
        max_freq = 0
        for (label, freq) in labels.items():
            if (freq > max_freq) :
                max_label = label
                max_freq = freq
        return max_label
    else :
	return labels
                   
class Segments(JSONObject) :
    fields = [ 'config',
               'segments']
    
    def __init__(self, config, segments=[]):
        self.config = config
        self.segments = segments

    @classmethod
    def fromJSONDict(cls, json):
        return cls(Configuration.Configuration.fromJSONDict(json['config']), 
                   cond_get_obj_list(json, 'segments', Segment))

    @staticmethod
    def get_iterable_field() :
        return 'segments'

    @staticmethod
    def get_segment_filename(config, gz=True):
        raise NotImplementedError()

import Configuration
def main(argv) :
    args = Configuration.parse_args(argv)
    config = list(Configuration.ArgsIter(args))
    
    if (len(config) > 1) :
        print "Unit testing currently supports only one configuration possibility"
    config = Configuration.Configuration.fromJSONDict(config[0])
    # Please don't put colons in your data_file names if you want this to work
    # We interpert "filea:fileb" as ["filea", "fileb"]
    segments_module = importlib.import_module( 'persistence.' + config['data_type'])    
    segments_class = getattr(segments_module, config['data_type']) 

    segments = segments_class(config)
    # generate all the segments to save to disk
    
    if not('outfile' in args[0]) or args[0]['outfile'] == None :
        outfile = segments_class.get_segment_filename(segments.config)
    else :
        outfile = args[0]['outfile']

    print "Writing %s" % outfile
    # Unless told otherwise, don't rewrite the output, because disk IO and gzip are slow
    if (isinstance(segments.config.reevaluate, dict) and 
        'segments' in segments.config.reevaluate.keys() and 
        segments.config.reevaluate['segments'] == True ) or \
       (not os.path.isfile(outfile)) :
        
        save_data(outfile, segments.toJSONDict())

if __name__=="__main__" :
    main(sys.argv)
