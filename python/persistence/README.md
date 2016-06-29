# Tool Suite for Exploring Learning Techniques on Time Varying Data

This directory contains a suite of tools used to explore methods of
machine learning using time varying data, including Topological
Persistence Diagrams and similarity and distance measures on them.

## Data Types

The definitions for all data types used in the tstop project are
contained in the directory python/persistence/Datatypes. The structure
of the data types is organized around the format used to serialize
them, JavaScript Object Notation (JSON), and all of the elements can
be accessed by name, or as if it were a python dict object. When
creating a new data type, the object should inherit from `JSONObject`,
define the fields field as a list of all the accessible data fields in
the object, and override `__init__` and `fromJSONDict`. Overriding
`toJSONDict` should only be necessary for complex object types where the
fields are neither basic python types nor objects that inherit from
`JSONObject`. Objects that are intended to be used as a file format
should also include a static method that returns a generated filename
corresponding to a supplied Configuration object. These methods
normally call the get_filename function in
`tstop/python/persistence/Datatypes/Configuration.py`.

### JSONObject

Base Class for serialization and deserialization of child
classes. Allows subclasses to be accessed as dictionary objects in
python. The `load_data` function takes a (optionally gziped) JSON file
which can then be fed to a child class's `fromJSONDict` function for
initialization. The `save_data` function takes the output of a child
class's `toJSONDict` function and saves it into a (optionally gzipped)
JSON File.

### Configuration

Class for specifying and recording configuration parameters used for evaluation of learning techniques.

In the simplest form, a configuration object is a dictionary with the following fields:

* `segment_stride` : number of data samples seperating the starts of consecutive segments
* `segment_size` : number of consecutive data samples to include when generating a segment
* `window_size` : number of consecutive data samples to include when generating a window
* `window_stride` : number of data samples seperating the starts of consecutive windows
* `data_type` : class name to use for parsing of input data into segments
* `data_file` : file or list of files defining a dataset being considered
* `data_index` : index or list of indices to use from each data sample for generating segments
* `label_index` : index in data sample to use as a classification label (not used in all data formats)
* `out_directory` : directory name to use for generating output files
* `max_simplices` : argument to specify the maximum number of simplices to consider when generating Persistence Diagrams
* `persistence_epsilon` : alternative to `max_simplices` to use for generating Persistence Diagrams
* `kernel_scale` : configuration parameter for generating a Persistence Kernel or Scale Space Similarity
* `kernel_gamma` : configuration parameter for RBF Kernels
* `invariant_epsilon` : configuration parameter for Chaotic Invariant Features of Chaos Post processing
* `learning_split` : ratio of training data to testing data for generating train / test partitions
* `learning_iterations` : number of train / test partitions to generate
* `learning_C` : configuration parameter for generating SMV classifiers for Kernel or Feature Learning
* `persistence_degree` : degree of points in a Persistence Diagram to consider
* `post_process` : class name to use for post processing of segment data
* `post_process_arg` : generic argument for post processing class
* `status` : last processing step performed on this data

The fields from `segment_stride` to `label_index` are used for crafting an initial configuration (or as command line arguments to the `tstop/persistence/Datatypes/Segments.py`), and command line arguments to processing steps can be used to fill in or orverride the other configuration parameters.

An example configuration file corresponding to [the tutorial](tutorial.md)
```json
{
"data_file": "/mnt/data2/topo_ts/data/PAMAP/subject101.dat", 
"window_size": 20, 
"data_type": "PAMAPSegments", 
"data_index": [2, 4, 5, 6, 21, 22, 23], 
"window_stride": 1,
"segment_stride": 500, 
"label_index": 1, 
"out_directory": "/mnt/data2/topo_ts/2015-11-19-PAMAP", 
"segment_size": 1000
}
```

### Segments

Base Class for holding time series data. The field `config` holds the
configuration data used to create this Segments file, and the list
segments holds the segmented data. The Segment class holds a single
segment of data, along with associated metadata. The data is stored as
an array of windows, each window holding the floating point time
series. For non windowed data, this will be stored as a single window
the same size as the segment. The labels field is a dictionary with
the possible labels as keys and the number of samples in this segment
corresponding to each label as the values. The learning field is null
(JSON) or None (Python) for datasets without a preset train / test
split, otherwise it is the string 'test' or 'train' depending on
whether this Segment is in the test dataset or train dataset
respectively.

