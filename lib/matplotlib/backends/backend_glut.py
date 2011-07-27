"""
This is a fully functional do nothing backend to provide a template to
backend writers.  It is fully functional in that you can select it as
a backend with

  import matplotlib
  matplotlib.use('Template')

and your matplotlib scripts will (should!) run without error, though
no output is produced.  This provides a nice starting point for
backend writers because you can selectively implement methods
(draw_rectangle, draw_lines, etc...) and slowly see your figure come
to life w/o having to have a full blown implementation before getting
any results.

Copy this to backend_xxx.py and replace all instances of 'template'
with 'xxx'.  Then implement the class methods and functions below, and
add 'xxx' to the switchyard in matplotlib/backends/__init__.py and
'xxx' to the backends list in the validate_backend methon in
matplotlib/__init__.py and you're off.  You can use your backend with::

  import matplotlib
  matplotlib.use('xxx')
  from pylab import *
  plot([1,2,3])
  show()

matplotlib also supports external backends, so you can place you can
use any module in your PYTHONPATH with the syntax::

  import matplotlib
  matplotlib.use('module://my_backend')

where my_backend.py is your module name.  Thus syntax is also
recognized in the rc file and in the -d argument in pylab, eg::

  python simple_plot.py -dmodule://my_backend

The files that are most relevant to backend_writers are

  matplotlib/backends/backend_your_backend.py
  matplotlib/backend_bases.py
  matplotlib/backends/__init__.py
  matplotlib/__init__.py
  matplotlib/_pylab_helpers.py

Naming Conventions

  * classes Upper or MixedUpperCase

  * varables lower or lowerUpper

  * functions lower or underscore_separated

"""

from __future__ import division

import OpenGL.GL as gl
import OpenGL.GLUT as glut

import os, sys
def fn_name(): return sys._getframe(1).f_code.co_name

import matplotlib
from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import RendererBase, GraphicsContextBase,\
     FigureManagerBase, FigureCanvasBase, NavigationToolbar2, cursors
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox, Affine2D


_frame, _timebase = 0,0
_debug = False
#_debug = True

class RendererGL(RendererBase):
    """
    The renderer handles drawing/rendering operations.

    This is a minimal do-nothing class that can be used to get started when
    writing a new backend. Refer to backend_bases.RendererBase for
    documentation of the classes methods.
    """
    def __init__(self, width, height, dpi):
        self.dpi = dpi
        self.width = width
        self.height = height

    def draw_path(self, gc, path, transform, rgbFace=None):
        return

    # draw_markers is optional, and we get more correct relative
    # timings by leaving it out.  backend implementers concerned with
    # performance will probably want to implement it
    def draw_markers(self, gc, marker_path, marker_trans,
                     path, trans, rgbFace=None):
        return

    # draw_path_collection is optional, and we get more correct
    # relative timings by leaving it out. backend implementers concerned with
    # performance will probably want to implement it
    def draw_path_collection(self, master_transform, cliprect, clippath,
                             clippath_trans, paths, all_transforms, offsets,
                             offsetTrans, facecolors, edgecolors, linewidths,
                             linestyles, antialiaseds):
        return

    # draw_quad_mesh is optional, and we get more correct
    # relative timings by leaving it out.  backend implementers concerned with
    # performance will probably want to implement it
    def draw_quad_mesh(self, master_transform, cliprect, clippath,
                        clippath_trans, meshWidth, meshHeight, coordinates,
                        offsets, offsetTrans, facecolors, antialiased,
                        showedges):
        return

    def draw_image(self, x, y, im, bbox, clippath=None, clippath_trans=None):
        return

    def draw_text(self, gc, x, y, s, prop, angle, ismath=False):
        return

    def flipy(self):
        return True

    def get_canvas_width_height(self):
        x,y,width,height = gl.glGetInteger(gl.GL_VIEWPORT)
        return width, height

    def get_text_width_height_descent(self, s, prop, ismath):
        return 1, 1, 1

    def new_gc(self):
        return GraphicsContextGL()

    def points_to_pixels(self, points):
        # if backend doesn't have dpi, eg, postscript or svg
        return points
        # elif backend assumes a value for pixels_per_inch
        #return points/72.0 * self.dpi.get() * pixels_per_inch/72.0
        # else
        #return points/72.0 * self.dpi.get()


