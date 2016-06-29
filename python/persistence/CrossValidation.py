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
import argparse
import importlib
from copy import copy 
import itertools 
import multiprocessing
import numpy
import signal
import Queue
import random
import time
import traceback
from struct import pack, unpack

from persistence.Datatypes.JSONObject import JSONObject, load_data, save_data, cond_get
from persistence.Datatypes.Configuration import Configuration, parse_range, get_filename
from persistence.Datatypes.Segments import Segments, SegmentInfo, max_label
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams 
from persistence.Datatypes.TrainTestPartitions import TrainTestPartitions, TrainTestPartition
from Datatypes.Learning import Learning
import persistence.KernelLearning

class Validator :
    """
    Callable class to hold state for multiprocessing.Pool invocation
    """
    def __init__(self, config, 
                 kernel_class, kernel_args, distances_class, distances_args, learning_class, 
                 kernel_objects, distances_object, input, 
                 partitions, cv_partitions) :
        self.config = config 
        self.kernel_class = kernel_class
        self.kernel_args = kernel_args
        self.distances_class = distances_class
        self.distances_args = distances_args
        self.learning_class = learning_class 
        self.kernel_objects = kernel_objects
        self.distances_object = distances_object
        self.input = input 
        self.partitions = partitions
        self.cv_partitions = cv_partitions

    def __call__(self, (kernel_arg, distances_arg, learning_arg, partition)) :
        learning_scale = self.learning_class.get_scale_arg()
        config = copy(self.config)
        kernel_scale = None
        distances_scale = None
        if learning_scale != None :
            config[learning_scale] = learning_arg
        if self.kernel_class != None and self.kernel_args != None :
            kernel_scale = self.kernel_class.get_scale_arg()
            if kernel_scale != None :
                config[kernel_scale] = kernel_arg
            learning_object = self.learning_class(config, self.kernel_objects[self.kernel_args.index(kernel_arg)], 
                                                  self.cv_partitions[self.partitions.cross_validation.index(partition)])
        elif self.distances_class != None and distances_args != None :
            distances_scale = self.distances_class.get_scale_arg()
            if distances_scale != None :
                config[distances_scale] = distances_arg
            learning_object = self.learning_class(config, self.distances_objects[self.distances_args.index(distances_arg)], 
                                                  self.cv_partitions[self.partitions.cross_validation.index(partition)])
        else :
            learning_object = self.learning_class(config, self.input, partition)

        learning_object.train()
        result = learning_object.test()
            
        return (kernel_arg, distances_arg, learning_arg, result)
        

