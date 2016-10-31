#! /usr/bin/python
#===============================================================================
# File Name      : /home/satheesh/python_scripts/loggy/globalS.py
# Date           : 12-16-2014
# Input Files    : Nil
# Author         : Satheesh <mari.satheesh.paramasivan@oracle.com>
# Description    : globals variable which has to be used across this framework
#                  should be defined here
#
#===============================================================================
def init():
    global dictDb
    dictDb = {}