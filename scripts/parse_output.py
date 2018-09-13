#!/usr/bin/env python
"""
Input a flat text file of variant call data derived from ANNOVAR, and output
a filtered dataset by gene.  
"""
import sys
import os
import csv
import argparse

from pprint import pprint as pp
from collections import defaultdict

version = '0.8.20180912'
cantran_file = os.path.join(os.path.dirname(__file__), '..', 'resource', 
    'refseq.txt')

def get_args():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('input_file', help='Data file to parse')
    parser.add_argument('-g', '--gene', metavar="<gene>", default='TP53',
        help='Gene (or comma separated list of genes) on which to filter the '
        'data. If you want to get the output for every gene in the file, use '
        '"all". DEFAULT: %(default)s')
    parser.add_argument('-o', '--outfile', metavar='<output_file>',
        help='File to which the output should be written.')
    parser.add_argument('-v', '--version', action='version', 
        version = '%(prog)s - v' + version)
    args = parser.parse_args()
    return args

def read_file(input_file):
    with open(input_file) as fh:
        header = fh.readline().split('\t')
        data = [dict(zip(header, line.split('\t'))) for line in fh]
    return data

def filter_data(data, genes, cantran):
    results = []
    renamed = {
        'TIAF1;MYO18A' : 'MYO18A',
        'APEX1;OSGEP' : 'APEX1',
    }
    for var in data:
        # Sometimes, for some reason, the gene names are combined. Just pick one
        # use that instead.
        var_gene = renamed.get(var['Gene.refGene'], var['Gene.refGene'])

        # Filter on gene if we have requested this.
        if genes and var_gene not in genes:
            continue
        # Filter by function
        elif var['ExonicFunc.refGene'].startswith('synonymous'):
            continue
        # Filter out Intronic variants
        elif var['AAChange.refGene'] == '.' and var['GeneDetail.refGene'] == '.':
            continue
        # Filter by maximum population frequency (combined ExAC, 1000G and dbSNP)
        elif var['PopFreqMax'] != '.' and float(var['PopFreqMax']) > 0.01:
            continue

        # The way that Annovar does this is to have the transcript, CDS, etc. in 
        # the "AAChange.refGene" field unless it's a non-coding change, and then
        # the info can be found in the GeneDetail.refGene column.  Wish it was all
        # in one!
        our_tscript_id = cantran[var_gene]
        if var['AAChange.refGene'] == '.':
            transcript, cds = get_varinfo_from_gd(
                var['GeneDetail.refGene'], 
                cantran
            )
            # Will be something like UTR3, UTR5, etc.
            var['ExonicFunc.refGene'] = var['Func.refGene']
            aa = 'p.?'
        else:
            transcript, cds, aa = get_varinfo_from_aa(
                var['AAChange.refGene'], 
                cantran
            )

        wanted_data = {k : var[k] for k in ('Chr', 'Start', 'Ref', 'Alt', 
            'ExonicFunc.refGene', 'Gene.refGene')}
        wanted_data.update({'transcript' : transcript, 'cds' : cds, 'aa' : aa })
        results.append(wanted_data)
    return results

def get_varinfo_from_gd(variant, cantran):
    """
    Get the wanted CDS and transcript info for a non-coding change. We can either
    get a UTR variant here or a splicing variant.
    """
    vrt = [x.split(':') for x in variant.split(';')]
    for v in vrt:
        # If we have a splice variant, we have a 3 element list, and we want
        # indices 0 and 2. If we have a UTR variant, we have a 2 element list,
        # and we want indices 0 and 1.
        cds_index = len(v)-1
        if v[0] == cantran:
            return v[0], v[cds_index]
    # If we got here, we can't map to one of our transcripts, so take the first 
    # one from ANNOVAR and just use that one.
    return vrt[0][0], vrt[0][cds_index]

def get_varinfo_from_aa(variant, cantran):
    """
    Get the wanted CDS and transcript info for a coding change.
    """
    vrt = [x.split(':') for x in variant.split(',')]
    for v in vrt:
        if v[1] == cantran:
            # Sometimes no AA change for some reason.
            if len(v) == 5:
                return v[1], v[3], v[4]
            else:
                pp(v)
                continue
    # If we got here, we can't map to one of our transcripts, so take the first 
    # one from ANNOVAR and just use that one.
    return vrt[0][1], vrt[0][3], vrt[0][4]

def read_cantran(input_file):
    tscripts = {}
    with open(input_file) as fh:
        for line in fh:
            if line.startswith('#'):
                continue
            x = line.rstrip('\n').split(',')
            # take last one in list, presumably latest, and strip off version
            tscripts[x[0]] = x[-1].split('.')[0] 
    return tscripts
            
def print_results(results, outfile):
    if outfile:
        sys.stderr.write("Writing output to %s.\n" % outfile)
        outfh = open(outfile, 'w')
    else:
        outfh = sys.stdout
    csv_writer = csv.writer(outfh, lineterminator="\n", delimiter=",")
    wanted = ('Chr', 'Start', 'Ref', 'Alt', 'Gene.refGene', 'transcript', 
        'cds', 'aa', 'ExonicFunc.refGene')

    csv_writer.writerow(('Chr', 'Pos', 'Ref', 'Alt', 'Gene', 'Transcript', 'CDS',
        'AA', 'Function'))
    for var in results:
        csv_writer.writerow([var.get(x) for x in wanted])

def main(input_file, genes, outfile):
    transcripts = read_cantran(cantran_file)
    data = read_file(input_file)
    filtered = filter_data(data, genes, transcripts)
    print_results(filtered, outfile)

if __name__ == '__main__':
    args = get_args()
    if args.gene == 'all':
        genes = []
    else:
        genes = args.gene.split(',')
    main(args.input_file, genes, args.outfile)

