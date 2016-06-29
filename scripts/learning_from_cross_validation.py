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
import argparse
import importlib
import subprocess
from persistence.Datatypes.JSONObject import load_data
from persistence.Datatypes.Configuration import Configuration
from persistence.CrossValidation import CrossValidation

if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description="Utility to generate kernels and learning results from a cross validation result")
    parser.add_argument("--pool", "-p", type=int)
    parser.add_argument("--input", "-i")
    parser.add_argument("--cross-validation", "-v")
    parser.add_argument("--train-test-partitions", "-t")
    args = parser.parse_args(sys.argv[1:])
    print args.cross_validation
    cv_json = load_data(args.cross_validation, "cross validation", None, None, sys.argv[0]+": ")
    cv = CrossValidation.fromJSONDict(cv_json)
    config = cv.config
    print config

    if cv.kernel_module != None :
        kernel_module = importlib.import_module("persistence." + cv.kernel_module)
        kernel_class = getattr(kernel_module, cv.kernel_module)
        scale_arg = kernel_class.get_scale_arg()
        kernel_filename = kernel_class.get_kernel_filename(config)
        kernel_command = ["python", "-u", "-O", "-m", "persistence."+cv.kernel_module, 
                          "--"+scale_arg.replace("_","-"), str(config[scale_arg]),
                          "--infile", args.input]
        if args.pool != None :
            kernel_command.extend(["--pool", str(args.pool)])
        else :
            kernel_command.extend(["--pool", "1"])

        if not os.path.isfile(kernel_filename):
            subprocess.call(kernel_command)

    elif cv.distances_module != None :
        distances_module = importlib.import_module("persistence." + cv.distances_module)
        distances_class = getattr(distances_module, cv.distances_module)
        scale_arg = distances_class.get_scale_arg()
        distances_filename = distances_class.get_distances_filename(config)
        distances_command =  ["python", "-u", "-O", "-m", "persistence."+cv.distances_module, 
                              "--infile", args.input]
        if scale_arg != None :
            distances_command.extend(["--"+scale_arg.replace("_","-"), str(config[scale_arg])])
        if args.pool != None :
            distances_command.extend(["--pool", str(args.pool)])
        else :
            distances_command.extend(["--pool", "1"])

        if not os.path.isfile(distances_filename):
            subprocess.call(distances_command)

    learning_module = importlib.import_module("persistence." + cv.learning_module)
    learning_class = getattr(learning_module, cv.learning_module)
    scale_arg = learning_class.get_scale_arg()
    print scale_arg, str(config[scale_arg])
    learning_command = ["python", "-u", "-O", "-m", "persistence."+cv.learning_module, "--infile"]
    if cv.kernel_module != None : 
        learning_command.append(kernel_filename)
    elif cv.distances_module != None :
        learning_command.append(distances_filename)
        if cv.distances_module == "ScaleSpaceSimilarity":
            learning_command.append("--max-mode")
    else :
        learning_command.append(args.input)
    if scale_arg != None :
        learning_command.extend(["--"+scale_arg.replace("_","-"), str(config[scale_arg])])
    if args.pool != None :
        learning_command.extend(["--pool", str(args.pool)])
    else :
        learning_command.extend(["--pool", "1"])
    if args.train_test_partitions != None :
        learning_command.extend(["--train-test-partitions", args.train_test_partitions])
    print ' '.join(learning_command)    
    subprocess.call(learning_command)
    
