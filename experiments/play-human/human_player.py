#!/usr/bin/python
#
# You should have received a copy of the GNU General Public License
# along with comm module.  If not, see <http://www.gnu.org/licenses/>.
#

#
# Playing custom datafiles (.lpd) to remote submodules.
# The .lpd entries shall be sorted according to their 1st field (time).
#

import sys
import time
import comm
import conf
import threading
import signal

import logging
logging.basicConfig(level=logging.INFO, format=comm.FORMAT)

conf.load()

class moduleConnection(comm.BaseClient, threading.Thread):

  """Connection to the server"""
  def __init__(self, addr_port, name):
    threading.Thread.__init__(self)
    self._addr_port = addr_port
    self._name = name
    self._connected = threading.Event()
    self.start()
    self._connected.wait()

  def run (self):
    comm.BaseClient.__init__(self, self._addr_port)
    self.connect_and_run()
    
  def handle_connect(self):
    print "Module [" + self._name + "] Connected to %s:%s" % self.target_addr 
    self._connected.set()

  def handle_disconnect(self):
    print "Disconnect"
    exit(0)

  def handle_error(self, e):
    print "Communication error", e
    exit(0)
    
  def handle_timeout(self):
    print "timeout"
    exit(-1)
      
class interpretLDPFile():

  """Reads a data file got from xml2ldp.py and"""
  """ sends contents to appropriate endpoints."""
  def __init__(self, file, jump_first):
    """Small bufferized player"""
    self.read_and_play(file, jump_first)

  def read_and_play(self, file, jump_first):

    def read_and_parse(self, f):
      line, bIndex = "", f.tell()
      while not line.strip():
        line = f.readline()
      if bIndex == f.tell():
        return (0,None,None)
      frame_time, cmdline = line.split(':')
      cmd, argline = cmdline.split(None, 1)
      try:
        fct = getattr(self, "set_"+cmd)
      except AttributeError:
        print "command not available:", cmd
      return (float(frame_time), fct, argline)
        
    self.playing = True
    f = open(file)
    last_ftime = 0
    ftime, fct, args = read_and_parse(self,f)
    if jump_first:
      print "jumping to", ftime, "s."
    last_ftime = ftime
    start_time = time.time()
    start_time -= last_ftime
        
    while fct:
      if (time.time() - start_time) > ftime:
        print "**!!!** congestion detected at frame time", ftime
      
      print "sleep for", ftime - last_ftime, "s."
      time.sleep(ftime - last_ftime)
      fct(args)
      last_ftime = ftime
      ftime, fct, args = read_and_parse(self,f)
    f.close()
            
  def set_eyes(self, argline):
    """set gaze: vector3 normalized_angle time_in_s"""
    gaze.send_msg("orientation "+argline)

  def set_blink(self, argline):
    """set blink: duration in seconds"""
    face.send_msg("blink "+argline)
      
  def set_f_expr(self, argline):
    """set facial expression"""
    face.send_msg("f_expr "+argline)

def signal_handler(signal, frame):
  sys.exit(0)
        
if __name__ == "__main__":

  signal.signal(signal.SIGINT, signal_handler)
  
  gaze = moduleConnection((sys.argv[1], 4243), "Gaze")
  face = moduleConnection((sys.argv[1], 4244), "Face")

  interpretLDPFile(sys.argv[2], False)



