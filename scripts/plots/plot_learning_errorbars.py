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
import numpy
# Used to guarantee to use at least Wx2.8
import wxversion
wxversion.ensureMinimal('2.8')

import matplotlib

matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure

import wx

from persistence.Datatypes.JSONObject import load_data
from persistence.Datatypes.Learning import Learning, LearningResult

class CanvasFrame(wx.Frame):

    def __init__(self, argv):
        wx.Frame.__init__(self,None,-1,
                         'Segment Size',size=(550,350))
        parser = argparse.ArgumentParser(description="utility to graph success levels for learning over a single configuration parameter")
        parser.add_argument('--label', '-l')
        parser.add_argument('files', metavar='FILE', nargs='*')
        self.args = vars(parser.parse_args(argv[1:]))
        self.files = self.args['files']

        self.filedict = []
        # load in the data files
        for f in self.files :
            learning = Learning.fromJSONDict(load_data(f, 'learning', None, None, argv[0] + ": "))
            correct = []
            for result in learning.results : 
                num_correct = reduce((lambda s, (t0, t1) : s + 1 if t0 == t1 else s), 
                                     zip(result['test_labels'], result['test_results']), 0)
                correct.append(float(num_correct) / float(len(result['test_labels'])))
            print "file %s correct %0.2f%%" % (f, numpy.average(correct)*100.0)
            self.filedict.append(dict([('file', f), ('correct', numpy.average(correct)), ('config', learning.config)]))
            if "PersistenceKernelLearning" in f :
                self.filedict[-1]['label'] = "Persistence Kernel " + learning.config.data_index
                if learning.config.post_process != None :
                    self.filedict[-1]['label'] = self.filedict[-1]['label'] + " " + learning.config.post_process
            elif "AverageKernelLearning" in f :
                self.filedict[-1]['label'] = "Average Kernel"
                if learning.config.post_process != None :
                    self.filedict[-1]['label'] = self.filedict[-1]['label'] + " " + learning.config.post_process
            elif "ChaoticInvariantFeaturesLearning" in f :
                self.filedict[-1]['label'] = " Chaotic Invariant Features"
            elif "ScaleSpaceSimilarityLearning" in f :
                self.filedict[-1]['label'] = "Scale Space Similarity"
            elif "DTWDistancesLearning" in f :
                self.filedict[-1]['label'] = "DTW Distance"
            elif "EuclideanDistancesLearning" in f :
                self.filedict[-1]['label'] = "Euclidean Distance"
            if (len(correct) > 1) :
                self.filedict[-1]['correct_std'] = numpy.std(correct)
                self.filedict[-1]['correct_top'] = numpy.percentile(correct, 0.75)
                self.filedict[-1]['correct_bot'] = numpy.percentile(correct, 0.25)
            else :
                self.filedict[-1]['correct_std'] = 0.0
                self.filedict[-1]['correct_top'] = 0.0
                self.filedict[-1]['correct_bot'] = 0.0
        
        self.SetBackgroundColour(wx.NamedColour("WHITE"))
        self.figure = Figure()
        self.axes = self.figure.add_subplot(211)
        
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(NavigationToolbar2Wx(self.canvas), 1, wx.LEFT | wx.TOP | wx.GROW)
        self.sizer.Add(self.canvas, 8, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.title = self.figure.suptitle("")
        self.Fit()
        self.background = self.axes.figure.canvas.copy_from_bbox(self.axes.bbox)
        self.colors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#b3de69', '#fb9a99', '#e31a1c', '#fb8072', '#ff7f00', '#a65628', '#fdb462', '#cab2d6']
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)
        self.point_Refresh()

    def point_Refresh(self) :
        self.title.set_text("")
        
        self.canvas.restore_region(self.background)
        self.axes.cla()
        color = 0
        lines = []
        plots = []
        for f_dict in self.filedict : 
            current = [f_dict['label']]
            found = False
            for plot in plots :
                found = found or reduce((lambda x, (y1, y2) : x and (y1 == y2)), zip(current, plot), True)
            if not found :
                plots.append(current)
        vals = sorted([ (f_dict['label'], float(numpy.average(f_dict['correct'])), \
                         f_dict['correct_top'] if 'correct_top' in f_dict else 0.0, \
                         f_dict['correct_bot'] if 'correct_bot' in f_dict else 0.0) \
                        for f_dict in self.filedict], key=(lambda x: x[0]))
            
        # if the iterated value is a string, plot vs. lexicographic sorting
        if (isinstance(vals[0][0], (str,unicode))) :
            xs = [] 
            x = 0
            for v in vals:
                if not ('ChaosPost' in v[0]) :
                    xs.append(x)
                    x = x + 1
        else :
            xs = [x[0] for x in vals]
        bottom = 0.75
        ys = [x[1] - bottom for x in vals if ('Chao' in x[0])]
        y_err = [[abs(v[3]-v[1]) for v in vals if ('Chao' in v[0])] , [abs(v[2]-v[1]) for v in vals if ('Chao' in v[0])]]
        colors = [self.colors[x % len(self.colors)] for x in range(len(xs))]
        rects0 = self.axes.bar([xs[0]], [ys[0]],
                               color=colors[2],
                               yerr=[[y_err[0][0]], [y_err[1][0]]],
                               width=0.85,
                               bottom=bottom,
                               error_kw=dict(elinewidth=2, color=colors[3]))
        rects1 = self.axes.bar(xs[1:], ys[1:],
                               color=[colors[0] for x in xs[1:]],
                               yerr=[y_err[0][1:],y_err[1][1:]],
                               width=0.85,
                               bottom=bottom,
                               error_kw=dict(elinewidth=2, color=colors[4]))
        bottom = [y + 0.75 for y in ys[1:]]
        vs= [v for v in vals if not ('Chao' in v[0])]
        ys = [v[1] - b  for v,b in zip(vs,bottom)]
        y_err = [[abs(v[3]-v[1]) for v in vs] , [abs(v[2]-v[1]) for v in vs]]
        

        rects2 = self.axes.bar(xs[1:], ys,
                               color=[colors[1] for x in xs[1:]],
                               yerr=y_err,
                               width=0.85,
                               bottom=bottom,
                               error_kw=dict(elinewidth=2, color=colors[5]))
        self.axes.set_ylabel("Accuracy")
        self.axes.set_xticks([x + 0.5 for x in range(len(xs))])
        self.axes.set_xticklabels([val[0] for val in vals if not ('ChaosPost' in val[0])], rotation=45, ha='right')
        lines.append(rects1)
        self.axes.legend([rects0,rects1,rects2],["Chaotic Invariant", "Dynamic Window", "Window Size 15"], ncol=3).draggable()
        self.Fit()

    def KeyEvent(self, event):
        keycode = event.GetKeyCode()
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
