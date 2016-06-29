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
import gzip
import os
import json
import traceback 

# Base class for serialization / deserialization from dictionary suitable for encoding in JSON
#
# Author: Shelby Davis, Black River Systems davis@brsc.com shelby.davis.ctr@rl.af.mil


class JSONObject(object) :
    fields = []

    def __init__(self) :
        pass
        
    # placeholder, subclasses need to override this
    @classmethod
    def fromJSONDict(cls, json):
        return cls()
        
    # Handles the simple cases where fields are easily JSON serializable (int, float, str, list, dict),
    # subclasses of JSONDict, or lists of objects that are subclasses of JSONDict
    # override if the subclass has special fields that don't fit in this scheme
    def toJSONDict(self):
        item_dict = dict()
        for key in self.__class__.fields :
            item = self.__getitem__(key)
            if issubclass(type(item), JSONObject) :
                item = item.toJSONDict()
            elif isinstance(item, list) :
                # handle matrices
                if len(item) > 0 and isinstance(item[0], list) and issubclass(type(item[0][0]), JSONObject) :
                    item = [[i.toJSONDict() for i in row] for row in item]
                else :
                    item = [i if not issubclass(type(i), JSONObject) else i.toJSONDict() for i in item]
            elif item == None:
                continue
            item_dict[key] = item
        return item_dict

    def __eq__(self, other) :
        return self.__class__ == other.__class__ and \
            reduce((lambda x, (y0,y1): x and y0 == y1), zip([self[f] for f in self.__class__.fields],
                                                            [other[f] for f in self.__class__.fields]), True)

    def __contains__ (self, item):
        if item in self.__class__.fields:
            return True
        else :
            return False

    def __getitem__ (self, key):
        if isinstance(key, str) :
            if self.__contains__(key) :
                return getattr(self, key)
            else :
                raise KeyError("%s is not a field in %s" % (key, self.__class__.__name__))
        else :
            raise TypeError("%s key must be a string" % (self.__class__.__name__,))

    def __setitem__ (self, key, value):
        if isinstance(key, str) :
            if self.__contains__(key) :
                return setattr(self, key, value)
            else :
                raise KeyError("%s is not a field in %s" % (key, self.__class__.__name__))
        else :
            raise TypeError("%s key must be a string" % (self.__class__.__name__,))

def verify_config(a, b, fields) :
    return reduce((lambda x, y: x and (not y in a and not y in b) or (y in a and y in b and a[y] == b[y])), fields, True)

def load_data(data_file, label, config, config_keys, prefix) :
    # If we haven't been told to reevaluate all the data and the file 
    # exists, load it in
    load_file = (config == None or not config['reevaluate'][label])
    data = None
    if load_file :
        if not os.path.isfile(data_file):
            print "%sCould not find file %s" % ('' if prefix == None else prefix, data_file)
            return None
        if prefix != None :
            print "%sLoading %s from %s" % (prefix, label, data_file)
            
        try :
            if data_file.endswith(".gz") :
                with gzip.GzipFile(data_file, 'r') as data_fd :
                    json_data = json.load(data_fd)
            else :
                with open(data_file, 'r') as data_fd :
                    json_data = json.load(data_fd)
            if config == None or (verify_config(json_data['config'], config, config_keys)) :
                data = json_data
        except :
            traceback.print_exc()
    return data

def save_data(data_file, data) :
    try :
        if data_file.endswith(".gz") :
            with gzip.GzipFile(data_file, 'w') as data_fd :
                json.dump(data, data_fd, indent=0)
        else :
            with open(data_file, 'w') as data_fd :
                json.dump(data, data_fd, indent=0)
    except IOError:
        print "Could not write data file %s" % data_file
        raise

def cond_get(json_dict, key) :
    if key in json_dict :
        return json_dict[key]
    else :
        return None

def cond_get_list(json_dict, key) :
    if key in json_dict :
        if isinstance(json_dict[key], list) :
            return json_dict[key]
        else :
            return [json_dict[key]]
    else :
        return [None]

def cond_get_obj_list(json_dict, key, type) :
    if key in json_dict :
        if isinstance(json_dict[key], list) :
            return [type.fromJSONDict(i) for i in json_dict[key]]
        else :
            return [type.fromJSONDict(json_dict[key])]
    else :
        return None
