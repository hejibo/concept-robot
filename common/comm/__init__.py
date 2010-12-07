#!/usr/bin/python

# Lighthead-bot programm is a HRI PhD project at the University of Plymouth,
#  a Robotic Animation System including face, eyes, head and other
#  supporting algorithms for vision and basic emotions.  
# Copyright (C) 2010 Frederic Delaunay, frederic.delaunay@plymouth.ac.uk

#  This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.

#  You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
comm package for python.
versions >= 2.5
Copyright (C) 2009 frederic DELAUNAY, University of Plymouth (UK).
"""
"""
A fully functional template server and associated client talking ASCII:
Provides async socket-based communication layer for modules + logging support.
Look at exemple.py for an overview.

recognized module communication arguments:
client mode: [module_id=ip_address:port]
server mode: [interface_address:port]
"""

__author__  = "frederic Delaunay f dot d at chx-labs dot org"
__status__  = "beta"
__version__ = "0.3"
__date__    = "$$"

import os
import socket
import select
import logging

import SocketServer
# removes port availability delay
SocketServer.TCPServer.allow_reuse_address = True

LOGFORMAT = "%(lineno)4d:%(filename).21s\t-%(levelname)s-\t%(message)s"
# create our logging object and set log format
LOG = logging.getLogger(__package__)

class ProtocolError(Exception):
    """Base Exception class for protocol error.
    Failed transmissions shall raise exceptions inherting from this class.
    """
    pass

class CmdError(Exception):
    """Base Exception class for error in command processing.
    Failed commands shall raise exceptions inherting from this class.
    """
    pass

class ClassError(Exception):
    """Exception for dealing with type generation"""
    pass


class BaseServer(object):
    """Allows using a single threaded approach to SocketServer.
    See set_hooks()'s docstring for how to use it.
    Also allows user classes not to inherit from anything (see create_server() )
    """
    def __init__(self):
        # set default looping behaviour for comm.RequestHandler
        self.handler_looping = True
        self.clients = []

    def finish_request(self, request, client_addr):
        """Hook of SocketServer function so we can set a connection timeout."""
        LOG.debug('finish_request hook')
        self.RequestHandlerClass(request, client_addr, self)
        request.settimeout(self.handler_timeout)

    def close_request(self, request):
        LOG.debug('close_request hook (ignoring close)')
        pass

    def set_hooks(self, obj, looping, timeout):
        """Hooks finish_request and close_request for SocketServer to behave as
        we want:
        * not blocking in the Handler's __init__
        * not closing connection after __init__
        """
        self.handler_looping = looping
        self.handler_timeout = timeout
        if looping:
            return
        cls = obj.__class__
        import types
        # disable closing of socket while we're still on it (ugly, I know..)
        obj.finish_request = types.MethodType(BaseServer.finish_request,obj,cls)
        obj.close_request  = types.MethodType(BaseServer.close_request, obj,cls)
        LOG.debug('overriden finish_request and close_request')

    def threading_lock(self):
        """Transparent threading support."""
        """When handlers are threaded, it's good to have a way to sync them."""
        pass

    def threading_unlock(self):
        """Transparent threading support."""
        pass


class BaseComm:
    """Basic protocol handling and command-to-function resolver. This is the
     base class for a local client connecting to a server (BaseClient) or for a
     handler of a remote client connecting to the local server (RequestHandler).
    """

    CMD_PREFIX = "cmd_"

    def __init__(self):
        self.command = ''

    def read_once(self, timeout=0):
        """Non-blocking call for processing client commands (see __init__).
        No check for self.running.
        Return: False on error
        """
        r, w, e = select.select([self.request], [], [self.request], timeout)
        if not r: #and not self.handle_timeout():
            return True
        if e:
            self.handle_error()
            return self.abort()
        try:
            buff = self.request.recv(1024)
            if not buff:
                return self.abort()
            self.command += buff
        except socket.error, e:
            self.handle_error(e)
            return False
        self.command = self.command[self.process(self.command):]
        return True

    def read_while_running(self):
        """Blocking call for processing of client commands (see __init__).
        Returns if self.running is True.
        """
        self.running = True
        while self.running and self.read_once():
            pass

