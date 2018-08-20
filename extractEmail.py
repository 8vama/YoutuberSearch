#!/usr/bin/env python
#
# Extracts email addresses from one or more plain text files.
#
# Notes:
# - Does not save to file (pipe the output to a file if you want it saved).
# - Does not check for duplicates (which can easily be done in the terminal).
#
# (c) 2013  Dennis Ideler <ideler.dennis@gmail.com>

from optparse import OptionParser
import os.path
import re

regex = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                    "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))

music_regex = re.compile(("(songs?)|(spotify)|(music\W)|(soundcloud)|(tracks?)"))

def file_to_str(filename):
    """Returns the contents of filename as a string."""
    with open(filename) as f:
        return f.read().lower() # Case is lowered to prevent regex mismatches.

def containsMusic(s):

    return music_regex.search(s)



def get_emails(s):
    """Returns an iterator of matched emails found in string s."""
    # Removing lines that start with '//' because the regular expression
    # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
    i = (email[0] for email in re.findall(regex, s) if not email[0].startswith('//'))
    result = ""
    for email in i:
        result += str(email) 
        result += "\n"
    return result



#s = "check out the Music "
#t = s.lower()

#print get_emails("maming@gmail.com, hahah@yahoo.com")

#print containsMusic(t) != None

'''
if __name__ == '__main__':
    parser = OptionParser(usage="Usage: python %prog [FILE]...")
    # No options added yet. Add them here if you ever need them.
    options, args = parser.parse_args()

    if not args:
        parser.print_usage()
        exit(1)

    for arg in args:
        if os.path.isfile(arg):
            print get_emails(file_to_str(arg)):

        else:
            print '"{}" is not a file.'.format(arg)
            parser.print_usage()
'''