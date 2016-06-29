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
import itertools
import numpy
import math
import sys
import argparse
import multiprocessing
import time
import functools
import os
from Datatypes.JSONObject import load_data, save_data
from Datatypes.Configuration import get_filename
from Datatypes.Segments import Segments, max_label, SegmentInfo
from Datatypes.Kernel import Kernel

class RBFEntryWrapper:
    def __init__(self, gamma):
        self.gamma = gamma
    def __call__(self, (s0, s1)):
        return math.exp(-1.0 * self.gamma * functools.reduce((lambda y, (x0,x1) : (x1 - x0) * (x1 - x0) + y), itertools.izip(s0, s1), 0.0))

class RBFKernel(Kernel):
    ''' Implement an RBF (Radial Basis Function) kernel '''
    @staticmethod
    def get_input_type():
        return "Segments"

    @staticmethod
    def get_output_type():
        return "Kernel"

    @staticmethod
    def get_scale_arg():
        return "kernel_gamma"

    def __init__(self, config, segment_data, pool=None) :
        super(self.__class__, self).__init__(config)
        # segment data has to have window size == segment size so each segment is 1-d data
        self.segment_info = [SegmentInfo.fromJSONDict(segment) for segment in segment_data.segments]
        self.max_labels = [max_label(segment.labels) for segment in segment_data.segments]
        self.segments = [[float(w) for w in segment.windows[0]] for segment in segment_data.segments]
        self.gamma = config.kernel_gamma
        if config.kernel_gamma != 'cv' :
            self.kernel_fun = RBFEntryWrapper(self.gamma)
        else :
            self.kernel_fun = None
        self.kernel_matrix = None
        self.pool = pool
        
    def compute_kernel(self) :
        if self.gamma == 'cv' :
            seed = 0xdeadbeef
            while self.kernel_fun == None :
                try :
                    # search for the correct gamma and C value using cross validation
                    from sklearn import svm
                    from sklearn.grid_search import GridSearchCV
                    from sklearn.cross_validation import StratifiedShuffleSplit
                    from sklearn.cross_validation import train_test_split
                
                    indices = xrange(0, len(self.max_labels))
                    if self.learning[0] != None :
                        train_indices = [i for i in indices if self.learning[i] == 'train']
                    else :
                        train_indices, test_indices = train_test_split(indices,
                                                                       train_size=self.config.learning_split,
                                                                       random_state=seed)
                    train_labels = [self.max_labels[i] for i in train_indices]
                    train_segments = [self.segments[i] for i in train_indices]
                    C_range     = numpy.logspace(-10, 10, 20)
                    gamma_range = numpy.logspace(-10, 10, 20)
                    param_grid = dict([("gamma", gamma_range), ("C", C_range)])
                    cv = StratifiedShuffleSplit(train_labels, n_iter=5, test_size=0.2, random_state=seed)
                    grid = GridSearchCV(svm.SVC(), param_grid=param_grid, cv=cv)
                    grid.fit(train_segments, train_labels)
                    print("RBFKernel : The best parameters are %s with a score of %0.2f"
                          % (grid.best_params_, grid.best_score_))
                    self.config.learning_C = grid.best_params_['C']
                    self.config.kernel_gamma = grid.best_params_['gamma']
                    self.gamma = grid.best_params_['gamma']
                    self.kernel_fun = RBFEntryWrapper(self.gamma)
                except ValueError as e :
                    print "ValueError (%s) in cv search, trying again (%x)" % (e, seed)
                    random_state = os.urandom(4)
                    seed = ord(random_state[0]) + 256 * (ord(random_state[1]) + 256 * (ord(random_state[2]) + 256 * ord(random_state[3])))
                    self.kernel_fun = None

        segment_iter = itertools.combinations_with_replacement(self.segments, 2)
        if (self.pool == None) :
            value_iter = itertools.imap(self.kernel_fun, segment_iter)
        else :
            value_iter = self.pool.imap(self.kernel_fun, segment_iter, 
                                        max(1, len(self.segments) * (len(self.segments) + 1) / (5 * 2 * len(multiprocessing.active_children()))))

        self.kernel_matrix = [[0.0 for x in range(len(self.segments))] for y in range(len(self.segments))]
        for ((i,j), val) in itertools.izip(itertools.combinations_with_replacement(range(len(self.segments)), 2), value_iter) :
            self.kernel_matrix[i][j] = val
            self.kernel_matrix[j][i] = val

    @staticmethod
    def get_kernel_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size', 'segment_stride', 'kernel_gamma']
        if config.post_process != None :
            fields.extend(['post_process', 'post_process_arg'])

        return get_filename(config, fields, 'RBFKernel', gz)
    
def main(argv) :
    parser = argparse.ArgumentParser(description='Tool to generate a radial basis kernel from segmented data')
    parser.add_argument('-i', '--infile', help='Input JSON Segment file')
    parser.add_argument('-o', '--outfile', help='Output JSON RBF Kernel Matrix file')
    parser.add_argument('-g', '--kernel-gamma')
    parser.add_argument('-p', '--pool', default=multiprocessing.cpu_count(), help='Threads of computation to use')
    args = vars(parser.parse_args(argv[1:]))
    sf_json = load_data(args['infile'], 'segments', None, None, "RBFKernel: ")
    if sf_json == None :
        print "Could not load --infile : %s" % (args['infile'],)
        exit()
    segments = Segments.fromJSONDict(sf_json)
    config = segments.config
    if (int(args['pool']) > 1) :
      pool = multiprocessing.Pool(int(args['pool']))
    else :
      pool = None
    if (args['kernel_gamma'] != None) :
        if args['kernel_gamma'] == 'cv' :
            config.kernel_gamma = 'cv'
        else :
            config.kernel_gamma = float(args['kernel_gamma'])
    rk = RBFKernel(config, segments, pool=pool)
    start = time.clock() 
    rk.compute_kernel()
    stop = time.clock()
    print "%f seconds" % (stop - start,)
    if args['outfile'] == None :
        outfile = RBFKernel.get_kernel_filename(config)
    else :
        outfile = args['outfile']
    print "RBFKernel: Writing %s" % (outfile,)
    rk.config.status = "RBFKernel"
    save_data(outfile, rk.toJSONDict())
                                
if __name__ == "__main__" :
        main(sys.argv)
