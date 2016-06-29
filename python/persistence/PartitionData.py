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


import random
import os
import sys
import argparse
from math import ceil
import numpy

from sklearn.cross_validation import StratifiedKFold

from Datatypes.JSONObject import load_data, save_data
from Datatypes.Segments import SegmentInfo
from Datatypes.Configuration import Configuration
from Datatypes.TrainTestPartitions import TrainTestPartition, TrainTestPartitions

def PartitionData(segment_info, split, avoid_overlap=False, segment_size=0, 
                  file_based=False, preserve_labels=False, override_preset=False, surpress_warning=False, seed=None) :
    '''
    Accepts a list of Datatype.Segments.SegmentInfo and a float between 0 and 1, 
    and outputs a pair of lists of indices, (train, test) corresponding 
    to a parition of the input list
    len(train) approximates split * len(segment_info)
    Intersection of train and test is an empty set
    Union of train and test is not guaranteed to be range(len(segment_info))

    Optional arguments:
    avoid_overlap omits entries in test that would have overlapping data with entries in train, 
        as indicated by the range [segment_start:segment_start+segment_size]
    segment_size interacts with avoid overlap, because only segment_start is contained in the 
        SegmentInfo class
    file_based creates partitions where segments with the same filename for source data are 
        in the same partition
    preserve_label tries to split the populations of labels evenly
    '''

    segment_count = len(segment_info)
    segment_range = range(segment_count)

    # check to see if we have a preset train / test split for all data and we aren't overriding that
    if not override_preset and [0 for s in segment_info if s.learning == None] == [] :
        return TrainTestPartition([i for i in segment_range if segment_info[i].learning == 'train'],
                                  [i for i in segment_range if segment_info[i].learning == 'test'], None)

    train_goal_len = int(ceil(segment_count * split))

    if preserve_labels :
        labels = [s.max_label() for s in segment_info]
        label_set = list(set(labels))
        label_count = [(l0,len([l for l in labels if l == l0])) for l0 in label_set]
        label_goal = [(str(l), int(round(c * split))) for (l,c) in label_count]
        for ((l0,g),(l1,c)) in zip(label_goal, label_count) :
            if (g == 0) or (g == c) and not surpress_warning:
                print "PartitionData warning: not enough entries (%d) of label %s to properly make a train / test split of ratio %s" % (c, l0, split)
        label_goal = dict(label_goal)

    train = []
    test = []
    if seed != None :
        random.seed(seed)
    state = random.getstate()
    if file_based :
        files = list(set([s.filename for s in segment_info]))
        random.shuffle(files)
        for f in files :
            f_indices = [x for (x,y) in zip(segment_range, segment_info) if y.filename == f]
            if preserve_labels :
                f_labels = [str(labels[i]) for i in f_indices]
                extend_train = True
                for l in label_goal.keys() :
                    count = len([l0 for l0 in f_labels if l0 == l])
                    if count > label_goal[l] :
                        extend_train = False
                        break
                if extend_train :
                    train.extend(f_indices)
                    for l in label_goal.keys() :
                        count = len([l0 for l0 in f_labels if l0 == l])
                        label_goal[l] = label_goal[l] - count
                else :
                    test.extend(f_indices)
            else :
                if len(train) + len(f_indices) < train_goal_len :
                    train.extend(f_indices)
                else :
                    test.extend(f_indices)
    else :
        random.shuffle(segment_range)
        if preserve_labels :
            for i in segment_range:
                l = str(labels[i])
                if label_goal[l] > 0 :
                    train.append(i)
                    label_goal[l] = label_goal[l] - 1
                else :
                    test.append(i)
        else :
            train = segment_range[0:train_goal_len]
            test = segment_range[train_goal_len:]

    return TrainTestPartition(train,test,state)
        
def generate_partitions(config, segment_info, cv_iterations=0, seed=None) :
    partition = PartitionData(segment_info, 
                              config.learning_split, 
                              avoid_overlap=True, 
                              segment_size=config.segment_size, 
                              file_based=True if (config.data_type == "BirdSoundsSegments" or 
                                                  config.data_type == "KitchenMocapSegments") \
                              else False,
                              preserve_labels=True,
                              seed=seed)

    all_labels = [segment_info[i].max_label() for i in partition.train]
    if cv_iterations > 0 :
        skf = StratifiedKFold(all_labels, n_folds=cv_iterations)

        cross_validation = [TrainTestPartition([partition.train[i] for i in train_index],
                                               [partition.train[i] for i in test_index], None) \
                            for train_index, test_index in skf]
    else :
        cross_validation = None
    learning_trials = [PartitionData(segment_info, 
                                     config.learning_split, 
                                     avoid_overlap=True, 
                                     segment_size=config.segment_size, 
                                     file_based=True if (config.data_type == "BirdSoundsSegments" or 
                                                         config.data_type == "KitchenMocapSegments") \
                                     else False,
                                     preserve_labels=True,
                                     seed=None) for i in range(config.learning_iterations)]
    return TrainTestPartitions(config, segment_info, cross_validation, learning_trials)


if __name__ == "__main__" :
    parser = argparse.ArgumentParser("Tool to generate train / test splits for testing and cross validation")
    parser.add_argument("--segments", "-i")
    parser.add_argument("--outfile", "-o")
    parser.add_argument("--learning-split", "-s", type=float)
    parser.add_argument("--learning-iterations", "-I", type=int)
    parser.add_argument("--cv-iterations", "-v", default=5, type=int)
    parser.add_argument("--seed", "-S")
    args = parser.parse_args(sys.argv[1:])

    segments_json = load_data(args.segments, 'segments', None, None, sys.argv[0] + " : ")
    if segments_json == None :
        print "Could not load Segments from %s" % (args.segments,)
        sys.exit(1)
    segment_info = [SegmentInfo.fromJSONDict(s) for s in segments_json['segments']]
    config = Configuration.fromJSONDict(segments_json['config'])
    if args.learning_split != None :
        config.learning_split = args.learning_split
    if args.learning_iterations != None : 
        config.learning_iterations = args.learning_iterations
    
    output = generate_partitions(config, segment_info, cv_iterations=args.cv_iterations, seed=args.seed)
    
    if args.outfile == None :
        args.outfile = TrainTestPartitions.get_partition_filename(config)

    print "Writing %s" % (args.outfile,)
    save_data(args.outfile, output.toJSONDict())
    
