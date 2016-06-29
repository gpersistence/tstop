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

from persistence.Datatypes.JSONObject import load_data
from persistence.Datatypes import Learning

parser = argparse.ArgumentParser(description="utility to print stats about learning JSON")
parser.add_argument('--csv', action="store_true")
parser.add_argument('files', metavar='FILE', nargs='*')
args = vars(parser.parse_args(sys.argv[1:]))
if args['csv'] :
    print "Data File,Learning Type,Data Index,Segment Size,Segment Stride,Window Size,Max Simplices,Kernel Scale,C,Correct,Std. Dev.,Top Quart,Bot Quart,Train,Test,Classes,Kernel Weights"
for f in args['files']:
    try:
        lf_json = load_data(f, 'learning', None, None, 'learning_stats: ' if not args['csv'] else None)
        if lf_json == None :
            print "Could not load file : %s" % (f,)
            exit()
        
        learning = Learning.Learning.fromJSONDict(lf_json)
        correct = []
        if (isinstance(learning.config.data_file, list)):
            (filename, ext) = os.path.splitext(os.path.basename(learning.config.data_file[0]))
            import string
            filename = string.join(filename.split("_")[0:-1])
        elif (isinstance(learning.config.data_file, dict)) :
            filename = 'placeholder'
        else :
            (filename, ext) = os.path.splitext(os.path.basename(learning.config.data_file))
        learning_type = (f.split('-')[-1]).split('.')[0]
        for result in learning['results'] :
            # count the correct test results
            num_correct = reduce((lambda s, (t0, t1) : s + 1 if t0 == t1 else s), 
                                 zip(result['test_results'], result['test_labels']), 0)
            correct.append(float(num_correct) / float(len(result['test_results'])))
        num_classes = len(list(set(learning['results'][0]['train_labels'] + learning['results'][0]['test_labels'])))
        mkl_weights = None
        if learning['results'][0]['mkl_weights'] != None :
            mkl_weights = [0.0 for e in learning['results'][0]['mkl_weights']]
            for index in range(len(learning['results'][0]['mkl_weights'])) :
                mkl_weights[index] = numpy.average([w['mkl_weights'][index] for w in learning['results']])
                
        if isinstance(learning.config.data_index, list) :
            data_index = '_'.join([str(i) for i in learning.config.data_index])
        else :
            data_index = learning.config.data_index

        if (len(correct) > 1) :
            average = numpy.average(correct)
            if args['csv'] :
                output = ','.join([filename,
                                   learning_type + (learning.config.post_process if learning.config.post_process != None else ""),
                                   str(data_index),
                                   str(learning.config.segment_size),
                                   str(learning.config.segment_stride),
                                   str(learning.config.window_size),
                                   str(learning.config.max_simplices),
                                   str(learning.config.kernel_scale),
                                   str(learning.config.learning_C),
                                   str(average),
                                   str(numpy.std(correct)),
                                   str(average + numpy.percentile(correct, 0.75)),
                                   str(average - numpy.percentile(correct, 0.25)),
                                   str(len(learning['results'][0]['train_labels'])), 
                                   str(len(learning['results'][0]['test_labels'])), 
                                   str(num_classes)])
                if mkl_weights != None :
                    for weight in mkl_weights :
                        output = output + "," + str(weight)
                print output
            else:
                print "file %s avg %s std %s top quartile %s bot quartile %s weights %s" % \
                    (f, average, numpy.std(correct), 
                     average + numpy.percentile(correct, 0.75),
                     average - numpy.percentile(correct, 0.25), mkl_weights)
        else :
            if args['csv']:
                
                output = ','.join([filename,
                                   learning_type + (learning.config.post_process if learning.config.post_process != None else ""),
                                   str(data_index),
                                   str(learning.config.segment_size),
                                   str(learning.config.segment_stride),
                                   str(learning.config.window_size),
                                   str(learning.config.max_simplices),
                                   str(learning.config.kernel_scale),
                                   str(learning.config.learning_C),
                                   str(correct[0]),
                                   str(0.0),
                                   str(correct[0]),
                                   str(correct[0]), 
                                   str(len(learning['results'][0]['train_labels'])), 
                                   str(len(learning['results'][0]['test_labels'])), 
                                   str(num_classes)])
                if learning['results'][0]['mkl_weights'] != None :
                    for weight in learning['results'][0]['mkl_weights']:
                        output = output + "," + str(weight)
                print output
            else:
                print "file %s correct %s" % (f, correct)
                if learning['results'][0]['mkl_weights'] != None :
                    print learning['results'][0]['mkl_weights']
            


    except :
        import traceback
        print "Error %s occurred in file %s" % (traceback.format_exc(), f)
