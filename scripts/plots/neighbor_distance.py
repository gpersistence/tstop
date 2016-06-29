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


import multiprocessing
import argparse
import os
import sys
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
from persistence.Datatypes.Distances import Distances, Distance

class CanvasFrame(wx.Frame):

    def __init__(self, distances, segment_info):
        wx.Frame.__init__(self,None,-1,
                         'Persistence Diagram Neighbor Distance', size=(1920,550))
        self.distances = distances
        self.xs = range(len(self.distances))
        self.SetBackgroundColour(wx.NamedColour("WHITE"))
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.segment_info = segment_info
        self.index = 0

        self.spans = []
        span_start = 0
        for i in range(1,len(self.segment_info)):
            if self.segment_info[i-1].max_label() != self.segment_info[i].max_label() :
                self.spans.append((span_start, i-1, self.segment_info[i-1].max_label()))
                span_start = i
        self.spans.append((span_start, i-1, self.segment_info[i-1].max_label()))
        self.labels = list(set([s.max_label() for s in self.segment_info]))
        self.labels.sort()
        self.axes.set_title("Segment %s file %s start %s label %s distance %s" % (self.index, 
                                                                                  self.segment_info[self.index].filename, 
                                                                                  self.segment_info[self.index].segment_start, 
                                                                                  self.segment_info[self.index],
                                                                                  self.distances[self.index].mean))
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(NavigationToolbar2Wx(self.canvas), 1, wx.LEFT | wx.TOP | wx.GROW)
        self.sizer.Add(self.canvas, 8, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)

        self.background = self.axes.figure.canvas.copy_from_bbox(self.axes.bbox)
        self.colors = ['red', 'green', 'yellow', 'violet', 'orange', 'blue', 'black' ]
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)
        print self.spans

        self.point_Refresh()

    def point_Refresh(self) :
        lines = [] 
        self.canvas.restore_region(self.background)
        self.axes.cla()
        self.axes.set_title("Segment %s file %s start %s label %s distance %s" % (self.index, 
                                                                                  self.segment_info[self.index].filename, 
                                                                                  self.segment_info[self.index].segment_start, 
                                                                                  self.segment_info[self.index].labels,
                                                                                  self.distances[self.index].mean))
        max_val = 0
        for span in self.spans :
            xs_0 = self.xs[span[0]:span[1]+1]
            ys_0 = [self.distances[i].mean for i in xs_0]
            line = self.axes.plot(xs_0, ys_0, self.colors[self.labels.index(span[2]) % len(self.colors)])
            lines.append(line)
            max_val = max(ys_0 + [max_val])

        
        line = self.axes.plot([self.index, self.index], [0,max_val], 'r')
        lines.append(line)

    def KeyEvent(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_LEFT :
            self.index = (self.index - 1) % len(self.distances)
	    self.point_Refresh()
            wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_RIGHT :
            self.index = (self.index + 1) % len(self.distances)
	    self.point_Refresh()
	    wx.PostEvent(self,wx.PaintEvent())
        else :
            event.Skip()
            
    def TimeEvent(self, event) :
        self.point_Refresh()
        wx.PostEvent(self,wx.PaintEvent())

    def OnPaint(self, event):
        paint_dc = wx.PaintDC(self)
        self.canvas.draw()

class App(wx.App):
    def __init__(self, arg, distances, segment_info):
        self.distances = distances
        self.segment_info = segment_info
        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.distances, self.segment_info)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def display(distances, segment_info):
    app = App(0, distances, segment_info)
    app.MainLoop()

def main(argv) :
    current_dir = os.getcwd()
    parser = argparse.ArgumentParser(description="utility to plot distance persistence diagram")
    parser.add_argument("-d", "--distances")

    args = parser.parse_args(argv[1:])
    if args.distances != None :
        distances = Distances.fromJSONDict(load_data(args.distances, "distances", None, None, argv[0]+": "))
        segment_info = distances.segment_info
    else :
        print "You must supply a distances filename"
        sys.exit(1)

    processes = []
    try:
        display_thread = \
          multiprocessing.Process(target=display, 
                                  args=([distances.distances[i][i+1] for i in range(len(distances.distances)-1)], segment_info))
        display_thread.start()
        processes.append(display_thread)
        display_thread.join()
    except KeyboardInterrupt:
        print "Caught cntl-c, shutting down..."
        exit(0)
        

if __name__ == "__main__":
        main(sys.argv)
