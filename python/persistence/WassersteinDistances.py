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
import sys
import os
import argparse
import json
import multiprocessing
import itertools
import time
import math
import numpy
import py_persistence

from Datatypes.JSONObject import JSONObject, load_data, save_data
from Datatypes.Configuration import get_filename
from Datatypes.PersistenceDiagrams import PersistenceDiagrams, PersistenceDiagram
from Datatypes.Distances import Distances, Distance

class distance_callable:
    def __init__(self, persistence_degree, wasserstein_degree):
        self.persistence_degree = persistence_degree
        self.wasserstein_degree = wasserstein_degree

    def __call__(self, (persistence_a, persistence_b)) :
        distance = py_persistence.wasserstein_distance(persistence_a.points, persistence_b.points, 
                                                       self.persistence_degree, self.wasserstein_degree)
        return Distance(None, distance, None, None)

def pairs_without_replacement(iterable):
    pool = tuple(iterable)
    n = len(pool)
    for indices in itertools.product(range(n), repeat=2):
        if sorted(indices) == list(indices) and indices[0] != indices[1]:
            yield tuple(pool[i] for i in indices)

class WassersteinDistances(Distances):
    """
    Generates a distance matrix from PersistenceDiagrams using the bottleneck distance between persistence diagrams as a measure.
    """
    @staticmethod
    def get_input_type():
        return "PersistenceDiagrams"

    @staticmethod
    def get_output_type():
        return "Distances"

    @staticmethod
    def get_scale_arg():
        return None

    def __init__(self, config, persistences_a, persistences_b=None, persistence_degree=1, wasserstein_degree=2,pool=None) :
        super(self.__class__, self).__init__(config, 
                                             segment_info=[p.segment_info for p in persistences_a.diagrams])
        self.persistences_a = persistences_a
        if persistences_b != None :
            self.persistences_b = persistences_b
        else :
            self.persistences_b = persistences_a
        self.pool = pool
        self.persistence_degree = persistence_degree
        self.wasserstein_degree = wasserstein_degree

        self.distances = None

    def compute_distances(self) :
        if self.persistences_a == self.persistences_b :
            # Limit the computations to unique pairs
            # This only works if the distance measure is associative and the distance to one's self is zero
            iterator = pairs_without_replacement(self.persistences_a.diagrams)
            index_iterator = pairs_without_replacement(range(len(self.persistences_a.diagrams)))
            length = len(list(index_iterator))
            index_iterator = pairs_without_replacement(range(len(self.persistences_a.diagrams)))
        else :
            iterator = itertools.product(self.persistences_a.diagrams, self.persistences_b.diagrams)
            index_iterator = itertools.product(range(len(self.persistences_a.diagrams)), 
                                               range(len(self.persistences_b.diagrams)))        
            length = len(list(index_iterator))
            index_iterator = itertools.product(range(len(self.persistences_a.diagrams)), 
                                               range(len(self.persistences_b.diagrams)))        
            
        if self.pool == None:
            result = itertools.imap(distance_callable(self.persistence_degree, self.wasserstein_degree), iterator)
        else : 
            result = self.pool.imap(distance_callable(self.persistence_degree, self.wasserstein_degree), iterator, 
                                    max(1, length / (10 * len(multiprocessing.active_children()))))

        self.distances = [[None for p in self.persistences_a.diagrams] for q in self.persistences_b.diagrams]

        for ((i,j), d) in itertools.izip(index_iterator, result) :
            self.distances[i][j] = d
            if self.persistences_a == self.persistences_b :
                self.distances[j][i] = d

        if self.persistences_a == self.persistences_b :
            for i in range(len(self.persistences_a.diagrams)) :
                self.distances[i][i] = Distance(0,0,0,0)

        return self.distances
            
    @staticmethod
    def get_distances_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 'window_size', 'window_stride', 'max_simplices']
        return get_filename(config, fields, 'WassersteinDistances', gz)


def main(argv) :
    parser = argparse.ArgumentParser(description='Tool to evaluate the Wasserstein Distances between two Arrays of Persistence Diagrams')
    parser.add_argument('-a', '--infile-a', help="JSON Persistence Diagram file of the first set of Persistence Diagrams")
    parser.add_argument('-b', '--infile-b', help="JSON Persistence Diagram file of the second set of Persistence Diagrams")
    parser.add_argument('-o', '--outfile', help="JSON Output File")
    parser.add_argument('-d', '--degree', type=int, default=1, help="Persistence Degree to consider")
    parser.add_argument('-p', '--pool', default=multiprocessing.cpu_count(), help='Threads of computation to use')
    args = vars(parser.parse_args(argv[1:]))
    if (not os.path.exists(args['infile_a']) or \
        ((not (args['infile_a'] == args['infile_b'] or args['infile_b'] == None) and not os.path.exists(args['infile_b'])))) :
        parser.print_help()
        exit()
    pfa_json = load_data(args['infile_a'], 'persistence_diagrams', None, None, "WassersteinDistances: ")
    if pfa_json == None :
        print "Could not load --infile-a : %s" % (args['infile_a'],)
        exit()
    persistences_a = PersistenceDiagrams.fromJSONDict(pfa_json)
    if args['infile_a'] == args['infile_b'] or args['infile_b'] == None :
        persistences_b = persistences_a
    else :
        pfb_json = load_data(args['infile_b'], 'persistence_diagrams', None, None, "WassersteinDistances: ")
        if pfb_json == None :
            print "Could not load --infile-b : %s" % (args['infile_b'],)
            exit()
        persistences_b = PersistenceDiagrams.fromJSONDict(pfb_json)
    if (int(args['pool']) > 1) :
      pool = multiprocessing.Pool(int(args['pool']))
    else :
      pool = None
    start = time.time()
    distances =  WassersteinDistances(persistences_a.config, persistences_a, persistences_b, pool=pool, persistence_degree=args['degree'], wasserstein_degree=2)
    dist = distances.compute_distances()
    end = time.time()
    print "Time elapsed %f" % (end - start)
    if not('outfile' in args) or args['outfile'] == None :
        outfile = WassersteinDistances.get_distances_filename(distances.config)
    else :
        outfile = args['outfile']
    print "Writing %s" % (outfile,)
    distances.config.status = "WassersteinDistance"
    save_data(outfile, distances.toJSONDict())


if __name__ == "__main__" :
    main(sys.argv)
