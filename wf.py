#-*- coding:UTF-8 -*-
#import cProfile as profile

`
# In outer section of code
#pr = profile.Profile()
#pr.disable()

# In section you want to profile
#pr.enable()
# code of interest
#pr.disable()

# Back in outer section of code
#pr.dump_stats('profile.pstat')
#import just what we need
#import numpy
import os
#import math
#import sys
import getopt
import string
#import copy
import operator
#import os.path as osp
#import time

import io , sys
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

#import logging
#logging.getLogger().setLevel(logging.INFO)

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hcfd:n:x:p:v:") #h, c, f不需要带参数
    except getopt.GetoptError:
        logging.error('usage : wf.py -c <count> -f <frequency> -d <directory> -n <number> -x <stopword file> -p <number2> -v <verb file>')
        sys.exit(1)
    flag_c = False
    flag_f = False
    flag_d = False
    flag_n = False
    flag_x = False
    flag_p = False
    flag_v = False
    for opt, arg in opts:
        if opt == '-h':
            logging.info('usage : wf.py -c <count> -f <frequency> -d <directory> -n <number> -x <stopword file> -p <number2> -v <verb file>')
            sys.exit(0)
        elif opt in ("-c"):
            flag_c = True
        elif opt in ("-f"):
            flag_f = True
        elif opt in ("-d"):
            directory_name = arg
            flag_d = True
        elif opt in ("-n"):
            top_number = arg
            flag_n = True
        elif opt in ("-x"):
            stop_file = arg
            flag_x = True
        elif opt in ("-p"):
            phrase_length = arg
            flag_p = True
        elif opt in ("-v"):
            verb_file = arg
            flag_v = True
        else:
            logging.error('usage : wf.py -c <count> -f <frequency> -d <directory> -n <number> -x <stopword file> -p <number2> -v <verb file>')
            sys.exit(1)
    
    
    txt_file_list = [] # txt_file_list stores the txt files' names
    if flag_d==False:
        filename = args
        current_folder = './'
        txt_file_list.append(os.path.join(current_folder, filename[0]))
    else:
        file_list = os.listdir(str(directory_name))
        for i, elem in enumerate(file_list):
            if os.path.splitext(elem)[1] == '.txt':
                txt_file_list.append(os.path.join(directory_name, elem))
    
    for file_index in range(len(txt_file_list)):

        if flag_x:
            my_all_lines = drop_stop_words(txt_file_list[file_index], stop_file)

            if flag_v:
                all_lines = unify_verb_after_x(my_all_lines, verb_file)
            
            else:
                all_lines = my_all_lines

            if flag_p:
                results = calculate_phrase_freq_after_v(all_lines, int(phrase_length))# after_v的函数只是为了实现输入为txt的all lines的情况，并不一定要after_v, e.g. after_x 之后得到的也是all lines

            elif flag_c:
                results = calculate_character_freq_after_v(all_lines)

            elif flag_f:
                results = calculate_word_freq_after_v(all_lines)
            
            else:
                raise ValueError("You must specify one of the <-f -c -p>")
        
        else: #flag_x==False:
            if flag_v:
                all_lines = unify_verb(txt_file_list[file_index], verb_file)

                if flag_p:
                    results = calculate_phrase_freq_after_v(all_lines, int(phrase_length))

                elif flag_c:
                    results = calculate_character_freq_after_v(all_lines)


                elif flag_f:
                    results = calculate_word_freq_after_v(all_lines)
                
                else:
                    raise ValueError("You must specify one of the <-f -c -p>")
                    
            else:
                if flag_p:
                    results = calculate_phrase_freq(txt_file_list[file_index], int(phrase_length))

                elif flag_f:
                    results = calculate_word_freq(txt_file_list[file_index])
                
                elif flag_c:
                    results = calculate_character_freq(txt_file_list[file_index])

                else:
                    raise ValueError("You must specify one of the <-f -c -p>")
        
        if flag_n:
            print_word_dict_top_n(results, txt_file_list[file_index], top_number)
        else:
            print_word_dict(results, txt_file_list[file_index])
        

def is_lower_letter(chatr):
    return 97 <= ord(chatr) <= 122

def is_upper_letter(chatr):
    return 65 <= ord(chatr) <= 90

def is_digit(chatr):
    return 48 <= ord(chatr) <= 57

def is_space(chatr):
    return ord(chatr) in (9, 10, 13, 32)

#\r=13, \t=9, \n= 10

def calculate_character_freq(filename):
    chatr_dict = dict.fromkeys(string.ascii_letters, 0)
    with open(filename, 'r', encoding='utf-8') as in_file:
        all_lines = in_file.readlines()
        for item in all_lines:
            for chatr in item:
                if chatr in string.ascii_letters:
                    chatr_dict[chatr] += 1
    return chatr_dict


def calculate_character_freq_after_v(all_lines):
    chatr_dict = dict.fromkeys(string.ascii_letters, 0)
    for item in all_lines:
        for chatr in item:
            if chatr in string.ascii_letters:
                chatr_dict[chatr] += 1
    return chatr_dict

def calculate_word_freq(filename):
    word_dict = {}
    with open(filename, 'r', encoding='utf-8') as in_file:
        all_lines = in_file.readlines()
        for sentence in all_lines:
            #length = len(item)
            started = False
            word = ""
            #sentence = sentence
            for chatr in sentence:
                if started == False and ( is_lower_letter(chatr) or is_upper_letter(chatr) ):
                    started = True
                    word += chatr.lower()
                elif started and ( is_digit(chatr) or is_lower_letter(chatr) or is_upper_letter(chatr) ):
                    word += chatr.lower()
                elif started and not ( is_digit(chatr) or is_lower_letter(chatr) or is_upper_letter(chatr) ):
                    started = False
                    if word in word_dict.keys():
                        word_dict[word] += 1
                    else:
                        word_dict[word] = 1
                    word = ""
                else:
                    pass
    return word_dict

def calculate_word_freq_after_v(all_lines):
    word_dict = {}
    for sentence in all_lines:
        started = False
        word = ""
        for chatr in sentence:
            if started == False and ( is_lower_letter(chatr) or is_upper_letter(chatr) ):
                started = True
                word += chatr.lower()
            elif started and ( is_digit(chatr) or is_lower_letter(chatr) or is_upper_letter(chatr) ):
                word += chatr.lower()
            elif started and not ( is_digit(chatr) or is_lower_letter(chatr) or is_upper_letter(chatr) ):
                started = False
                if word in word_dict.keys():
                    word_dict[word] += 1
                else:
                    word_dict[word] = 1
                word = ""
            else:
                pass
    return word_dict

#def add_to_dict(input_dict, key)

def calculate_phrase_freq(filename, phrase_length):
    phrase_dict = {}
    with open(filename, 'r', encoding='utf-8') as in_file:
        all_contents = in_file.read()#是否考虑文件大于内存的情况
        started = False
        previous_words = []
        previous_words_num = 0
        current_word = ""
        for chatr in all_contents:
            # sentence = sentence
            # for chatr in sentence:
            if started == False and (is_lower_letter(chatr) or is_upper_letter(chatr)):
                started = True
                current_word += chatr.lower()
            elif started and (is_digit(chatr) or is_lower_letter(chatr) or is_upper_letter(chatr)):
                current_word += chatr.lower()
            elif started and is_space(chatr) and current_word:
                previous_words.append(current_word)
                previous_words_num += 1
                current_word = ""
                if previous_words_num == phrase_length:
                    phrase = ' '.join(previous_words)
                    if phrase in phrase_dict.keys():
                        phrase_dict[phrase] += 1
                    else:
                        phrase_dict[phrase] = 1
                    previous_words.pop(0)
                    previous_words_num -= 1

            elif started and not (is_space(chatr)):
                if current_word:
                    previous_words.append(current_word)
                    previous_words_num += 1
                    if previous_words_num == phrase_length:
                        phrase = ' '.join(previous_words)
                        if phrase in phrase_dict.keys():
                            phrase_dict[phrase] += 1
                        else:
                            phrase_dict[phrase] = 1
                started = False
                previous_words = []
                previous_words_num = 0
                current_word = ""
            else:
                pass
    return phrase_dict

def calculate_phrase_freq_after_v(all_lines, phrase_length):
    phrase_dict = {}
    all_contents = ""
    all_contents = all_contents.join(all_lines)
    started = False
    previous_words = []
    previous_words_num = 0
    current_word = ""
    for chatr in all_contents:
        if started == False and (is_lower_letter(chatr) or is_upper_letter(chatr)):
            started = True
            current_word += chatr.lower()
        elif started and (is_digit(chatr) or is_lower_letter(chatr) or is_upper_letter(chatr)):
            current_word += chatr.lower()
        elif started and is_space(chatr) and current_word:
            previous_words.append(current_word)
            previous_words_num += 1
            current_word = ""
            if previous_words_num == phrase_length:
                phrase = ' '.join(previous_words)
                if phrase in phrase_dict.keys():
                    phrase_dict[phrase] += 1
                else:
                    phrase_dict[phrase] = 1
                previous_words.pop(0)
                previous_words_num -= 1
        elif started and not (is_space(chatr)):
            if current_word:
                previous_words.append(current_word)
                previous_words_num += 1
                if previous_words_num == phrase_length:
                    phrase = ' '.join(previous_words)
                    if phrase in phrase_dict.keys():
                        phrase_dict[phrase] += 1
                    else:
                        phrase_dict[phrase] = 1
            started = False
            previous_words = []
            previous_words_num = 0
            current_word = ""
        else:
            pass
    return phrase_dict

def unify_verb(filename, verb_file):
    verb_dict = {}
    with open(verb_file, 'r', encoding='utf-8') as infile:
        all_verb_lines = infile.readlines()
        for verb_line in all_verb_lines:
            verb_info = verb_line.strip().split(' -> ')
            deformed_verbs = verb_info[1].split(',')
            try:
                assert len(deformed_verbs) > 0
            except AssertionError:
                raise AssertionError(verb_info[0])
            origin_verb = verb_info[0]
            for deformed_verb in deformed_verbs:
                if deformed_verb in verb_dict.keys():
                    pass
                    #raise ValueError("deformed verb" + deformed_verb + " has more than one origin verb!")
                else:
                    verb_dict[deformed_verb] = origin_verb
    replaced_lines = []
    with open(filename, 'r', encoding='utf-8') as in_file:
        all_lines = in_file.readlines()
        for sentence in all_lines:
            replaced_sentance = ""
            #length = len(item)
            started = False
            word = ""
            #sentence = sentence
            for chatr in sentence:
                if started == False and ( is_lower_letter(chatr) or is_upper_letter(chatr) ):
                    started = True
                    word += chatr.lower()
                elif started and ( is_digit(chatr) or is_lower_letter(chatr) or is_upper_letter(chatr) ):
                    word += chatr.lower()
                elif started:
                    origin_verb = verb_dict.get(word)
                    if origin_verb == None:
                        replaced_sentance += (word + chatr)
                    else:
                        replaced_sentance += (origin_verb + chatr)
                    started = False
                    word = ""
                else:
                    replaced_sentance += chatr
            replaced_lines.append(replaced_sentance)
    return replaced_lines

def unify_verb_after_x(all_lines, verb_file):
    verb_dict = {}
    with open(verb_file, 'r', encoding='utf-8') as infile:
        all_verb_lines = infile.readlines()
        for verb_line in all_verb_lines:
            verb_info = verb_line.strip().split(' -> ')
            deformed_verbs = verb_info[1].split(',')
            try:
                assert len(deformed_verbs) > 0
            except AssertionError:
                raise AssertionError(verb_info[0])
            origin_verb = verb_info[0]
            for deformed_verb in deformed_verbs:
                if deformed_verb in verb_dict.keys():
                    pass
                    #raise ValueError("deformed verb" + deformed_verb + " has more than one origin verb!")
                else:
                    verb_dict[deformed_verb] = origin_verb
    replaced_lines = []

    if 1==1: # 只是为了对齐代码
        for sentence in all_lines:
            replaced_sentance = ""
            #length = len(item)
            started = False
            word = ""
            #sentence = sentence
            for chatr in sentence:
                if started == False and ( is_lower_letter(chatr) or is_upper_letter(chatr) ):
                    started = True
                    word += chatr.lower()
                elif started and ( is_digit(chatr) or is_lower_letter(chatr) or is_upper_letter(chatr) ):
                    word += chatr.lower()
                elif started:
                    origin_verb = verb_dict.get(word)
                    if origin_verb == None:
                        replaced_sentance += (word + chatr)
                    else:
                        replaced_sentance += (origin_verb + chatr)
                    started = False
                    word = ""
                else:
                    replaced_sentance += chatr
            replaced_lines.append(replaced_sentance)
    return replaced_lines

def drop_stop_words_v2(filename, stop_file):
    with open(stop_file, 'r', encoding='utf-8') as infile:
        stop_words = []
        for stop_word in infile.readlines():
            stopword = stop_word.strip('\n')
            stop_words.append(stopword)
        #print(stop_words)
        with open(filename, 'r', encoding='utf-8') as in_file:
            all_lines = in_file.readlines()
            new_all_lines = []
            for line in all_lines:
                for stop_word in stop_words:
                    #print (stop_word)
                    #line = line.replace(str(' '+str(stopword)), '').replace(str(str(stopword)+' '), '')
                    line = (line.lower()).replace(' '+stop_word+' ', ' ')#.replace(stop_word+' ', '').replace(' '+stop_word, '')
                new_all_lines.append(line)
        with open(filename+'.replace', 'w', encoding='utf-8') as outfile:
            for line in new_all_lines:
                outfile.write(line)# ssss

    return new_all_lines




def drop_stop_words(filename, stop_file):
    with open(stop_file, 'r', encoding='utf-8') as infile:
        stop_words = []
        for stop_word in infile.readlines():
            stopword = stop_word.strip('\n')
            stop_words.append(stopword)
        with open(filename, 'r', encoding='utf-8') as in_file:
            all_lines = in_file.read()
            for stop_word in stop_words:
                new_all_lines = (all_lines.lower()).replace(' '+stop_word+' ', ' ').replace(' '+ stop_word+'\n', '\n').replace('\n'+stop_word+' ', '\n')
        '''
        with open(filename+'.replace', 'w', encoding='utf-8') as outfile:
            outfile.write(new_all_lines)# ssss
        #print(new_all_lines[:500])
        '''
        new_all_lines = new_all_lines.split('\n')


    return new_all_lines

        

'''
def print_dict(input_dict, reverse=True):
    # input_dict = [a:25, b:36]
    #if reverse = True, use descend order
    total = sum(input_dict.values())
    def sort_matrix(kv):
        return input_dict[kv]-ord(kv)/1000

    sorted_input_dict = sorted(input_dict, key=sort_matrix , reverse=reverse)
    for dict_elem in sorted_input_dict:
        print(dict_elem + ': ' + str(input_dict[dict_elem]/total))
'''

def print_word_dict(input_dict, filename, reverse=True):
    total = sum(input_dict.values())
    word_list = [(key, input_dict[key]) for key in input_dict.keys()]
    sorted_input_dict = sorted(word_list, key=operator.itemgetter(0) , reverse=False)
    sorted_input_dict = sorted(sorted_input_dict, key=operator.itemgetter(1) , reverse=True)
    for key, value in sorted_input_dict[:50]:
        #a = "I'm %s. I'm %d year old" % ('Vamei', 99)
        #print(key + ': ' + str(value/total) + ',' + str(value))
        print("%40s\t%d" % (key, value))

def print_word_dict_top_n(input_dict, filename, top_number, reverse=True):
    total = sum(input_dict.values())
    word_list = [(key, input_dict[key]) for key in input_dict.keys()]
    sorted_input_dict = sorted(word_list, key=operator.itemgetter(0) , reverse=False)
    sorted_input_dict = sorted(sorted_input_dict, key=operator.itemgetter(1) , reverse=True)
    top_number = int(top_number)
    print(filename)
    for key, value in sorted_input_dict[:top_number]:
        #print(key + ': ' + str(value/total) + ',' + str(value))
        print("%40s\t%d" % (key, value))


if __name__ == "__main__":
    main(sys.argv[1:])
