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
import sys
import traceback
import numpy
import json
from persistence.Datatypes.JSONObject import JSONObject, load_data, save_data, cond_get, cond_get_list
# Configuration.py implements a container to encapsulate a single
# configuration of segmentation-persistence-kernel-learning processing

class Configuration(JSONObject):
    fields = ['max_simplices',
              'persistence_epsilon',
              'segment_filename',
              'segment_stride',
              'segment_size',
              'window_size',
              'window_stride',
              'kernel_scale',
              'kernel_gamma',
              'invariant_epsilon',
              'data_file',
              'data_index',
              'label_index',
              'out_directory',
              'threads',
              'learning_split',
              'learning_iterations',
              'cv_iterations',
              'learning_C',
              'persistence_degree',
              'reevaluate',
              'data_type',
              'post_process',
              'post_process_arg',
              'stop_after',
              'status']
    def __init__ (self, 
                  max_simplices       = 1000000, 
                  persistence_epsilon = None, 
                  segment_stride      = None, 
                  segment_size        = None,
                  window_size         = None, 
                  window_stride       = 1, 
                  kernel_scale        = None, 
                  kernel_gamma        = None, 
                  invariant_epsilon   = None, 
                  data_file           = None, 
                  data_index          = None,
                  label_index         = None, 
                  out_directory       = 'out', 
                  threads             = None, 
                  learning_split      = None,
                  learning_iterations = None, 
                  learning_C          = None, 
                  cv_iterations       = None,
                  persistence_degree  = 1, 
                  reevaluate          = False, 
                  data_type           = None,
                  post_process        = None, 
                  post_process_arg    = None, 
                  stop_after          = 'learning', 
                  status              = None):
        self.max_simplices = max_simplices
        self.persistence_epsilon = persistence_epsilon
        self.invariant_epsilon = invariant_epsilon
        self.segment_stride = segment_stride
        self.segment_size = segment_size
        self.segment_filename = None
        self.window_size = window_size
        self.window_stride = window_stride
        self.kernel_scale = kernel_scale
        self.kernel_gamma = kernel_gamma
        self.data_file = data_file
        self.data_index = data_index
        self.label_index = label_index
        self.out_directory = out_directory
        self.threads = threads
        self.learning_split = learning_split
        self.learning_iterations = learning_iterations
        self.cv_iterations = cv_iterations
        self.learning_C = learning_C
        self.persistence_degree = persistence_degree
        if (isinstance(reevaluate, dict)) :
            self.reevaluate = reevaluate
        else :
            self.reevaluate = dict([('segments', reevaluate),
                                    ('post_process', reevaluate),
                                    ('persistence_diagrams', reevaluate),
                                    ('distances', reevaluate),
                                    ('kernel', reevaluate),
                                    ('learning', reevaluate)])
        self.data_type = data_type
        if (post_process == None or post_process == '' or post_process == 'None') :
            self.post_process = None
        else :
            self.post_process = post_process 
        self.post_process_arg = post_process_arg
        self.stop_after = stop_after
        self.status = status

    @classmethod
    def fromJSONDict(cls, json) :
        return cls( cond_get(json,'max_simplices'), 
                    cond_get(json,'persistence_epsilon'), 
                    cond_get(json,'segment_stride'),
                    cond_get(json,'segment_size'), 
                    cond_get(json,'window_size'),
                    cond_get(json,'window_stride'), 
                    cond_get(json,'kernel_scale'),
                    cond_get(json,'kernel_gamma'),
                    cond_get(json,'invariant_epsilon'), 
                    cond_get(json,'data_file'), 
                    cond_get(json,'data_index'),
                    cond_get(json,'label_index'), 
                    cond_get(json,'out_directory'),
                    cond_get(json,'threads'), 
                    cond_get(json,'learning_split'),
                    cond_get(json,'learning_iterations'), 
                    cond_get(json,'learning_C'),
                    cond_get(json,'cv_iterations'),
                    cond_get(json,'persistence_degree'), 
                    cond_get(json,'reevaluate'),
                    cond_get(json,'data_type'), 
                    cond_get(json,'post_process'),
                    cond_get(json,'post_process_arg'), 
                    cond_get(json,'stop_after'),
                    cond_get(json,'status'))


    def __str__(self) :
        return ("Configuration max_simplices %s persistence_epsilon %s segment_stride %s segment_size %s \n" + 
                "  segment_filename %s\n" +
                "  window_size %s window_stride %s kernel_scale %s kernel_gamma %s invariant_epsilon %s\n" +
                "  data_file %s data_index %s label_index %s out_directory %s\n" +
                "  threads %s learning_split %s learning_iterations %s cv_iterations %s learning_C %s\n" +
                "  persistence_degree %s\n" +
                "  reevaluate [%s %s %s %s %s %s] data_type %s post_process %s post_process_arg %s stop_after %s status %s") % \
            (self.max_simplices, self.persistence_epsilon, self.segment_stride,
             self.segment_size, self.segment_filename,
             self.window_size, self.window_stride, self.kernel_scale, self.kernel_gamma, self.invariant_epsilon,
             self.data_file, self.data_index, self.label_index,
             self.out_directory, self.threads, self.learning_split,
             self.learning_iterations, self.cv_iterations, self.learning_C,
             self.persistence_degree,
             self.reevaluate['segments'] if isinstance(self.reevaluate, dict) and 'segments' in self.reevaluate.keys() else '', 
             self.reevaluate['post_process'] if isinstance(self.reevaluate, dict) and 'post_process' in self.reevaluate.keys() else '', 
             self.reevaluate['persistence_diagrams'] if isinstance(self.reevaluate, dict) and 'persistence_diagrams' in self.reevaluate.keys() else '',
             self.reevaluate['distances'] if isinstance(self.reevaluate, dict) and 'distances' in self.reevaluate.keys() else '', 
             self.reevaluate['kernel'] if isinstance(self.reevaluate, dict) and 'kernel' in self.reevaluate.keys() else '',
             self.reevaluate['learning'] if isinstance(self.reevaluate, dict) and 'learning' in self.reevaluate.keys() else '', 
             self.data_type,
             self.post_process, self.post_process_arg,
             self.stop_after, self.status) 

    # shared_prefix compares two configurations and sees if they share a common 
    # computational prefix
    def shared_prefix(self, c2) :
        prefix = None
        if self['data_file']           == c2['data_file'] and \
           self['data_index']          == c2['data_index'] and \
           self['segment_size']        == c2['segment_size'] and \
           self['segment_stride']      == c2['segment_stride'] and \
           self['window_size']         == c2['window_size'] and \
           self['window_stride']       == c2['window_stride'] :
            prefix = 'segments'
        else :
            return prefix
        if self['post_process'] != None and \
           self['post_process']        == c2['post_process'] and \
           self['post_process_arg']    == c2['post_process_arg'] :
            prefix = 'post_process'
        else :
            return prefix
        if self['max_simplices']       == c2['max_simplices'] and \
           self['persistence_epsilon'] == c2['persistence_epsilon'] :
            prefix = 'distances'
        else :
            return prefix
        if self['kernel_scale']        == c2['kernel_scale'] :
            prefix = 'kernel'
        else :
            return prefix
        if self['learning_iterations'] == c2['learning_iterations'] and \
           self['learning_split']      == c2['learning_split'] and \
           self['learning_C']          == c2['learning_C']:
            return 'learning'
        else :
            return prefix
                
    def same_config(self, c2) :
        return self.shared_prefix(c2) == 'learning'
                        