class GraphicsContextGL(GraphicsContextBase):
    """
    The graphics context provides the color, line styles, etc...  See the gtk
    and postscript backends for examples of mapping the graphics context
    attributes (cap styles, join styles, line widths, colors) to a particular
    backend.  In GTK this is done by wrapping a gtk.gdk.GC object and
    forwarding the appropriate calls to it using a dictionary mapping styles
    to gdk constants.  In Postscript, all the work is done by the renderer,
    mapping line styles to postscript calls.

    If it's more appropriate to do the mapping at the renderer level (as in
    the postscript backend), you don't need to override any of the GC methods.
    If it's more appropriate to wrap an instance (as in the GTK backend) and
    do the mapping here, you'll need to override several of the setter
    methods.

    The base GraphicsContext stores colors as a RGB tuple on the unit
    interval, eg, (0.5, 0.0, 1.0). You may need to map this to colors
    appropriate for your backend.
    """
    pass



########################################################################
#
# The following functions and classes are for pylab and implement
# window/figure managers, etc...
#
########################################################################

def draw_if_interactive():
    """
    For image backends - is not required
    For GUI backends - this should be overriden if drawing should be done in
    interactive python mode
    """
    pass

def show():
    """
    For image backends - is not required
    For GUI backends - show() is usually the last line of a pylab script and
    tells the backend that it is time to draw.  In interactive mode, this may
    be a do nothing func.  See the GTK backend for an example of how to handle
    interactive versus batch mode
    """
    if _debug: print 'FigureCanvasGLUT.%s' % fn_name()
    #for manager in Gcf.get_all_fig_managers():
    #    manager.window.set_visible(True)
    if len(Gcf.get_all_fig_managers())>0:
        glut.glutMainLoop()


