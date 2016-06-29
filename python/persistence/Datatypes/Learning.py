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

from persistence.Datatypes.JSONObject import JSONObject, cond_get, cond_get_obj_list
from persistence.Datatypes.Configuration import Configuration, get_filename

class LearningResult(JSONObject) :
    fields = ['seed',
              'train_labels',
              'test_labels',
              'test_results',
              'mkl_weights']
    def __init__(self, seed, train_labels, test_labels, test_results, mkl_weights=None) :
        self.seed = seed
        self.train_labels = train_labels
        self.test_labels  = test_labels
        self.test_results = test_results
        self.mkl_weights = mkl_weights

    @classmethod
    def fromJSONDict(cls, json) :
        return cls(cond_get(json, 'seed'),
                   json['train_labels'], 
                   json['test_labels'], 
                   json['test_results'], 
                   cond_get(json, 'mkl_weights'))

class Learning(JSONObject) :
    fields = ['config',
              'results',
              'kernel_files']
    def __init__(self, config, results, kernel_files=None):
        self.config = config
        self.results = results
        self.kernel_files = None

    @classmethod
    def fromJSONDict(cls, json):
        return cls(Configuration.fromJSONDict(json['config']), 
                   cond_get_obj_list(json, 'results', LearningResult),
                   cond_get(json, 'kernel_files'))

    def get_average_correct(self) :
        correct = []
        for result in self.results : 
            num_correct = reduce((lambda s, (t0, t1) : s + 1 if t0 == t1 else s), 
                                 zip(result['test_labels'], result['test_results']), 0)
            correct.append(float(num_correct) / float(len(result['test_labels'])))
        import numpy
        return numpy.average(correct)

    @staticmethod
    def get_learning_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size',
                  'segment_stride', 'window_size', 'window_stride',
                  'max_simplices', 'persistence_epsilon',
                  'kernel_scale', 'kernel_gamma', 'learning_C']
        if config.post_process != None :
            fields.extend(['post_process', 'post_process_arg'])

        return get_filename(config, fields, "Learning", gz)