class label :
    def __init__(self, name):
        if name == 'segments' or \
           name == 'post_process' or \
           name == 'persistence_diagrams' or \
           name == 'distances' or \
           name == 'kernel' or \
           name == 'learning' :
            self.name = name
        else :
            raise TypeError("%s not a valid label initializer" % (name,))

    def __eq__( self, other ) :
        if isinstance(other, label) :
            return self.name == other.name
        else :
            return False
            
    def __lt__( self, other ) :
        ol = other
        if not isinstance(other, label) :
            ol = label(other)
        if self.name == 'segments' and  ol.name != 'segments':
            return True
        if self.name == 'post_process' and  (ol.name != 'segments' or ol.name != 'post_process') :
            return True
        if self.name == 'persistence_diagrams' and (ol.name != 'segments'  or ol.name != 'post_process' or ol.name != 'persistence_diagrams') :
            return True
        if self.name == 'distances' and (ol.name == 'kernel' or ol.name == 'learning') :
            return True
        if self.name == 'kernel' and ol.name == 'learning':
            return True
        else : 
            return False

import itertools
def ArgsIter(args_l):
    for args in args_l :
        # make all the variable entries lists if they aren't already
        iterargs = dict(map(lambda x: (x, cond_get_list(args,x)), 
                            ['segment_size', 'segment_stride', 'window_size', 'window_stride', \
                             'max_simplices', 'persistence_epsilon', 'post_process_arg']))
        if not ('data_index' in args.keys()) or args['data_index'] == None :
            iterargs['data_index'] = [None]
        elif not isinstance(args['data_index'], list) :
            iterargs['data_index'] = [args['data_index']]
        else :
            if isinstance(args['data_index'][0], list) :
                iterargs['data_index'] = args['data_index']
            else :
                iterargs['data_index'] = [args['data_index']]
        for (data_index, segment_size, segment_stride, window_size,
             window_stride, max_simplices, persistence_epsilon, post_process_arg) in \
            itertools.product(iterargs['data_index'], 
                              iterargs['segment_size'], 
                              iterargs['segment_stride'], 
                              iterargs['window_size'], 
                              iterargs['window_stride'], 
                              iterargs['max_simplices'],
                              iterargs['persistence_epsilon'],
                              iterargs['post_process_arg']) :
            yield Configuration(max_simplices, 
                                persistence_epsilon, 
                                segment_stride,
                                segment_size, 
                                window_size, 
                                window_stride,
                                cond_get(args,'kernel_scale'), 
                                cond_get(args,'kernel_gamma'), 
                                cond_get(args,'invariant_epsilon'), 
                                cond_get(args, 'data_file'), 
                                data_index,
                                cond_get(args,'label_index'),
                                cond_get(args,'out_directory'), 
                                cond_get(args,'threads'),
                                cond_get(args,'learning_split'),
                                cond_get(args,'learning_iterations'), 
                                cond_get(args,'learning_C'),
                                cond_get(args,'cv_iterations'),
                                cond_get(args,'persistence_degree'),
                                cond_get(args,'reevaluate'), 
                                cond_get(args,'data_type'),
                                cond_get(args,'post_process'),
                                post_process_arg,
                                cond_get(args,'stop_after'),
                                cond_get(args,'status'))

