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

usage = "usage: python activity_persistence.py [<save file>] | " \
        "[<data file> <segment size> <segment stride> <window size> " \
        "<window stride> <data index> <label index> [<save file>]]"

from Segment import SegmentFileDescriptor
from PersistenceGenerator import PersistenceGenerator
class CanvasFrame(wx.Frame):

    def __init__(self, persistences, num_segments, save_dir):
        wx.Frame.__init__(self,None,-1,
                         'Segment 0',size=(550,350))
        self.persistences = persistences
        self.num_segments = num_segments
        self.point_array = [None for x in range(self.num_segments)]
        self.frame = 0
        self.SetBackgroundColour(wx.NamedColour("WHITE"))
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)

        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.title = self.figure.suptitle("No Segment Loaded for Segment 0")
        self.Fit()
        self.background = self.axes.figure.canvas.copy_from_bbox(self.axes.bbox)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_UP, self.KeyEvent)
        self.pipeThread = threading.Thread(target = self.emptyPipe)
        self.pipeThread.daemon = True
        self.pipeThread.start()
        self.save_dir = save_dir

    def emptyPipe(self) :
        while (True) :
            if (self.persistences.poll(0.025)) :
                (index, points, segment, segment_dict) = self.persistences.recv()
                self.point_array[index] = (points, segment, segment_dict)
                if (self.save_dir != None) :
                    # Create PNG Plot of data
                    figure_file = Figure()
                    from matplotlib.backends.backend_agg import FigureCanvasAgg
                    canvas_file = FigureCanvasAgg(figure_file)
                    axes_file = figure_file.add_subplot(111)
                    figure_title = figure_file.suptitle("Segment of size %s starting at %s\nWindow size %d stride %s" % 
                                                        (segment_dict['segment size'], segment_dict['segment start'],
                                                         segment_dict['window size'], segment_dict['window stride']))
                    x = [p[0] for p in points if p[2] != 0]
                    y = [p[1] for p in points if p[2] != 0]
                    max_xy = max(max(x), max(y))
                    axes_file.scatter(x, y, color='red', s=50)
                    axes_file.plot([0,max_xy],[0,max_xy],color='black')
                    figure_file.savefig("%s/%05d.png" % (self.save_dir,index))
                    # Save off the persistence
                    segment_dict['persistence'] = points
                    with open("%s/%05d.json" % (self.save_dir, index), 'w') as p_save :
                        json.dump(segment_dict, p_save)
                if (index == self.frame) :
                    self.point_Refresh()
                    wx.PostEvent(self,wx.PaintEvent())

    def point_Refresh(self) :
        if (self.point_array[self.frame] != None) :
            (points,segment,segment_dict) = self.point_array[self.frame]
            self.title.set_text("Segment of size %s starting at %s\nWindow size %d stride %s" % 
                                (segment_dict['segment size'], segment_dict['segment start'],
                                 segment_dict['window size'], segment_dict['window stride']))
            x = [p[0] for p in points if p[2] != 0]
            y = [p[1] for p in points if p[2] != 0]
            max_xy = max(max(x), max(y))

            self.canvas.restore_region(self.background)
            self.axes.cla()
            self.axes.scatter(x, y, color='red', s=50)
            self.axes.plot([0,max_xy],[0,max_xy],color='black')
        else :
            self.title.set_text("We have not finished computation for frame %s" % (self.frame,))
            self.axes.cla()

    def KeyEvent(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_LEFT :
            if ( self.frame > 0 ) :
                self.frame = self.frame - 1
                self.SetTitle("Segment %s" %(self.frame,))
                self.point_Refresh()
                wx.PostEvent(self,wx.PaintEvent())
        elif keycode == wx.WXK_RIGHT :
            if ( self.frame < self.num_segments - 1) :
                self.frame = self.frame + 1
                self.SetTitle("Segment %s" %(self.frame,))
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
    def __init__(self, arg, persistences, num_segments, save_dir):
        self.persistences = persistences
        self.num_segments = num_segments
        self.save_dir = save_dir
        wx.App.__init__(self,0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame(self.persistences, self.num_segments, self.save_dir)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

def display(persistences, num_segments, save_dir):
    app = App(0, persistences, num_segments, save_dir)
    app.MainLoop()

def main(argv) :
    current_dir = os.getcwd()
    save_dir = None
    if (len(argv) == 8 or len(argv) == 9) :
        data_file      = argv[1]
        segment_size   = int(argv[2])
        segment_stride = int(argv[3])
        window_size    = int(argv[4])
        window_stride  = int(argv[5])
        data_index     = int(argv[6])
        label_index    = int(argv[7])
        if (len(argv) == 9) :
            save_dir = argv[8]
    elif (len(argv) == 2):
        save_dir = argv[1]
    else :
        print usage
        exit(0)

    if (save_dir != None) :
        if (save_dir[0] == '~') :
            save_dir = os.path.expanduser(save_dir)
        elif (save_dir[0] != '/') :
            save_dir = "%s/%s" % (current_dir, save_dir)
        if (os.path.exists(save_dir) and not os.path.isdir(save_dir)) :
            print "%s exists and is not a directory!"
            print usage
            exit(0)
        elif (not os.path.exists(save_dir)) :
            try :
                os.makedirs(save_dir)
            except OSError as e:
                print "Could not make directory %s (err: %s)" % (save_dir, errno.errorcode[e.errno])
                exit(0)

        if (data_file != None) :
            segments = SegmentFileDescriptor("%s/json" % save_dir, None, data_file, segment_size, 
                                             segment_stride, window_size, 
                                             window_stride, data_index, label_index)
        else :
            segments = SegmentFileDescriptor.fromSegmentFile("%s/json" % save_dir)
    else :
        segments = SegmentFileDescriptor(None, data_file, segment_size, 
                                         segment_stride, window_size, 
                                         window_stride, data_index, label_index)



    processes = []
    try:
        pg = PersistenceGenerator(segments)
        pg.start()
        processes.append(pg.thread)
        display_thread = \
          multiprocessing.Process(target=display, 
                                  args=(pg.pipe_out, segments.getSegmentCount(), save_dir))
        display_thread.start()
        processes.append(display_thread)
        display_thread.join()
    except KeyboardInterrupt:
        print "Caught cntl-c, shutting down..."
        exit(0)
        

if __name__ == "__main__":
        main(sys.argv)
