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
import math
import itertools
import argparse
import copy

from Datatypes.Configuration import get_filename
from Datatypes.Kernel import Kernel
from Datatypes.JSONObject import load_data, save_data

def AverageKernel(kernels, weights=None) :
    config = copy.copy(kernels[0].config)
    config.data_index = [kernel.config.data_index for kernel in kernels]
    config.status = 'AverageKernel'
    segment_info = copy.copy(kernels[0].segment_info)
    nkernels = len(kernels)
    kernel_dimension = len(kernels[0].segment_info)
    if weights == None :
        weights = [1] * kernel_dimension
    kernel_matrix = [[numpy.average([k.kernel_matrix[i][j] for k in kernels]) for i in range(kernel_dimension)] for j in range(kernel_dimension)]
    return Kernel(config, kernel_matrix, segment_info)

if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description="Tool to take multiple Kernels and average them")
    parser.add_argument("--infile", "-i", nargs="+")
    parser.add_argument("--outfile", "-o")
    parser.add_argument("--ratio", "-r", type=float, default=0.5)
    parser.add_argument("--pool", "-p")
    
    args = parser.parse_args(sys.argv[1:])
    kernels_json = [load_data(infile, 'kernel', None, None, sys.argv[0]+": ") for infile in args.infile]
    kernels = [Kernel.fromJSONDict(kernel_json) for kernel_json in kernels_json]

    if len(kernels) == 2 :
        weights = [args.ratio, 1.0 - args.ratio]
    else :
        weights = None
    average_kernel = AverageKernel(kernels, weights)

    if args.outfile == None :
        args.outfile = get_filename(average_kernel.config, 
                                    ['max_simplices', 'persistence_epsilon', 
                                     'segment_filename', 'segment_stride', 'segment_size', 
                                     'window_size', 'window_stride', 
                                     'kernel_scale', 'kernel_gamma', 'invariant_epsilon', 
                                     'data_file', 'data_index', 'label_index', 'persistence_degree', 
                                     'data_type', 'post_process', 'post_process_arg'], "AverageKernel")
    print "Writing %s" % (args.outfile,)
    save_data(args.outfile, average_kernel.toJSONDict())