# parse_range interprets a string containing integers and colons or commas
# a:b returns the list of numbers [a,b) seperated by one i.e. range(a,b)
# a:b:c returns a list of numbers [a,b) seperated by c, i.e. range(a,b,c)
# a;b;c returns a list of numbers [a,b] with c increments in a log scale
# a,b,c,... returns all the integers provided as a list 
import string
import math
def parse_range(in_str, t=int) :
    try :
        if (string.find(in_str,":") != -1) :
            nums = string.split(in_str, ":")
            if (len(nums) == 2) :
                return [a for a in numpy.arange(t(nums[0]),t(nums[1]))]
            elif (len(nums) == 3) :
                return [a for a in numpy.arange(t(nums[0]),t(nums[1]),t(nums[2]))]
        elif (string.find(in_str, ";") != -1) :
            nums = string.split(in_str, ";")
            log_a = math.log(float(nums[0]))
            log_b = math.log(float(nums[1]))
            steps = int(nums[2])
            step = (log_b - log_a) / float(steps - 1)
            if t==int :
                return [t(round(math.exp(log_a + float(i) * step))) for i in range(steps)]
            else :
                return [t(math.exp(log_a + float(i) * step)) for i in range(steps)]

        elif (string.find(in_str, ",") != -1) :
            return [t(a) for a in string.split(in_str, ",")]
        else :
            return t(in_str)
    except ValueError:
        print "parse_range: Could not parse a value or range of values from the input string '%s' for %s" % (in_str, t)
        raise
# data_index pares from a string "x,y,z;a,b;c" to [[x,y,z],[a,b],[c]]
def parse_index(in_str) :
    return [[int(i) for i in r.split(',')] for r in in_str.split(';')]

