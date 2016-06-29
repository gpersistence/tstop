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

class Features(JSONObject) :
    fields = ['config',
              'features',
              'segment_info']
    def __init__(self, config, features=None, segment_info=None):
        self.config = config
        self.features = features
        self.segment_info = segment_info

    @classmethod
    def fromJSONDict(cls, json):
        return cls(Configuration.fromJSONDict(json['config']), 
                   [f for f in json['features']],
                   cond_get_obj_list(json, 'segment_info', SegmentInfo))

    @staticmethod
    def get_features_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size',
                  'segment_stride', 'window_size', 'window_stride',
                  'max_simplices', 'persistence_epsilon', 'invariant_epsilon']
        if config.post_process != None :
            fields.extend(['post_process', 'post_process_arg'])

        return get_filename(config, fields, "Features", gz)
