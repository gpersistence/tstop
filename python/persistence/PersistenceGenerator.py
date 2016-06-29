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


import multiprocessing
import itertools
import argparse
import os
import sys
import json

from Datatypes.JSONObject import load_data, save_data
from Datatypes.Segments import Segments, SegmentInfo
from Datatypes.PersistenceDiagrams import PersistenceDiagram as PD
from Datatypes.PersistenceDiagrams import PersistenceDiagrams as PDS
import py_persistence
from py_persistence import PersistenceDiagram
from py_persistence import PersistentHomology

def process_full((segment, (max_simplices, epsilon))) :
    filtration = py_persistence.rips_filtration_generator(segment.windows, 2)
    persistence = PersistentHomology()
    pd = persistence.compute_persistence_full(filtration, 2)
    pd_points = []
    
    all_generators = []
    for p in range(pd.num_pairs()):
        pair = pd.get_pair(p)
        pd_points.append([pair.birth_time(), pair.death_time(), pair.dim()])
        
    return PD(segment_info=SegmentInfo.fromJSONDict(segment), points=pd_points)

def process((segment, (max_simplices, epsilon))) :
    filtration = py_persistence.sparse_rips_filtration_generator(segment.windows, max_simplices, epsilon, 2)
    persistence = PersistentHomology()
    pd = persistence.compute_persistence_sparse(filtration, 2)
    if (not pd.get_size_satisfied()) :
        print "Whoops, overran our iteration quota. %s" % (segment_dict, )
    pd_points = []
    
    all_generators = []
    for p in range(pd.num_pairs()):
        pair = pd.get_pair(p)
        pd_points.append([pair.birth_time(), pair.death_time(), pair.dim()])
        
    return PD(segment_info=SegmentInfo.fromJSONDict(segment), points=pd_points)

class PersistenceGenerator:
    def __init__(self, sfd, max_simplices=None, epsilon=1.0/3.0) :
        self.sfd = sfd
        self.max_simplices = max_simplices
        self.epsilon = epsilon

    def __call__(self):
        for (segment, segment_dict) in self.sfd :
            yield process((segment, (self.max_simplices, self.epsilon)))

def main(argv) :
    parser = argparse.ArgumentParser(description="Tool to generate Persistence Diagrams from segmented data")
    parser.add_argument('-i', '--infile', help='Input JSON Segment Data file')
    parser.add_argument('-o', '--outfile', help='Output JSON Persistence Diagram file')
    parser.add_argument('-m', '--max-simplices')
    parser.add_argument('-e', '--epsilon')
    parser.add_argument('-p', '--pool', default=multiprocessing.cpu_count(), help='Threads of computation to use')
    args = vars(parser.parse_args(argv[1:]))

    if (not os.path.exists(args['infile'])) :
        print "Could not find %s for reading" % (args['infile'],)
        return

    if (int(args['pool']) > 1) :
      pool = multiprocessing.Pool(int(args['pool']))
    else :
      pool = None

    segments_json = load_data(args['infile'], 'segments', None, None, "PersistenceGenerator: ")
    if segments_json == None :
        print "Could not load --infile : %s" % (args['infile'],)
        exit()
    segments = Segments.fromJSONDict(segments_json)
    config = segments.config
    if (args['max_simplices'] != None) :
        config.max_simplices = int(args['max_simplices'])
        config.persistence_epsilon = None
    if (args['epsilon'] != None) :
        config.persistence_epsilon = float(args['epsilon'])
        config.max_simplices = None

    def identity(x) :
        return x

    if pool != None :
        persistences = pool.imap(process, itertools.product(segments.segments, [(config.max_simplices, config.persistence_epsilon)]))
    else :
        persistences = itertools.imap(process, itertools.product(segments.segments, [(config.max_simplices, config.persistence_epsilon)]))

    persistences = PDS(config, list(persistences))
    
    if args['outfile'] == None :
        outfile = PDS.get_persistence_diagrams_filename(config)
    else :
        outfile = args['outfile']
    print "PersistenceGenerator: Writing %s" % (outfile,)
    persistences.config.status = "PersistenceGenerator"
    save_data(outfile, persistences.toJSONDict())

import sys

if __name__ == "__main__" :
    main(sys.argv)