def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance
    """
    # if a main-level app must be created, this is the usual place to
    # do it -- see backend_wx, backend_wxagg and backend_tkagg for
    # examples.  Not all GUIs require explicit instantiation of a
    # main-level app (egg backend_gtk, backend_gtkagg) for pylab
    FigureClass = kwargs.pop('FigureClass', Figure)
    thisFig = FigureClass(*args, **kwargs)
    canvas = FigureCanvasGLUT(thisFig)
    manager = FigureManagerGLUT(canvas, num)
    return manager


class FigureCanvasGLUT(FigureCanvasBase):
    """
    The canvas the figure renders into.  Calls the draw and print fig
    methods, creates the renderers, etc...

    Public attribute

      figure - A Figure instance

    Note GUI templates will want to connect events for button presses,
    mouse movements and key presses to functions that call the base
    class methods button_press_event, button_release_event,
    motion_notify_event, key_press_event, and key_release_event.  See,
    eg backend_gtk.py, backend_wx.py and backend_tkagg.py
    """


    def __init__(self, figure):
        if _debug: print 'FigureCanvasGLUT.%s' % fn_name()
        FigureCanvasBase.__init__(self, figure)
        self.fps = None

    def on_reshape(self, width, height):
        if _debug: print 'FigureCanvasGLUT.%s' % fn_name()
        dpi = self.figure.dpi
        winch = width/dpi
        hinch = height/dpi
        self.figure.set_size_inches(winch, hinch)
        gl.glViewport( 0, 0, width, height )
        gl.glMatrixMode( gl.GL_PROJECTION )
        gl.glLoadIdentity( )
        gl.glOrtho( 0, width, 0, height, -1, 1 )
        gl.glMatrixMode( gl.GL_MODELVIEW )
        gl.glLoadIdentity( )


    def on_entry(self, state):
        if _debug: print 'FigureCanvasGLUT.%s' % fn_name()
        if state == glut.GLUT_ENTERED:
            FigureCanvasBase.enter_notify_event(self)
        elif state == glut.GLUT_LEFT:
            FigureCanvasBase.leave_notify_event(self)

    def on_mouse(self, button, state, x, y):
        if _debug: print 'FigureCanvasGLUT.%s' % fn_name()
        mapping = {glut.GLUT_LEFT_BUTTON   : 0,
                   glut.GLUT_MIDDLE_BUTTON : 1,
                   glut.GLUT_RIGHT_BUTTON  : 2}
        if state == glut.GLUT_DOWN:
            FigureCanvasBase.button_press_event(self, x, y, mapping[button])
        elif state == glut.GLUT_UP:
            FigureCanvasBase.button_release_event(self, x, y, mapping[button])

    def on_motion(self, x, y):
        if _debug: print 'FigureCanvasGLUT.%s' % fn_name()
        FigureCanvasBase.motion_notify_event(self, x, y)


    def on_keyboard(self, key, x, y):
        if _debug: print 'FigureCanvasGLUT.%s' % fn_name()
        FigureCanvasBase.key_press_event(self, key)

    def on_keyboard_up(self, key, x, y):
        if _debug: print 'FigureCanvasGLUT.%s' % fn_name()
        FigureCanvasBase.key_release_event(self, key)

#    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
#        if _debug: print 'FigureCanvasGLUT.%s' % fn_name()
#        if scroll_y > 0:
#            step = 1
#        else:
#            step = -1
#        FigureCanvasBase.scroll_event(self, x, y, step)
#        return True


    def on_draw(self):
        if _debug: print 'FigureCanvasGLUT.%s' % fn_name()
        self.draw()
        return True

    def draw(self):
        """
        Draw the figure using the renderer
        """
        global _frame, _timebase
	_frame = _frame+1
	time = glut.glutGet( glut.GLUT_ELAPSED_TIME )
        if (time - _timebase > 1000):
            fps = _frame*1000.0/(time-_timebase)
            print fps
            _timebase = time
            _frame = 0
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self._render_figure()
        self.toolbar.draw()
        glut.glutSwapBuffers( )


    def _render_figure(self):
        if _debug: print 'FigureCanvasGLUT.%s' % fn_name()
        self.renderer = self.get_renderer()
        self.figure.draw(self.renderer)

    def get_renderer(self):
        l, b, w, h = self.figure.bbox.bounds
        key = w, h, self.figure.dpi
        try: self._lastKey, self.renderer
        except AttributeError: need_new_renderer = True
        else:  need_new_renderer = (self._lastKey != key)
        if need_new_renderer:
            self.renderer = RendererGL(w, h, self.figure.dpi)
            self._lastKey = key
        return self.renderer


    # You should provide a print_xxx function for every file format
    # you can write.

    # If the file type is not in the base set of filetypes,
    # you should add it to the class-scope filetypes dictionary as follows:
    filetypes = FigureCanvasBase.filetypes.copy()
    filetypes['foo'] = 'My magic Foo format'

    def print_foo(self, filename, *args, **kwargs):
        """
        Write out format foo.  The dpi, facecolor and edgecolor are restored
        to their original values after this call, so you don't need to
        save and restore them.
        """
        pass

    def get_default_filetype(self):
        return 'foo'



class FigureManagerGLUT(FigureManagerBase):
    """
    Public attributes

    canvas      : The FigureCanvas instance
    num         : The Figure number
    toolbar     : The gtk.Toolbar  (gtk only)
    vbox        : The gtk.VBox containing the canvas and toolbar (gtk only)
    window      : The gtk.Window   (gtk only)
    """

    def __init__(self, canvas, num):
        if _debug: print 'FigureManagerGLUT.%s' % fn_name()

        width = int (canvas.figure.bbox.width)
        height = int (canvas.figure.bbox.height)


        glut.glutInit( sys.argv )
        glut.glutInitDisplayMode( glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH )
        glut.glutCreateWindow( "GLUT matplotlib backend" )
        glut.glutReshapeWindow( width, height )
        self.toolbar = NavigationToolbarGLUT(canvas)

        FigureManagerBase.__init__(self, canvas, num)
        self.canvas.toolbar = self.toolbar

        glut.glutIdleFunc(self.canvas.draw)
        glut.glutDisplayFunc(self.canvas.draw)
        glut.glutEntryFunc(self.canvas.on_entry)
        glut.glutKeyboardFunc(self.canvas.on_keyboard)
        glut.glutKeyboardUpFunc(self.canvas.on_keyboard_up)
        glut.glutMotionFunc(self.canvas.on_motion)
        glut.glutMouseFunc(self.canvas.on_mouse)
        glut.glutReshapeFunc(self.canvas.on_reshape)
        # glut.glutSpecialFunc()
        # glut.glutSpecialUpFunc()
        # glut.glutVisibilityFunc()

        def notify_axes_change(fig):
            if self.toolbar is not None:
                self.toolbar.update()
        self.canvas.figure.add_axobserver(notify_axes_change)

    def show(self):
        if _debug: print 'FigureManagerPyglet.%s' % fn_name()
        return

    def full_screen_toggle (self):
        if _debug: print 'FigureManagerPyglet.%s' % fn_name()
        self._full_screen_flag = not self._full_screen_flag
        self.window.set_fullscreen(self._full_screen_flag)
    _full_screen_flag = False


    def set_window_title(self, title):
        if _debug: print 'FigureManagerPyglet.%s' % fn_name()
        self.window.set_title(title)


class NavigationToolbarGLUT(NavigationToolbar2):
    def __init__(self, canvas):
        NavigationToolbar2.__init__(self, canvas)
    def _init_toolbar(self):
        pass
    def set_message(self, s):
        return
    def draw(self):
        return


########################################################################
#
# Now just provide the standard names that backend.__init__ is expecting
#
########################################################################


FigureManager = FigureManagerGLUT

