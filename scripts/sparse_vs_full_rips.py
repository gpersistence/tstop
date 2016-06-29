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
import multiprocessing
import numpy
import time
from persistence.py_persistence import sparse_rips_filtration_generator, rips_filtration_generator, bottleneck_distance, wasserstein_distance
from persistence.py_persistence import PersistentHomology
from persistence.py_persistence import PersistenceDiagram

from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.Segments import Segment, Segments
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagram as PD
from persistence.Datatypes.Configuration import parse_range
from persistence.Datatypes.Distances import Distance

class segment_processing_callable:
    def __init__(self, outfile, max_simplices, epsilon, num_segments) :
        self.outfile = outfile
        self.max_simplices = max_simplices
        self.epsilon = epsilon
        self.num_segments = num_segments

    def __call__(self, (segment, index)) :
        print "Computing full rips filtration"
        start = time.clock()
        filtration = rips_filtration_generator(segment.windows, 2)
        persistence = PersistentHomology()
        full_persistence_diagram = persistence.compute_persistence_full(filtration, 2)
        full_runtime = time.clock() - start
        diagram_points = []
        for p in range(full_persistence_diagram.num_pairs()) :
            pair = full_persistence_diagram.get_pair(p)
            diagram_points.append([pair.birth_time(), pair.death_time(), pair.dim()])
        full_pd = PD(segment_start=segment.segment_start,
                     labels=segment.labels, learning=segment.learning,
                     filename=segment.filename, points=diagram_points)

        sparse_pds = []
        if self.max_simplices != None :
            for m in self.max_simplices :
                print "Computing sparse rips filtration max_simplices %s" % (int(round(m)),)
                start = time.clock()
                filtration = sparse_rips_filtration_generator(segment.windows, int(round(m)), None, 2)
                persistence = PersistentHomology()
                sparse_persistence_diagram = persistence.compute_persistence_sparse(filtration, 2)
                sparsity = [filtration.get_simplex_sparsity(i) for i in [0,1,2]]
                sparse_runtime = time.clock() - start
                
                diagram_points = []
                for p in range(sparse_persistence_diagram.num_pairs()) :
                    pair = sparse_persistence_diagram.get_pair(p)
                    diagram_points.append([pair.birth_time(), pair.death_time(), pair.dim()])
                    
                sparse_pd = PD(segment_start=segment.segment_start,
                               labels=segment.labels, learning=segment.learning,
                               filename=segment.filename, points=diagram_points)
                
                bottleneck = bottleneck_distance(full_pd.points, sparse_pd.points, 1)
                w1 = wasserstein_distance(full_pd.points, sparse_pd.points, 1, 1)
                w2 = wasserstein_distance(full_pd.points, sparse_pd.points, 1, 2)
                print "Distances: Bottleneck %g Wasserstein L1 %g L2 %g" % (bottleneck, w1, w2)
                sparse_pds.append(dict([("diagram", sparse_pd.toJSONDict()),
                                        ("max_simplices", int(round(m))), 
                                        ("sparsity", sparsity),
                                        ("bottleneck_distance", bottleneck),
                                        ("wasserstein_l1", w1),
                                        ("wasserstein_l2", w2),
                                        ("runtime", sparse_runtime)]))
        else :
            for e in self.epsilon :
                print "Computing sparse rips filtration epsilon %s" % (e,)
                start = time.clock()
                filtration = sparse_rips_filtration_generator(segment.windows, None, e, 2)
                persistence = PersistentHomology()
                sparse_persistence_diagram = persistence.compute_persistence_sparse(filtration, 2)
                sparsity = [filtration.get_simplex_sparsity(i) for i in [0,1,2]]
                sparse_runtime = time.clock() - start                
                
                diagram_points = []
                for p in range(sparse_persistence_diagram.num_pairs()) :
                    pair = sparse_persistence_diagram.get_pair(p)
                    diagram_points.append([pair.birth_time(), pair.death_time(), pair.dim()])
                    
                sparse_pd = PD(segment_start=segment.segment_start,
                               labels=segment.labels, learning=segment.learning,
                               filename=segment.filename, points=diagram_points)
                
                bottleneck = bottleneck_distance(full_pd.points, sparse_pd.points, 1)
                w1 = wasserstein_distance(full_pd.points, sparse_pd.points, 1, 1)
                w2 = wasserstein_distance(full_pd.points, sparse_pd.points, 1, 2)
                print "Distances: Bottleneck %g Wasserstein L1 %g L2 %g" % (bottleneck, w1, w2)
                sparse_pds.append(dict([("diagram", sparse_pd.toJSONDict()),
                                        ("epsilon", e), 
                                        ("sparsity", sparsity),
                                        ("bottleneck_distance", bottleneck),
                                        ("wasserstein_l1", w1),
                                        ("wasserstein_l2", w2),
                                        ("runtime", sparse_runtime)]))
        
        print "Saving data for segment %04d of %d to %s " % (index, self.num_segments, "%s.%04d" % (self.outfile, index))
        save_data("%s.%04d" % (self.outfile, index), 
                  [dict([("full_diagram",full_pd.toJSONDict()), ("runtime", full_runtime)])] + sparse_pds)
        return full_pd.toJSONDict()

if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description=('Creates Persistence Diagrams using sparse rips ' + \
                                                  'filtration with varying max_simplices to compare ' + \
                                                  'with full rips filtration'))
    parser.add_argument('-i', '--infile', help='Segments file to use as input data')
    parser.add_argument('-o', '--outfile', help='File to save output into')
    parser.add_argument('-m', '--max-simplices', help='range of max_simplices values to use')
    parser.add_argument('-e', '--epsilon', help='range of epsilon values to use')
    parser.add_argument('-p', '--pool')
    parser.add_argument('-n', '--number', help='limit to n persistence diagrams')
    args = parser.parse_args(sys.argv[1:])

    infile = Segments.fromJSONDict(load_data(args.infile, 'segments', None, None, sys.argv[0] + " : "))

    if args.number != None :
        infile.segments = infile.segments[0:int(args.number)]

    if args.max_simplices != None :
        max_simplices = parse_range(args.max_simplices, t=float)
        epsilon = None
    else :
        epsilon = parse_range(args.epsilon, t=float)
        max_simplices = None

    if int(args.pool) > 1 :
        pool = multiprocessing.Pool(int(args.pool))
        
        mapped = pool.imap(segment_processing_callable(args.outfile, max_simplices, epsilon, len(infile.segments)),
                           itertools.izip(infile.segments, range(len(infile.segments))))
    else :
        mapped = itertools.imap(segment_processing_callable(args.outfile, max_simplices, epsilon, len(infile.segments)),
                           itertools.izip(infile.segments, range(len(infile.segments))))
    pds = list(mapped)
