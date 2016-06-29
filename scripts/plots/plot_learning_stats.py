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


import json
import os
import sys
import argparse
import numpy

from Datatypes.JSONObject import load_data
from Datatypes.Learning import Learning

def correct_count(learning) :
    correct = []
    for result in learning.results : 
        num_correct = reduce((lambda s, (t0, t1) : s + 1 if t0 == t1 else s), 
                             zip(result.test_results, result.test_labels), 0)
        correct.append(float(num_correct) / float(len(result.test_results)))
    return correct

def get_mkl_weights(learning) : 
    mkl_weights = None
    if learning.results[0].mkl_weights != None :
        print learning.results[0].mkl_weights
        mkl_weights = [0.0 for e in learning.results[0].mkl_weights]
        for index in range(len(learning.results[0].mkl_weights)) :
            if len(learning.results) > 1 :
                mkl_weights[index] = numpy.average([w.mkl_weights[index] for w in learning.results])
            else :
                mkl_weights[index] = learning.results[0].mkl_weights[index]
    return mkl_weights
        

parser = argparse.ArgumentParser(description="utility to plot stats about learning JSON")
parser.add_argument('--rbf', help="One learning file from KernelLearning using an RBFKernel")
parser.add_argument('--svm', nargs='+', help="N learning files using KernelLearning using a PersistenceKernel")
parser.add_argument('--mkl', nargs='+', help="N learning files using MultipleKernelLearning using a PersistenceKernel and an RBFKernel")

args = vars(parser.parse_args(sys.argv[1:]))

entries = []

rbf_json = load_data(args['rbf'], 'learning', None, None, "plot learning stats ")
if rbf_json == None :
    print "Could not load --rbf : %s" % (args['rbf'],)
    exit()
rbf = Learning.fromJSONDict(rbf_json)
rbf_correct = correct_count(rbf)
x_base = 0
colors = ["red", "blue", "orange", "green"]
x_ticks = []
x_labels = []
bar_xs = []
bar_0_ys = []
bar_1_ys = []

rbf_xs = []
rbf_ys = []
rbf_yerr = []

svm_xs = []
svm_ys = []
svm_yerr = []

mkl_0_ys = []
mkl_1_ys = []
mkl_weight_yerr = []

mkl_xs = []
mkl_yerr = []


for (svm, mkl) in zip(args['svm'], args['mkl']):
    try:
        rbf_xs.append(x_base)
        rbf_ys.append(numpy.average(rbf_correct)*100)
        rbf_yerr.append(numpy.std(rbf_correct)*100)

        svm_json = load_data(svm, 'learning', None, None, "plot learning stats ")
        if svm_json == None :
            print "Could not load --svm : %s" % (svm,)
            exit()
        svm_learning = Learning.fromJSONDict(svm_json)
        svm_correct = correct_count(svm_learning)
        svm_xs.append(x_base+1)
        svm_ys.append(numpy.average(svm_correct)*100)
        svm_yerr.append(numpy.std(svm_correct)*100)
        
        mkl_json = load_data(mkl, 'learning', None, None, "plot learning stats ")
        if mkl_json == None :
            print "Could not load --mkl : %s" % (mkl,)
            exit()
        mkl_learning = Learning.fromJSONDict(mkl_json)
        mkl_correct = correct_count(mkl_learning)
        mkl_weights = get_mkl_weights(mkl_learning)
        
        mkl_xs.append(x_base+2)
        mkl_avg = numpy.average(mkl_correct) if len(mkl_correct) > 1 else mkl_correct[0]
        mkl_0_ys.append(mkl_weights[0] * mkl_avg * 100)
        mkl_1_ys.append(mkl_weights[1] * mkl_avg * 100)
        mkl_yerr.append(numpy.std(mkl_correct) * 100 if len(mkl_correct) > 1 else 0.0)
        x_ticks.append(x_base+1)
        x_labels.append("%s" % (svm_learning.config.window_size,))
        x_base += 4
    except :
        import traceback
        print "Error %s occurred in file %s or %s" % (traceback.format_exc(), svm, mkl)

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
rbf_rects = ax.bar(rbf_xs, rbf_ys, yerr=rbf_yerr, color=colors[0])
svm_rects = ax.bar(svm_xs, svm_ys, yerr=svm_yerr, color=colors[1])
print mkl_0_ys
mkl_0_rects = ax.bar(mkl_xs, mkl_0_ys, color=colors[1])
mkl_1_rects = ax.bar(mkl_xs, mkl_1_ys, bottom=mkl_0_ys, yerr=mkl_yerr, color=colors[0])
if (isinstance(rbf.config.data_file, list)):
    (filename, ext) = os.path.splitext(os.path.basename(rbf.config.data_file[0]))
    import string
    filename = string.join(filename.split("_")[0:-1])
else :
    (filename, ext) = os.path.splitext(os.path.basename(rbf.config.data_file))
ax.set_title("Learning Results for %s Segment Size %s Stride %s Data Index %s" % (filename, rbf.config.segment_size, rbf.config.segment_stride, rbf.config.data_index))
ax.set_ylabel("Percent Correct")
ax.set_ylim([0,100])
ax.set_xticks(x_ticks)
ax.set_xticklabels(x_labels)

plt.show()