#    def handle_timeout(self):
#        """called on timeout from select.
#        (there's actually better ways to do this I'm sure, like Exceptions)"""
#        LOG.debug("timeout on select for %s", self.client_address)

    def handle_notfound(self, cmd, args):
        """When a method (a command) is not found in self. See process().
        To be overriden.
        """
        LOG.debug("function %s not found in %s [args: '%s']", cmd, self, args)

    def handle_error(self, e):
        """Callback for connection error.
        """
        LOG.warning("Connection error :%s", e)

    def parse_cmd(self, cmdline):
        cmd_tokens = cmdline.split(None,1) # keep 1
        cmd, args = self.CMD_PREFIX+cmd_tokens.pop(0),\
                    cmd_tokens and cmd_tokens[0] or ""
        try:
            try:
                bound_fct = getattr(self, cmd)
            except AttributeError:
                self.handle_notfound(cmd, args)
            else:
                bound_fct(args)
        except Exception, e:
            LOG.warning("%s> unsuccessful command '%s' [%s]",
                        self.request.fileno(), cmdline, e)
            if LOG.getEffectiveLevel() == logging.DEBUG:
                LOG.debug('=' * 42)
                import traceback;
                LOG.debug(traceback.format_exc())

    def process(self, command):
        """Command dispatcher function.

        Tokenize command and calls 'cmd_ + 1st_token' function defined in self.
         Calls self.handle_notfound if the built function name isn't defined.
         Function is called with remaining tokens (array) as one argument.
         Simultaneous commands (called within the same step) can be issued
          linking them with '&&'.

        command: string of text to be parsed
        Returns the number of bytes read.
        """        
        length = 0
        buffered = ''
        LOG.debug("%s> command [%iB]: '%s'",
                  self.request.fileno(), len(command), command)

        for cmdline in command.splitlines(True):
            length += len(cmdline)
            cmdline = cmdline.strip()
            if not cmdline or cmdline.startswith('#'):
                continue
            if cmdline.endswith('\\'):
                buffered += cmdline[:-1]
                continue
            cmdline = buffered + cmdline
            buffered = ''
            for cmd in cmdline.split('&&'):
                self.parse_cmd(cmd)
        return length

    def send_msg(self, msg):
        """Sends msg with a trailing \\n as required by the protocol."""
        LOG.debug("sending %s\n", msg)
        self.request.send(msg+'\n')

    def cmd_bye(self, args):
        """Disconnects that client."""
        self.running = False
    cmd_EOF = cmd_bye
        

