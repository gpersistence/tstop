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


import subprocess
import argparse
import threading
import multiprocessing
import itertools
import traceback
import os
import os.path
import errno
import sys
import time
import json
# Used to guarantee to use at least Wx2.8
import wxversion
wxversion.ensureMinimal('2.8')

import matplotlib

matplotlib.use('pdf')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure

import wx

from persistence.Datatypes.JSONObject import load_data
from persistence.Datatypes.Learning import Learning

class CanvasFrame(wx.Frame):

    def __init__(self, argv):
        wx.Frame.__init__(self,None,-1,
                         'UCR 2015 Learning Results',size=(550,350))
        parser = argparse.ArgumentParser(description="utility to graph success levels for learning on the UCR Dataset")
        parser.add_argument('-d', '--directory', help='Directory where the learning results are stored', required=False)
        parser.add_argument('files', metavar='FILE', nargs='*')
        self.args = vars(parser.parse_args(argv[1:]))
        if self.args['directory'] != None and len(self.args['files']) != 0 :
            print "Ignoring files after the directory argument"
        elif self.args['directory'] == None and len(self.args['files']) == 0 :
            parser.print_help()
            sys.exit()
        
        if self.args['directory'] != None :
            if os.path.isdir(self.args['directory']) :
                self.files = subprocess.check_output(["find", self.args['directory'], "-name", "*Learning.json*"])
                self.files = [f for f in self.files.split("\n") if f != '']
            else :
                parser.print_help()
                sys.exit()
        else :
            self.files = self.args['files']
        def learning_type(text) :
            fields = text.split('-')
            t = fields[-1].split('.')[0][:-len('Learning')]
            try :
                if t == 'PersistenceKernel' or t == 'ScaleSpaceSimilarity' or t == 'MultipleKernel' or t == 'AverageKernel':
                    if 'ChaosPost' in fields :
                        w = '-Chaos'
                    else :
                        w = '-' + fields[fields.index('win')+1]
                else :
                    w = ''
            except ValueError :
                w = ''
            return t + w
        self.learning_types = list(set([learning_type(f) for f in self.files]))
        self.learning_types.sort()
        datasets = list(set([f.split('/')[-2] for f in self.files]))
        datasets.sort()

        self.filedict = dict([(s, dict([(t,0) for t in self.learning_types])) for s in datasets])

        # load in the data files
        for f in self.files :
            learning_t = learning_type(f)
            dataset = f.split('/')[-2]
            learning_json = load_data(f, "learning", None, None, None)
            learning = Learning.fromJSONDict(learning_json)
            best = self.filedict[dataset][learning_t]
            current = learning.get_average_correct()
            if (isinstance(best, list) and current > sum(best)) or (not isinstance(best, list) and current > best) :
                if learning.results[0].mkl_weights != None :
                    self.filedict[dataset][learning_t] = [current * w for w in learning.results[0].mkl_weights]
                else :
                    self.filedict[dataset][learning_t] = current

        keylen = max([len(key) for (key,val) in self.filedict.items() ])
        format = '%'+str(keylen)+'s %s'
        for (key, val) in self.filedict.items() :
            vals = [("%s %02.2f%%" % (k,v*100.0 if not isinstance(v, list) else sum(v) * 100.0)) + ((" " + str(["%02.2f%%" % v_ for v_ in v])) if isinstance(v,list) else "") for (k,v) in val.items()]
            vals.sort()
            print format % (key, vals)

        self.frame = 0
        self.SetBackgroundColour(wx.NamedColour("WHITE"))
        self.figure = Figure()
        self.axes = self.figure.add_subplot(121)
        plot_keys = self.filedict.items()[0][1].keys()
        dataset_width = len(plot_keys) + 1.5
        self.axes.set_xticks([(0.5 + i) * dataset_width for i in range(len(self.filedict.items()))])
        self.axes.set_xticklabels([key for (key,value) in self.filedict.items()])
        self.axes.set_ylim(0.0,1.0, auto=False)
        
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.title = self.figure.suptitle("UCR Learning")
        #self.Fit()
        self.background = self.axes.figure.canvas.copy_from_bbox(self.axes.bbox)
        self.colors = ['black', 'red', 'yellow', 'orange', 'blue', 'green', 'violet']
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)
        self.point_Refresh()

    def point_Refresh(self) :
        dataset_keys = self.filedict.keys()
        dataset_keys.sort()
        plot_keys = self.learning_types
        dataset_width = len(plot_keys) + 1.5

        self.canvas.restore_region(self.background)
        self.axes.cla()
        self.axes.set_xticks([(0.5 + i) * dataset_width for i in range(len(self.filedict.items()))])
        self.axes.set_xticklabels([key for key in dataset_keys])
        plots = []
        for (key,i) in zip(plot_keys, range(len(plot_keys))) : 
            left   = [j * dataset_width + i + 0.75 for j in range(len(dataset_keys))]
            height = [self.filedict[dataset][key] if not isinstance(self.filedict[dataset][key], list) else self.filedict[dataset][key][0] for dataset in dataset_keys]
            plots.append(self.axes.bar(left, height, color=self.colors[i % len(self.colors)]))

        self.axes.set_ylim(0.0,1.0, auto=False)
        self.axes.legend(plots, plot_keys, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.).draggable()
        #self.Fit()
        for (key,i) in zip(plot_keys, range(len(plot_keys))) : 
            if reduce(lambda x,dataset : isinstance(self.filedict[dataset][key], list) and x, dataset_keys, True) :
                left   = [j * dataset_width + i + 0.75 for j in range(len(dataset_keys)) if isinstance(self.filedict[dataset_keys[j]][key], list)]
                height = [self.filedict[dataset][key][1] for dataset in dataset_keys if isinstance(self.filedict[dataset][key], list)]
                bottom = [self.filedict[dataset][key][0] for dataset in dataset_keys if isinstance(self.filedict[dataset][key], list)]
                plots.append(self.axes.bar(left, height, color=self.colors[i+1 % len(self.colors)], bottom=bottom))
        self.figure.savefig(dataset_keys[0]+'.pdf')
        sys.exit(0)

    def KeyEvent(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_LEFT :
            self.frame = (self.frame - 1) % len(self.labels)
            self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_RIGHT :
            self.frame = (self.frame + 1) % len(self.labels)
            self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())
        else :
            self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())
            event.Skip()
            
    def OnPaint(self, event):
        paint_dc = wx.PaintDC(self)
        self.canvas.draw()

class App(wx.App):
    def __init__(self, arg, argv):
        self.argv = argv
        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.argv)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def display(argv):
    app = App(0, argv)
    app.MainLoop()

def main(argv) :
    current_dir = os.getcwd()

    processes = []
    try:
        display_thread = \
          multiprocessing.Process(target=display, 
                                  args=(argv,))
        display_thread.start()
        processes.append(display_thread)
        display_thread.join()
    except KeyboardInterrupt:
        print "Caught cntl-c, shutting down..."
        exit(0)
        

if __name__ == "__main__":
        main(sys.argv)
