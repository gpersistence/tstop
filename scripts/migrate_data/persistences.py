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
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams, PersistenceDiagram
from persistence.Datatypes.Configuration import Configuration
from persistence.Datatypes.Segments import SegmentInfo

if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description="Utility to add SegmentInfo data to a PersistenceDiagrams file")
    parser.add_argument("--infile")
    parser.add_argument("--outfile")
    args = parser.parse_args(sys.argv[1:])
    in_json = load_data(args.infile, "persistence diagrams", None, None, sys.argv[0] + " : ")
    pd = PersistenceDiagrams.fromJSONDict(in_json)
    module = importlib.import_module('persistence.' + pd.config.data_type)
    module_class = getattr(module, pd.config.data_type)
    segment_filename = module_class.get_segment_filename(pd.config)
    seg_json = load_data(segment_filename, "segments", None, None, sys.argv[0] + " : ")
    
    for (diagram, segment) in zip(pd.diagrams, seg_json['segments']) :
        diagram.segment_info = SegmentInfo.fromJSONDict(segment)

    print "Writing %s" % (args.outfile,)
    save_data(args.outfile, pd.toJSONDict())
