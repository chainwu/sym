#!/usr/bin/env python
# -*- coding: utf-8 -*- 

""" Usage:
      sym.py text_file
      This program convert the unknown characters with known characters with the same prounciation
"""

from pypinyin import pinyin, lazy_pinyin, Style
import os
import pickle
import sys
from opencc import OpenCC

def get_all_char_pinyin():
    path="single.dict"
    pinyin_dict={}
    char_dict=[]
    with open(path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            ch=line.strip()
            char_dict.append(ch)
            ch_pinyin = pinyin(ch, style=Style.TONE3, heteronym=False)
            for p_li in ch_pinyin:
                for p in p_li:
                    if p not in pinyin_dict:
                        pinyin_dict[p]=[ch]
                    else:
                        pinyin_dict[p].append(ch)

    f.close()
    return char_dict, pinyin_dict

def convert(txt):
    char_dict, pinyin_dict=get_all_char_pinyin()
    cc = OpenCC('t2s')
    with open(txt, "r", encoding="utf-8") as fl:
        for line in fl.readlines():
            line=line.strip()
            line=cc.convert(line)
            similar_dict={}
            for c in line:
                if c not in char_dict: 
                    ch_pinyin=pinyin(c, style=Style.TONE3, heteronym=False)
                    #print(c, "not in dict")
                    #print(ch_pinyin)

                    res=[]
                    try:
                        for p_li in ch_pinyin:
                            for p in p_li:
                                res.extend(pinyin_dict[p])
                    
                        print(format('{}*'.format(res[0])),end=" ")
                    except:
                        #print(p, end=" ")
                        continue
                else:
                    print(c, end=" ")
                    
    print()

if __name__=='__main__':
    try:
        txt=sys.argv[1]
        convert(txt)
    except:
        print(__doc__)
        sys.exit(0)
