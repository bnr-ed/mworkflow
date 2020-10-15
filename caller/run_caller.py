#!/usr/bin/env python
import sys, os, re
from Bio import SeqIO
import pysam
from itertools import groupby
from argparse import ArgumentParser

BIN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../core'))
import brc

if __name__ == '__main__':
    # Parameters to be input.
    parser = ArgumentParser(description="you know")
    parser.add_argument("-b","--bam", action="store", dest="bam",
            help="dedup bam", required=True)
    parser.add_argument("-r","--bed", action="store", dest="bed",
            help="target region", required=True)
    parser.add_argument("-f","--reference", action="store", dest="reference",
            help="reference fasta", required=True)
    parser.add_argument("-o","--outdir", action="store", dest="outdir",
            help="output dir", required=True)
    parser.add_argument("-p","--prefix", action="store", dest="prefix",
            help="prefix", required=True)
    parser.add_argument("--sambamba", action="store", dest="sambamba",
            help="sambamba tools", required=True)

    myargs = parser.parse_args()

    output_path = os.path.abspath(myargs.outdir)
    brc.createDirectory(output_path)

    cmd = " ".join(["java -jar ", BIN_PATH + "/mbs.v1.0.jar", "--rawbam", myargs.bam, "--region", myargs.bed, 
        "--reference", myargs.reference, "--outdir", output_path, "--sample", myargs.prefix, "--sambamba", myargs.sambamba])
    brc.run_command(cmd, "")

    brc.rm_files(output_path + "/*stitch.bam*")
    brc.rm_files(output_path + "/tmp")
