#!/usr/bin/python

# Lighthead-bot programm is a HRI PhD project at
#  the University of Plymouth,
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
conf package for the CONCEPT project.
versions >= 2.5
Copyright (C) 2009 frederic DELAUNAY, University of Plymouth (UK).
"""
"""
Global configuration system reading module. Reads file 'lightHead.conf'.
This module reads the global configuration file and checks missing definitions.
Configuration file search path order:
 1) current user's home directory (posix systems: $HOME)
 2) globlal system configuration file (posix: /etc/)
 3) any path defined by the system variable $(LIGHTHEAD_CONF)

Syntax is the python syntax.
This software package shall come with a default configuration file.
"""

import os, sys

MODULE=sys.modules[__name__]

NAME=None       # this is the one-file-takes-all approach to configuration

ERR_UNAVAILABLE="""No configuration file was found. Aborting!
 You can define %s system variable for complete filepath definition."""

LOADED_FILE=False

class LoadException(Exception):
    pass


# TODO: this should just be in the configuration file itself.
def get_unix_sockets(print_flag=False):
    """Try to get unix sockets from the loaded configuration.
    Returns: [ declared_unix_sockets ]
    """
    if not LOADED_FILE:
        load()
    entries=[getattr(MODULE,c) for c in dir(MODULE) if c.startswith('conn_')]
    sockets=[port for host, port in entries if type(port) == type("")]
    if print_flag:
        print " ".join(sockets)
    return sockets


def check_missing():
    """check for missing mandatory configuration entries.
    conf_required+NAME[:-5] (eg: conf_required_lighthead.py) is a module where
     required definitions are set. ie: if you need to make sure a specific entry
     is present in your config file.
    Returns: [missing_definitions]
    """
    global NAME
    if not NAME:
        raise LoadException('unset','conf.NAME has not been set')
    required_file = 'conf_required_'+NAME[:-5]
    try:
        exec 'from %s import REQUIRED' % required_file
    except ImportError,e:
        LOG.debug('could not find module %s => not enforcing any config entry')
    if not REQUIRED:
        return []
    return [ i for i in REQUIRED if i not in dir(MODULE) ]


def build_env():
    """Builds a string from the value of NAME using:
    * NAME's basename
    * upper case
    * translation of dot ('.') to underscore ('_')
    """
    global NAME
    return os.path.basename(NAME).upper().replace('.','_')


def build_paths():
    """Builds paths where conf file could be.
    Checks for a environment variable, name being built from build_env()
    """
    global NAME
    if not NAME:
        raise LoadException('unset','conf.NAME has not been set')

    conf_files=[]
    try:
        conf_files.append(os.path.join(os.path.expanduser('~/'), '.'+NAME))
    except OSError, err:
        raise LoadException(err, 'Cheesy OS error')
    else:
        conf_files.append(os.path.join('/etc', NAME))
        try:
            conf_files.append(os.environ[build_env()])
        except (OSError,KeyError):
            pass
    return conf_files


def load(raise_exception=True, reload=False):
    """Try to load 1st available configuration file, ignoring Subsequent calls
    unless reload is set to True.
    required_names: iterable of strings specifying variable names to be found.

    Returns: see check_missing()
    """
    global LOADED_FILE
    if reload:
        raise LoadException(LOADED_FILE, "reload of conf not coded yet")
    elif LOADED_FILE:
        return check_missing()

    for conf_file in build_paths():
        if os.path.isfile(conf_file):
            msg = None
            try:
                execfile(conf_file, globals())
                LOADED_FILE = conf_file
            except SyntaxError, err:
                msg = "error line %i." % err.lineno
            except Exception, e:
                msg = e
            else:
                break
            if msg and raise_exception:
                raise LoadException(conf_file, msg)
                break

    if LOADED_FILE == False and raise_exception:
        raise LoadException(conf_file, ERR_UNAVAILABLE % build_env())
    return check_missing()