### Kernel

Base class for holding kernels. The field `config` holds the
configuration data used to generate this Kernel file. The
`kernel_matrix` field holds a square matrix relating the similarity of
each segment in the dataset to each other segment. This matrix needs
to be positive semidefinite for learning to work properly. The field
labels contains the label used for each segment in the dataset, and
the field learning encodes the test / train split among segments in
much the same way as in the Segments class.

### Distances

Base class for distance measures. The field `config` holds the
configuration data used to generate this Distances file. The `distances`
field holds a matrix of Distance objects, corresponding to the
measures relating the distance of each segment in the dataset to each
other segment. Each Distance object holds an optional `min`, `mean`, `max`,
and `std` field to hold the measured distance and statistical
information. The field labels contains the label used for each segment
in the dataset, and the field learning encodes the test / train split
among segments in much the same way as in the Segments class.

### PersistenceDiagrams

Class for holding persistence diagrams generated from Segment
data. The field `config` holds the configuration data used to generate
this PersistenceDiagrams file. The field `diagrams` holds each
PersistenceDiagram generated from each Segment in the source file. In
each individual PersistenceDiagram, you have the array of points, with
are 3 element tuples consisting of a birth, death, and dimension, The
field labels contains the label used for each segment in the dataset,
and the field learning encodes the test / train split among segments
in much the same way as in the Segments class.

### Learning

Class for holding results of machine learning tests generated from
various methods of classification. The field `config` holds the
configuration data used to generate this Learning file. The results
field holds a list of LearningResult structures that hold results from
a single train and test split. Each LearningResult holds an array of
the training labels in `train_labels`, testing labels (i.e. truth) in
`test_labels`, labels generated from classification in `test_results`, and
kernel weights from multiple kernel learning in `mkl_weights`.

### TrainTestPartitions

Class for recording train / test partitions of data used for
evaluation of learning results as well as cross validation. The field
`config` holds the configuration data used to generate this
TrainTestPartitions file. The field `cross_validation` holds train /
test partitions on a subset of the full dataset to use for cross
validation of parameters used to create Kernel or Distances objects
and scaling values used for Learning.

## Segment Types

### BirdSoundsSegments

