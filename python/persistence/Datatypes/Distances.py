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

from persistence.Datatypes.JSONObject import JSONObject, cond_get, cond_get_obj_list
from persistence.Datatypes.Configuration import Configuration, get_filename
from persistence.Datatypes.Segments import SegmentInfo

class Distance(JSONObject) :
    fields = ['min',
              'mean',
              'max', 
              'std']
    def __init__(self, min=None, mean=None, max=None, std=None) :
        self.min = min
        self.max = max
        self.mean = mean
        self.std = std

    @classmethod
    def fromJSONDict(cls, json):
        return cls(cond_get(json,'min'),
                   cond_get(json,'mean'),
                   cond_get(json,'max'),
                   cond_get(json,'std'))
        

class Distances(JSONObject) :
    fields = ['config',
              'distances',
              'segment_info']
    def __init__(self, config, distances=None, segment_info=None):
        self.config = config
        self.distances = distances
        self.segment_info = segment_info

    @classmethod
    def fromJSONDict(cls, json):
        return cls(Configuration.fromJSONDict(json['config']), 
                   [[Distance.fromJSONDict(d) for d in row] for row in json['distances']],
                   cond_get_obj_list(json, 'segment_info', SegmentInfo))

    @staticmethod
    def get_distances_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size',
                  'segment_stride', 'window_size', 'window_stride',
                  'max_simplices', 'persistence_epsilon']
        if config.post_process != None :
            fields.extend(['post_process', 'post_process_arg'])

        return get_filename(config, fields, "Distances", gz)
