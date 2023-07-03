#!python2.6.2

'''wmrws's android port

wmrws is Weakish's Minimalistic Recite Words System

(c) 2009-2011 Jakukyo Friel  <weakish@gmail.com>
This program is licensed under GPL v2.

https://gist.github.com/900426

'''

import os
import sys
import time
import pickle
import random
import gtts

def raw_input(prompt=''):
    return input (prompt)

class word_list():
    def __init__(self, pickle_name):
        self._pickle_name = pickle_name
        self.load()

    def load(self):
        try:
            with open(self._pickle_name, 'rb') as inp:
                self._words = pickle.load(inp)
        except FileNotFoundError:
            self._words = {}

    def save(self):
        with open(self._pickle_name, 'wb') as outp:
            pickle.dump(self._words, outp, pickle.HIGHEST_PROTOCOL)

    def size(self):
        return len(self._words)

    def add(self, english, chinese):
        if english in self._words:
            print ('Warning: {} already in the list, replacing meaning from {} to {}'.format(english, self._words[english]['chinese'], chinese))
            rate = self._words[english]['rate']
            self._words[english] = {'chinese':chinese, 'rate':rate}
        else:
            if has_audio(english):
                # add a new word to the list, set initial weight to 10.0
                self._words[english] = {'chinese':chinese, 'rate':10.0}
            else:
                print ("Cannot add {} because audio file does not exist.".format(english))
                print ("Please download audio file and try again.")

    def delete(self, english):
        if english in self._words:
            self._words.pop(english)

    def up_rate(self, english):
        if not english in self._words:
            print ('Error: {} is not in word list'.format(english))
            return
        rate = self._words[english]['rate']
        self._words[english]['rate'] = rate * 1.5

    def down_rate(self, english):
        if not english in self._words:
            print ('Error: {} is not in word list'.format(english))
            return
        rate = self._words[english]['rate']
        self._words[english]['rate'] = rate / 1.5

    def pick_with_rate(self, threshold):
        total_rate = 0
        for key in self._words:
            if self._words[key]['rate'] >= threshold:
                total_rate += self._words[key]['rate']
        if total_rate == 0 and threshold > 0:
            return self.pick_with_rate(-1.0)
        elif total_rate == 0:
            return None
        r = random.uniform(0, total_rate)
        current_accumulated_rate = 0
        for key in self._words:
            if self._words[key]['rate'] >= threshold:
                current_accumulated_rate += self._words[key]['rate']
                if current_accumulated_rate >= r:
                    return key
        # did't find words with rate above threshold
        return None

    def get_chinese(self, english):
        return self._words[english]['chinese']

    def get_rate(self, english):
        return self._words[english]['rate']

    def get_int_rate(self, english):
        rate = self._words[english]['rate']
        if rate < 0.1:
            return 5
        elif rate < 0.5:
            return 4
        elif rate < 2:
            return 3
        elif rate <10:
            return 2
        else:
            return 1

    def print_new(self):
        sorted_words = sorted(self._words)
        for english in sorted_words:
            chinese = self._words[english]['chinese']
            rate = self._words[english]['rate']
            if rate < 8:
                continue
            print ("{} : {}".format(english, chinese), end = '')
            total_len = len(english) + 2*len(chinese)
            pad = 30 - total_len
            for i in range(pad):
                print (' ', end='')
            print ("熟练度: ", end='')
            if rate < 0.1:
                print ("5")
            elif rate < 0.5:
                print ("4")
            elif rate < 2:
                print ("3")
            elif rate <10:
                print ("2")
            else:
                print ("1")

    def print(self):
        sorted_words = sorted(self._words)
        counts = [0, 0, 0, 0, 0, 0]
        count = 0
        for english in sorted_words:
            count += 1
            chinese = self._words[english]['chinese']
            rate = self._words[english]['rate']
            print ("{} : {}".format(english, chinese), end = '')
            total_len = len(english) + 2*len(chinese)
            pad = 30 - total_len
            for i in range(pad):
                print (' ', end='')
            print ("熟练度: ", end='')
            if rate < 0.1:
                print ("5")
                counts[5] += 1
            elif rate < 0.5:
                print ("4")
                counts[4] += 1
            elif rate < 2:
                print ("3")
                counts[3] += 1
            elif rate <10:
                print ("2")
                counts[2] += 1
            else:
                print ("1")
                counts[1] += 1
        print (f'Total: {count}')
        print ('Word with ranks:')
        print (f' 5 - {counts[5]}')
        print (f' 4 - {counts[4]}')
        print (f' 3 - {counts[3]}')
        print (f' 2 - {counts[2]}')
        print (f' 1 - {counts[1]}')
        average_rank = (5*counts[5] + 4*counts[4] + 3* counts[3] + 2* counts[2] + 1* counts[1])/count
        average_rank = int(average_rank * 10)/10
        print (f' average rank {average_rank}')

    _pickle_name = None
    _words = None

