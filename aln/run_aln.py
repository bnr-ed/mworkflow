#!/usr/bin/env python
import os,sys
from argparse import ArgumentParser

BIN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../core'))
import brc

version = "v1.0.0"

if __name__ == '__main__':
    # Parameters to be input.
    parser = ArgumentParser(description="mapping module, version {}".format(version))
    parser.add_argument("-1","--fq1", action="store", dest="fq1", 
            help="fastq end 1", required=True)
    parser.add_argument("-2","--fq2", action="store", dest="fq2",
            help="fastq end 2", required=True)
    parser.add_argument("-c","--config", action="store", dest="cfg",
            help="pipeline configure file", required=True)
    parser.add_argument("-o","--outdir", action="store", dest="outdir",
            help="output dir", required=True)
    parser.add_argument("-p","--prefix", action="store", dest="prefix",
            help="prefix", required=True)

    myargs = parser.parse_args()
    fq1 = os.path.abspath(myargs.fq1)
    fq2 = os.path.abspath(myargs.fq2)

    # check and create dir
    brc.check_files([fq1, fq2, myargs.cfg])
    config = brc.resolveConfig(myargs.cfg)

    output_path = os.path.abspath(myargs.outdir)
    brc.createDirectory(output_path)

    sample_prefix = myargs.prefix
    outprefix = output_path + '/' + myargs.prefix

    # software and app
    python = config["python"]
    bwa_meth = config['bwa_meth']
    java = config["java"]
    picard = config['picard']
    sambamba = config['sambamba']
    cpu_aln = "8"
    mem_aln = "100G"
    tmp_dir = "%s/tmp" % output_path

    sortbam = outprefix+'.sorted.bam'
    bwa_meth_cmd = " ".join([python, bwa_meth, '--reference', config['bwmeth_index'], '-t',
        cpu_aln, fq1, fq2, '|', config['samblaster'], '-e -M --addMateTags -d', outprefix + '.disc.sam',
        '|', java, '-jar', picard, 'AddOrReplaceReadGroups', 'TMP_DIR=' + tmp_dir, 
        'I=/dev/stdin', 'O=' + sortbam, 'SO=coordinate','RGID=' + sample_prefix, 
        'RGLB=Targetseq RGPL=illumina RGPU=RSseq', 'RGSM=' + sample_prefix])
    
    brc.run_command(bwa_meth_cmd, ">>> run bwa meth Failed!!!")

    index_cmd = " ".join([sambamba, 'index', sortbam])
    brc.run_command(index_cmd, ">>> run sambamba index Failed!!!")

    cleanbam = outprefix + '.clean.bam'
    regex = 'mapping_quality >= 20 and [NM] < 5 and proper_pair'
    regex += ' and not (unmapped or failed_quality_control or secondary_alignment or supplementary)'

    filterBam_cmd = " ".join([sambamba, 'view -h -t 4 -f bam -F "%s"' % regex, sortbam, '>', cleanbam])
    brc.run_command(filterBam_cmd, ">>> run sambamba filter bam Failed!!!")

    index1_cmd = " ".join([sambamba, 'index', cleanbam])
    brc.run_command(index1_cmd, ">>> run sambamba index Failed!!!")

    dedupbam = "{}.first.dedup.bam".format(outprefix)
    dedup_cmd  = " ".join([sambamba, 'view -h -t 4 -f bam -F "not duplicate"', cleanbam, '>', dedupbam])
    brc.run_command(dedup_cmd, ">>> run sambamba remove duplicate Failed!!!")

    index2_cmd = " ".join([sambamba, 'index', dedupbam])
    brc.run_command(index2_cmd, ">>> run sambamba index Failed!!!")

    cmd = " ".join([java, "-jar", BIN_PATH + "/fuzzy.dedup.v1.0.jar", "--bam", dedupbam, "--shift_size 3", 
        "--output_path", output_path, "--output_prefix", sample_prefix])
    brc.run_command(cmd, ">>> run fuzzy window failed")

    cmd = " ".join([sambamba, 'index', "{}.dedup.bam".format(outprefix)])
    brc.run_command(cmd, "run sambamba index Failed!!!")

    brc.rm_files(outprefix + '.sorted.bam*')
    brc.rm_files(outprefix + '.clean.bam*')
    brc.rm_files(outprefix + '.dedup.metrics')
    brc.rm_files(outprefix + '.first.dedup.bam*')
    brc.rm_files(outprefix + '.disc.sam')
    brc.rm_files(tmp_dir)
