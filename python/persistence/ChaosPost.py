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
import argparse
import itertools
import math
import multiprocessing
from copy import copy
from numpy import array, ndarray

from Datatypes.Configuration import get_filename
from Datatypes.Segments import Segments, Segment
from Datatypes.JSONObject import load_data, save_data

def euclidean_distance(w0, w1) :
    return math.sqrt(sum([(x-y)**2 for (x,y) in zip(w0,w1)]))

class windowizer :
    def __init__(self, config, threshold=0.05, dimensions=1, index=0) :
        self.config = config
        self.threshold = threshold
        self.dimensions = dimensions
        self.index = index

    def __call__(self, segment) :
        windows = []
        # reconstruct data from a single dimension of the time series
        all_data = [segment.windows[0][i * self.dimensions + self.index] for i in range(self.config.segment_size)]
        data_len = len(all_data)
        min_data = min(all_data)
        max_data = max(all_data)
        d = abs(max_data - min_data)
        j = 20
        # splits the range the [min_data, max_data] into j partitions, 
        # and assigns data index with the partition index for that datum
        partitioned_data = [reduce(lambda x,y : y if min_data + float(y) * d / float(j) < datum else x, range(j)) 
                            for datum in all_data]
        last_value = (sys.float_info.max,0)
        # finds the count of the data elements in each partition
        partition_count = [float(reduce(lambda x,y: x + 1 if y == i else x, partitioned_data, 0)) for i in range(j)] 
        # precompute 1.0 / (P_h * P_k)
        inv_p_h_p_k = [ [ float(data_len**2) / float(partition_count[h] * partition_count[k]) 
                          if partition_count[h] * partition_count[k] != 0 else 0.0 
                          for h in range(j)] 
                        for k in range(j)]
        for tau in range(1,len(all_data)) :
            new_data_len = data_len - tau
            def prob_calc(h,k) : 
                # counts data where all_data[i] is in partition h and all_data[i+tau] is in partition k
                c_h_k = reduce(lambda x,(p_h, p_k): x + 1 if p_h == h and p_k == k else x, 
                               itertools.izip(partitioned_data[:new_data_len], partitioned_data[tau:]), 0)
                p_h_k = float(c_h_k) / float(new_data_len)
                # calculates P_hk(tau) * ln(P_hk(tau) / (P_h * P_k))
                return p_h_k * math.log(p_h_k * inv_p_h_p_k[h][k]) if c_h_k != 0.0 and inv_p_h_p_k[h][k] != 0.0 else 0.0
            this_value = sum([prob_calc(h,k) for h in range(j) for k in range(j)])
            # print "I(%s) = %g" % (tau, this_value)
            if this_value < last_value[0] :
                last_value = (this_value,tau)
            else :
                break
        # last_value is now the first local minimum for tau
        tau = last_value[1]

        embed_dimension = 1
        for m in range(1,data_len / tau - 5) :
            len_m_dim_data = range(len(all_data) - tau * m)
            def false_nearest_neighbors(i) :
                point_i = [all_data[i + tau * dim] for dim in range(m)]
                distances = [(euclidean_distance(point_i, [all_data[_i + tau * dim] for dim in range(m)]),_i) 
                             for _i in len_m_dim_data if _i != i]
                neighbors = [min(distances, key = lambda d: d[0])]
                false_neighbors = [(abs(all_data[i+tau*m] - all_data[_i+tau*m]) / dist > self.threshold) 
                                   if dist != 0.0 else False 
                                   for (dist,_i) in neighbors if dist < (d * 0.05)]
                
                return false_neighbors
            false_neighbors = reduce(lambda x, y: x + 1 if y else x, 
                                     itertools.chain.from_iterable(map(false_nearest_neighbors, len_m_dim_data)), 0)
            # print tau, m, len(all_data) - tau * m, false_neighbors
            embed_dimension = m
            if float(false_neighbors) / float(len(all_data) - tau * m) < 0.1 :
                break

        segment.tau = tau
        segment.windows = [[all_data[i + tau * _i] for _i in range(embed_dimension)] 
                           for i in range(len(all_data) - tau * embed_dimension)]
        return segment


class ChaosPost(Segments):
    """
    Implements the time delay and embedded dimension scheme for windowing segmented data
    from "Chaotic Invariants for Human Action Recognition", Saad Ali, Arslan Basharat, Mubarak Shah
    for the calculation of their invariant and exploring their method in creating persistence diagrams
    Input segments but be non-windowed, that is window size == segment size
    Creates one output file for each data index in the input segment file
    """
    @staticmethod
    def get_input_type():
        return "Segments"

    @staticmethod
    def get_output_type():
        return "Segments"

    def __init__(self, config, segments, threshold=0.05, dimensions=1, index=0, pool=None):
        super(self.__class__, self).__init__(config)
        self.config.post_process = "ChaosPost"
        self.threshold = threshold
        self.windowizer = windowizer(config, threshold, dimensions, index)
        if pool == None :
            self.segments = list(map(self.windowizer, segments))
        else :
            self.segments = list(pool.imap(self.windowizer, segments))

    @staticmethod
    def get_segment_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size',
                  'segment_stride', 'window_size', 'window_stride']
        return get_filename(config, fields, 'ChaosPost', gz)

def main(argv):
    parser = argparse.ArgumentParser(description='Post Processing tool for Segment Data')
    parser.add_argument('-i', '--infile')
    parser.add_argument('-o', '--outfile')
    parser.add_argument('-p', '--pool', type=int, default=min(1,multiprocessing.cpu_count()-2))
    args = vars(parser.parse_args(argv[1:]))
    segments_json = load_data(args['infile'], 'segments', None, None, "ChaosPost: ")
    if segments_json == None :
        print "Could not load --infile : %s" % (args['infile'],)
        exit()
    print "input read"
    segments = Segments.fromJSONDict(segments_json)
    segments.config.post_process="ChaosPost"
    dimensions = len(segments.segments[0].windows[0]) / segments.config.window_size
    if args['pool'] == 1 :
        pool = None
    else :
        pool = multiprocessing.Pool(args['pool'])
        print "%d processes started" % args['pool']
    for index in range(dimensions) :
        config = copy(segments.config)
        config.data_index = segments.segments[0].data_index[index]
        post_processed = ChaosPost(config, segments.segments, dimensions=dimensions, index=index, pool=pool)
        if args['outfile'] == None:
            outfile = ChaosPost.get_segment_filename(config)
        else :
            outfile = args['outfile']
        print "Writing %s" % outfile
        post_processed.config.status = "ChaosPost"
        save_data(outfile, post_processed.toJSONDict())

if __name__=="__main__" :
    main(sys.argv)
