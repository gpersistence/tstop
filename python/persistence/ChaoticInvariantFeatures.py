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
from Datatypes.Features import Features

def euclidean_distance(w0, w1) :
    return math.sqrt(sum([(x-y)**2 for (x,y) in zip(w0,w1)]))

class generate_features:
    def __init__(self, epsilon, segment_size, threshold) :
        self.epsilon = epsilon
        self.segment_size = segment_size
        self.threshold = threshold
        
    def __call__(self, segment) :
        dimensions = len(segment.windows[0]) / self.segment_size
        features = []
        for index in range(dimensions) :
            # reconstruct data from a single dimension of the time series
            all_data = [segment.windows[0][i * dimensions + index] for i in range(self.segment_size)]
            data_len = len(all_data)
            min_data = min(all_data)
            max_data = max(all_data)
            d = abs(max_data - min_data)
            j = 20
            # splits the range the [min_data, max_data] into j partitions, and assigns data index with the partition index for that datum
            partitioned_data = [reduce(lambda x,y : y if min_data + float(y) * d / float(j) < datum else x, range(j)) for datum in all_data]
            last_value = (sys.float_info.max,0)
            # finds the count of the data elements in each partition
            partition_count = [float(reduce(lambda x,y: x + 1 if y == i else x, partitioned_data, 0)) for i in range(j)] 
            # precompute 1.0 / (P_h * P_k)
            inv_p_h_p_k = [ [ float(data_len**2) / float(partition_count[h] * partition_count[k]) if partition_count[h] * partition_count[k] != 0 else 0.0 for h in range(j)] for k in range(j)]
            for tau in range(1,len(all_data)) :
                new_data_len = data_len - tau
                def prob_calc(h,k) : 
                    # counts data where all_data[i] is in partition h and all_data[i+tau] is in partition k
                    c_h_k = reduce(lambda x,(p_h, p_k): x + 1 if p_h == h and p_k == k else x, 
                                   itertools.izip(partitioned_data[:new_data_len], partitioned_data[tau:]), 0)
                    p_h_k = float(c_h_k) / float(new_data_len)
                    # calculates P_hk(tau) * ln(P_hk(tau) / (P_h * P_k))
                    """
                    if c_h_k != 0 :
                        print "p_%d_%d = %06.4g, p_%d = %06.4g, p_%d = %06.4g, p_%d * p_%d = %06.4g" % \
                            (h, k, p_h_k, \
                             h, partition_count[h] / float(data_len), k, partition_count[k] / float(data_len), \
                             h, k, p_h_p_k)
                    """
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
                    distances = [(euclidean_distance(point_i, [all_data[_i + tau * dim] for dim in range(m)]),_i) for _i in len_m_dim_data if _i != i]
                    neighbors = [min(distances, key = lambda d: d[0])]
                    # print i, neighbors[0], all_data[i+tau*m], all_data[neighbors[0][1]+tau*m], (abs(all_data[i+tau*m] - all_data[neighbors[0][1]+tau*m]) / neighbors[0][0])
                    false_neighbors = [(abs(all_data[i+tau*m] - all_data[_i+tau*m]) / dist > self.threshold) if dist != 0.0 else False for (dist,_i) in neighbors if dist < (d * 0.05)]
                    
                    return false_neighbors
                false_neighbors = reduce(lambda x, y: x + 1 if y else x, itertools.chain.from_iterable(map(false_nearest_neighbors, len_m_dim_data)), 0)
                # print tau, m, len(all_data) - tau * m, false_neighbors
                embed_dimension = m
                if float(false_neighbors) / float(len(all_data) - tau * m) < 0.1 :
                    break

            reconstruction = [[all_data[i + tau * _i] for _i in range(embed_dimension)] for i in range(len(all_data) - tau * embed_dimension)]
            window_len = len(reconstruction)
            window_range = range(window_len)
            # print "tau %d m %d, reconstruction size %s" % (tau, embed_dimension, len(reconstruction))
            # find the indices of all windows that are within epsilon
            neighbor_lists = [[w1 for w1 in window_range if w != w1 and euclidean_distance(reconstruction[w1],reconstruction[w]) <= self.epsilon] 
                              for w in window_range]
            if len([l for l in neighbor_lists if len(l) != 0]) == 0 :
                print "Zero length neighbor list, epsilon %s is too small" % (self.epsilon)
                sys.exit(1)
            correlation_integral = sum([len([n for n in neighbor_lists[i] if n > i]) for i in window_range]) * 2.0 / (window_len * (window_len + 1))
            correlation_dimension = math.log(correlation_integral, self.epsilon)
            variance = numpy.var(all_data, dtype=numpy.float64)
        
            S = []
            for delta_n in range(10) :
                D_i = []
                for (i, neighbors) in zip(window_range, neighbor_lists) :
                    if i + (embed_dimension - 1) * tau + delta_n < len(all_data) :
                        distances = [abs(all_data[i + (embed_dimension - 1) * tau + delta_n] - 
                                         all_data[n + (embed_dimension - 1) * tau + delta_n]) 
                                     for n in neighbors if n + (embed_dimension - 1) * tau + delta_n < len(all_data)]
                        if (len(distances) > 0) :
                            D_i.append(numpy.mean(distances))
                D_i = [d_i for d_i in D_i if d_i > 0.0]
                S.append((delta_n, numpy.mean(map(math.log,D_i)) if len(D_i) > 0 else 0.0))

            def line(x,a,b) :
                return a * x + b
            m, c = numpy.linalg.lstsq([[float(delta_n),1.0] for (delta_n, s) in S], [s for (delta_n, s) in S])[0]
            maximal_lyapunov_exponent = m

            features.extend([ maximal_lyapunov_exponent, correlation_integral, correlation_dimension, variance ])

        return features


