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
from copy import copy
import subprocess

from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.Segments import Segments, Segment
from persistence.Datatypes.Configuration import Configuration, parse_args, parse_range
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams
from persistence.Datatypes.TrainTestPartitions import TrainTestPartitions
from persistence.PersistenceKernel import PersistenceKernel
from persistence.ScaleSpaceSimilarity import ScaleSpaceSimilarity
from persistence.DistanceLearning import DistanceLearning
from persistence.KernelLearning import KernelLearning
from persistence.RBFKernel import RBFKernel
from persistence.EuclideanDistances import EuclideanDistances

if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description="Utility to run common variations of learning tasks on a configuration file, generating segments, distances, kernels, and learning results as appropriate")
    parser.add_argument("--config")
    parser.add_argument("--pool", default=1, type=int)
    args = parser.parse_args(sys.argv[1:])
    config = Configuration.fromJSONDict(parse_args([sys.argv[0], "--config", args.config])[0])
    print config

    module = importlib.import_module('persistence.' + config.data_type)
    module_class = getattr(module, config.data_type)
    segment_filename = module_class.get_segment_filename(config)

    segments = module_class(config)
    print "Writing %s" % segment_filename
    save_data(segment_filename, segments.toJSONDict())

    #TrainTestSplit
    partition_command = ["python", "-u", "-O", "-m", "persistence.PartitionData", 
                         "--segments", segment_filename, 
                         "--learning-split", str(config.learning_split), 
                         "--learning-iterations", str(config.learning_iterations), 
                         "--cv-iterations", "5"]
    subprocess.call(partition_command)
    partition_filename = TrainTestPartitions.get_partition_filename(config)

    #PersistenceDiagrams
    persistence_command = ["python", "-u", "-O", "-m", "persistence.PersistenceGenerator", 
                           "--pool", str(args.pool),
                           "--infile", segment_filename]
    subprocess.call(persistence_command)
    persistence_filename = PersistenceDiagrams.get_persistence_diagrams_filename(config)

    #PersistenceKernel
    persistence_kernel_command = ["python", "-u", "-O", "-m", "persistence.PersistenceKernel", 
                                  "--pool", str(args.pool),
                                  "--infile", persistence_filename]
    subprocess.call(persistence_kernel_command)
    persistence_kernel_filename = PersistenceKernel.get_kernel_filename(config)
    
    #ScaleSpaceSimilarities
    scale_space_command = ["python", "-u", "-O", "-m", "persistence.ScaleSpaceSimilarity", 
                           "--kernel-file", persistence_kernel_filename]
    subprocess.call(scale_space_command)
    scale_space_filename = ScaleSpaceSimilarity.get_distances_filename(config)

    #ScaleSpaceSimilarityLearning
    distance_learning_command = ["python", "-u", "-O", "-m", "persistence.DistanceLearning", 
                                 "--max-mode", "--infile", scale_space_filename,
                                 "--train-test-partitions", partition_filename]
    subprocess.call(distance_learning_command)

    #Persistence KernelLearning
    kernel_learning_command = ["python", "-u", "-O", "-m", "persistence.KernelLearning", 
                               "--learning-C", "1e-6;1;10", "--pool", str(args.pool),
                               "--infile", persistence_kernel_filename,
                               "--train-test-partitions", partition_filename]
    subprocess.call(kernel_learning_command)

    windowless_config = copy(config)
    windowless_config.window_size = windowless_config.segment_size
    windowless_segment_filename = module_class.get_segment_filename(windowless_config)

    windowless_segments = module_class(windowless_config)
    print "Writing %s" % windowless_segment_filename
    save_data(windowless_segment_filename, windowless_segments.toJSONDict())

    #RBFKernel
    rbf_kernel_filenames = []
    for gamma in parse_range("1e-6;1e6;10", t=float) :
        rbf_kernel_command = ["python", "-u", "-O", "-m", "persistence.RBFKernel", 
                              "--pool", str(args.pool), "--kernel-gamma", "%g" % gamma, 
                              "--infile", windowless_segment_filename]
        windowless_config.kernel_gamma = gamma
        subprocess.call(rbf_kernel_command)
        rbf_kernel_filenames.append(RBFKernel.get_kernel_filename(windowless_config))
        
    #RBFKernelLearning
    for f in rbf_kernel_filenames :
        kernel_learning_command = ["python", "-u", "-O", "-m", "persistence.KernelLearning", 
                                   "--learning-C", "1e-6;1;10", "--pool", str(args.pool),
                                   "--infile", f,
                                   "--train-test-partitions", partition_filename]
        subprocess.call(kernel_learning_command)

    #EuclideanDistances
    euclidean_distance_command = ["python", "-u", "-O", "-m", "persistence.EuclideanDistances",
                                  "--pool", str(args.pool),
                                  "--infile", windowless_segment_filename]
    subprocess.call(euclidean_distance_command)
    euclidean_distance_filename = EuclideanDistances.get_distances_filename(windowless_config)

    #Euclidean DistanceLearning
    distance_learning_command = ["python", "-u", "-O", "-m", "persistence.DistanceLearning",
                                 "--infile", euclidean_distance_filename,
                                 "--train-test-partitions", partition_filename]
    subprocess.call(distance_learning_command)


