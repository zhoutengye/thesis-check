import re
import json
import os
import sys
import pycorrector
from pycorrector.ernie.ernie_corrector import ErnieCorrector
from pycorrector.macbert.macbert_corrector import MacBertCorrector

def get_param(json_file):
    # load json file
    with open(json_file,'r') as load_f:
        load_json = json.load(load_f)
    # get list of files
    tex_files = get_path(load_json)
    report_file = load_json['dir']['report']
    # get oral check options
    oral_check = get_oralrules(load_json)
    # load options
    options = load_json['options']
    return report_file, tex_files, oral_check, options

def get_path(js):
    # get the list of tex files
    path = js['dir']['path']
    ignore = js['dir']['ignore']
    all_files = os.walk(path)
    tex_files = []
    # get the list of tex files
    for dir_files in all_files :
        file_dir = dir_files[0]
        files = dir_files[2]
        for file in files:
            if file[-4:] == ".tex":
                tex_files.append([file_dir,file])
    return tex_files

def get_oralrules(js):
    options = js['options']
    if options['oral_detect'] == False:
        return {"check":False}
    oral_check = {}
    oral_check.update({"check":True})
    level = options["level"]
    oral_rules = js['oral']
    oral_check.update({"level":level})
    oral_check.update({"customize":oral_rules['customize']})
    oral_keywords=[]
    for i in range(level):
        key = 'level'+str(int(i+1))
        oral_keywords += oral_rules[key]
    oral_check.update({"default":oral_keywords})
    return oral_check

def find_duplicate(texfile):
    texfile=open(texfile,'r')
    duplicates = []
    n = 0
    for line in texfile:
        n+=1
        ind = 0
        if line[0]=='%':
            continue
        for i in range(len(line)-1):
            ind+=1
            for j in range(4):
                wl = j+1
                wl2 = wl+wl
                if line[i:i+wl]==line[i+wl:i+wl2] and '\u4e00' <= line[i] <= '\u9fa5':
                    duplicates.append([n,wl2,ind,line])
                    # print ('第',n,'行，第',ind,'个字符:',
                            # line[:ind-1],'<<<',line[ind-1:ind+wl2-1],'>>>',line[ind+wl2-1:])
    texfile.close()
    return duplicates

def find_oral_words(texfile,oral_check):
    texfile=open(texfile,'r')
    orals = []
    n = 0
    level = oral_check['level']
    for line in texfile:
        n+=1
        if line[0]=='%':
            continue
        for word in oral_check['default']:
            ind = line.find(word)
            if ind != -1:
                orals.append([word,n,ind,line])
                # print ('第',n,'行，第',ind,'个字符:',
                        # line[:ind],'<<<',line[ind:ind+len(word)],'>>>',line[ind+len(word):])
    texfile.close()
    return orals

def AIcorrect(texfile,engine):
    texfile=open(texfile,'r')
    # choose engine
    if engine == 'kelnm':
        pycorrector.enable_char_error(enable=False)
        corrector = pycorrector.correct
    elif engine == 'erine':
        m = ErnieCorrector()
        corrector = m.ernie_correct
    elif engine == 'macbert':
        m2 = MacBertCorrector("shibing624/macbert4csc-base-chinese")
        corrector = m2.macbert_correct
    else:
        print("错误的 engine 类型，请选择 kelnm, erine, macbert 之一")
        quit()

    # run AI correct
    AIcorrects = []
    n = 0
    for line in texfile:
        correct_sent, err = corrector(line)
        n+=1
        if err != []:
            AIcorrects.append([n,line, correct_sent, err])

    return AIcorrects

def find_singlefile(texfile,oral_check,options):
    single_check = {}
    single_check.update({"filename":texfile})

    # get duplicate check result for single file
    if options['duplicate_detect']:
        duplicates = find_duplicate(texfile)
        if duplicates == []:
            single_check.update({"duplicate_check":False})
        else:
            single_check.update({"duplicate_check":True})
            single_check.update({"duplicates":duplicates})
    else:
        single_check.update({"duplicate_check":False})

    # get oral check result for single file
    if options['oral_detect']:
        orals = find_oral_words(texfile,oral_check)
        if orals == []:
            single_check.update({"oral_check":False})
        else:
            single_check.update({"oral_check":True})
            single_check.update({"orals":orals})
    else:
        single_check.update({"oral_check":False})

    # get AI correct result for single file
    if options['AIcorrect']:
        engine = options['corrector_engine']
        AIs = AIcorrect(texfile,engine)
        if AIs == []:
            single_check.update({"AI_check":False})
        else:
            single_check.update({"AI_check":True})
            single_check.update({"AIs":AIs})
    else:
        single_check.update({"AI_check":False})

    return single_check

def write_single(f,single_check):
    if (single_check['oral_check'] or single_check['duplicate_check']):
        f.write('# '+single_check['filename']+'\n')
    else:
        return
    # write oral check part
    if (single_check['oral_check']):
        f.write('## orals:'+'\n')
        ol = single_check['orals']
        for i in range(len(ol)):
            word = ol[i][0]
            n = ol[i][1]
            ind = ol[i][2]
            line = ol[i][3]
            f.write('第'+str(n)+'行，第'+str(ind)+'个字符:'+
                    line[:ind]+'<<<'+line[ind:ind+len(word)]+'>>>'+line[ind+len(word):]+'\n')
    # write duplicate check part
    if (single_check['duplicate_check']):
        f.write('## duplicates:'+'\n')
        du = single_check['duplicates']
        for i in range(len(du)):
            n = du[i][0]
            wl2 = du[i][1]
            ind = du[i][2]
            line = du[i][3]
            f.write('第'+str(n)+'行，第'+str(ind)+'个字符:'+
                    line[:ind-1]+'<<<'+line[ind-1:ind+wl2-1]+'>>>'+line[ind+wl2-1:]+'\n')
    # write AI correct part
    if (single_check['AI_check']):
        f.write('## AI_check:'+'\n')
        AIs = single_check['AIs']
        for i in range(len(AIs)):
            n = AIs[i][0]
            line = AIs[i][1]
            correct_sent = AIs[i][2]
            err = AIs[i][3]
            f.write('第'+str(n)+'行 '+line)
            for i in range(len(err)):
                f.write(str(err[i]))
            f.write('\n')

def write_to_report(report_file, tex_files, oral_check, options):
    f = open(report_file,'w')
    for file in tex_files:
        tex_file = file[0]+'/'+file[1]
        single_check = find_singlefile(tex_file,oral_check,options)
        write_single(f,single_check)
    return

json_file = 'thesis_check.json'
report_file, tex_files, oral_check, options = get_param(json_file)
write_to_report(report_file, tex_files, oral_check, options)