class ChaoticInvariantFeatures(Features) :
    @staticmethod
    def get_input_type():
        return "Segments"

    @staticmethod
    def get_output_type():
        return "Features"

    @staticmethod
    def get_scale_arg():
        return "epsilon"

    def __init__(self, config, segments, epsilon=None, pool=None) :
        super(self.__class__, self).__init__(config, 
                                             segment_info=[SegmentInfo.fromJSONDict(segment) for segment in segments.segments])
        self.config = config
        if epsilon != None :
            self.config.invariant_epsilon = epsilon
        self.segments = segments
        self.distances = None
        self.epsilon = self.config.invariant_epsilon
        self.pool = pool

    def compute_features(self) :
        feature = generate_features(self.epsilon, self.config.segment_size, 0.05)
        self.features = []
        if self.pool == None :
            feat_iter = itertools.imap(feature, self.segments.segments)
        else :
            feat_iter = self.pool.imap(feature, self.segments.segments)
        for (feat, count) in itertools.izip(feat_iter, itertools.count(1)) :
            self.features.append(feat)
            if count % 20 == 0 :
                print "%s features completed" % (count,)

    @staticmethod
    def get_features_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 'window_size', 'window_stride', 'invariant_epsilon']
        if config.post_process != None :
            fields.extend(['post_process', 'post_process_arg'])
        return get_filename(config, fields, 'ChaoticInvariantFeatures', gz)

def main(argv) :
    parser = argparse.ArgumentParser(description='Tool to classify data based on chaotic invariants of segment data')
    parser.add_argument('-i', '--infile', help='Input JSON Segment File')
    parser.add_argument('-o', '--outfile', help='Output JSON Learning File')
    parser.add_argument('-e', '--epsilon', type=float, default=1.0, help='epsilon value used for generation of chaotic invariants')
    parser.add_argument('-p', '--pool', default=max(1,multiprocessing.cpu_count()-2), help='Threads of computation to use')
    args = parser.parse_args(argv[1:])
    segments_json = load_data(args.infile, 'segments', None, None, "Chaotic Invariant Features: ")
    if segments_json == None :
        print "Could not load --infile : %s" % (args.infile,)
        exit()

    segments = Segments.fromJSONDict(segments_json)
    if segments.config.segment_size != segments.config.window_size :
        print "%s ERROR ill formed input, segment_size != window_size in %s" % (argv[0], args.infile) 
        sys.exit(1)

    if args.epsilon != None :
        segments.config.invariant_epsilon = args.epsilon
    
    if int(args.pool) != 1 :
        pool = multiprocessing.Pool(int(args.pool))
    else :
        pool = None

    cid = ChaoticInvariantFeatures(segments.config, segments, epsilon=segments.config.invariant_epsilon, pool=pool)
    cid.compute_features()

    if (args.outfile == None) :
        args.outfile = ChaoticInvariantFeatures.get_features_filename(cid.config)

    print "Writing %s" % (args.outfile,)
    cid.config.status = "ChaoticInvariantFeatures"
    save_data(args.outfile, cid.toJSONDict())

if __name__ == "__main__":
    main(sys.argv)
