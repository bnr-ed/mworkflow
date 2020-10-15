#!/usr/bin/env python
version = "v1.0.0"

import os, sys
from argparse import ArgumentParser

# import inhouse module
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../core'))
import brc

if __name__ == '__main__':
    #Parameters to be input.
    parser=ArgumentParser(description="report module, version {}".format(version))
    parser.add_argument("-i", "--input_path", action="store", dest="input_path",
            help="Sample analysis path", required=True)
    parser.add_argument("-o", "--report_path", action="store", dest="report_path",
            help="report path", required=True)
    parser.add_argument("-p", "--sample_prefix", action="store", dest="sample_prefix",
            help="output tumor prefix", required=True)
    parser.add_argument("-c", "--config", action="store", dest="config", 
            help="pipeline configure file", required=True)

    args = parser.parse_args()

    brc.check_files([args.config])
    cfg_file = os.path.abspath(args.config)
    config = brc.resolveConfig(cfg_file)

    sample_prefix = args.sample_prefix
    input_path = os.path.abspath(args.input_path)
    report_path = os.path.abspath(args.report_path)
    brc.createDirectory(report_path)

    brc.run_command("cp -rf {}/caller/{}.calling.result.txt {}".format(input_path, sample_prefix, report_path), ">> copy failed")

    brc.run_command(" ".join([config["Rscript"], config["report_classifier"], "--outdir", report_path, "--config", cfg_file,
        "--prefix", args.sample_prefix]), ">> run classifier failed")
