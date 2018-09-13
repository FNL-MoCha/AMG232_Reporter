#!/usr/bin/python
import sys
import os
from ion.plugin import *

class AMG232_Reporter(IonPlugin):
    """
    Plugin to generate a TP53 variant report in support of the AMG-232 study.
    """
    version = '0.1.20180912'
    major_block = False
    allow_autorun = True
    runtypes = [RunType.COMPOSITE]
    runlevels = [RunLevel.DEFAULT] # XXX: Do we want "LAST" here?
    depends = ['variantCaller']

    # Other attrs needed?
    # startplugin = {}
    # launch = True | False
    # barcodetable_columns = []

