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
from Datatypes.Segments import max_label, Segments, Segment
from Datatypes.Learning import Learning, LearningResult
from Datatypes.PersistenceDiagrams import PersistenceDiagrams as PD
from Datatypes.Distances import Distance, Distances
from PersistenceKernel import ScaleSpaceWrapper

def closest_squared_l2_distance(point, diagram) :
    distances = map(lambda ((x_0, y_0), (x_1, y_1)) : (x_0 - x_1) * (x_0 - x_1) + (y_0 - y_1) * (y_0 - y_1),
                    itertools.product([point], diagram + [((point[0] + point[1])/2, (point[0] + point[1])/2)])) 
    if len(distances) != 0 :
        return min(distances)
    else :
        return float('inf')

def average_pairing_distance((diagram_1, diagram_2)) :
    distances = [closest_squared_l2_distance(p, diagram_2) for p in diagram_1] + \
                [closest_squared_l2_distance(p, diagram_1) for p in diagram_2]
    if len(distances) != 0 :
        return numpy.average(distances)
    else :
        return float('inf')

# ScaleSpaceSimilarity computes a matrix of the scale space 
# similarities between persistence diagrams

class ScaleSpaceSimilarity(Distances):
    @staticmethod
    def get_input_type():
        return "PersistenceDiagrams"

    @staticmethod
    def get_output_type():
        return "Distances"

    @staticmethod
    def get_scale_arg():
        return "kernel_scale"

    def __init__(self, config, persistences, kernel_scale=1.0, degree=1, pool=None) :
        super(self.__class__, self).__init__(config, 
                                             segment_info=[p.segment_info for p in persistences.diagrams])
        self.distances = None
        self.persistences = persistences
        self.kernel_scale = kernel_scale
        self.degree = degree
        self.pool = pool

    def compute_distances(self):
        points_list  = [[(p[0], p[1]) for p in persistence.points if p[2] == self.degree]\
                        for persistence in self.persistences.diagrams]

        ij_iterator = itertools.combinations_with_replacement(range(len(points_list)),2)
        if self.pool == None :
            similarities = itertools.imap(ScaleSpaceWrapper(float(self.kernel_scale)), 
                                          itertools.combinations_with_replacement(points_list,2))
            #distances = itertools.imap(average_pairing_distance, 
            #                           itertools.combinations_with_replacement(points_list,2))
        else :
            work_unit_size = max(1, (len(points_list) + 1) * len(points_list) / \
                                 (len(multiprocessing.active_children())*2*5))
            similarities = self.pool.imap(ScaleSpaceWrapper(float(self.kernel_scale)), 
                                          itertools.combinations_with_replacement(points_list,2),
                                          work_unit_size)
            #distances = self.pool.imap(average_pairing_distance,
            #                           itertools.combinations_with_replacement(points_list,2),
            #                           work_unit_size)


        self.distances = [[0.0 for p in range(len(points_list))] for q in range(len(points_list))]
        #for ((i,j),similarity,distance) in itertools.izip(ij_iterator, similarities, distances) :
        for ((i,j),similarity) in itertools.izip(ij_iterator, similarities) :
            self.distances[i][j] = Distance(None, similarity, None, None) #distance)
            self.distances[j][i] = Distance(None, similarity, None, None) #distance)

    @staticmethod
    def get_distances_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 
                  'window_size', 'window_stride', 'max_simplices', 'persistence_degree',
                  'kernel_scale', 'persistence_epsilon']
        if config.post_process != None :
            fields.extend(['post_process', 'post_process_arg'])

        return get_filename(config, fields, 'ScaleSpaceSimilarities', gz)


def main(argv) :
    parser = argparse.ArgumentParser(description='Tool to generate the scale space similarity between all pairs of persistence diagrams')
    parser.add_argument('-i', '--infile', help='Input JSON Persistence Diagram File')
    parser.add_argument('-o', '--outfile', help='Output JSON Learning File')
    parser.add_argument('-k', '--kernel-scale', type=float, help='Kernel Scale to use for Scale Space Similarity')
    parser.add_argument('-d', '--persistence-degree', type=float, help='Persistence degree to consider when computing Scale Space Similarity')
    parser.add_argument('--kernel-file', help='translate from PersistenceKernel instead of redoing calculation')
    parser.add_argument('-p', '--pool', default=multiprocessing.cpu_count(), help='Threads of computation to use')
    args = parser.parse_args(argv[1:])
    
    if args.kernel_file != None :
        from Datatypes.Kernel import Kernel
        kernel_json = load_data(args.kernel_file, 'kernel', None, None, "Scale Space Similarity: ")
        if kernel_json == None :
            print "Could not load --kernel-file : %s" % (args.kernel_file, )
            exit()
        kernel = Kernel.fromJSONDict(kernel_json)

        sss = Distances(kernel.config, 
                        [[Distance(mean=k) for k in row] for row in kernel.kernel_matrix],
                        kernel.segment_info)
        
        if (args.outfile == None) :
            args.outfile = ScaleSpaceSimilarity.get_distances_filename(sss.config)
        
        print "Writing %s" % (args.outfile, )
        sss.config.status = "ScaleSpaceSimilarity"
        save_data(args.outfile, sss.toJSONDict())

    else :
        persistences_json = load_data(args.infile, 'persistence_diagrams', None, None, "Scale Space Similarity: ")
        if persistences_json == None :
            print "Could not load --infile : %s" % (args.infile, )
            exit()
        persistences = PD.fromJSONDict(persistences_json)
        if args.kernel_scale == None :
            args.kernel_scale = float(persistences.config.kernel_scale)
        else :
            persistences.config.kernel_scale = args.kernel_scale

        if args.pool != 1 :
            pool = multiprocessing.Pool(int(args.pool))
        else :
            pool = None

        sss = ScaleSpaceSimilarity(persistences.config, persistences, 
                                   persistences.config.kernel_scale, persistences.config.persistence_degree,
                                   pool=pool)
        
        sss.compute_distances()

        if (args.outfile == None) :
            args.outfile = ScaleSpaceSimilarity.get_distances_filename(sss.config)

        print "Writing %s" % (args.outfile, )
        sss.config.status = "ScaleSpaceSimilarity"
        save_data(args.outfile, sss.toJSONDict())

if __name__ == "__main__":
    main(sys.argv)
