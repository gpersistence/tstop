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

from sklearn import svm

from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.Configuration import get_filename, parse_range
from persistence.Datatypes.Segments import max_label
from persistence.Datatypes.Kernel import Kernel
from persistence.Datatypes.Learning import Learning, LearningResult
from persistence.Datatypes.TrainTestPartitions import TrainTestPartition, TrainTestPartitions
from persistence.PartitionData import PartitionData, generate_partitions

class LearningWrapper:
    def __init__(self, kernel) :
        self.kernel = kernel

    def __call__(self, (partition, C)) :
        config = copy(self.kernel.config)
        config.learning_C = C
        learn = KernelLearning(config, self.kernel, partition) 
        learn.train()
        return (C, learn.test())

class KernelLearning:
    @staticmethod
    def get_input_type():
        return "Kernel"

    @staticmethod
    def get_output_type():
        return "LearningResult"

    @staticmethod
    def get_scale_arg():
        return "learning_C"

    def __init__(self, config, kernel, partition) :
        self.config = config
        self.C = self.config.learning_C
        self.full_kernel = kernel.kernel_matrix
        self.segment_info = kernel.segment_info
        self.full_labels = [s.max_label() for s in self.segment_info]


        self.partition = partition
        self.train_indices = self.partition.train
        self.test_indices = self.partition.test
        self.test_kernel =  [[self.full_kernel[i][j] for i in self.train_indices] for j in self.test_indices]
        self.train_kernel = [[self.full_kernel[i][j] for i in self.train_indices] for j in self.train_indices]

        self.training_labels = [self.full_labels[i] for i in self.train_indices]
        self.label_set = list(set(self.training_labels))
        self.testing_labels = [self.full_labels[i] for i in self.test_indices] 
        self.svm = svm.SVC(kernel='precomputed', C=self.C)


    def train(self) :
        self.svm.fit(self.train_kernel, self.training_labels)
        return self.training_labels
    
    def test(self) :
        testing = self.svm.predict(self.test_kernel)
        return LearningResult(self.partition.state, self.training_labels, self.testing_labels, testing.tolist())

    @staticmethod
    def get_learning_filename(config, gz=True) :
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 'window_size', 'window_stride', 'learning_C']
        if config.post_process != None :
            fields.extend(['post_process', 'post_process_arg'])
        if config.status == 'RBFKernel' :
            fields.append('kernel_gamma')
        elif config.status == 'PersistenceKernel' :
            fields.append('max_simplices')
            fields.append('kernel_scale')
        
        return get_filename(config, fields, (config.status + 'Learning') if config.status != None else 'KernelLearning', gz)
        

def main(argv):
    parser = argparse.ArgumentParser(description='Tool to generate a similarity kernel from persistence data')
    parser.add_argument('-i', '--infile', help='Input JSON Similarity Kernel file')
    parser.add_argument('-o', '--outfile', help='Output JSON Learning file')
    parser.add_argument('-p', '--pool', default=multiprocessing.cpu_count(), help='Threads of computation to use')
    parser.add_argument('-c', '--learning-C', help='C value for SVM. Specify a range for 1-dimensional cross-validation')
    parser.add_argument('-t', '--train-test-partitions', help='Precomputed train / test partitions')
    args = vars(parser.parse_args(argv[1:]))
    
    kf_json = load_data(args['infile'], 'kernel', None, None, "KernelLearning: ")
    if kf_json == None :
        print "Could not load Kernel from %s" % (args['infile'],)
        sys.exit(1)
    kernel = Kernel.fromJSONDict(kf_json)
    config = kernel.config
    segment_info = kernel.segment_info
    if (int(args['pool']) > 1) :
      pool = multiprocessing.Pool(int(args['pool']))
    else :
      pool = None
    
    if (args['learning_C'] != None) :
        learning_C = parse_range(args['learning_C'], t=float)
        if not isinstance(learning_C,list) :
            learning_C = [learning_C]
    elif not isinstance(learning_C,list) :
        learning_C = [config.learning_C]
    else :
        learning_C = config.learning_C

    if (args['train_test_partitions'] != None) :
        partitions_json = load_data(args['train_test_partitions'], 'partitions', None, None, "KernelLearning: ")
        if partitions_json == None :
            print "Could not load Train / Test Partitions from %s" % (args['train_test_partitions'],)
            sys.exit(1)
        partitions = TrainTestPartitions.fromJSONDict(partitions_json)
    else :
        partitions = generate_partitions(config, segment_info, 
                                         cv_iterations=5 if (len(learning_C) > 1) else 0)

    if isinstance(learning_C, list) and len(learning_C) > 1 and len(partitions.cross_validation) > 0 :
        num_cv = len(partitions.cross_validation)
        learning_wrap = LearningWrapper( kernel )
        if pool != None :
            results = pool.map(learning_wrap, itertools.product(partitions.cross_validation, learning_C))
        else :
            results = map(learning_wrap, itertools.product(partitions.cross_validation, learning_C))
        max_correct = 0.0
        best_C = learning_C[0]
        results = list(results)
        print len(results)
        for C in learning_C :
            correct = Learning(config, [_result for (_C, _result) in results if C == _C]).get_average_correct()
            if correct > max_correct :
                best_C = C
                max_correct = correct
        config.learning_C = best_C
        print "KernelLearning: using C = %s, correct = %s" % (config.learning_C, max_correct)
    else :
        if isinstance(learning_C, list) :
            config.learning_C = learning_C[0]
        else :
            config.learning_C = learning_C

    learning_wrap = LearningWrapper( kernel )

    if pool != None :
        results = pool.map(learning_wrap, itertools.product(partitions.evaluation, [config.learning_C]))
    else :
        results = map(learning_wrap, itertools.product(partitions.evaluation, [config.learning_C]))
    learning = Learning(config, [result for (C,result) in results])

    if args['outfile'] == None :
        learning_filename = KernelLearning.get_learning_filename(config)
    else :
        learning_filename = args['outfile']

    correct = learning.get_average_correct()
    print "%s correct %2.2f%% error %2.2f%% classes %s" % ("KernelLearning:", correct * 100.0, (1.0 - correct)*100.0, 
                                                   len(set([s.max_label() for s in kernel.segment_info])))
    print "Writing %s" % (learning_filename, )
    learning.config.status = "KernelLearning"
    save_data(learning_filename, learning.toJSONDict())

if __name__ == "__main__" :
    main(sys.argv)
