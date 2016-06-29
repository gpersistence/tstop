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


import argparse
import itertools
import functools
import os
import os.path
import sys
import csv
import json
import multiprocessing 

# Used to guarantee to use at least Wx2.8
import wxversion
wxversion.ensureMinimal('2.8')


import matplotlib
matplotlib.use('WXAgg')
import numpy

import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

import wx

from persistence.Datatypes.JSONObject import load_data, save_data
from persistence import PersistenceGenerator
from persistence import PersistenceKernel
from persistence.Datatypes.Segments import Segments, max_label
from persistence.Datatypes.PersistenceDiagrams import PersistenceDiagrams as PD
from persistence.Datatypes.Kernel import Kernel
colors = ['green','red','blue','orange','purple','yellow','black','grey']

class CanvasFrame(wx.Frame):

    def __init__(self, data_file, persistence_file, kernel_file):
        wx.Frame.__init__(self,None,-1,
                         'Data Visualization',size=(550,350))
        self.segment_file = data_file
        segments_json = load_data(self.segment_file, 'segments', None, None, "explore_persistence: ")
        if segments_json == None:
            print "Could not load segment file : %s" % (self.segment_file,)
            exit()
        self.segments = Segments.fromJSONDict(segments_json)

        self.persistence_file = persistence_file
        persistence_json = load_data(self.persistence_file, 'persistence', None, None, "explore_persistence: ")
        if persistence_json == None :
            print "Could not load persistence file : %s" % (self.persistence_file,)
            exit()
        self.persistences = PD.fromJSONDict(persistence_json)

        self.kernel_file = kernel_file
        kernel_json = load_data(self.kernel_file, 'kernel', None, None, "explore_persistence: ")
        if kernel_json == None :
            print "Could not load kernel file : %s" % (self.kernel_file,)
            exit()
        self.kernel = Kernel.fromJSONDict(kernel_json)

        self.kernel_config = self.kernel.config

        self.spans = []
        self.similarities = []

        for segment in self.segments.segments :
            window_stride = segment.window_stride
            label = max_label(segment.labels)
            data = []
            # We need to account for data overlap in the windows, which is not useful for this visualization
            for window in segment.windows :
                data.extend(window[0:window_stride])
            data.extend(segment.windows[-1][window_stride:])
            self.spans.append((label, segment.segment_start, data))
        self.mins = None
        self.maxs = None
        for  (l, start, xs) in self.spans :
            for x in xs :
                if self.maxs == None or x > self.maxs :
                    self.maxs = x
                if self.mins == None or x < self.mins :
                    self.mins = x
        
        self.labels = set([span[0] for span in self.spans])
        
        self.index = 1

        self.SetBackgroundColour(wx.NamedColour("WHITE"))
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.title = self.figure.suptitle("Data for Column %s" % (self.index,))

        self.sub_figure_a = Figure()
        self.sub_axes_a = self.sub_figure_a.add_subplot(111)
        self.sub_canvas_a = FigureCanvas(self, -1, self.sub_figure_a)
        self.sub_title_a = self.sub_figure_a.suptitle("Data for Segment beginning at %s, label %s" % (" ", " "))

        self.sub_figure_ap = Figure()
        self.sub_axes_ap = self.sub_figure_ap.add_subplot(111)
        self.sub_canvas_ap = FigureCanvas(self, -1, self.sub_figure_ap)
        self.sub_title_ap = self.sub_figure_ap.suptitle("Persistence for Segment beginning at %s, label %s" % (" ", " "))

        self.sub_figure_b = Figure()
        self.sub_axes_b = self.sub_figure_b.add_subplot(111)
        self.sub_canvas_b = FigureCanvas(self, -1, self.sub_figure_b)
        self.sub_title_b = self.sub_figure_b.suptitle("Data for Segment beginning at %s, label %s" % (" ", " "))

        self.sub_figure_bp = Figure()
        self.sub_axes_bp = self.sub_figure_bp.add_subplot(111)
        self.sub_canvas_bp = FigureCanvas(self, -1, self.sub_figure_bp)
        self.sub_title_bp = self.sub_figure_bp.suptitle("Persistence for Segment beginning at %s, label %s" % (" ", " "))

        self.click_cid_down = self.canvas.mpl_connect('button_press_event', self.mouseDown)
        self.click_cid_up = self.canvas.mpl_connect('button_release_event', self.mouseUp)
        self.click_cid_move = self.canvas.mpl_connect('motion_notify_event', self.mouseMove)
        self.sizer = wx.GridBagSizer(hgap=5, vgap=5)
        self.sizer.Add(NavigationToolbar2Wx(self.canvas), pos=(0,0), span=(1,2), flag=wx.EXPAND)
        self.sizer.AddGrowableCol(1,0)
        self.sizer.Add(self.canvas, pos=(1,0), span=(8,2), flag=wx.EXPAND)
        self.sizer.AddGrowableCol(9,0)
        self.sizer.Add(self.sub_canvas_a, pos=(9,0), span=(4,1), flag=wx.EXPAND)
        self.sizer.Add(self.sub_canvas_b, pos=(9,1), span=(4,1), flag=wx.EXPAND)
        self.sizer.AddGrowableCol(13,0)
        self.sizer.Add(self.sub_canvas_ap, pos=(13,0), span=(4,1), flag=wx.EXPAND)
        self.sizer.Add(self.sub_canvas_bp, pos=(13,1), span=(4,1), flag=wx.EXPAND)
        
        self.SetSizer(self.sizer)

        self.caption = self.figure.text(0.15, 0.8, "%s Samples Read" % (\
                                        reduce((lambda x,y: x+y),[len(span[2]) for span in self.spans], 0)))
        self.caption.set_backgroundcolor('#ffffff')
        self.Fit()
        self.background = self.axes.figure.canvas.copy_from_bbox(self.axes.bbox)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)
        self.click = 0
        self.index_a = None
        self.index_b = None
        self.point_Refresh()
        self.state = (None, 0)

    def mouseDown(self, event):
        pass

    def mouseUp(self, event):
        if (event != None and event.xdata != None) :
            click_segment = None
            click_index = None
            for (persistence, index) in itertools.izip(self.persistences.diagrams, 
                                                       range(len(self.persistences.diagrams))) :
                if persistence['segment_start'] < int(event.xdata) :
                    click_segment = persistence
                    click_index = index

            self.click = self.click + 1
            if self.click % 2 == 1 :
                self.index_a = click_index
            else :
                self.index_b = click_index
                    
            self.similarities = [(segment['segment_start'],segment['segment_size'],similarity) for (segment, similarity) in \
                                 itertools.izip(self.segments.segments, self.kernel.kernel_matrix[int(click_index)])]
            self.point_Refresh()
        else :
            self.caption.set_text("No segment at %s, %s" % (event.xdata, event.ydata))
                
        wx.PostEvent(self,wx.PaintEvent())

    def mouseMove(self, event):
        if (event != None and event.xdata != None) :
            click_segment = None
            for segment in self.segments.segments:
                if (segment['segment_start'] < int(event.xdata) and 
                    (segment['segment_start'] + segment['segment_size']) > int(event.xdata)) :
                    click_segment = segment
            similarity = None
            for (x, y, z) in self.similarities :
                if x < int(event.xdata) and (x + y) > int(event.xdata) :
                    similarity = z

            if (click_segment != None) :
                if similarity != None :
                    self.caption.set_text("Segment Labels %s start %s size %s similarity %s" % (\
                        click_segment['labels'], click_segment['segment_start'], click_segment['segment_size'], similarity))
                else :
                    self.caption.set_text("Segment Labels %s start %s size %s" % (\
                        click_segment['labels'], click_segment['segment_start'], click_segment['segment_size']))

        else :
            self.caption.set_text("No segment at %s, %s" % (event.xdata, event.ydata))
                                      
        wx.PostEvent(self,wx.PaintEvent())

    def point_Refresh(self) :
        self.canvas.restore_region(self.background)
        self.title.set_text("Activity Data for Column %s" % (self.index,))
        self.axes.cla()
        if len(self.similarities) != 0 :
            minimum = min([s[2] for s in self.similarities])
            maximum = max([s[2] for s in self.similarities])
            patches = []
            facecolors = []
            for (start, length, similar) in self.similarities :
                value = int((similar-minimum) * (255.0/(maximum - minimum)))
                strval = "#%0.2x%0.2x%0.2x" % (value, value, value)
                facecolors.append(strval)
                patches.append(Polygon([[start, self.mins], [start, self.maxs], 
                                        [start + length, self.maxs], [start + length, self.mins]] , 
                                       closed=True, edgecolor='none',
                                       fill=True, facecolor=strval, visible=True))
            p = PatchCollection(patches, match_original=True)
            self.axes.add_collection(p)

        for span in self.spans :
            xs = range(span[1], span[1]+len(span[2]))
            ys = [p for p in span[2]]
            self.axes.plot(xs,ys,color= colors[int(float(span[0])) % len(colors)])
                
        if self.index_a != None :
            self.sub_canvas_a.restore_region(self.background)
            self.sub_axes_a.cla()
            span = self.spans[self.index_a]
            xs = range(span[1], span[1]+len(span[2]))
            ys = [p for p in span[2]]
            self.sub_axes_a.plot(xs,ys,color="black")
            self.sub_title_a.set_text("Data for Segment beginning at %s, label %s" % (xs[0], span[0]))
            self.sub_canvas_ap.restore_region(self.background)
            self.sub_axes_ap.cla()
            persistence = self.persistences.diagrams[self.index_a]
            data = persistence.points
            xs = [d[0] for d in data if d[2] > 0]
            ys = [d[1] for d in data if d[2] > 0]
            max_val = max([max(xs),max(ys)])
            self.sub_axes_ap.scatter(xs,ys)
            self.sub_axes_ap.plot([0,max_val],[0,max_val],color="red")
            self.sub_title_ap.set_text("Persistence for Segment beginning at %s" % (persistence.segment_start))

        if self.index_b != None :
            self.sub_canvas_b.restore_region(self.background)
            self.sub_axes_b.cla()
            span = self.spans[self.index_b]
            xs = range(span[1], span[1]+len(span[2]))
            ys = [p for p in span[2]]
            self.sub_axes_b.plot(xs,ys,color="black")
            self.sub_title_b.set_text("Data for Segment beginning at %s, label %s" % (xs[0], span[0]))
            self.sub_canvas_bp.restore_region(self.background)
            self.sub_axes_bp.cla()
            persistence = self.persistences.diagrams[self.index_b]
            data = persistence.points
            xs = [d[0] for d in data if d[2] > 0]
            ys = [d[1] for d in data if d[2] > 0]
            max_val = max([max(xs),max(ys)])
            self.sub_axes_bp.scatter(xs,ys)
            self.sub_axes_bp.plot([0,max_val],[0,max_val],color="red")
            self.sub_title_bp.set_text("Persistence for Segment beginning at %s" % (persistence.segment_start))


    def KeyEvent(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_LEFT :
            pass
        elif keycode == wx.WXK_RIGHT :
            pass
        else :
            pass
        event.Skip()
            
    def OnPaint(self, event):
        paint_dc = wx.PaintDC(self)
        self.canvas.draw()
        self.sub_canvas_a.draw()
        self.sub_canvas_b.draw()
        self.sub_canvas_ap.draw()
        self.sub_canvas_bp.draw()

class App(wx.App):
    def __init__(self, arg, data_file, persistence_file, kernel_file):
        self.data_file = data_file
        self.persistence_file = persistence_file
        self.kernel_file = kernel_file
        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.data_file, self.persistence_file, self.kernel_file)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def main(argv) :
    parser = argparse.ArgumentParser(description='Data Visualization to guesstimate segment sizes')
    parser.add_argument('-d', '--data-file', help="Segment Data to examine")
    parser.add_argument('-p', '--persistence-file', help="Persistence Data for segments")
    parser.add_argument('-k', '--kernel-file', help="Kernel Similarity for persistence")
    args = vars(parser.parse_args(argv[1:]))
    current_dir = os.getcwd()
    if (args['data_file'][0] == '~') :
        data_filename        = os.path.expanduser(args['data_file'])
    elif (args['data_file'][0] != '/') :
        data_filename        = "%s/%s" % (current_dir, args['data_file'])
    else :
        data_filename        = args['data_file']

    if (args['persistence_file'][0] == '~') :
        persistence_filename        = os.path.expanduser(args['persistence_file'])
    elif (args['persistence_file'] != '/') :
        persistence_filename        = "%s/%s" % (current_dir, args['persistence_file'])
    else :
        persistence_filename        = args['persistence_file']

    if (args['kernel_file'][0] == '~') :
        kernel_filename        = os.path.expanduser(args['kernel_file'])
    elif (args['kernel_file'] != '/') :
        kernel_filename        = "%s/%s" % (current_dir, args['kernel_file'])
    else :
        kernel_filename        = args['kernel_file']

    try:
        app = App(0, data_filename, persistence_filename, kernel_filename)
        app.MainLoop()

    except KeyboardInterrupt:
        print "Caught cntl-c, shutting down..."
        exit(0)
        

if __name__ == "__main__":
        main(sys.argv)
