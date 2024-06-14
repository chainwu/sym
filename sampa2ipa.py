#!/usr/bin/env python3
# coding: utf-8
""" Usage:
      sampa2ipa.py [options] textgrid_file output_file
      This program will add a layer of IPA based on SAMPA layer
      where options may include:
          -w word_tier_name: word tier name (default 'word')
          -p phone_tier_name: phoneme tier name (default 'phone')
"""

import tgt
import sys
import getopt
import pandas as pd

def getopt2(name, opts, default = None) :
    value = [v for n,v in opts if n==name]
    if len(value) == 0 :
        return default
    return value[0]
    
def read_textgrid(txtgrdfile, word_name = "word", phone_name="phone"):
    tg = tgt.io3.read_textgrid(txtgrdfile)
    ptier = tg.get_tier_by_name(phone_name)
    wtier = tg.get_tier_by_name(word_name)

    return tg, wtier, ptier

def read_sampadict():
    # 讀入 SAMPA 
    sampadict = pd.read_excel('sampa_revised.xlsx')
    #print(sampadict)
    return(sampadict)

def get_result_len(x):
    if x[-2] == None:
        return 1
    elif x[-1] == None:
        return 2
    else:
        return 3

def is_sampa_notation(sampa, text):
    sz = sampa[sampa['SAMPA'] == text].size
    return sz != 0

CONSONANT=['b', 'p', 'f', 'd', 't', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'Z', 'C', 'S', 'r', 'z', 'c', 's']

def get_ipa(sampa, note1, note2, note3):
    """get_ipa takes SAMPA dictionary and 3 consecutive notations, and return an IPA Note list to be replaced, 
       for example, when given SAMPA note1, note2, note3
             ('m', DONTCARE, DONTCARE), it will return [m, None, None]
             when given 
             ('W', '@', 'n'), it will return ['ɥ', 'ɛ', 'n']
             
             if the result contains "_", it means that the two SAMPA notes needs to be merged into one IPA note
    """
    if note1 in CONSONANT and note2 == 'w' and note3 == 'o':
        return [note1, 'w', 'ɔ']
    elif note1 not in ['@', 'W', 'y', '&', 'w']:
        return [sampa.loc[sampa['SAMPA'] == note1]['IPA'].to_string(index = False).strip(), None, None]
    elif note1 == '@':
        return ['a', None, None]
    elif note1 == 'W':
        if note2 == '@' and note3 == 'n':
            return ['ɥ', 'ɛ', 'n']
        elif note2 == '&' and note3 == 'n':
            return ['y', '_', 'n']
        else:
            return ['ɥ', None, None]
    elif note1 == 'y':
        if note2 == 'i' and note3 == 'n':
            return ['i', '_', 'n']
        else:
            return ['j', None, None]
    elif note1 == '&':
        if note2 == 'N':
            return ['ə', 'ŋ', None]
        elif note2 == 'n':
            return ['ə', 'n', None]
        else:
            return ['ɤ', None, None]
    elif note1 == 'w':
        if note2 == '&' and note3 == 'N':
            return ['o','_', 'ŋ']
        elif note2 == 'u':
            return ['u', "_", None]
        elif note2 == 'o':
            return ['ɔ', "_", None]
        elif note2 == '>':
            return ['w', 'ɔ', None]
        else:
            return ['w', None, None]

def ipa_tier(sampadict, wordtier, phonetier):
    et = phonetier.end_time
    st = phonetier.start_time
    ipatier = tgt.core.IntervalTier(st, et, "ipa phone")

    wst = wordtier.start_time
    wet = wordtier.end_time
    tierlen = phonetier.__len__()
    
    for wann in wordtier._objects:
        annlist = phonetier.get_annotations_between_timepoints(wann.start_time, wann.end_time)
        tierlen = len(annlist)
        i = 0
        while i < tierlen :
            ann = annlist[i]
            #print(i, ":", ann.text)

            if ann.text == "sp":
                newann = tgt.core.Annotation(ann.start_time, ann.end_time, 'sp')
                ipatier.add_annotation(newann)
                i = i + 1
                continue

            if not is_sampa_notation(sampa, ann.text):
                newann = tgt.core.Annotation(ann.start_time, ann.end_time, "")
                i = i + 1
                continue
                
            if i < tierlen - 2:
                annplus1 = annlist[i+1]
                annplus2 = annlist[i+2]
                arg = ann.text
                arg1 = annplus1.text
                arg2 = annplus2.text
            elif i == tierlen - 2:
                annplus1 = annlist[i+1]
                arg = ann.text
                arg1 = annplus1.text
                arg2 = None
            else:
                arg = ann.text
                arg1 = None
                arg2 = None                
                
            resultlist = get_ipa(sampa, arg, arg1, arg2)
            results_len = get_result_len(resultlist)
            #print(resultlist)
            
            for j in range(len(resultlist)):
                if resultlist[j] == None:
                    continue
                if resultlist[j] == '_':
                    i = i + 1
                    newann = tgt.core.Annotation(prevann.start_time, annplus1.end_time, prevann.text)
                    ipatier.delete_annotation_by_start_time(prevann.start_time)
                    ipatier.add_annotation(newann)
                else:
                    ann = annlist[i]
                    newann = tgt.core.Annotation(ann.start_time, ann.end_time, resultlist[j])
                    i = i + 1
                    prevann = newann   
                    ipatier.add_annotation(newann)
     
    #print(ipatier)
    return(ipatier)

def add_ipa_tier(tg, ipatier, outtxtgrdfile):
    tg.insert_tier(ipatier,1)
    tgt.io.write_to_file(tg, outtxtgrdfile)
    
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:],"p:w:")
        txtgrdfile, outtxtgrdfile = args

        phone_name =  getopt2("-p", opts, "phone")
        word_name  =  getopt2("-w", opts, "word")
    except:
        print(__doc__)
        sys.exit(0)

    tg, wtier, ptier = read_textgrid(txtgrdfile, word_name, phone_name)
    sampa = read_sampadict()
    ipatier = ipa_tier(sampa, wtier, ptier)
    add_ipa_tier(tg, ipatier, outtxtgrdfile)
