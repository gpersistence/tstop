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


import curses
import os
import string
from persistence.Datatypes.Configuration import parse_args, ArgsIter, label
from persistence.ParseConfigurations import parse_configuration_files
def file_fun(filename) :
    if isinstance(filename, list) :
        return os.path.basename(filename[0]).split('_')[0]
    elif isinstance(filename, dict) :
        keys = filename.keys()
        if isinstance(filename[keys[0]], list) :
            return os.path.basename(filename[keys[0]][0])
        else :
            return os.path.basename(filename[keys[0]])
    else :
        return os.path.basename(filename)

def status_fun(config) :
    if config['status'] == None :
        return ''
    else :
        return config['status']


class StatusWindow:
    def __init__(self, configs) :
        self.configs = configs 
        self.stdscr = None
        self.fields = dict([('data_type',           'Type'),
                            ('data_file',           'File'),
                            ('data_index',          'Data'),
                            ('label_index',         'Label'),
                            ('segment_size',        'Seg'),
                            ('segment_stride',      'Stride'),
                            ('window_size',         'Win'),
                            ('window_stride',       'Stride'),
                            ('post_process_arg',    'Post'),
                            ('max_simplices',       'Simplices'),
                            ('persistence_epsilon', 'epsilon'),
                            ('kernel_scale',        'Scale'),
                            ('learning_C',          'C'),
                            ('status',              'Status')])
        self.field_len = dict()
        for (key,value) in self.fields.items() :
            if key == 'data_file' :
                self.field_len[key] = max([len(value)] + [len(file_fun(config[key])) for config in self.configs])
            elif key == 'status' :
                self.field_len[key] = max([len(value)] + [len(status_fun(config)) for config in self.configs])
            else :
                self.field_len[key] = max([len(value)] + [len(str(config[key])) for config in self.configs])

    def __call__(self, stdscr) :
        self.stdscr = stdscr
        curses.halfdelay(10)
        line = 0
        start = 0


        line_fun = (lambda x: string.join(["{:>{}}".format(file_fun(x[key]) if key == 'data_file' else \
                                                           status_fun(x) if key == 'status' else x[key],
                                                           self.field_len[key]) for key in \
                                           ['data_type', 'data_file', 'data_index', 'label_index',
                                            'segment_size', 'segment_stride', 'window_size',
                                            'window_stride', 'post_process_arg', 'max_simplices', 'persistence_epsilon',
                                            'kernel_scale', 'learning_C', 'status']]))
        
        while True:
            for (key,value) in self.fields.items() :
                if key == 'data_file' :
                    self.field_len[key] = max([len(value)] + [len(file_fun(config[key])) for config in self.configs])
                elif key == 'status' :
                    self.field_len[key] = max([len(value)] + [len(status_fun(config)) for config in self.configs])
                else :
                    self.field_len[key] = max([len(value)] + [len(str(config[key])) for config in self.configs])

            (max_y, max_x) = self.stdscr.getmaxyx()
            blank = " " * (max_x - 1)
            heading = string.join(["{:>{}}".format(self.fields[key], self.field_len[key]) \
                                   for key in ['data_type','data_file', 'data_index', 'label_index',
                                               'segment_size', 'segment_stride', 'window_size',
                                               'window_stride', 'post_process_arg', 'max_simplices', 'persistence_epsilon',
                                               'kernel_scale', 'learning_C', 'status']])
            if len(heading) < (max_x - 1) :
                heading = heading + blank[len(heading):]
            heading = heading[:max_x-1]
            self.stdscr.addstr(0,0,heading)

            
            if len(self.configs) - (max_y - 1) < start :
                start = max(0, len(self.configs) - (max_y - 1))
            cfgs = self.configs[start:start+max_y-1]
            rng = range(1,len(cfgs)+1)
            for (config, y) in zip(cfgs, rng) :
                output = line_fun(config)
                if len(output) < (max_x - 1) :
                    output = output + blank[len(output):]
                output = output[0:max_x-1]
                if start + (y - 1) == line :
                    self.stdscr.addstr(y,0, output, curses.A_REVERSE)
                else :
                    self.stdscr.addstr(y,0, output, curses.A_NORMAL)
            self.stdscr.refresh()
            c = self.stdscr.getch()
            if c == curses.KEY_UP :
                line = max(0, (line - 1))
            elif c == curses.KEY_DOWN :
                line = min((line + 1), len(self.configs)-1)
            elif c == ord('q'):
                break
            if line < start :
                start = line
            while (line - start) >= (max_y - 1) :
                start = line - (max_y - 2)
        curses.nocbreak()
            
import sys
import argparse
if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description="Tool to visualize configurations that will be computed")
    parser.add_argument("--config", "-c", nargs="+")
    args = parser.parse_args(sys.argv[1:])
    configs = parse_configuration_files(args.config, verbose=True)
    print len(configs)
    w = StatusWindow(configs)
    curses.wrapper(w)
