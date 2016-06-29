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

from persistence.Datatypes.JSONObject import load_data, save_data
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams as PD
class CanvasFrame(wx.Frame):

    def __init__(self, argv):
        wx.Frame.__init__(self,None,-1,
                         'Segment Size',size=(550,350))
        parser = argparse.ArgumentParser(description="utility to plot a persistence diagram")
        parser.add_argument('file')
        self.args = vars(parser.parse_args(argv[1:]))
        self.file = self.args['file']
        pf_json = load_data(self.file, 'persistence', None, None, None)
        if pf_json == None :
            print "Could not load persistence file : %s" % (self.args['file'],)
            exit()
        self.persistences = Persistences.fromJSONDict(pf_json)
        
        self.SetBackgroundColour(wx.NamedColour("WHITE"))
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(NavigationToolbar2Wx(self.canvas), 1, wx.LEFT | wx.TOP | wx.GROW)
        self.sizer.Add(self.canvas, 8, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()
        self.background = self.axes.figure.canvas.copy_from_bbox(self.axes.bbox)
        self.colors = ['black', 'red', 'yellow', 'orange', 'blue', 'green', 'violet']
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)
        self.index = 0
        self.point_Refresh()

    def point_Refresh(self) :
        lines = [] 
        self.canvas.restore_region(self.background)
        self.axes.cla()
        p = self.persistences['persistences'][self.index].points
        xs_0 = [point[0] for point in p if point[2]==0]
        ys_0 = [point[1] for point in p if point[2]==0]
        line = self.axes.plot(xs_0, ys_0, 'bo')
        lines.append(line)
        xs_1 = [point[0] for point in p if point[2]==1]
        ys_1 = [point[1] for point in p if point[2]==1]
        line = self.axes.plot(xs_1, ys_1, 'r+')
        lines.append(line)
        max_val = max([max(xs_0) if len(xs_0) != 0 else 0.0,\
                       max(ys_0) if len(ys_0) != 0 else 0.0,\
                       max(xs_1) if len(xs_1) != 0 else 0.0,
                       max(ys_1) if len(ys_1) != 0 else 0.0])
	line = self.axes.plot([0,max_val],[0,max_val],'-')
        lines.append(line)
        print self.persistences['persistences'][self.index].labels
        self.Fit()

    def KeyEvent(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_LEFT :
            self.index = (self.index - 1) % len(self.persistences['persistences'])
	    self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())
	    print self.index
        elif keycode == wx.WXK_RIGHT :
            self.index = (self.index + 1) % len(self.persistences['persistences'])
	    self.point_Refresh()
	    wx.PostEvent(self,wx.PaintEvent())
            print self.index
        else :
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
