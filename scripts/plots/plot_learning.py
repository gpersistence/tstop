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

matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure

import wx

class CanvasFrame(wx.Frame):

    def __init__(self, argv):
        wx.Frame.__init__(self,None,-1,
                         'Segment Size',size=(550,350))
        parser = argparse.ArgumentParser(description="utility to graph success levels for learning vs configuration parameters")
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
                self.files = ["%s/%s" % (self.args['directory'], f) for f in os.listdir(self.args['directory']) \
                              if f.endswith('learning.json')]
            else :
                parser.print_help()
                sys.exit()
        else :
            self.files = self.args['files']

        self.filedict = []

        # load in the data files
        for f in self.files :
            with open(f, 'r') as j_file :
                learning = json.load(j_file)
                correct = []
                for iteration in learning['learning'] :
                    # count the correct test results
                    num_correct = reduce((lambda s, (t0, t1) : s + 1 if t0 == t1 else s), zip(iteration['test'], iteration['truth']), 0)
                    correct.append(float(num_correct) / float(len(iteration['test'])))
                learning['config']['correct'] = correct
                if isinstance(learning['config']['data_file'], list) :
                    learning['config']['data_file'] = os.path.basename(learning['config']['data_file'][0]).split('_')[0]
                else :
                    learning['config']['data_file'] = os.path.basename(learning['config']['data_file'])
                del(learning['config']['segment_filename'])
                self.filedict.append(learning['config'])

        # Add a label for each varying parameter
        self.labels = []
        for key in self.filedict[0].keys() :
            if key != 'correct' and len(set([config[key] for config in self.filedict])) > 1 :
                self.labels.append(key)
        print self.labels

        self.frame = 0
        self.SetBackgroundColour(wx.NamedColour("WHITE"))
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.title = self.figure.suptitle(self.labels[0])
        self.Fit()
        self.background = self.axes.figure.canvas.copy_from_bbox(self.axes.bbox)
        self.colors = ['black', 'red', 'yellow', 'orange', 'blue', 'green', 'violet']
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)
        self.point_Refresh()

    def point_Refresh(self) :
        labels = [ label for label in self.labels if label != self.labels[self.frame] ]
        plots = []
        for f_dict in self.filedict : 
            current = [f_dict[label] for label in labels] 
            found = False
            for plot in plots :
                found = found or reduce((lambda x, (y1, y2) : x and (y1 == y2)), zip(current, plot), True)
            if not found :
                plots.append(current)
        self.title.set_text(self.labels[self.frame])
        
        self.canvas.restore_region(self.background)
        self.axes.cla()
        color = 0
        lines = []
        plots = sorted(plots, key=(lambda x: reduce((lambda y,z: y + " " + str(z)), x, "")))
        for plot in plots :
            vals = sorted([ (f_dict[self.labels[self.frame]], f_dict['correct']) for f_dict in self.filedict if \
                            reduce((lambda x_, (x,y) : x_ and (f_dict[x] == y)), zip(labels, plot), True)], key=(lambda x: x[0]))
            
            label = ''
            for (key,index) in zip(labels, range(len(labels))):
                if key != self.labels[self.frame] :
                    label = label + " " + key + " " + str(plot[index])

            if (isinstance(vals[0][0], (str,unicode))) :
                line = self.axes.plot([x for x in range(len(vals))],[x[1] for x in vals],
                                      color=self.colors[color % len(self.colors)],
                                      label=label)
            else :
                line = self.axes.plot([x[0] for x in vals],[x[1] for x in vals],
                                      color=self.colors[color % len(self.colors)],
                                      label=label)
                
            lines.append(line)
            color = color + 1
        self.axes.legend(loc='best')

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
