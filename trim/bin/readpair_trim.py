import sys, os
import gzip
import numpy as np
from itertools import izip
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-1',"--fq1", action="store", dest="fq1", help="fastq end 1", required=True)
parser.add_argument('-2',"--fq2", action="store", dest="fq2", help="fastq end 2", required=True)
parser.add_argument('-o',"--output_path", action="store", dest="output_path", help="output path", required=True)
parser.add_argument('-p',"--output_prefix", action="store", dest="output_prefix", help="output prefix", required=True)
parser.add_argument('-a',"--adapter_type", action="store", dest="adapter_type", help="adapter type", required=True)

myargs = parser.parse_args()

def trim_read(rlist, base1, base2, _len):
    seqs=rlist[1]
    quals=rlist[3]
    sqlen=len(seqs)
    k1=_len;k2=sqlen
    if len(base1)>0:
        for i in range(1,sqlen):
            bs=seqs[i]
            qual=ord(quals[i])-33
            if bs not in base1 and qual>=30:
                k1=i
                break
    if len(base2)>0:
        for i in range(sqlen-20,-1,-1):
            bs=seqs[i]
            qual=ord(quals[i])-33
            if bs not in base2 and qual>=30:
                k2=i
                break
    rlist[1]=rlist[1][k1:k2+1]
    rlist[3]=rlist[3][k1:k2+1]
    return rlist

def check_adapter_length(base, fr):
    if base == 'N':
        return 0
    icount = 0
    read_list = []
    base_length_count = []
    for line in fr:
        line = line.strip()
        if icount%4==0 and icount!=0:
            read_seq = read_list[1]
            for idx, eb in enumerate(read_seq):
                if eb not in base:
                    base_length_count.append(idx + 1)
                    break
            read_list = []
        if icount > 400000:
            break
        read_list.append(line)
        icount+=1
    return int(np.mean(base_length_count))

f1=gzip.open(os.path.abspath(myargs.fq1))
f2=gzip.open(os.path.abspath(myargs.fq2))

ft1=open('{}/{}_R1.clean.fq'.format(myargs.output_path, myargs.output_prefix),'w')
ft2=open('{}/{}_R2.clean.fq'.format(myargs.output_path, myargs.output_prefix),'w')

(adpR1, adpR2, cmpR1, cmpR2) = myargs.adapter_type.split(",")
min_len=50

_len1 = check_adapter_length(adpR1, gzip.open(os.path.abspath(myargs.fq1)))
_len2 = check_adapter_length(adpR2, gzip.open(os.path.abspath(myargs.fq2)))

rlist1=[];rlist2=[];n=0;
for line1,line2 in izip(f1,f2):
    if n%4==0 and n!=0:
        if rlist1[0].split()[0]!=rlist2[0].split()[0]:
            sys.exit(rlist1[0]+'\t'+rlist2[0])
        mlen=min(len(rlist1[1]),len(rlist2[1]))
        if mlen > min_len:
            sq1=rlist1[1];sq2=rlist2[1]
            rlist1=trim_read(rlist1,adpR1,cmpR2, _len1)
            rlist2=trim_read(rlist2,adpR2,cmpR1, _len2)
            if len(rlist1[1])>min_len and len(rlist2[1])>min_len:
                for out1,out2 in izip(rlist1,rlist2):
                    print>>ft1,out1.strip()
                    print>>ft2,out2.strip()
        rlist1=[];rlist2=[]
    rlist1.append(line1.strip())
    rlist2.append(line2.strip())
    n+=1
ft1.close()
ft2.close()
