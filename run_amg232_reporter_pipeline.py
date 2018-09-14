#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline wrapper script for the AMG-232 Reporter plugin.
"""

import sys
import os
import subprocess
import argparse

from pprint import pprint as pp

version = '1.0.20180914'

# Globals
output_root = os.getcwd()
scripts_dir = os.path.join(output_root, 'scripts')
resources = os.path.join(output_root, 'resource')
lib = os.path.join(output_root, 'lib')

def get_args():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('vcf', metavar="<VCF File>",
        help='VCF file on which to run the analysis. VCF files must be derived '
            'from the Ion Torrent TVC plugin.')
    parser.add_argument('-g', '--genes', metavar="<gene>", default="TP53",
        help='Gene or comma separated list of genes to report. DEFAULT: '
            '%(default)s.')
    parser.add_argument('-n', '--name', metavar="<sample_name>", 
        help='Sample name to use for output.')
    parser.add_argument('-o', '--outdir', metavar='<output_directory>',
        help='Directory to which the output data should be written. DEFAULT: '
            '<sample_name>_out/')
    parser.add_argument('-v', '--version', action='version',
        version='%(prog)s - v' + version)
    args = parser.parse_args()
    return args

def get_name_from_vcf(vcf):
    name = ''
    with open(vcf) as fh:
        for line in fh:
            if line.startswith('#CHROM'):
                elems = line.split()
                try:
                    name = elems[9]
                except IndexError:
                    # We don't have a name field in this VCF for some reason, so
                    # just use the VCF filename.
                    name = vcf.rstrip('.vcf')
    return name

def simplify_vcf(vcf, outdir):
    """
    Use the `simplify_vcf.pl` script to remove reference and NOCALLs from the 
    input VCF. Return a simplified VCF containing only 1 variant per line, and 
    with only the critical VAF and coverage info.  Return the resultant simple
    VCF filename for downstream processing.
    """
    new_name = '{}_simple.vcf'.format(os.path.join(outdir, vcf.rstrip('.vcf')))
    cmd = [os.path.join(scripts_dir, 'simplify_vcf.pl'), '-f', new_name, vcf]
    status = run(cmd, 'simplify the Ion VCF')
    if status:
        sys.exit(1)
    else:
        return new_name

def run_annovar(simple_vcf):
    """
    Run Annovar on the simplified VCF to generate an annotate dataset that can
    then be filtered by gene. Return the resultant Annovar .txt file for 
    downstream processing.
    """
    annovar_out = ''
    cmd = [
        os.path.join(scripts_dir, 'annovar_wrapper.sh'), 
        simple_vcf, 
    ]
    status = run(cmd, 'annotate VCF with Annovar')
    if status:
        sys.exit(1)
    else:
        # Rename the files to be shorter and cleaner
        annovar_txt_out = os.path.abspath('%s.hg19_multianno.txt' % simple_vcf)
        annovar_vcf_out = os.path.abspath('%s.hg19_multianno.vcf' % simple_vcf)
        for f in (annovar_vcf_out, annovar_txt_out):
            new_name = f.replace('vcf.hg19_multianno', 'annovar')
            os.rename(f, new_name)
            if new_name.endswith('txt'):
                annovar = new_name
        return new_name

def generate_report(annovar_data, genes, outdir):
    """
    Process the Annovar file to filter out data by gene, population frequency, 
    and any other filter.
    """
    new_name = annovar_data.replace('annovar.txt', 'amg-232_report.csv')
    cmd = [
        os.path.join(scripts_dir, 'parse_output.py'),
        '-g', genes,
        '-o', new_name,
        annovar_data
    ]
    status = run(cmd, "generate a variant report")
    if status:
        sys.exit(1)
    else:
        sys.stderr.write('AMG-232 Reporter completed successfully! Data can '
            'be found in %s.\n' % outdir)
        sys.exit()

def run(cmd, task):
    """
    Generic subprocess runner.
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    msg, err = proc.communicate()
    # TODO: Can we / should we capture these and write them to a log file?
    # print(msg)
    if proc.returncode != 0:
        sys.stderr.write('An error has occurred while trying to %s.\n' % task)
        sys.stderr.write(err.decode('utf-8'))
        return 1
    return 0

def main(vcf, sample_name, genes, outdir):
    # Create an output directory based on the sample_name
    if sample_name is None:
        sample_name = get_name_from_vcf(vcf)
        
    outdir_path = os.path.abspath(output_root)
    if outdir is None:
        outdir_path = os.path.join(outdir_path, '%s_out' % sample_name)
    else:
        outdir_path = os.path.join(outdir_path, outdir)

    if not os.path.exists(outdir_path):
        os.mkdir(os.path.abspath(outdir_path), 0o755)

    # Simplify the VCF
    # TODO: Move to a logger? Log4Python?
    sys.stderr.write('Simplifying the VCF file.\n')
    sys.stderr.flush()
    simple_vcf = simplify_vcf(vcf, outdir_path)
    sys.stderr.write('Done!\n')

    # Annotate the vcf with ANNOVAR.
    sys.stderr.write('Annotating the simplified VCF with Annovar.\n')
    sys.stderr.flush()
    annovar_file = run_annovar(simple_vcf)
    sys.stderr.write('Done.\n')

    # Generate a filtered CSV file of results for the report.
    sys.stderr.write('Generating a report.\n')
    sys.stderr.flush()
    generate_report(annovar_file, genes, outdir_path)

if __name__ == '__main__':
    args = get_args()
    main(args.vcf, args.name, args.genes, args.outdir)
