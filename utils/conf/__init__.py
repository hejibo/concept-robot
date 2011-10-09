#!/usr/bin/python
# -*- coding: utf-8 -*-

# LightHead programm is a HRI PhD project at the University of Plymouth,
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
Configuration file reading and setting module..

The main function is load() which relies on set_name(project_name) to set the
 name of the project, thus setting the name of the config file to open.

The NAME variable:
------------------
NAME is a string identifying your project.
That string is filtered by isalnum() for portability reasons. Filtered
 characters are replaced with '_'.
From this *filtered* NAME, the configuration file <NAME>.conf is searched.

That file is a python script, declarations are expected to be in that file's
global namespace. In other words is just straightforward declarations.

Configuration file search path order:
-------------------------------------
 1) any path defined by the system variable built from (filtered) NAME value:
   $<NAME>_CONF. eg: MY_PROJECT_CONF='/opt/my_project/my_project.conf'

 2) current user's home directory:
   for POSIX systems: $HOME/.<NAME>.conf

 3) global system configuration file:
   for POSIX: /etc/<NAME>.conf


Important Point:  there's only one value for NAME per python process (VM).
================
"""

__version__ = "0.3"
__date__ = ""
__author__ = "Frédéric Delaunay"
__email__ = "frederic.delaunay@plymouth.ac.uk"
__copyright__ = "Copyright 2011, University of Plymouth"
__license__ = "GPL"
__maintainer__ = "Frédéric Delaunay"
__status__ = "Prototype" # , "Development" or "Production"

import sys
from os import path, environ

__NAME = None
__LOADED_FILE = None

BASE_PATH=path.normpath(__path__[0]+'/../..')+'/'


class LoadException(StandardError):
    """Exception with 2 elements: filename and error_message. Use like:
    import conf
    try:
      load()
    except conf.LoadException, e:
      print 'file {0[0]} : {0[1]}'.format(e)"""
    pass

def set_name(project_name):
    """Sets the project name and returns the filtered version of it."""
    global __NAME
    __NAME = filter(lambda x: x.isalnum() and x or '_', project_name)
    return __NAME

def get_name():
    """Return global (filtered) project name"""
    global __NAME
    if __NAME:
        return __NAME
    else:
        raise LoadException('project name has not been set; use conf.set_name.')

def build_candidates():
    """Creates locations where conf file could be.
    Checks for a environment variable, name being built from build_env()
    """
    locs=[]
    try:
        locs.append(environ[__NAME])
    except (OSError,KeyError):
        pass
    try:
        locs.append(path.join(path.expanduser('~/'),'.'+__NAME+'.conf'))
    except OSError, err:
        raise LoadException(None, 'Cheesy OS error: %s' % err)
    else:
        locs.append(path.join('/etc', __NAME+'.conf'))
    return locs

def load(raise_exception=True, reload=False, required_entries=()):
    """Try to load 1st available configuration file, ignoring Subsequent calls
    unless reload is set to True.
    required_names: iterable of strings specifying variable names to be found.
    Returns: [missing_definitions]
    """
    global __NAME, __LOADED_FILE
    if not __NAME:
        get_name()

    def check_missing(required_entries):
        """check for missing mandatory configuration entries.
        Returns:
        """
        return [ i for i in required_entries if
                 i not in dir(sys.modules[__name__]) ]

    def load_from_candidates():
        for conf_file in build_candidates():
            if path.isfile(conf_file):
                msg = None
                try:
                    execfile(conf_file, globals())
                except SyntaxError, err:
                    msg = "error line %i." % err.lineno
                except Exception, e:
                    msg = e
                else:
                    return conf_file
                if msg and raise_exception:
                    raise LoadException(conf_file, msg)

    if __LOADED_FILE and not reload:
        return []
    else:
        __LOADED_FILE = load_from_candidates()

    if not __LOADED_FILE and raise_exception:
        raise LoadException(None,
                            "No configuration file found for project {0}. "
                            "Aborting!\nYou can define the environment variable"
                            " '{0}' for complete configuration file path "
                            "definition.".format(__NAME) )
    return check_missing(required_entries)
