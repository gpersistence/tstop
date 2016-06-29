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
from scipy.fftpack import dct
from numpy import array, ndarray

from Datatypes.Configuration import get_filename
from Datatypes.Segments import Segments, Segment
from Datatypes.JSONObject import load_data, save_data

def normalize(array) :
    scale = 1.0 / (sum(array) / len(array))
    return [a * scale for a in array]

class NormalizePost(Segments):
    @staticmethod
    def get_input_type():
        return "Segments"

    @staticmethod
    def get_output_type():
        return "Segments"

    def __init__(self, config, segments):
        super(self.__class__, self).__init__(config)
        transformed = []
        for segment in segments :
            transform = [normalize(w) for w in segment.windows]
            transformed.append(Segment(windows=transform,
                                       segment_start=segment.segment_start,
                                       segment_size=segment.segment_size,
                                       window_stride=segment.window_stride,
                                       window_size=len(transform),
                                       labels=segment.labels,
                                       filename=segment.filename,
                                       data_index=segment.data_index,
                                       label_index=segment.label_index,
                                       learning=segment.learning))
        self.segments = transformed

    @staticmethod
    def get_segment_filename(config, gz=True):
        fields = ['data_file', 'data_index', 'segment_size',
                  'segment_stride', 'window_size', 'window_stride']
        return get_filename(config, fields, 'NormalizePost', gz)

def main(argv):
    parser = argparse.ArgumentParser(description='Post Processing tool for Segment Data')
    parser.add_argument('-i', '--infile')
    parser.add_argument('-o', '--outfile')
    args = vars(parser.parse_args(argv[1:]))
    segments_json = load_data(args['infile'], 'segments', None, None, "NormalizePost: ")
    if segments_json == None :
        print "Could not load --infile : %s" % (args['infile'],)
        exit()
    segments = Segments.fromJSONDict(segments_json)
    segments.config.post_process="NormalizePost"
    post_processed = NormalizePost(segments.config, segments.segments)
    if args['outfile'] == None:
        outfile = NormalizePost.get_segment_filename(segments.config)
    else :
        outfile = args['outfile']
    print "Writing %s" % outfile
    post_processed.config.status = "NormalizePost"
    save_data(outfile, post_processed.toJSONDict())

if __name__=="__main__" :
    main(sys.argv)
