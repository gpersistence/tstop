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
import itertools

from persistence.Datatypes.JSONObject import load_data
from persistence.Datatypes.Configuration import Configuration, parse_range

def parse_configuration_files(files, verbose=True) :
    if not isinstance(files, list) :
        files = [files]

    final_configs = []
    for f in files :
        configs = load_data(f, "Configurations", None, None, (sys.argv[0] + ": ") if verbose else None)
        if configs == None :
            sys.exit(0)
        if isinstance(configs, dict) :
            configs = [configs]
        cond_parse_range = lambda x,y,t: parse_range(str(x[y]), t=t) if y in x.keys() else None
        cond_list = lambda x: x if isinstance(x,list) else [x]
        cond_get = lambda x,y: x[y] if y in x.keys() else None
        for config in configs :
            for (window_size, window_stride, segment_size, segment_stride, persistence_epsilon, max_simplices) in \
                itertools.product(cond_list(cond_parse_range(config, 'window_size', int)),
                                  cond_list(cond_parse_range(config, 'window_stride', int)),
                                  cond_list(cond_parse_range(config, 'segment_size', int)),
                                  cond_list(cond_parse_range(config, 'segment_stride', int)),
                                  cond_list(cond_parse_range(config, 'persistence_epsilon', float)),
                                  cond_list(cond_parse_range(config, 'max_simplices', int))) :
                final_configs.append(Configuration(max_simplices       = max_simplices, 
                                                   persistence_epsilon = persistence_epsilon, 
                                                   segment_stride      = segment_stride,
                                                   segment_size        = segment_size, 
                                                   window_size         = window_size, 
                                                   window_stride       = window_stride,
                                                   kernel_scale        = cond_get(config, 'kernel_scale'), 
                                                   kernel_gamma        = cond_get(config, 'kernel_gamma'), 
                                                   invariant_epsilon   = cond_get(config, 'invariant_epsilon'), 
                                                   data_file           = cond_get(config, 'data_file'), 
                                                   data_index          = cond_get(config, 'data_index'),
                                                   label_index         = cond_get(config, 'label_index'),
                                                   out_directory       = cond_get(config, 'out_directory'), 
                                                   learning_split      = cond_get(config, 'learning_split'),
                                                   learning_iterations = cond_get(config, 'learning_iterations'), 
                                                   learning_C          = cond_get(config, 'learning_C'), 
                                                   persistence_degree  = cond_get(config, 'persistence_degree'),
                                                   data_type           = cond_get(config, 'data_type'),
                                                   post_process        = cond_get(config, 'post_process'),
                                                   post_process_arg    = cond_get(config, 'post_process_arg')))
    return final_configs