# SocketServer.BaseRequestHandler is just a pain. As it's rather small, we have 
#  our own version inspired from it.
class RequestHandler(BaseComm):
    """Instancied on successful connection to the server: a remote client.

    Reads data from self.request and adds default functions :
     cmd_shutdown, cmd_clients and cmd_verb.
    If needed, define your own protocol handler overriding BaseComm.process.
    """

    def __init__(self, request, client_address, server):
        BaseComm.__init__(self)
        self.request = request
        self.client_address = client_address
        self.server = server

    def run(self):
        try:
            self.setup()
            self.handle()
            self.finish()
        finally:
            import sys
            sys.exc_traceback = None    # Help garbage collection

    def setup(self):
        """Overrides SocketServer"""
        self.server.clients.append(self)
        # check if we want to block in self.handle()
        self.handle = self.server.handler_looping and \
                      self.read_while_running or self.read_once
        self.addr_port = type(self.client_address) == type("") and \
            ("localhost", "UNIX Socket") or self.client_address
        LOG.info("%i> connection accepted from %s on "+str(self.addr_port[1]),
                 self.request.fileno(), self.addr_port[0])

    def finish(self):
        """Overrides SocketServer"""
        if not self.server.handler_looping:
            return
        LOG.info("%i> connection terminated : %s on "+str(self.addr_port[1]),
                 self.request.fileno(), self.addr_port[0])
        self.server.clients.remove(self)

    def abort(self):
        """For read_while_running"""
        LOG.debug("communication with remote client has been interrupted")
        self.running = False
        return False

    def cmd_shutdown(self, args):
        """Disconnects all clients and terminate the server process."""
        if self.server == None:
            raise CmdError("cannot shutdown server")
        LOG.info("%s> stopping server", self.request.fileno())
        self.server.shutdown()
        self.running = False

    def cmd_clients(self, args):
        """Lists clients currently connected."""
        LOG.info("%s> listing %i clients.",
                 self.request.fileno(), len(self.server.clients))
        clients_infos = []
        for cl in self.server.clients:
            clients_infos.append( type(cl.client_address) == type("") and
                                  (cl.request.fileno(), "UNIX", "localhost") or
                                  (cl.request.fileno(), cl.client_address[1],
                                                    cl.client_address[0]) )
        clients_infos.sort()
        obuffer = "clients: %i connected: (ID, PORT, ADDR)"%(len(clients_infos))
        for client_info in clients_infos:
            obuffer += "\\\n> %s:  %5s  %s" % client_info
        self.send_msg(obuffer)
        
    def cmd_verb(self, args):
        """Changes LOG verbosity level."""
        if not args:
            self.send_msg("CRITICAL 50\nERROR	 40\nWARNING  30\n"
                          "INFO     20\nDEBUG	 10\nNOTSET    0")
        else:
            LOG.warning("changing log level to %s", args[0])
            LOG.setLevel(args[0])
        self.send_msg("verb is %s now" % LOG.getEffectiveLevel())


class BaseClient(BaseComm):
    """Client creating a connection to a (remote) server.

       Remember it's impossible to use the file interface of the socket while
        setting a socket timeout.
    """
    def __init__(self, addr_port):
        BaseComm.__init__(self)
        family, self.target_addr = get_conn_infos(addr_port)
        self.request = socket.socket(family)
        self.connected = False

    def set_timeout(self, timeout):
        self.request.settimeout(timeout)

    def disconnect(self):
        """Set flag for disconnection.
        You need to set a timeout to connect_and_run() or read_until_done()"""
        self.running = False

    def connect_and_run(self):
        try:
            self.request.connect(self.target_addr)
        except socket.error, e:
            self.handle_error('%s with %s:%i' % (
                    e, self.target_addr[0], self.target_addr[1]))
            self.request.close()
            return False
        self.connected = True
        self.handle_connect()

	try:
	    self.read_while_running()
	except select.error, e:
	    self.handle_error(e)
	finally:
            self.request.close()
            self.connected = False
            self.handle_disconnect()
        return True

    def abort(self):
        """For read_while_running"""
        LOG.debug("communication with remote server has been interrupted")
        self.running = False

    def handle_connect(self):
        """Callback for client successful connection to (remote) server.
        """
        LOG.debug('client connected to remote server %s', self.target_addr)

    def handle_timeout(self):
        """Callback for timeout on waiting for input
        Returning False would skip recv()
        """
        pass

    def handle_disconnect(self):
        """Callback after client disconnection to (remote) server.
        """
        LOG.debug('client disconnected from remote server %s', self.target_addr)


def set_default_logging(debug=False):
    """This function does nothing if the root logger already has
    handlers configured."""
    logging.basicConfig(level=(debug and logging.DEBUG or logging.INFO),
                        format=LOGFORMAT)


def get_conn_infos(addr_port):
    if hasattr(socket, "AF_UNIX") and \
            type(addr_port[1]) == type("") and \
            addr_port[0] in ["127.0.0.1", "localhost"]:
        return socket.AF_UNIX, addr_port[1]
    return socket.AF_INET, addr_port


