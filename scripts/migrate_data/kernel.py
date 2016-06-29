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
from persistence.Datatypes.Kernel import Kernel
from persistence.Datatypes.Configuration import Configuration
from persistence.Datatypes.Segments import SegmentInfo

if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description="Utility to add SegmentInfo data to a Kernel file")
    parser.add_argument("--infile")
    parser.add_argument("--outfile")
    args = parser.parse_args(sys.argv[1:])
    in_json = load_data(args.infile, "kernel", None, None, sys.argv[0] + " : ")
    k = Kernel.fromJSONDict(in_json)
    module = importlib.import_module('persistence.' + k.config.data_type)
    module_class = getattr(module, k.config.data_type)
    segment_filename = module_class.get_segment_filename(k.config)
    seg_json = load_data(segment_filename, "segments", None, None, sys.argv[0] + " : ")
    k.segment_info = [SegmentInfo.fromJSONDict(segment) for segment in seg_json['segments']]

    print "Writing %s" % (args.outfile,)
    save_data(args.outfile, k.toJSONDict())
