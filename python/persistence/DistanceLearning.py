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
import math

from Datatypes.Configuration import get_filename
from Datatypes.JSONObject import load_data, save_data
from Datatypes.Segments import max_label, Segments, Segment
from Datatypes.Learning import Learning, LearningResult
from Datatypes.Distances import Distance, Distances
from Datatypes.TrainTestPartitions import TrainTestPartition, TrainTestPartitions
from PartitionData import PartitionData, generate_partitions

class LearningWrapper:
    def __init__(self, distances, max_mode) :
        self.distances = distances
        self.max_mode = max_mode
        

    def __call__(self, partition) :
        learn = DistanceLearning(self.distances, partition, max_mode=self.max_mode) 
        learn.train()
        return learn.test()

class DistanceLearning:
    """ 
    Takes a matrix of Distances and uses it to perform first nearest neighbor classification
    """
    @staticmethod
    def get_input_type():
        return "Distances"

    @staticmethod
    def get_output_type():
        return "LearningResult"

    @staticmethod
    def get_scale_arg():
        return None

    def __init__(self, distances, partition, distance_key="mean", max_mode=False) :
        self.distances = distances
        self.config = self.distances.config
        self.distance_key = distance_key
        self.segment_info = self.distances.segment_info
        self.distance_matrix = None
        self.max_mode = max_mode
        self.full_labels = [s.max_label() for s in self.segment_info]
        self.partition = partition
        indices = range(len(self.full_labels))
        self.train_indices = partition.train
        self.test_indices = partition.test

    # technically just precomputing the distance matrix
    def train(self): 
        self.distance_matrix = [[self.distances.distances[y][x][self.distance_key] for x in self.train_indices] \
                                for y in self.test_indices]

    def test(self) :
        match_count = 0
        match_dist  = 0.0
        # Choose the label from element in the training data with the maximum or minimum distance to the test segment
        if self.max_mode == True :
            results = [max(zip(row, self.train_indices), key=lambda x:x[0])[1] for row in self.distance_matrix]
        else :
            results = [min(zip(row, self.train_indices), key=lambda x:x[0])[1] for row in self.distance_matrix]
        for (test, result) in zip(self.test_indices, results) :
            if self.segment_info[test].filename == self.segment_info[result].filename and \
               self.segment_info[test].max_label() == self.segment_info[result].max_label() :
                if ((self.segment_info[test].segment_start < self.segment_info[result].segment_start and self.segment_info[test].segment_start + self.config.segment_size > self.segment_info[result].segment_start) or \
                    (self.segment_info[test].segment_start > self.segment_info[result].segment_start and self.segment_info[result].segment_start + self.config.segment_size > self.segment_info[test].segment_start)) :
                    print "File %s segment at %s matches segment at %s, overlap" % \
                        (self.segment_info[test].filename, self.segment_info[result].segment_start, 
                         self.segment_info[test].segment_start)
                    match_count = match_count + 1
                    match_dist  = match_dist + float(abs(self.segment_info[test].segment_start - self.segment_info[result].segment_start)) / float(self.config.segment_stride)
        if match_count != 0 :
            print "Average match distance %s segments" % (match_dist / match_count, )
        return LearningResult(self.partition.state, 
                              [self.full_labels[i] for i in self.train_indices],
                              [self.full_labels[i] for i in self.test_indices], 
                              [self.full_labels[i] for i in results], None)

    @staticmethod
    def get_learning_filename(config, gz=True) :
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 'window_size', 'window_stride']
        if config.post_process != None :
            fields.extend(['post_process', 'post_process_arg'])
        if config.status == 'LandscapeDistances' :
            fields.append('max_simplices')
        elif config.status == 'ScaleSpaceSimilarity' :
            fields.append('max_simplices')
            fields.append('kernel_scale')
        return get_filename(config, fields, (config.status + 'Learning') if config.status != None else 'DistanceLearning', gz)
            
def main(argv) :
    parser = argparse.ArgumentParser(description='Tool to classify data based on 1-NN matching based on the supplied distance matrix')
    parser.add_argument('-i', '--infile', help='Input JSON Distance File')
    parser.add_argument('-o', '--outfile', help='Output JSON Learning File')
    parser.add_argument('-m', '--max-mode', action='store_true', help='Use maximum "Distance" instead of minimum (for Similarity measures"')
    parser.add_argument('-t', '--train-test-partitions', help='Precomputed train / test partitions')
    parser.add_argument('-p', '--pool', default=1, type=int)
    args = parser.parse_args(argv[1:])
    distances_json = load_data(args.infile, 'distances', None, None, "DistanceLearning: ")

    if distances_json == None :
        print "Could not load --infile : %s" % (args.infile, )
        sys.exit(1)

    distances = Distances.fromJSONDict(distances_json)

    if (args.train_test_partitions != None) :
        partitions_json = load_data(args.train_test_partitions, 'partitions', None, None, "KernelLearning: ")
        if partitions_json == None :
            print "Could not load Train / Test Partitions from %s" % (args.train_test_partitions,)
            sys.exit(1)
        partitions = TrainTestPartitions.fromJSONDict(partitions_json)
    else :
        partitions = generate_partitions(distances.config, distances.segment_info, cv_iterations=0)

    if (args.pool > 1) :
      pool = multiprocessing.Pool(args.pool)
    else :
      pool = None

    learning_wrap = LearningWrapper(distances, args.max_mode)

    if pool != None :
        results = pool.map(learning_wrap, partitions.evaluation)
    else :
        results = map(learning_wrap, partitions.evaluation)

    learning = Learning(distances.config, list(results))

    if (args.outfile == None) :
        args.outfile = DistanceLearning.get_learning_filename(learning.config)

    print "Writing %s, %2.2f%% correct" % (args.outfile, learning.get_average_correct()*100.0)
    learning.config.status = "DistanceLearning"
    save_data(args.outfile, learning.toJSONDict())

if __name__ == "__main__":
    main(sys.argv)