SERVER_CLASSES = {
    type(42): {'udp': { True : SocketServer.ThreadingUDPServer,
                        False: SocketServer.UDPServer },
               'tcp': { True : SocketServer.ThreadingTCPServer,
                        False: SocketServer.TCPServer }
               },
    type(''): {'':{True : hasattr(SocketServer,"ThreadingUnixStreamServer") and\
                   SocketServer.ThreadingUnixStreamServer,
                   False: hasattr(SocketServer,"UnixStreamServer") and\
                   SocketServer.UnixStreamServer }
               },
    }

def getBaseServerClass(addr_port, threaded):
    """Returns the appropriate base class for server according to addr_port"""
    """protocol can be specified using a prefix from 'udp:' or 'tcp:' in the
     port field (eg. 'udp:4242'). Default is udp."""
    D_PROTO = 'tcp'
    addr, port = addr_port
    if type(port) == type(''):
        proto, port = port.find(':') > 0 and port.split(':') or (D_PROTO, port)
        if port.isdigit():
            port = int(port)
            addr_port = (addr, port)
    else:
        proto = D_PROTO
    try:
        srv_class = SERVER_CLASSES[type(port)][proto][threaded]
        if type(port) == '' and \
           srv_class == isinstance(srv_class, SocketServer.UnixStreamServer):
            addr_port = addr_port[1]
        LOG.debug('address-port: %s, selected server class: %s',
                  addr_port, srv_class)
        return addr_port, srv_class
    except KeyError:
        raise Exception('No suitable server class from addr_port. Check conf.')


def create_requestHandler_class(handler_class, threaded=False):
    """Creates a new (compound) type of RequestHandler suitable for inclusion to
    a compound server. Users can simply ignore networking in the class code.
    """
    if not issubclass(handler_class, object):
        raise ClassError('class %s must inherit from object' % handler_class)

    def requestHandler_init(self, request, client_addr, server):
        """Call all subclasses initializers"""
        LOG.debug('initializing compound request handler %s', self.__class__)
        # add runtime support for threading (sending clients)
        if threaded:
            import threading
            self._threading_lock = threading.Lock()
            def th_send_msg(self, msg):
                self._threading_lock.acquire()
                BaseComm.send_msg(self, msg)
                self._threading_lock.release()
        # most of this mess because it can be done and I have fun doing it
        RequestHandler.__init__(self, request, client_addr, server)
        handler_class.__init__(self)
        self.run()

    return type(handler_class.__name__+'RequestHandler',
                (handler_class, RequestHandler),
                {"__init__":requestHandler_init})

def create_server(ext_class, handler_class, addr_port, threaded=True):
    """Creates a new (compound) type of server according to addr_port, also
     creates a new type of RequestHandler so users don't inherit from anything.

        ext_class: extension class to be a base of the new type.
        handler_class: class to be instancied on accepted connection.
        addr_port: (address, port). port type is relevant, see conf module.
    """
    if not issubclass(ext_class, object):
        raise ClassError('class %s must inherit from object' % ext_class)

    addr_port, base_class = getBaseServerClass(addr_port, threaded)
    mixed_handler_class = create_requestHandler_class(handler_class,
                                                      threaded)
    def server_init(self, addr_port, handler_class):
        """Call all subtypes initializers and add support for threading locks"""
        # add runtime support for threading (accessing server)
        if threaded:
            import threading
            self._threading_lock = threading.Lock()
            def threading_lock(self):
                self._threading_lock.acquire()
            def threading_unlock(self):
                self._threading_lock.release()
        LOG.debug('initializing compound server %s', self.__class__)
        # most of this mess because of parameters in SocketServer.__init__
        base_class.__init__(self, addr_port, handler_class)
        BaseServer.__init__(self)
        ext_class.__init__(self)

    return type(ext_class.__name__+base_class.__name__,
                (base_class, BaseServer, ext_class),
                {"__init__":server_init})(addr_port, mixed_handler_class)
