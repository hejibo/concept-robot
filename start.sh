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

export PYTHONOPTIMIZE=1	# optimize and also remove docstrings
BGE_PYTHON_VERS=2.6
PROJECT_NAME=lightHead

if ! python -c 'print'; then
    echo "python not found. Did you set your PATH ?"
    exit 1
fi

if ! test -d "./common"; then
	echo "could not find directory $CONCEPT_DIR/common . Aborting ..."
	exit 1
fi
# set environment
. ./common/source_me_to_set_env.sh


PREFIX="./"

# handle MinGW and Windows suffix
case `uname -s` in
    MINGW*)
        BIN_SUFFIX=".exe"
        ;;
    Darwin*)
    	BIN_SUFFIX=".app/"
    	PREFIX="open "
    	;;
    *)
        BIN_SUFFIX=""
        ;;
esac

getopts "w" OPTS
if [ "$OPTS" = "w" ]; then
    shift;
    if [ "$OPTS" = "w" ]; then
    	PROJECT_NAME=$PROJECT_NAME-window
    fi
fi

getopts "i" OPTS
if [ "$OPTS" = "i" ]; then
    shift;
    if [ "$OPTS" = "i" ]; then
    	PREFIX="optirun ./"
    fi
fi

if ! test -x ./$PROJECT_NAME$BIN_SUFFIX; then
    echo "Could not find executable file '$PROJECT_NAME' in this directory."
    exit 2
fi

if test -z "$CONF_FILE"; then
    exit 3
fi

# Now launch

echo -n "--- launching face ---"
if [ $# -ge 1 ]; then echo "using options: $@"; else echo "";
fi

$PREFIX$PROJECT_NAME$BIN_SUFFIX $@
