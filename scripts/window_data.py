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


"""
Script to take a segmented data set where segment_size ==
window_size and extract a single dimension from the data and write it
to a windowed data file
"""

import os
import sys
import argparse
import importlib
from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.Segments import Segments, Segment


parser = argparse.ArgumentParser(description="Creates windowed segments of a single dimension for a multidimensioned dataset")
parser.add_argument("-i","--infile")
parser.add_argument("-d","--data-index", default=0, type=int)
parser.add_argument("-w","--window-size", type=int)
parser.add_argument("-W","--window-stride", default=1, type=int)
args = parser.parse_args(sys.argv[1:])
segments = Segments.fromJSONDict(load_data(args.infile, "segments", None, None, sys.argv[0] + ": "))
orig_window_size = segments.config.window_size
segments.config.window_size = args.window_size
segments.config.window_stride = args.window_stride
dimensions = len(segments.segments[0].data_index)
segments.config.data_index = segments.segments[0].data_index[args.data_index]
for segment in segments.segments :
    windows = [[segment.windows[0][(i + j) * dimensions + args.data_index] for j in range(args.window_size)]
               for i in range(0, orig_window_size, args.window_stride) if ((i + args.window_size - 1) * dimensions + args.data_index) < len(segment.windows[0])]
    segment.data_index = segment.data_index[args.data_index]
    segment.window_size = args.window_stride
    segment.windows = windows
segment_module = importlib.import_module("persistence." + segments.config.data_type)
segment_class = getattr(segment_module, segments.config.data_type)
segment_filename = segment_class.get_segment_filename(segments.config)
print "Writing " + segment_filename
save_data(segment_filename, segments.toJSONDict())
