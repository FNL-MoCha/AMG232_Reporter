#!/usr/bin/env python3
import sys
import os
import subprocess

from ion.plugin import *

class AMG232_Reporter(IonPlugin):
    """
    Plugin to generate a TP53 variant report in support of the AMG-232 study.
    """
    version = '0.6.20180919'
    major_block = False
    runtypes = [RunType.FULLCHIP, RunType.THUMB, RunType.COMPOSITE]
    runlevels = [RunLevel.DEFAULT]
    depends = ["variantCaller"]

    def launch(self, data=None):
        cmd = [
            os.path.join(os.environ['DIRNAME'], 'amg232_reporter_plugin.py'),
            '-V', self.version, 
            'startplugin.json',
            'barcodes.json'
        ]
        plugin = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=False)
        plugin.communicate()
        sys.exit(plugin.poll())

if __name__ == '__main__':
    PluginCLI()
