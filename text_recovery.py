#!/usr/bin/env python3
# coding: utf-8
""" Usage:
      text_recovery.py [options] textgrid_file original_text output_file
      This program will find the best way to the replace the textgrid text back to its original text
      where options may include:
          -w word_tier_name: word tier name (default 'word')
"""

import tgt
from Levenshtein import editops, apply_edit
import sys
import getopt

def getopt2(name, opts, default = None) :
    value = [v for n,v in opts if n==name]
    if len(value) == 0 :
        return default
    return value[0]
    
def read_textgrid(txtgdfile, word_name="word"):
    try:
        tg = tgt.io3.read_textgrid(txtgdfile)
        wtier=tg.get_tier_by_name(word_name)
        txtlst = []
        for ann in wtier._objects:
            txtlst.append(ann.text)
        return tg, wtier, txtlst
    except Exception as error:
        print("error in read_textgrid", error)
        sys.exit(-1)

def read_textfile(txtfile):
    SPEC=['puncs','monophones']
    spec = []
    for f in SPEC:
        fh= open(f, "r")
        xpuncs = fh.readlines()
        for p in xpuncs:
            for ip in p:
                spec.append(ip)
                spec=[x for x in spec if x != '\n']
    
    file1 = open(txtfile, 'r')
    Lines = file1.readlines()

    ans=[]
    for line in Lines:
        for c in list(line):
            ans.append(c)

    ans=[x for x in ans if x not in spec and x != '\n']
    return(ans)

def replace_text(tg, wtier, finlst, outfile):
    for ann, fnt in zip(wtier._objects, finlst):
        ann.text = fnt

    tgt.io.write_to_file(tg, outfile)
        
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "w:")
        #print(opts, args)
        # mandatory arguments
        txtgridfile, txtfile, outfile = args
    
        # get options
        word_name = getopt2("-w", opts, "word")
    except:
        print(__doc__)
        sys.exit(0)

    tg, wtier, txtlst=read_textgrid(txtgridfile, word_name)
    anslst=read_textfile(txtfile)

    xed=editops(anslst, txtlst)
    finlst=txtlst.copy()
    for xtep in xed:
        (act, aidx, tidx) = xtep
        if act == 'replace':
            finlst[tidx]=anslst[aidx]
  
    print(finlst)
    replace_text(tg, wtier, finlst, outfile)
    
