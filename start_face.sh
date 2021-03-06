#!/bin/sh

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


#
# Starter script for LightHead-bot.
#

BGE_PYTHON_VERS=2.6
PROJECT_NAME=lightHead

if ! python -c 'print'; then
    echo "python not found. Did you set your PATH ?"
    exit 1
fi

. ./source_me_to_set_env.sh 

if ! test -x ./$PROJECT_NAME; then
    echo "Could not find executable file '$PROJECT_NAME' in this directory."
    exit 1
fi

if test -z "$CONF_FILE"; then
    exit 1
fi

# the config file is a python script, let's use a function from it
ADDR_PORT=`python -c "execfile('$CONF_FILE'); print "$PROJECT_NAME"_server"`
if ( test $? != 0 ) || ( test -z "$ADDR_PORT" ); then
    echo "!!! problem getting value for "$PROJECT_NAME"_server in $CONF_FILE"
else
    echo "--- Using $CONF_FILE -> Listening on $ADDR_PORT "
fi

# remove old unix sockets if present
SOCKETS=`python -c "execfile('$CONF_FILE'); get_unix_sockets(True)"`
if test $? -ne 0; then
	echo "ERROR: Failure to get socket list !"
	exit 1
fi
if test -n "$SOCKETS" ; then
	echo "deleting old sockets: "
	for s in $SOCKETS; do
	  if test -S "$s"; then echo "  "`rm -v "$s"` ; fi
	done
fi


# Now launch
getopts "w" OPTS
if [ "$OPTS" = "w" ]; then
    shift;
fi

echo -n "--- launching face "
if [ $# -ge 1 ]; then echo "using options: $@"; else echo "";
fi

if [ "$OPTS" = "w" ]; then
    ./$PROJECT_NAME-window $@ "$PROJECT_NAME"
else
    ./$PROJECT_NAME $@ "$PROJECT_NAME"
fi
