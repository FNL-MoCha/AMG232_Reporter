#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main plugin script. Relies heavily on run_amg232_reporter_pipeline.py to 
run.
"""
import sys
import os
import json
import subprocess
import argparse
import datetime

from pprint import pprint as pp

from django.conf import settings
from django.template.loader import render_to_string
from django.conf import global_settings
global_settings.LOGGING_CONFIG=None

from django import template

# Set up some logger defaults. 
loglevel = 'debug' # Min level to be reported to log.
logfile = sys.stdout

barcode_input = {}
plugin_params = {}
plugin_result = {}
plugin_report = {}
barcode_summary = []
barcode_report = {}
help_dictionary = {}



######
# From TVC, some methods we may want:
    # - get_options(): 213 - 324
    # - get_configurations(): 590 - 671
    # - make_directories(): 684 - 695
    # - variant_caller_pipeline() 713 - 772
    # - setup_webpage_support(): 935 - 939
    # - load_render_context(): 941 - 971
    # - create_symlinks(): 973 - 996
    # - render_webpages(): 998 - 1009
    # - add_output_files(): 1083 - 1108
    # - process_results(): 1110 - 1178
    # - setup_results_json(): 1180 - 1189
    # - load_barcode_sample_info(): 1191 - 1200
    # - generate_download_files(): 1261 - 1280
    # - setup_run(): 1288 - 1296

def get_barcodes():
    pass

def writelog(level, msg):
    """
    Simple logger for this plugin. Can use Python's builtin, but just needed
    something more simple.
    """
    now = datetime.datetime.now().strftime('%c')
    log_levels = {
        'i' : (0, 'INFO:'),
        'w' : (1, 'WARN:'),
        'e' : (1, 'ERROR:'),
        'd' : (2, 'DEBUG:'),
    }
    tier, flag = log_levels[level[0].lower()]
    logstr = '{:27s} {:7s} {}\n'.format(now, flag, msg)

    if tier <= log_levels[loglevel[0].lower()][0]:
        logfile.write(logstr)
        logstr.flush()

def loadPluginParams():
    """
    Process default command args and json parameters file to extract TSS
    plugin environment
    """
    global plugin_params
    get_args()

def get_args():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('start_plugin_json')
    parser.add_argument('barcodes_json')
    parser.add_argument('-d', '--install-dir', dest='install_dir',
        help="Directory containing plugin files.")
    parser.add_argument('-o', '--output-dir', dest='output_dir',
        help='Directory for results files.')
    parser.add_argument('-u', '--output-url', dest='output_url',
        help='URL matching the output directory.')
    parser.add_argument('-r', '--report-dir', dest='report_dir',
        help='Directory containing analysis report files.')
    args = parser.parse_args()

    # Load the startplugin.json data into a dict
    with open(args.start_plugin_json) as json_fh:
        json_params = json.load(json_fh)

    global plugin_params, barcode_input
    with open(args.barcodes_json) as json_fh:
        barcode_input = json.load(json_fh)

    plugin_params['cmd_options'] = vars(args)
    plugin_params['json_params'] = json_params
    plugin_params['json_input']  = args.start_plugin_json
    plugin_params['barcode_input'] = args.barcodes_json



def plugin_main():
    '''
    Main entry point for plugin.
    steps: 
        1. load params
        2. print startup messages.
        3. runForBarcodes()
    '''

    #global DIRNAME # Home dir for plugin files.
    #global TSP_URLPATH_PLUGIN_DIR # Target pluing results dir.
    #global ANALYSIS_DIR # Main report dir.
    #global TSP_FILEPATH_PLUGIN_DIR # XXX
    #global OUTPUT_FILES

     #Keep the old (skool) env variables.
    #DIRNAME = args.install_dir
    #TSP_FILEPATH_PLUGIN_DIR = args.output_dir
    #ANALYSIS_DIR = args.report_dir
    #TSP_URLPATH_PLUGIN_DIR = args.output_url
    #OUTPUT_FILES = []

    logfile.write('\nAMG-232 Reporter has started.\n')
    logfile.flush()

    barcoded_samples = get_barcodes()
    pp(barcoded_samples)

    # XXX
    #write_results_json(results_json)

    logfile.write('\nAMG-232 Reporter has finished.\n')
    logfile.flush()

    return 0


    
if __name__ == '__main__':
    exit(plugin_main())
