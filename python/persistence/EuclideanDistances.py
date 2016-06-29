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

from Datatypes.JSONObject import load_data, save_data
from Datatypes.Configuration import get_filename
from Datatypes.Segments import max_label, Segments, Segment, SegmentInfo
from Datatypes.Distances import Distances, Distance
# EuclideanSegmentClassifier finds the 1-NN label match from the
# training data set for each member of the testing data set based on
# the Euclidean distance between segments

def segment_distance((segment_a, segment_b)) :
    running_sum = 0
    for (win_a, win_b) in zip(segment_a.windows, segment_b.windows) :
        running_sum = reduce(lambda s, (a,b) : math.pow((float(a)-float(b)),2) + s, zip(win_a, win_b), running_sum)
    dist = math.sqrt(running_sum)
    return Distance(dist, dist, dist, 0)

class EuclideanDistances(Distances):
    @staticmethod
    def get_input_type():
        return "Segments"

    @staticmethod
    def get_output_type():
        return "Distances"

    @staticmethod
    def get_scale_arg():
        return None

    def __init__(self, config, segments, seed=0xcafebabe, pool=None) :
        super(self.__class__, self).__init__(config, 
                                             segment_info=[SegmentInfo.fromJSONDict(segment) for segment in segments.segments])
        self.config = config
        self.segments = segments
        self.distances = None
        self.pool = pool

    def compute_distances(self) :
        if self.pool == None :
            results = itertools.imap(segment_distance, itertools.combinations_with_replacement(self.segments.segments,2))
        else :
            results = self.pool.imap(segment_distance, itertools.combinations_with_replacement(self.segments.segments,2),
                                     len(self.segments.segments) * (len(self.segments.segments) + 1) / \
                                     (10.0 * len(multiprocessing.active_children())))
        self.distances = [[None for x in self.segments.segments] for y in self.segments.segments]
        print 
        for ((i,j),distance) in itertools.izip(itertools.combinations_with_replacement(range(len(self.segments.segments)),2),
                                               results) :
            self.distances[i][j] = distance
            self.distances[j][i] = distance

    @staticmethod
    def get_distances_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 'window_size', 'window_stride']
        if config.post_process != None :
            fields.extend(['post_process', 'post_process_arg'])
        return get_filename(config, fields, 'EuclideanDistances', gz)

def main(argv) :
    parser = argparse.ArgumentParser(description='Tool to classify data based on 1-NN of segment data')
    parser.add_argument('-i', '--infile', help='Input JSON Segment File')
    parser.add_argument('-o', '--outfile', help='Output JSON Learning File')
    parser.add_argument('-p', '--pool', default=multiprocessing.cpu_count(), help='Threads of computation to use')
    args = parser.parse_args(argv[1:])
    segments_json = load_data(args.infile, 'segments', None, None, "Euclidean Segment Distances: ")
    if segments_json == None :
        print "Could not load --infile : %s" % (args.infile,)
        exit()

    segments = Segments.fromJSONDict(segments_json)

    if int(args.pool) != 1 :
        pool = multiprocessing.Pool(int(args.pool))
    else :
        pool = None

    esd = EuclideanDistances(segments.config, segments, pool=pool)
    esd.compute_distances()

    if (args.outfile == None) :
        args.outfile = EuclideanDistances.get_distances_filename(esd.config)

    print "Writing %s" % (args.outfile,)
    esd.config.status = "EuclideanDistances"
    save_data(args.outfile, esd.toJSONDict())

if __name__ == "__main__":
    main(sys.argv)
