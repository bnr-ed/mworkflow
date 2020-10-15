#!/usr/bin/env python
import sys,os,re
import subprocess
import glob

def resolveConfig(configure_file):
    file = open(configure_file, 'r')
    count_lines = 0
    myDict = {}
    for line in file.readlines():
        line = line.strip()
        count_lines +=1
        if re.match(r'^#.*', line):
            continue
        match_key_value = re.match(r'^\s*([^=\s]+)\s*=\s*(.*)$', line)
        if match_key_value == None:
            continue
        key    = match_key_value.group(1)
        value  = match_key_value.group(2)
        if key == '' or value == '' :
            print("Could not find key or value at line %s.\n" %(count_lines))
            continue
        match_var_value = re.match(r'^\$\((.*)\)(.*)$', value)
        if match_var_value != None:
            variable_key = match_var_value.group(1)
            variable_value = match_var_value.group(2)
            if myDict.has_key(variable_key):
                value = myDict[variable_key] + variable_value
        myDict[key]=value
    return myDict

def createDirectory(dirctory):
    if not os.path.exists(dirctory):
        run_command('mkdir -p %s' % dirctory, ">>> Create dirctory %s failed." % dirctory, False)

def run_command(run_cmd, error_log, error_exit = True):
    try:
        for cmd in run_cmd.split("\n"):
            if cmd.strip() == "":
                continue
            subprocess.check_call(cmd, shell=True)
    except:
        if error_exit:
            sys.exit(error_log)

def rm_files(path):
    flist = glob.glob(path)
    if len(flist)>0:
        os.system("rm -rf " + path)

def check_files(files):
    error_flag = 0
    for efile in files:
        if not os.path.isfile(efile):
            print("ERROR: Could not find file %s." % efile)
            error_flag = 1
    if error_flag:
        exit(error_flag)
