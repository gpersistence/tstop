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

from Datatypes.Configuration import get_filename
from Datatypes.Distances import Distances, Distance
from Datatypes.PersistenceDiagrams import PersistenceDiagrams as PD
from Datatypes.JSONObject import load_data, save_data

class distance_callable:
    def __init__(self, degree):
        self.degree = degree
    def __call__(self, (persistence_a, persistence_b)) :
        distance = py_persistence.persistence_landscape_distance(persistence_a.points, persistence_b.points, self.degree)
        return distance

def pairs_without_replacement(iterable):
    pool = tuple(iterable)
    n = len(pool)
    for indices in itertools.product(range(n), repeat=2):
        if sorted(indices) == list(indices) and indices[0] != indices[1]:
            yield tuple(pool[i] for i in indices)

class LandscapeDistances(Distances):
    """
    Computes the distances between the persistence landscape representations to make a matrix of Distances
    """
    @staticmethod
    def get_input_type():
        return "PersistenceDiagrams"

    @staticmethod
    def get_ouput_type():
        return "Distances"

    @staticmethod
    def get_scale_arg():
        return None

    def __init__(self, config, persistences_a, persistences_b=None, pool=None) :
        super(self.__class__, self).__init__(config, None, 
                                             segment_info=[p.segment_info for p in persistences_a.diagrams])
        self.persistences_a = persistences_a
        if persistences_b == None :
            self.persistences_b = self.persistences_a
        else :
            self.persistences_b = persistences_b
        self.pool = pool
        self.degree = config.persistence_degree
        self.distances = None

    def compute_distances(self) :
        if self.persistences_a == self.persistences_b :
            index_iterator = pairs_without_replacement(range(len(self.persistences_a.diagrams)))
            iterator = pairs_without_replacement(self.persistences_a.diagrams)
        else :
            index_iterator = itertools.product(range(len(self.persistences_a.diagrams)), 
                                               range(len(self.persistences_b.diagrams)))
            iterator = itertools.product(self.persistences_a.diagrams, self.persistences_b.diagrams)

        if self.pool == None:
            result = itertools.imap(distance_callable(self.degree), iterator)
        else : 
            index_iterator = list(index_iterator)
            elements = len(index_iterator)
            result = self.pool.imap(distance_callable(self.degree), iterator, 
                                    max(1, int(elements / (len(multiprocessing.active_children()) * 3))))

        self.distances = [[0.0 for a in self.persistences_a.diagrams] for b in self.persistences_b.diagrams]
        if self.persistences_a == self.persistences_b :
            for ((i,j),d) in itertools.izip(index_iterator, result) :
                self.distances[i][j] = Distance(d,d,d,0)
                self.distances[j][i] = Distance(d,d,d,0)
            for i in range(len(self.persistences_a.diagrams)) :
                self.distances[i][i] = Distance(0,0,0,0)
        else :
            for ((i,j),d) in itertools.izip(index_iterator, result) :
                self.distances[i][j] = Distance(d,d,d,0)
        return self.distances
            
    @staticmethod
    def get_distances_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 'window_size', 'window_stride', 'max_simplices']
        return get_filename(config, fields, 'LandscapeDistances', gz)


def main(argv) :
    parser = argparse.ArgumentParser(description='Tool to evaluate the Landscape Distances between two Arrays of Persistence Diagrams')
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
    pfa_json = load_data(args['infile_a'], 'persistence_diagrams', None, None, "LandscapeDistances: ")
    if pfa_json == None :
        print "Could not load --infile-a : %s" % (args['infile_a'],)
        exit()
    persistences_a = PD.fromJSONDict(pfa_json)
    if args['infile_a'] == args['infile_b'] or args['infile_b'] == None :
        persistences_b = persistences_a
    else :
        pfb_json = load_data(args['infile_b'], 'persistences', None, None, "LandscapeDistances: ")
        if pfb_json == None :
            print "Could not load --infile-b : %s" % (args['infile_b'],)
            exit()
        persistences_b = PD.fromJSONDict(pfb_json)

    config = persistences_a.config
    if args['degree'] != None :
        config.persistence_degree = args['degree']

    if (int(args['pool']) > 1) :
      pool = multiprocessing.Pool(int(args['pool']))
    else :
      pool = None

    start = time.time()
    distances =  LandscapeDistances(config, persistences_a, persistences_b, pool=pool)
    dist = distances.compute_distances()
    end = time.time()
    print "Time elapsed %f" % (end - start)
    if not('outfile' in args) or args['outfile'] == None :
        outfile = LandscapeDistances.get_distances_filename(config)
    else :
        outfile = args['outfile']
    print "Writing %s" % (outfile,)
    distances.config.status = "LandscapeDistance"
    save_data(outfile, distances.toJSONDict())


if __name__ == "__main__" :
    main(sys.argv)
