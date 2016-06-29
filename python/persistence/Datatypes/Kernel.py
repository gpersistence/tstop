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
from persistence.Datatypes.Configuration import Configuration
from persistence.Datatypes.JSONObject import JSONObject, cond_get, cond_get_obj_list
from persistence.Datatypes.Segments import SegmentInfo

class Kernel(JSONObject) :
    fields = ['config',
              'kernel_matrix',
              'segment_info']
    def __init__(self, config, kernel_matrix=None, segment_info=None):
        self.config        = config
        self.kernel_matrix = kernel_matrix
        self.segment_info = segment_info

    @classmethod
    def fromJSONDict(cls, json):
        return cls(Configuration.fromJSONDict(json['config']),
                   kernel_matrix=json['kernel_matrix'],
                   segment_info=cond_get_obj_list(json, 'segment_info', SegmentInfo))

    @staticmethod
    def get_kernel_filename(config, gz=True):
        raise NotImplementedError()