mfcc files generated from the audio files at [XenoCanto](http://www.xeno-canto.org).
Each file is generated from a recording for a single bird.

### CMUMocapSegments

From the [CMU Graphics Lab Motion Capture Database](http://mocap.cs.cmu.edu/)
The file format is an list of records, one
for each datapoint.  Each record is an integer followed by a series of
lines of the format : label float+

### ActivitySegments

Activity Recognition from a Single Chest-Mounted Accelerometer Updated
Nov, 2013 , P. Casale, `plcasale@ieee.org`

Each line in a file
contains the following information sequential number, x acceleration,
y acceleration, z acceleration, label

### EEGEyeSegments

Segments generated from the EEG data at
http://suendermann.com/corpus/EEG_Eyes.arff.gz from the paper 
[Comparison of EEG Devices for Eye State Classification](http://suendermann.com/su/pdf/aihls2014.pdf) 
Each line after the
line @data contains a list of 14 floating point values from EEG
sensors and one 0,1 value corresponding if the eyes are open (0) or
closed (1)

### KitchenMocapSegments

Segment generated from motion capture files from the 
[Quality of Life Grand Challenge Data Collection](http://kitchen.cs.cmu.edu/) 
files are in directories corresponding to the label of the data in the file

### PAMAPSegments

[Physical Activity Monitoring Data Set](https://archive.ics.uci.edu/ml/datasets/PAMAP2+Physical+Activity+Monitoring)
Labels are derived from the second value in each line of the file,
followed by a heart rate and readings from three inertial measurement
units (that sporadically have dropped values).

### UCRSegments

From the [UCR Dataset](http://www.cs.ucr.edu/~eamonn/time_series_data/)
Each line corresponds to a single segment, and the train / test split
is baked into the data by supplying seperate files for train and test

### WalkingSegments

[User Identification From Walking Activity](https://archive.ics.uci.edu/ml/datasets/User+Identification+From+Walking+Activity)
Each data file corresponds to a separate individual, so the file name
is used as our classification label.

## Post Processing Tools

### ChaosPost

Uses the concepts from "Chaotic Invariants for Human Action
Recognition" to generate a time delay, 'tau', and window size to
structure data for generation of Persistence Diagrams.

```sh
$ python -m persistence.ChaosPost --help
usage: ChaosPost.py [-h] [-i INFILE] [-o OUTFILE] [-p POOL]

Post Processing tool for Segment Data

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
  -o OUTFILE, --outfile OUTFILE
  -p POOL, --pool POOL
```

### DCTPost

Performs a Discrete Cosine Transform on each window of each segment

```sh
$ python -m persistence.DCTPost --help
usage: DCTPost.py [-h] [-i INFILE] [-o OUTFILE]

Post Processing tool for Segment Data

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
  -o OUTFILE, --outfile OUTFILE
```

### NormalizePost

Normalizes each window of each segment.

```sh
$ python -m persistence.NormalizePost --help
usage: NormalizePost.py [-h] [-i INFILE] [-o OUTFILE]

Post Processing tool for Segment Data

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
  -o OUTFILE, --outfile OUTFILE
```

### PCAPost

Performs Principal Component Analysis on each windowed segment 

```sh
$ python -m persistence.PCAPost --help
usage: PCAPost.py [-h] [-i INFILE] [-o OUTFILE] [-p POST_PROCESS_ARG]

Post Processing tool for Segment Data

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
  -o OUTFILE, --outfile OUTFILE
  -p POST_PROCESS_ARG, --post-process-arg POST_PROCESS_ARG
                        Variance Threshold, a float between 0 and 1
```

## Distance Measures

### BottleneckDistances

Measures the Bottleneck Distance between all pairs of Persistence
Diagrams

```sh
$ python -m persistence.BottleneckDistances --help
usage: BottleneckDistances.py [-h] [-a INFILE_A] [-b INFILE_B] [-o OUTFILE] [-d DEGREE] [-p POOL]

Tool to evaluate the Bottleneck Distances between two Arrays of Persistence Diagrams

optional arguments:
  -h, --help            show this help message and exit
  -a INFILE_A, --infile-a INFILE_A
                        JSON Persistence Diagram file of the first set of Persistence Diagrams
  -b INFILE_B, --infile-b INFILE_B
                        JSON Persistence Diagram file of the second set of Persistence Diagrams
  -o OUTFILE, --outfile OUTFILE
                        JSON Output File
  -d DEGREE, --degree DEGREE
                        Persistence Degree to consider
  -p POOL, --pool POOL  Threads of computation to use
```

### DTWDistances

Measures the Dynamic Time Warping distance between all pairs of
Segments

```sh
$ python -m persistence.DTWDistances --help
usage: DTWDistances.py [-h] [-i INFILE] [-o OUTFILE] [-p POOL]

Tool to generate Dynamic Time Warping distances based on segment data

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        Input JSON Segment File
  -o OUTFILE, --outfile OUTFILE
                        Output JSON Distances File
  -p POOL, --pool POOL  Threads of computation to use
```

### EuclideanDistances

Measures the Euclidean distance between all pairs of Segments

```sh
$ python -m persistence.EuclideanDistances --help
usage: EuclideanDistances.py [-h] [-i INFILE] [-o OUTFILE] [-p POOL]

Tool to classify data based on 1-NN of segment data

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        Input JSON Segment File
  -o OUTFILE, --outfile OUTFILE
                        Output JSON Learning File
  -p POOL, --pool POOL  Threads of computation to use
```

### LandscapeDistances

Measures the Landscape distance between all pairs of persistence
Diagrams

```sh
$ python -m persistence.LandscapeDistances --help
usage: LandscapeDistances.py [-h] [-a INFILE_A] [-b INFILE_B] [-o OUTFILE]
                             [-d DEGREE] [-p POOL]

Tool to evaluate the Landscape Distances between two Arrays of Persistence
Diagrams

optional arguments:
  -h, --help            show this help message and exit
  -a INFILE_A, --infile-a INFILE_A
                        JSON Persistence Diagram file of the first set of
                        Persistence Diagrams
  -b INFILE_B, --infile-b INFILE_B
                        JSON Persistence Diagram file of the second set of
                        Persistence Diagrams
  -o OUTFILE, --outfile OUTFILE
                        JSON Output File
  -d DEGREE, --degree DEGREE
                        Persistence Degree to consider
  -p POOL, --pool POOL  Threads of computation to use
```

### ScaleSpaceSimilarity

Measures the Scale Space Similarity between all pairs of Persistence
Diagrams (same measure as Persistence Kernel)

```sh
$ python -m persistence.ScaleSpaceSimilarity --help
usage: ScaleSpaceSimilarity.py [-h] [-i INFILE] [-o OUTFILE] [-k KERNEL_SCALE]
                               [-d PERSISTENCE_DEGREE]
                               [--kernel-file KERNEL_FILE] [-p POOL]

Tool to generate the scale space similarity between all pairs of 
persistence diagrams

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        Input JSON Persistence Diagram File
  -o OUTFILE, --outfile OUTFILE
                        Output JSON Learning File
  -k KERNEL_SCALE, --kernel-scale KERNEL_SCALE
                        Kernel Scale to use for Scale Space Similarity
  -d PERSISTENCE_DEGREE, --persistence-degree PERSISTENCE_DEGREE
                        Persistence degree to consider when computing Scale
                        Space Similarity
  --kernel-file KERNEL_FILE
                        translate from PersistenceKernel instead of redoing
                        calculation
  -p POOL, --pool POOL  Threads of computation to use
```

### WassersteinDistances

Measures the Wasserstein Distance between all pairs of Persistence
Diagrams

```sh
$ python -m persistence.WassersteinDistances --help
usage: WassersteinDistances.py [-h] [-a INFILE_A] [-b INFILE_B] [-o OUTFILE]
                               [-d DEGREE] [-p POOL]

Tool to evaluate the Wasserstein Distances between two Arrays of Persistence
Diagrams

optional arguments:
  -h, --help            show this help message and exit
  -a INFILE_A, --infile-a INFILE_A
                        JSON Persistence Diagram file of the first set of
                        Persistence Diagrams
  -b INFILE_B, --infile-b INFILE_B
                        JSON Persistence Diagram file of the second set of
                        Persistence Diagrams
  -o OUTFILE, --outfile OUTFILE
                        JSON Output File
  -d DEGREE, --degree DEGREE
                        Persistence Degree to consider
  -p POOL, --pool POOL  Threads of computation to use
```

## Persistence Diagram Creation

### PersistenceGenerator
 
Computes the Persistence Diagram of a windowed Segment

```sh
$ python -m persistence.PersistenceGenerator --help
usage: PersistenceGenerator.py [-h] [-i INFILE] [-o OUTFILE]
                               [-m MAX_SIMPLICES] [-e EPSILON] [-p POOL]

Tool to generate Persistence Diagrams from segmented data

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        Input JSON Segment Data file
  -o OUTFILE, --outfile OUTFILE
                        Output JSON Persistence Diagram file
  -m MAX_SIMPLICES, --max-simplices MAX_SIMPLICES
  -e EPSILON, --epsilon EPSILON
  -p POOL, --pool POOL  Threads of computation to use
```

## Learning Kernel Creation Tools

### AverageKernel

Averages all the input Kernels (optionally with weights) to create a
single output Kernel

```sh
$ python -m persistence.AverageKernel --help
usage: AverageKernel.py [-h] [--infile INFILE [INFILE ...]]
                        [--outfile OUTFILE] [--ratio RATIO] [--pool POOL]

Tool to take multiple Kernels and average them

optional arguments:
  -h, --help            show this help message and exit
  --infile INFILE [INFILE ...], -i INFILE [INFILE ...]
  --outfile OUTFILE, -o OUTFILE
  --ratio RATIO, -r RATIO
  --pool POOL, -p POOL
```

### PersistenceKernel

Computes the Scale Space similarity between all pairs of Persistence
Diagrams to generate an output Kernel
```sh
$ python -m persistence.PersistenceKernel --help
usage: PersistenceKernel.py [-h] [-i INFILE] [-o OUTFILE] [-p POOL]
                            [-k KERNEL_SCALE] [-d PERSISTENCE_DEGREE]

Tool to generate a similarity kernel from persistence data

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        Input JSON Persistence Diagram file
  -o OUTFILE, --outfile OUTFILE
                        Output JSON Kernel Similarity Matrix file
  -p POOL, --pool POOL  Threads of computation to use
  -k KERNEL_SCALE, --kernel-scale KERNEL_SCALE
  -d PERSISTENCE_DEGREE, --persistence-degree PERSISTENCE_DEGREE
                        Filter persistence to entries of this degree
```
### RBFKernel

Computes the Radial Basis Function between all pairs of Segments to
generate an output Kernel
```sh
$ python -m persistence.RBFKernel --help
usage: RBFKernel.py [-h] [-i INFILE] [-o OUTFILE] [-g KERNEL_GAMMA] [-p POOL]

Tool to generate a radial basis kernel from segmented data

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        Input JSON Segment file
  -o OUTFILE, --outfile OUTFILE
                        Output JSON RBF Kernel Matrix file
  -g KERNEL_GAMMA, --kernel-gamma KERNEL_GAMMA
  -p POOL, --pool POOL  Threads of computation to use
```

## Feature Generators

### ChaoticInvariantFeatures

Computes the Chaotic Invariant Feature for all dimensions of each
input Segment

```sh
$ python -m persistence.ChaoticInvariantFeatures --help
usage: ChaoticInvariantFeatures.py [-h] [-i INFILE] [-o OUTFILE] [-e EPSILON]
                                   [-p POOL]

Tool to classify data based on chaotic invariants of segment data

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        Input JSON Segment File
  -o OUTFILE, --outfile OUTFILE
                        Output JSON Learning File
  -e EPSILON, --epsilon EPSILON
                        epsilon value used for generation of chaotic
                        invariants
  -p POOL, --pool POOL  Threads of computation to use
```

## Classification Tools

### DistanceLearning

Uses a Distance file to find a first nearest neighbor match
```sh
$ python -m persistence.DistanceLearning --help
usage: DistanceLearning.py [-h] [-i INFILE] [-o OUTFILE] [-m]
                           [-t TRAIN_TEST_PARTITIONS] [-p POOL]

Tool to classify data based on 1-NN matching based on the supplied 
distance matrix

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        Input JSON Distance File
  -o OUTFILE, --outfile OUTFILE
                        Output JSON Learning File
  -m, --max-mode        Use maximum "Distance" instead of minimum (for
                        Similarity measures"
  -t TRAIN_TEST_PARTITIONS, --train-test-partitions TRAIN_TEST_PARTITIONS
                        Precomputed train / test partitions
  -p POOL, --pool POOL
```
### FeatureLearning

Uses a Feature file to classify using a Simple Vector Machine
```sh
$ python -m persistence.FeatureLearning --help
usage: FeatureLearning.py [-h] [-i INFILE] [-o OUTFILE] [-p POOL]
                          [-c LEARNING_C] [--timeout TIMEOUT]
                          [-t TRAIN_TEST_PARTITIONS]

Tool to perform learning on pregenerated features

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        Input JSON Similarity Feature file
  -o OUTFILE, --outfile OUTFILE
                        Output JSON Learning file
  -p POOL, --pool POOL  Threads of computation to use
  -c LEARNING_C, --learning-C LEARNING_C
                        C value for SVM. Specify a range for 1-dimensional
                        cross-validation
  --timeout TIMEOUT
  -t TRAIN_TEST_PARTITIONS, --train-test-partitions TRAIN_TEST_PARTITIONS
                        Precomputed train / test partitions
```
### KernelLearning

Uses a Kernel file to classify using an sklearn Simple Vector Machine
```sh
$ python -m persistence.KernelLearning --help
usage: KernelLearning.py [-h] [-i INFILE] [-o OUTFILE] [-p POOL]
                         [-c LEARNING_C] [-t TRAIN_TEST_PARTITIONS]

Tool to perform learning from a pregenerated similarity kernel

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        Input JSON Similarity Kernel file
  -o OUTFILE, --outfile OUTFILE
                        Output JSON Learning file
  -p POOL, --pool POOL  Threads of computation to use
  -c LEARNING_C, --learning-C LEARNING_C
                        C value for SVM. Specify a range for 1-dimensional
                        cross-validation
  -t TRAIN_TEST_PARTITIONS, --train-test-partitions TRAIN_TEST_PARTITIONS
                        Precomputed train / test partitions
```
### MultipleKernelLearning

Uses a list of Kernel files as input into a modshogun Simple Vector
Machine
```sh
$ python -m persistence.MultipleKernelLearning --help
usage: MultipleKernelLearning.py [-h] [-i INFILE [INFILE ...]] [-o OUTFILE]
                                 [-p POOL] [-c LEARNING_C]
                                 [-t TRAIN_TEST_PARTITIONS]

Tool to classify data using multiple similarity kernels

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE [INFILE ...], --infile INFILE [INFILE ...]
                        Input JSON Similarity Kernel file
  -o OUTFILE, --outfile OUTFILE
                        Output JSON Learning file
  -p POOL, --pool POOL  Threads of computation to use
  -c LEARNING_C, --learning-C LEARNING_C
                        C value for MKL. Specify a range for 1-dimensional
                        cross-validation
  -t TRAIN_TEST_PARTITIONS, --train-test-partitions TRAIN_TEST_PARTITIONS
                        Precomputed partitions for cross validation and
                        evalutaion
```

## Special Tools

### CrossValidation

Using a specified first module and learning module, performs cross
validation to approximate input values for best learning
classification results.

For example, can be used to generate the scale value for a Persistence
Kernel or a gamma value for a RBF Kernel as well as their
corresponding 'C' scale value for the SVM in Kernel Learning

```sh
$ python -m persistence.CrossValidation -h
usage: CrossValidation.py [-h] [--kernel-module KERNEL_MODULE]
                          [--kernel-arg KERNEL_ARG]
                          [--distances-module DISTANCES_MODULE]
                          [--distances-arg DISTANCES_ARG]
                          [--learning-module LEARNING_MODULE]
                          [--learning-arg LEARNING_ARG] [--infile INFILE]
                          [--outfile OUTFILE] [--partitions PARTITIONS]
                          [--pool POOL] [--timeout TIMEOUT]

General purpose cross validation tool

optional arguments:
  -h, --help            show this help message and exit
  --kernel-module KERNEL_MODULE
  --kernel-arg KERNEL_ARG
  --distances-module DISTANCES_MODULE
  --distances-arg DISTANCES_ARG
  --learning-module LEARNING_MODULE
  --learning-arg LEARNING_ARG
  --infile INFILE
  --outfile OUTFILE
  --partitions PARTITIONS
  --pool POOL
  --timeout TIMEOUT
```

### PartitionData

Generates a list of train and test splits to use for evaluation of
learning on a dataset from a Segment file. Also generates n-fold cross
validation splits from one training set. Can be used in
CrossValidation and Learning to have a consistent set of train test
splits over different configurations.

```sh
$ python -m persistence.PartitionData --help
usage: Tool to generate train / test splits for testing and cross validation
       [-h] [--segments SEGMENTS] [--outfile OUTFILE]
       [--learning-split LEARNING_SPLIT]
       [--learning-iterations LEARNING_ITERATIONS]
       [--cv-iterations CV_ITERATIONS] [--seed SEED]

optional arguments:
  -h, --help            show this help message and exit
  --segments SEGMENTS, -i SEGMENTS
  --outfile OUTFILE, -o OUTFILE
  --learning-split LEARNING_SPLIT, -s LEARNING_SPLIT
  --learning-iterations LEARNING_ITERATIONS, -I LEARNING_ITERATIONS
  --cv-iterations CV_ITERATIONS, -v CV_ITERATIONS
  --seed SEED, -S SEED
```

