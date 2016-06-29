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

from persistence.Datatypes.JSONObject import JSONObject, cond_get, cond_get_obj_list
from persistence.Datatypes.Configuration import Configuration, get_filename
from persistence.Datatypes.Segments import SegmentInfo

class TrainTestPartition(JSONObject) :
    fields = ['train', 
              'test', 
              'state']
    def __init__(self, train=None, test=None, state=None) :
        self.train = train
        self.test = test
        self.state = state

    @classmethod
    def fromJSONDict(cls, json):
        return cls(train = cond_get(json, 'train'),
                   test  = cond_get(json, 'test'),
                   state = cond_get(json, 'state'))


class TrainTestPartitions(JSONObject) :
    fields = ['config',
              'cross_validation',
              'evaluation']
    def __init__(self, config, segment_info=None, cross_validation=None, evaluation=None):
        self.config           = config
        self.segment_info     = segment_info
        self.cross_validation = cross_validation
        self.evaluation       = evaluation

    @classmethod
    def fromJSONDict(cls, json):
        return cls(Configuration.fromJSONDict(json['config']),
                   segment_info=cond_get_obj_list(json, 'segment_info', SegmentInfo),
                   cross_validation=cond_get_obj_list(json, 'cross_validation', TrainTestPartition),
                   evaluation=cond_get_obj_list(json, 'evaluation', TrainTestPartition))

    @staticmethod
    def get_partition_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size',
                  'segment_stride', 'window_size', 'window_stride']

        return get_filename(config, fields, "Partition", gz)

