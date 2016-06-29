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


import sys
import argparse
import importlib

from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.Configuration import Configuration, get_filename

if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description="Utility to copy ")
    parser.add_argument("--infile")
    parser.add_argument("--outdir")
    args = parser.parse_args(sys.argv[1:])
    if (args.infile.endswith(".json.gz")) :
        start = args.infile.rfind('-') + 1
        end = -len(".json.gz")
        file_class = args.infile[start:end]
    else :
        start = args.infile.rfind('-') + 1
        end = -len(".json")
        file_class = args.infile[start:end]
    print args.infile, file_class
    status = None
    if "CSVSegments" in file_class :
        file_class = "ActivitySegments"
    if   "Segments" in file_class or \
         "Post" in file_class :
        data_class = "Segments"
    elif "Features" in file_class :
        data_class = file_class
    elif "PersistenceDiagrams" in file_class :
        file_class = "Datatypes.PersistenceDiagrams"
        data_class = file_class
    elif "Partition" in file_class :
        file_class = "Datatypes.TrainTestPartitions"
        data_class = file_class
    elif "DistancesLearning" in file_class or \
         "SimilarityLearning" in file_class :
        status = file_class[0:-len("Learning")]
        file_class = "DistanceLearning"
        data_class = "Learning"
    elif "MultipleKernelLearning" in file_class :
        file_class = "MultipleKernelLearning"
        data_class = "Learning"
    elif "KernelLearning" in file_class :
        status = file_class[0:-len("Learning")]
        file_class = "KernelLearning"
        data_class = "Learning"
    elif "FeaturesLearning" in file_class :
        status = file_class[0:-len("Learning")]
        file_class = "FeatureLearning"
        data_class = "Learning"
    elif "Distances" in file_class :
        data_class = "Distances"
    elif "ScaleSpaceSimilarities" in file_class :
        file_class = "ScaleSpaceSimilarity"
        data_class = "Distances"
    elif "Kernel" in file_class :
        data_class = "Kernel"
    elif "CrossValidation" in file_class :
        data_class = file_class

    module = importlib.import_module('persistence.' + file_class)
    module_class = getattr(module, file_class.split('.')[-1])
    module = importlib.import_module('persistence.' + file_class)
    data_class = getattr(module, data_class.split('.')[-1])
        

    in_json = load_data(args.infile, "JSONObject", None, None, sys.argv[0] + " : ")
    in_obj = data_class.fromJSONDict(in_json)
    in_obj.config.out_directory = args.outdir
    if status != None :
        in_obj.config.status = status          
    if   "Segments" in file_class or \
         "Post" in file_class :
        out_file = module_class.get_segment_filename(in_obj.config, gz=False)
    elif "Features" in file_class :
        out_file = module_class.get_features_filename(in_obj.config, gz=False)
    elif "PersistenceDiagrams" in file_class :
        out_file = module_class.get_persistence_diagrams_filename(in_obj.config, gz=False)
    elif "Partition" in file_class :
        out_file = module_class.get_partition_filename(in_obj.config, gz=False)
    elif "Learning" in file_class :
        out_file = module_class.get_learning_filename(in_obj.config, gz=False)
    elif "Distances" in file_class or \
         "ScaleSpaceSimilarity" in file_class :
        out_file = module_class.get_distances_filename(in_obj.config, gz=False)
    elif "AverageKernel" in file_class : 
        out_file = get_filename(in_obj.config, 
                                ['max_simplices', 'persistence_epsilon', 
                                 'segment_filename', 'segment_stride', 'segment_size', 
                                 'window_size', 'window_stride', 
                                 'kernel_scale', 'kernel_gamma', 'invariant_epsilon', 
                                 'data_file', 'data_index', 'label_index', 'persistence_degree', 
                                 'data_type', 'post_process', 'post_process_arg'], "AverageKernel")
    elif "Kernel" in file_class :
        out_file = module_class.get_kernel_filename(in_obj.config, gz=False)
    elif "CrossValidation" in file_class :
        out_file = module_class.get_cross_validation_filename(in_obj.config, gz=False)
    print "Writing %s" % (out_file,)
    save_data(out_file, in_obj.toJSONDict())
