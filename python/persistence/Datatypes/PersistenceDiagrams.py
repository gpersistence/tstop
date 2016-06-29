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


#!/usr/bin/python
import os
from persistence.Datatypes.Configuration import Configuration, get_filename
from persistence.Datatypes.JSONObject import JSONObject, cond_get, cond_get_obj_list
from persistence.Datatypes.Segments import SegmentInfo

class PersistenceDiagram(JSONObject):
    fields = ['segment_info', 
              'points']

    def __init__(self, segment_info=None, points=None):
        self.segment_info = segment_info
        # Points are [birth, death, dimension]
        self.points = points

    @classmethod
    def fromJSONDict(cls, json):
        return cls(SegmentInfo.fromJSONDict(json['segment_info']) if 'segment_info' in json else None, 
                   points = cond_get(json, 'points'))

class PersistenceDiagrams(JSONObject) :
    fields = ['config',
              'diagrams']
    def __init__(self, config, diagrams):
        self.config = config
        self.diagrams = diagrams

    @classmethod
    def fromJSONDict(cls, json):
        return cls(Configuration.fromJSONDict(json['config']), 
                   cond_get_obj_list(json, 'diagrams', PersistenceDiagram))

    @staticmethod
    def get_iterable_field() :
        return 'diagrams'

    @staticmethod
    def get_persistence_diagrams_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size',
                  'segment_stride', 'window_size', 'window_stride',
                  'max_simplices', 'persistence_epsilon']
        if config.post_process != None :
            fields.extend(['post_process', 'post_process_arg'])

        return get_filename(config, fields, "PersistenceDiagrams", gz)