def pronounce(word):
    if has_audio(word):
        file = "resource/audio/{}.mp3".format(word.lower())
        os.system('mpv {} >/dev/null'.format(file))
    else:
        os.system('termux-tts-speak {}'.format(word))

def has_audio(word):
    file = "resource/audio/{}.mp3".format(word.lower())
    if os.path.exists(file):
        return True
    else:
        gtts.tts.gTTS(word, slow=True).save("tmp.mp3")
        os.rename("tmp.mp3", file)
        if os.path.exists(file):
            return True
    return False

def Test(word_list):
    '''Test your wordlist.
    '''
    if word_list.size() == 0:
        print ('Done.')
    else:
        score = 0
        num_tests = 30
        word_rates_before = {}
        word_rates_after = {}
        last_wrong_word = None
        for i in range (num_tests):
            os.system('clear')
            if last_wrong_word != None:
                english = last_wrong_word
            else:
                english = word_list.pick_with_rate(9.9)
            if not (english in word_rates_before):
                word_rates_before[english] = word_list.get_int_rate(english)
            print (word_list.get_chinese(english))
            pronounce(english)
            os.system('clear')
            time.sleep(0.5)
            print (word_list.get_chinese(english))
            pronounce(english)
            os.system('clear')
            print (word_list.get_chinese(english))
            result = input ("{} of 30 - Spell this word: ".format(i+1))
            if result == english:
                print ("Correct!")
                score += 1
                word_list.down_rate(english)
                word_rates_after[english] = word_list.get_int_rate(english)
                last_wrong_word = None
            else:
                pronounce("wrong")
                print ("Wrong!")
                print ("The word is '{}'.\n".format(english))
                print ("You entered '{}'.\n".format(result))
                word_list.up_rate(english)
                word_rates_after[english] = word_list.get_int_rate(english)
                print ("Spell the word 3 times.  Press enter to continue.")
                count = 0
                while count < 3:
                    word = input ("> ")
                    if word == english:
                        count += 1
                last_wrong_word = english
        print ("Score = {}".format(score*100/num_tests))

        # print rate changes
        for word in word_rates_before:
            if word_rates_after[word] > word_rates_before[word]:
                print ("{}: {} --> {}".format(word, word_rates_before[word], word_rates_after[word]))
            if word_rates_after[word] < word_rates_before[word]:
                print ("{}: {} --> {}".format(word, word_rates_before[word], word_rates_after[word]))

def Sleep(interval):
    if interval < 0: # hold until someone press Enter
        raw_input()
    else:
        time.sleep(interval)

def AddWord(word_list):
    english = input('Input English word: ')
    chinese = input('Input Chinese meaning: ')
    word_list.add(english, chinese)

def DeleteWord(word_list):
    english = input('Input English word: ')
    word_list.delete(english)


# Info


def Help():
    print ('''
Commands:
p    review all words
pn   review words that needs practice
t    30 words test
a    add a word
d    delete a word
s    save word list
l    load word list from file
q    quit
k    quit without saving
?    print this help page
    ''')



def Wordify(wordFile):
    '''convert wordlist files (one word/phrase per line) to lists'''
    return [line.strip('\n') for line in open(wordFile).readlines()]
    # note we strip the newline character.



# main program

def main(word_list):
    while True:
        Help()
        opt = raw_input('command: ')
        if opt == 'p':
            word_list.print()
        if opt == 'pn':
            word_list.print_new()
        elif opt == 'a':
            AddWord(word_list)
        elif opt == 'd':
            DeleteWord(word_list)
        elif opt == 't':
            Test(word_list)
        elif opt == 's':
            word_list.save()
        elif opt == 'l':
            word_list.load()
        elif opt == 'q':
            word_list.save()
            print ('Goodbye!')
            break
        elif opt == 'k':
            print ('Goodbye!')
            break

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        filename = 'word.pkl'
    else:
        filename = sys.argv[1]

    word_list = word_list(filename)
    main(word_list)