class CrossValidation(JSONObject) :
    """
    Run cross validation using a kernel generator / kernel learning or
    distances generator / k-NN learning using supplied the paritions
    in the cross_validation field in the supplied TrainTestParititons
    """
    fields = ['config',
              'kernel_module',
              'kernel_arg',
              'distances_module',
              'distances_arg',
              'learning_module',
              'learning_arg',
              'partitions']

    def __init__(self, input_json, config=None,
                 kernel_module=None, kernel_arg=None,
                 distances_module=None, distances_arg=None,
                 learning_module=None, learning_arg=None, 
                 partitions=None,
                 pool=None, timeout=600) :
        self.input_json = input_json
        self.config = config
        self.kernel_module = kernel_module
        self.kernel_arg = kernel_arg
        self.distances_module = distances_module
        self.distances_arg = distances_arg
        self.learning_module = learning_module
        self.learning_arg = learning_arg
        self.partitions = partitions
        self.pool = pool
        self.timeout = timeout # optional way to die if things are taking to long

    @classmethod
    def fromJSONDict(cls, json):
        return cls(None, 
                   config=Configuration.fromJSONDict(json['config']),
                   kernel_module=cond_get(json, 'kernel_module'), 
                   kernel_arg=cond_get(json, 'kernel_arg'),
                   distances_module=cond_get(json, 'distances_module'), 
                   distances_arg=cond_get(json, 'distances_arg'),
                   learning_module=cond_get(json, 'learning_module'), 
                   learning_arg=cond_get(json, 'learning_arg'), 
                   partitions=cond_get(json, 'partitions'))

    def cross_validate(self,) :
        cv_input = None
        # Make a mapping for just the segments / diagrams / whatever we need for cross validation
        cv_indices = list(set(itertools.chain.from_iterable([cv.train + cv.test for cv in self.partitions.cross_validation])))
        cv_indices.sort()
        
        cv_partitions = [TrainTestPartition(train=[cv_indices.index(i) for i in cv.train],
                                            test=[cv_indices.index(i) for i in cv.test],
                                            state=cv.state) for cv in self.partitions.cross_validation]
        learning_class = None
        kernel_class = None
        distances_class = None
        if self.kernel_module != None :
            print self.kernel_module
            kernel_module = importlib.import_module("persistence." + self.kernel_module)
            kernel_class = getattr(kernel_module, self.kernel_module)
            kernel_input_type = kernel_class.get_input_type()
            kernel_input_module =  importlib.import_module("persistence.Datatypes." + kernel_input_type)
            kernel_input_class = getattr(kernel_input_module, kernel_input_type)

            cv_input = kernel_input_class.fromJSONDict(self.input_json)
            field = kernel_input_class.get_iterable_field()
            # narrow the input to only the cross validation inputs
            cv_input[field] = [cv_input[field][i] for i in cv_indices]
        elif self.distances_module != None :
            distances_module = importlib.import_module("persistence." + self.distances_module)
            distances_class = getattr(distances_module, self.distances_module)
            distances_input_type = distances_class.get_input_type()
            distances_input_module =  importlib.import_module("persistence.Datatypes." + distances_input_type)
            distances_input_class = getattr(distances_input_module, distances_input_type)
            cv_input = distances_input_class.fromJSONDict(self.input_json)
            field = distances_input_class.get_iterable_field()
            # narrow the input to only the cross validation inputs
            cv_input[field] = [cv_input[field][i] for i in cv_indices]
        
        learning_module = importlib.import_module("persistence." + self.learning_module)
        learning_class = getattr(learning_module, self.learning_module)
        learning_input_type = learning_class.get_input_type()
        learning_input_module =  importlib.import_module("persistence.Datatypes." + learning_input_type)
        learning_input_class = getattr(learning_input_module, learning_input_type)

        # Cross validation only using the learning_arg value 
        if self.kernel_module == None and self.distances_module == None:
            cv_input = learning_input_class.fromJSONDict(self.input_json)


        learning_results = []
        if isinstance(self.kernel_arg, list) :
            kernel_args = self.kernel_arg
        else :
            kernel_args = [self.kernel_arg]
        
        if self.kernel_module != None :
            # Precompute kernel objects
            def computed_kernel(arg) :
                config = copy(self.config)
                scale_arg = kernel_class.get_scale_arg()
                if scale_arg != None :
                    config[scale_arg] = arg
                kernel = kernel_class(config, cv_input, pool=self.pool)
                print "Computing %s for %s of %s" % ( self.kernel_module, scale_arg, arg ) 
                kernel.compute_kernel()
                kernel.pool = None
                return kernel
            kernel_objects = [computed_kernel(arg) for arg in kernel_args]
        else :
            kernel_objects = None

        if isinstance(self.distances_arg, list) :
            distances_args = self.distances_arg
        else :
            distances_args = [self.distances_arg]

        if self.distances_module != None :
            # Precompute distances objects
            def computed_distances(arg) :
                config = copy(self.config)
                scale_arg = distances_class.get_scale_arg()
                if scale_arg != None :
                    config[scale_arg] = arg
                distances = distances_class(config, cv_input, pool=self.pool)
                print "Computing %s for %s of %s" % ( self.distances_module, scale_arg, arg ) 
                distances.compute_distances()
                distances.pool = None
                return distances
            distances_objects = [computed_distances(arg) for arg in distances_args]
        else :
            distances_objects = None

        if isinstance(self.learning_arg, list) :
            learning_args = self.learning_arg
        else :
            learning_args = [self.learning_arg]

        validator = Validator(self.config, 
                              kernel_class, kernel_args, distances_class, distances_args, learning_class, 
                              kernel_objects, distances_objects, cv_input, 
                              self.partitions, cv_partitions)
        if self.pool == None :
            print "single thread computations"
            results = itertools.imap(validator, 
                                     itertools.product(kernel_args, distances_args, learning_args, 
                                                       self.partitions.cross_validation))
            results = list(results)
        else :
            results = self.pool.imap(validator, 
                                     itertools.product(kernel_args, distances_args, learning_args, 
                                                       self.partitions.cross_validation),
                                     1)
            final_results = []
            try:
                while True:
                    if self.timeout > 0 :
                        result = results.next(self.timeout)
                    else :
                        result = results.next()
                    final_results.append(result)
            except StopIteration:
                pass
            except multiprocessing.TimeoutError as e:
                self.pool.terminate()
                print traceback.print_exc()
                sys.exit(1)
            results = final_results

        results = list(results)
        best_result = (None, 0.0)
        learning_scale = None
        kernel_scale = None
        distances_scale = None
        for (kernel_arg, distances_arg, learning_arg) in itertools.product(kernel_args, distances_args, learning_args) :
            these_results = [result for (_kernel_arg, _distances_arg, _learning_arg, result) in results if kernel_arg == _kernel_arg and distances_arg == _distances_arg and learning_arg == _learning_arg]
            config = copy(self.config)
            learning_scale = learning_class.get_scale_arg()
            if learning_scale != None :
                config[learning_scale] = learning_arg
            if self.kernel_module != None and kernel_args != None :
                kernel_scale = kernel_class.get_scale_arg()
                if kernel_scale != None :
                    config[kernel_scale] = kernel_arg
            elif self.distances_module != None and distances_args != None :
                distances_scale = distances_class.get_scale_arg()
                if distances_scale != None :
                    config[distances_scale] = distances_arg
            correct = Learning(config, these_results).get_average_correct()
            if correct > best_result[1]:
                best_result = (config, correct)

        self.config = best_result[0]
        print "Best result %02.2f%% %s%s%s" % \
            (best_result[1] * 100.0, 
             ("%s %s " % (kernel_scale, self.config[kernel_scale])) if kernel_scale != None else "", 
             ("%s %s " % (distances_scale, self.config[distances_scale])) if distances_scale != None else "",
             ("%s %s " % (learning_scale, self.config[learning_scale])) if learning_scale != None else "")
        self.config.status = 'CrossValidation'

    @staticmethod
    def get_cross_validation_filename(config, gz=False):
        fields = Configuration.fields

        return get_filename(config, fields, 'CrossValidation', gz)