import argparse
import multiprocessing
import os
# Returns the dictionary of the provided arguments 
def parse_args(argv) :
    parser = argparse.ArgumentParser(description='Test learning methods with varying segment sizes, strides, etc.')
    parser.add_argument('-m', '--max-simplices', help="Maximum number of simplices to process when creating a persistence diagram")
    parser.add_argument('-e', '--persistence-epsilon', help="Epsilon value for creating a persistence diagram, maximum 1/3")
    parser.add_argument('-s', '--segment-stride', default='1500')
    parser.add_argument('-S', '--segment-size', default='1500')
    parser.add_argument('-w', '--window-stride', default='1')
    parser.add_argument('-W', '--window-size', default='50')
    parser.add_argument('-d', '--data-index')
    parser.add_argument('-l', '--label-index', default=4, type=int)
    parser.add_argument('-f', '--data-file', default='data.csv')
    parser.add_argument('-T', '--data-type', default='ActivitySegments')
    parser.add_argument('-o', '--out-directory', default='out')
    parser.add_argument('-t', '--threads', default=max(1,(multiprocessing.cpu_count()-4)))
    parser.add_argument('-L', '--learning-split', default=0.5, type=float)
    parser.add_argument('-i', '--learning-iterations', default=1, type=int)
    parser.add_argument('-C', '--learning-C')
    parser.add_argument('-v', '--cv-iterations', type=int)
    parser.add_argument('-g', '--kernel-gamma')
    parser.add_argument('-k', '--kernel-scale')
    parser.add_argument('-E', '--invariant-epsilon', default=1.0, type=float)
    parser.add_argument('-p', '--persistence-degree', default=1, type=int)
    parser.add_argument('-P', '--post-process', default="None")
    parser.add_argument('--post-process-arg')
    parser.add_argument('-r', '--reevaluate', action='store_true')
    parser.add_argument('--stop-after', default="learning")
    parser.add_argument('--config')
    parser.add_argument('--curses', action='store_true')
    parser.add_argument('--outfile', help="filename to save segment data for Segments.py")
    args = vars(parser.parse_args(argv[1:]))
    current_dir     = os.getcwd()
    if args['curses'] == True :
        curses = True
    else :
        curses = False
    if (args['config'] != None) :
        if args['config'] == '-' :
            #read from stdin
            args = json.loads(sys.stdin.read())
        else :
            with open(args['config'], 'r') as config_in :
                args = json.load(config_in)
    if isinstance(args, list) :
        args_l = args
    else :
        args_l = [args]
    for arg in args_l :
        if not "stop_after" in arg : 
            arg["stop_after"] = "learning"

        if ('segment_size' in arg and not isinstance(arg['segment_size'], list) and arg['segment_size'] != None) :
            arg['segment_size']   = parse_range(str(arg['segment_size']))
        if ('segment_stride' in arg and not isinstance(arg['segment_stride'], list) and arg['segment_stride'] != None) :
            arg['segment_stride'] = parse_range(str(arg['segment_stride']))
        if ('window_size' in arg and not isinstance(arg['window_size']   , list) and arg['window_size'] != None) :
            arg['window_size']    = parse_range(str(arg['window_size']))
        if ('window_stride' in arg and not isinstance(arg['window_stride'] , list) and arg['window_stride'] != None) :
            arg['window_stride']  = parse_range(str(arg['window_stride']))
        if ('max_simplices' in arg and not isinstance(arg['max_simplices'], list) and arg['max_simplices'] != None) :
            arg['max_simplices'] = parse_range(str(arg['max_simplices']))
        elif ('persistence_epsilon' in arg and not isinstance(arg['persistence_epsilon'], list) and arg['persistence_epsilon'] != None) :
            arg['persistence_epsilon'] = parse_range(str(arg['persistence_epsilon']), t=float)
        if ('data_index' in arg and not isinstance(arg['data_index'], list) and arg['data_index'] != None) :
            arg['data_index']     = parse_index(str(arg['data_index']))
        if ('data_file' in arg and not isinstance(arg['data_file'], list) and not isinstance(arg['data_file'], dict) and arg['data_file'] != None) :
            arg['data_file']     = arg['data_file'].split(':')
        if ('threads' in arg and not isinstance(arg['threads'], list) and arg['threads'] != None) :
            arg['threads']        = parse_range(str(arg['threads']))
        if ('post_process_arg' in arg and not isinstance(arg['post_process_arg'] , list) and arg['post_process_arg']!=None) :
            arg['post_process_arg'] = parse_range(str(arg['post_process_arg']), t=float)

        save_dir = arg['out_directory']
        if (save_dir[0] == '~') :
            save_dir = os.path.expanduser(save_dir)
        #elif (save_dir[0] != '/') :
        #    save_dir = "%s/%s" % (current_dir, save_dir)
        if (os.path.exists(save_dir) and not os.path.isdir(save_dir)) :
            print "%s exists and is not a directory!" % save_dir
            parser.print_help()
            exit(0)
        elif (not os.path.exists(save_dir)) :
            try :
                os.makedirs(save_dir)
            except OSError as e:
                import errno
                print "Could not make directory %s (err: %s)" % (save_dir, errno.errorcode[e.errno])
                exit(0)
        arg['out_directory'] = save_dir
        arg['curses'] = curses
    return args_l

