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
import multiprocessing
import sys
import numpy
import json
import math
import time
import itertools
import argparse
import py_persistence

from Datatypes.Configuration import get_filename
from Datatypes.Kernel import Kernel
from Datatypes.PersistenceDiagrams import PersistenceDiagrams as PD
from Datatypes.JSONObject import load_data, save_data
# http://stackoverflow.com/questions/5563743/check-for-positive-or-semi-positive-definite-matrix
def isPSD(A, tol=1e-8):
    E = numpy.linalg.eigvalsh(A)
    return numpy.all(E > -tol)

def scale_space_distance((x_0, x_1), (y_0, y_1), scale) :
    a = x_0 - y_0
    b = x_1 - y_1
    c = x_0 - y_1
    d = x_1 - y_0
    return math.exp((a * a + b * b) * scale) - math.exp((c * c + d * d) * scale)


class persistenceScaleSpaceKernel :
    def __init__(self, sigma) :
      self.sigma = sigma
      self.scale = -1.0 / 8.0 / self.sigma

    def __call__(self, (a,b)) :
      return reduce((lambda _sum, (p0, p1): _sum + scale_space_distance(p0, p1, self.scale)), \
                    itertools.product(a, b), 0.0) / (8.0 * self.sigma * math.pi)

class ScaleSpaceWrapper :
    def __init__ (self, kernel_scale) :
        self.kernel_scale = kernel_scale
    def __call__ (self, (a, b)) :
        return py_persistence.ssk_similarity(a, b, self.kernel_scale)
      
class PersistenceKernel(Kernel) :
    @staticmethod
    def get_input_type():
        return "PersistenceDiagrams"

    @staticmethod
    def get_output_type():
        return "Kernel"

    @staticmethod
    def get_scale_arg():
        return "kernel_scale"

    def __init__(self, config, persistences, kernel_fun=None, pool=None) :
        super(self.__class__, self).__init__(config)
        self.segment_info = [p.segment_info for p in persistences.diagrams]
        self.diagrams = persistences.diagrams
        
        if kernel_fun == None : 
            self.kernel_fun = ScaleSpaceWrapper(config.kernel_scale)
        else :
            self.kernel_fun = kernel_fun
        self.degree = int(config.persistence_degree) if config.persistence_degree != None else 1
        self.pool = pool

    def compute_kernel(self) :
        points = []
        # each entry in points is a persistence diagram filtered to the specipied degree (default 1)
        for persistence in self.diagrams :
            points.append([(p[0], p[1]) for p in persistence.points if p[2] == self.degree])
        # Create an iterator that computes the kernel similarity for all pairs of persistence diagrams
        points_iter = itertools.combinations_with_replacement(points, 2)
        # Only compute the upper diagonal, and throw into the processing pool in chunks if pool != None
        if (self.pool != None) :
            result_iter = self.pool.imap(self.kernel_fun, points_iter, max(1,(len(points) * (len(points) + 1)) / max(1,(2 * 5 * len(multiprocessing.active_children())))))
        else :
            result_iter = itertools.imap(self.kernel_fun, points_iter)

        # Initialize the shape of the result matrix
        self.kernel_matrix = [[0.0 for x in range(len(points))] for y in range(len(points))]
        # Fill in the result matrix from the iterator map, mirroring along the diagonal
        for ((i,j),result) in itertools.izip(itertools.combinations_with_replacement(range(len(points)),2), result_iter) :
            self.kernel_matrix[i][j] = result
            self.kernel_matrix[j][i] = result

        return self.kernel_matrix

    @staticmethod
    def get_kernel_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 
                  'window_size', 'window_stride', 'max_simplices', 
                  'persistence_epsilon', 'persistence_degree', 'kernel_scale']
        if config.post_process != None :
            fields.extend(['post_process', 'post_process_arg'])

        return get_filename(config, fields, 'PersistenceKernel', gz)

def main(argv) :
    parser = argparse.ArgumentParser(description='Tool to generate a similarity kernel from persistence data')
    parser.add_argument('-i', '--infile', help='Input JSON Persistence Diagram file')
    parser.add_argument('-o', '--outfile', help='Output JSON Kernel Similarity Matrix file')
    parser.add_argument('-p', '--pool', default=multiprocessing.cpu_count(), help='Threads of computation to use')
    parser.add_argument('-k', '--kernel-scale')
    parser.add_argument('-d', '--persistence-degree', help='Filter persistence to entries of this degree')
    args = vars(parser.parse_args(argv[1:]))

    persistences_json = load_data(args['infile'], 'persistence_diagrams', None, None, "PersistenceKernel: ")
    if persistences_json == None :
        print "Could not load --infile : %s" % (args['infile'],)
        exit()
    persistences = PD.fromJSONDict(persistences_json)
    config = persistences.config
    
    if (int(args['pool']) > 1) :
        pool = multiprocessing.Pool(int(args['pool']))
    else :
        pool = None

    if (args['kernel_scale'] != None) :
	config.kernel_scale = float(args['kernel_scale'])

    if (args['persistence_degree'] != None) :
        config.persistence_degree = args['persistence_degree']

    pk = PersistenceKernel(config, persistences,
                           kernel_fun=ScaleSpaceWrapper(float(config.kernel_scale)),
                           pool=pool)
    start = time.clock() 
    pk.compute_kernel()
    stop = time.clock()
    print "%f seconds" % (stop - start,)
    print "Is Positive Semidefinite? %s" %  (isPSD(numpy.matrix(pk.kernel_matrix),))

    if args['outfile'] == None :
        outfile = PersistenceKernel.get_kernel_filename(config)
    else :
        outfile = args['outfile'] 
    print "PersistenceKernel: Writing %s" % (outfile,)
    pk.config.status = "PersistenceKernel"
    save_data(outfile, pk.toJSONDict())
    
if __name__ == "__main__" :
        main(sys.argv)
