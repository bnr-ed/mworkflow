#!/usr/bin/env python
version = "v1.0.0"

import os,os.path, sys
from argparse import ArgumentParser

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../core'))
import brc

if __name__ == '__main__':
    #Parameters to be input.
    parser=ArgumentParser(description="trimming module, version {}".format(version))
    parser.add_argument("-f1","--fq1", action="store", dest="fq1", 
            help="fastq end 1", required=True)
    parser.add_argument("-f2","--fq2", action="store", dest="fq2", 
            help="fastq end 2", required=True)
    parser.add_argument("-o","--output_path", action="store", dest="output_path", 
            help="output path", required=True)
    parser.add_argument("-c","--cfg", action="store", dest="cfg", 
            help="pipeline configure file", required=True)
    parser.add_argument("-p","--prefix", action="store", dest="prefix", 
            help="output prefix, sample id", required=True)

    args = parser.parse_args()

    brc.check_files([args.fq1, args.fq2, args.cfg])
    brc.createDirectory(args.output_path)
    
    config = brc.resolveConfig(args.cfg)
    prefix = args.prefix
    output_path = os.path.abspath(args.output_path)
    dirprefix = "%s/%s" %(output_path, prefix)

    # software and args
    java = config["java"]
    trimmomatic = config["trimmomatic"]
    cpu_trim = "6" 
    mem_trim = "80G"

    # trim fastq
    fq_1 = os.path.abspath(args.fq1)
    fq_2 = os.path.abspath(args.fq2)

    trimmo_fq_1 = "%s.trimmomatic.trimmed.R1.fq" % dirprefix
    trimmo_fq_2 = "%s.trimmomatic.trimmed.R2.fq" % dirprefix
    trimmo_cmd  = " ".join([java, "-jar -Xmx" + mem_trim, trimmomatic, "PE -threads", cpu_trim, "-phred33", 
        fq_1, fq_2, trimmo_fq_1, dirprefix + ".unPair.R1.fq", trimmo_fq_2, dirprefix + ".unPair.R2.fq", 
        "ILLUMINACLIP:" + config["adapter"] + ":2:30:10:1:true SLIDINGWINDOW:4:15 TRAILING:20"])
    brc.run_command(trimmo_cmd, ">>>Trimmomatic Failed")
    
    trim_cmd = " ".join([config["python"], config["adapter_trim"], '--fq1', fq_1, '--fq2', fq_2, 
        '--output_path', output_path, "--output_prefix", prefix, "--adapter_type", config["adapter_type"]])
    brc.run_command(trim_cmd, ">>> methylation trimming adapter Failed!!")

    fastqc_cmd = " ".join([config['fastqc'], '-o', output_path, '--extract -f fastq', "--threads", cpu_trim,
            "{}_clean.R1.fq".format(dirprefix), "{}_clean.R2.fq".format(dirprefix)])
    brc.run_command(fastqc_cmd, ">>> do FASTQC Failed!!!")

    brc.rm_files("%s*unPair*" % dirprefix)
    brc.rm_files("%s*trim.R*.fq" % dirprefix)
    brc.rm_files("%s.trimmed.reads.txt" % dirprefix)
    brc.rm_files("%s.trimmomatic.trimmed.R*.fq" % dirprefix)