def main(argv) :
    parser = argparse.ArgumentParser(description="General purpose cross validation tool")
    parser.add_argument("--kernel-module", "-K")
    parser.add_argument("--kernel-arg", "-k")
    parser.add_argument("--distances-module", "-D")
    parser.add_argument("--distances-arg", "-d")
    parser.add_argument("--learning-module", "-L")
    parser.add_argument("--learning-arg", "-l")
    parser.add_argument("--infile", "-i")
    parser.add_argument("--outfile", "-o")
    parser.add_argument("--train-test-partitions", "-t")
    parser.add_argument("--pool", "-p", type=int, default=max(1,multiprocessing.cpu_count()-2))
    parser.add_argument("--timeout", type=int, default=0)
    args = parser.parse_args(argv[1:])
    input_json = load_data(args.infile, "input", None, None, argv[0] + ":")
    partitions_json = load_data(args.train_test_partitions, "input", None, None, argv[0] + ":")
    partitions = TrainTestPartitions.fromJSONDict(partitions_json)
    if args.pool > 1 :
        pool = multiprocessing.Pool(args.pool)
    else :
        pool = None
    
    if args.kernel_arg != None :
        kernel_arg = parse_range(args.kernel_arg, t=float)
    else :
        kernel_arg = None

    if args.distances_arg != None :
        distances_arg = parse_range(args.distances_arg, t=float)
    else :
        distances_arg = None

    if args.learning_arg != None :
        learning_arg = parse_range(args.learning_arg, t=float)
    else :
        learning_arg = None

    print "Kernel %s distance %s learning %s" % (kernel_arg, distances_arg, learning_arg)
    cv = CrossValidation(input_json, 
                         config=Configuration.fromJSONDict(input_json['config']),
                         kernel_module=args.kernel_module, 
                         kernel_arg=kernel_arg, 
                         distances_module=args.distances_module, 
                         distances_arg=distances_arg, 
                         learning_module=args.learning_module, 
                         learning_arg=learning_arg, 
                         partitions=partitions, 
                         pool=pool,
                         timeout=args.timeout)
    cv.cross_validate()
    
    if args.outfile == None :
        args.outfile = CrossValidation.get_cross_validation_filename(cv.config)
    
    print "Writing %s" % args.outfile
    save_data(args.outfile, cv.toJSONDict())


if __name__=="__main__" :
    main(sys.argv)
