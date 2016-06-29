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
import sys
import numpy
import json
import time
import argparse 
import multiprocessing
import itertools 
from copy import copy

from Datatypes.JSONObject import load_data, save_data
from Datatypes.Configuration import get_filename, parse_range
from Datatypes.Segments import max_label
from Datatypes.Features import Features
from Datatypes.Learning import Learning, LearningResult
from Datatypes.TrainTestPartitions import TrainTestPartition, TrainTestPartitions
from PartitionData import PartitionData, generate_partitions

from sklearn import svm

class LearningWrapper:
    def __init__(self, features) :
        self.features = features

    def __call__(self, (partition, C)) :
        config = copy(self.features.config)
        config.learning_C = C
        learn = FeatureLearning(config, self.features, partition) 
        learn.train()
        return (C, learn.test())

class FeatureLearning:
    @staticmethod
    def get_input_type():
        return "Features"

    @staticmethod
    def get_output_type():
        return "LearningResult"

    @staticmethod
    def get_scale_arg():
        return "learning_C"

    def __init__(self, config, features, partition, width = 2.0) :
        self.C = config.learning_C
        self.width = width
        self.config = features.config
        self.features = features.features

        self.segment_info = features.segment_info
        self.full_labels = [s.max_label() for s in self.segment_info]

        self.partition = partition
        self.train_indices = self.partition.train
        
        self.train_features = numpy.asarray([self.features[i] for i in self.train_indices])
        self.training_labels = [self.full_labels[i] for i in self.train_indices]
        self.label_set = list(set(self.training_labels))

        self.test_indices = self.partition.test
        self.test_features = numpy.asarray([self.features[i] for i in self.test_indices])
        self.testing_labels = [self.full_labels[i] for i in self.test_indices] 

        self.kernel = None
        self.svm = None


    def train(self) :
        self.svm = svm.SVC(kernel='rbf', C = self.C)
        self.svm.fit(self.train_features, self.training_labels)
        return self.training_labels
    
    def test(self) :
        results = self.svm.predict(self.test_features)
        return LearningResult(self.partition.state, self.training_labels, self.testing_labels, results.tolist())

    @staticmethod
    def get_learning_filename(config, gz=True) :
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 'window_size', 'window_stride', 'learning_C', 'invariant_epsilon']
        if config.post_process != None :
            fields.extend(['post_process', 'post_process_arg'])
        
        return get_filename(config, fields, (config.status + 'Learning') if config.status != None else 'FeatureLearning', gz)
        

def main(argv):
    parser = argparse.ArgumentParser(description='Tool to perform learning on pregenerated features')
    parser.add_argument('-i', '--infile', help='Input JSON Similarity Feature file')
    parser.add_argument('-o', '--outfile', help='Output JSON Learning file')
    parser.add_argument('-p', '--pool', default=multiprocessing.cpu_count(), help='Threads of computation to use')
    parser.add_argument('-c', '--learning-C', help='C value for SVM. Specify a range for 1-dimensional cross-validation')
    parser.add_argument('--timeout', type=int, default=3600)
    parser.add_argument('-t', '--train-test-partitions', help='Precomputed train / test partitions')
    args = vars(parser.parse_args(argv[1:]))
    
    ff_json = load_data(args['infile'], 'features', None, None, "FeatureLearning: ")
    if ff_json == None :
        print "Could not load Features from %s" % (args['infile'],)
        sys.exit(1)
    features = Features.fromJSONDict(ff_json)
    config = features.config
    segment_info = features.segment_info
    if (int(args['pool']) > 1) :
      pool = multiprocessing.Pool(int(args['pool']))
    else :
      pool = None
    
    if (args['learning_C'] != None) :
        learning_C = parse_range(args['learning_C'], t=float)
    else :
        learning_C = config.learning_C
    if not isinstance(learning_C,list) :
        learning_C = [learning_C]
    else :
        learning_C = learning_C
    if (args['train_test_partitions'] != None) :
        partitions_json = load_data(args['train_test_partitions'], 'partitions', None, None, "FeatureLearning: ")
        if partitions_json == None :
            print "Could not load Train / Test Partitions from %s" % (args['train_test_partitions'],)
            sys.exit(1)
        partitions = TrainTestPartitions.fromJSONDict(partitions_json)
    else :
        partitions = generate_partitions(config, segment_info, 
                                         cv_iterations=5 if (len(learning_C) > 1) else 0)

    if len(learning_C) > 1 and len(partitions.cross_validation) > 0 :
        num_cv = len(partitions.cross_validation)
        learning_wrap = LearningWrapper( features )
        if pool != None :
            results = pool.imap(learning_wrap, itertools.product(partitions.cross_validation, learning_C))
            final_results = []
            try:
                while True:
                    result = results.next(args['timeout']) # timeout in case shogun died on us
                    final_results.append(result)
            except StopIteration:
                pass
            except multiprocessing.TimeoutError as e:
                self.pool.terminate()
                print traceback.print_exc()
                sys.exit(1)
            results = final_results
        else :
            results = map(learning_wrap, itertools.product(partitions.cross_validation, learning_C))
        max_correct = 0.0
        best_C = learning_C[0]
        print len(results)
        for C in learning_C :
            correct = Learning(config, [_result for (_C, _result) in results if C == _C]).get_average_correct()
            if correct > max_correct :
                best_C = C
                max_correct = correct
        config.learning_C = best_C
        print "FeatureLearning: using C = %s, correct = %s" % (config.learning_C, max_correct)
    else :
        if isinstance(learning_C, list) :
            config.learning_C = learning_C[0]
        else :
            config.learning_C = learning_C

    learning_wrap = LearningWrapper( features )

    if pool != None :
        results = pool.map(learning_wrap, itertools.product(partitions.evaluation, [config.learning_C]))
    else :
        results = map(learning_wrap, itertools.product(partitions.evaluation, [config.learning_C]))
    learning = Learning(config, [result for (C,result) in results])

    if args['outfile'] == None :
        learning_filename = FeatureLearning.get_learning_filename(config)
    else :
        learning_filename = args['outfile']

    correct = learning.get_average_correct()
    print "%s correct %2.2f%% error %2.2f%% classes %s" % ("FeatureLearning:", correct * 100.0, (1.0 - correct)*100.0, 
                                                   len(set([s.max_label() for s in features.segment_info])))
    print "Writing %s" % (learning_filename, )
    learning.config.status = "FeatureLearning"
    save_data(learning_filename, learning.toJSONDict())

if __name__ == "__main__" :
    main(sys.argv)