def get_filename(config, keys, filetype, gz=True):
    result = "%s/" % (config.out_directory,)
    if 'data_file' in keys and 'data_file' in config and config.data_file != None :
        filename = ''
        if isinstance(config.data_file, list) :
            for data_file in config.data_file[0:4] :
                # Strip directories out
                f = os.path.basename(data_file)
                # only use the first part of the filename for a train/test split
                # otherwise just remove any extension 
                if f.rfind('_TEST') != -1 :
                    f = f[0:f.rfind('_TEST')]
                elif f.rfind('_TRAIN') != -1 :
                    f = f[0:f.rfind('_TRAIN')]
                else :
                    (f, ext) = os.path.splitext(f)
                if filename == '' :
                    filename = f
                elif not filename.endswith(f) :
                    filename = filename + '_' + f
        elif isinstance(config.data_file, dict) :
            filename = "mocap"
        else :
            (filename, ext) = os.path.splitext(os.path.basename(config.data_file))
        result = result + filename

    if 'data_index' in keys and 'data_index' in config and config.data_index != None :
        if isinstance(config.data_index, list) :
            result = result + '-data-' + '_'.join([str(i) for i in config.data_index])
        else :
            result = result + '-data-' + str(config.data_index)

    if 'segment_size' in keys and 'segment_size' in config and config.segment_size != None :
        result = result + '-seg-' + str(config.segment_size)

    if 'segment_stride' in keys and 'segment_stride' in config and config. segment_stride != None :
        result = result + '-' + str(config.segment_stride)

    if 'window_size' in keys and 'window_size' in config and config.window_size != None :
        result = result + '-win-' + str(config.window_size)

    if 'window_stride' in keys and 'window_stride' in config and config.window_stride != None :
        result = result + '-' + str(config.window_stride)

    if 'post_process' in keys and 'post_process' in config and config.post_process != None :
        result = result + '-' + str(config.post_process)

    if 'post_process_arg' in keys and 'post_process_arg' in config and config.post_process_arg != None :
        result = result + '-' + str(config.post_process_arg)
        
    if 'max_simplices' in keys and 'max_simplices' in config and config.max_simplices != None :
        result = result + '-simplices-' + str(config.max_simplices)
    elif 'persistence_epsilon' in keys and 'persistence_epsilon' in config and config.persistence_epsilon != None :
        result = result + '-eps-' + str(config.persistence_epsilon)

    if 'kernel_scale' in keys and 'kernel_scale' in config and config.kernel_scale != None :
        try :
            scale = "%g" % (float(config.kernel_scale),)
        except:
            scale = str(config.kernel_scale)
        result = result + '-scale-' + scale

    if 'kernel_gamma' in keys and 'kernel_gamma' in config and config.kernel_gamma != None :
        try :
            gamma = "%g" % (float(config.kernel_gamma),)
        except:
            gamma = str(config.kernel_gamma)
        result = result + '-gamma-' + gamma
        
    if 'invariant_epsilon' in keys and 'invariant_epsilon' in config and config.invariant_epsilon != None :
        try :
            epsilon = "%g" % (float(config.invariant_epsilon),)
        except:
            epsilon = str(config.invariant_epsilon)
        result = result + '-epsilon-' + epsilon

    if 'learning_C' in keys and 'learning_C' in config and config.learning_C != None :
        try :
            C = "%g" % (float(config.learning_C),)
        except:
            C = str(config.learning_C)
        result = result + '-C-' + C

    result = result + '-' + filetype + '.json'
    if gz :
        result = result + '.gz'

    return result

if __name__ == "__main__":
    import sys
    import json
    print '['
    for config in list(ArgsIter(parse_args(sys.argv))) :
        print json.dumps(config.toJSONDict()) 
    print ']'
