#! python3

import sys
import os
import re
import logging

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.debug("start of logging")


def strsysargv():
    rest = ''
    for i in sys.argv[1:]:
        rest += i + ' '
        print(i)
    new = sys.argv[0:1]
    new.append(rest[:-1])
    print(new)
    return new


def opendecks(directory=''):  # open files with .dck ending and create deck classes
    if len(sys.argv) > 1:
        filelist = os.listdir(strsysargv()[1])
        os.chdir(strsysargv()[1])
    else:
        if directory == '':
            filelist = os.listdir(os.getcwd())
        else:
            os.chdir(directory)
            filelist = os.listdir(directory)
    logging.debug("filelist: (%s)" % filelist)
    for i in filelist:
        logging.debug("current filename: %s" % i)
        if ".dck" in i:
            logging.debug("final filename: %s" % i)
            Deck(i)
    return 0


class Deck:
    def __init__(self, name):
        lines = self.getlines(open(name, 'r'))
        newlines = self.parsedeck(lines)
        self.createtxt(newlines, name)
        
    def getlines(self, fullfile):  # read lines and remove last 2 lines
        decklines = fullfile.readlines()
        decklines = decklines[:-2]
        return decklines

    def parsedeck(self, decklines):  # creates new list of lines, parsed
        # set bracket and card number: [1-6 word characters :  1-3 word characters]
        bracketsregex = re.compile(r'\[\w{3,6}:\w{1,4}\]')
        # find and remove brackets and "SB:"
        newlines = []
        flag = 0
        for line in decklines:
            bracket = bracketsregex.search(line).group()
            logging.debug('bracket found: %s' % bracket)
            line = line.replace(bracket + ' ', '')
            if 'SB' in line and flag == 0:
                flag = 1
                line = '\n' + line
            line = line.replace('SB: ', '')
            logging.debug('line after removing bracket: %s' % line)
            newlines.append(line)
        return newlines

    def createtxt(self, newlist, filename):  # create txt file and write parsed lines
        newname = filename.replace('.dck', '.txt')
        newfile = open(newname, 'w')
        logging.debug('created: %s' % newname)
        for line in newlist:
            newfile.write(line)
            logging.debug('wrote: %s' % line)


opendecks()
