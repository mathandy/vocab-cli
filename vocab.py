#!/usr/bin/python
"""A CLI to define, create a list of, and quiz you on vocabulary words.

Usage:
------
Replace <word> with a word (or phrase) in the following examples::

    $ vocab <word>  # define and add given word to your vocabulary list
    $ vocab a <word>  # add given word to your vocabulary list
    $ vocab rm <word>  # remove given word from your vocabulary list
    $ vocab ls  # list the words in the vocabulary list
    $ vocab d <word>  # print the deinition(s) of given word.
    $ vocab q  # quiz on all words in list
    $ vocab q 10  # quiz on 10 random words from list

How to add words manually:
--------------------------
Definitions not available on dictionary.com (or that you wish to 
personalize) can be added manually by creating and adding a file to the 
`user-defs` subdirectory.  Simply paste the definition into a file 
named after the exact word/phrase (with no extension).  The `user-defs` 
subdirectory must be located in the same directory as `vocab.py` (you 
must create it).  
If you wish to be quized on this word/definition, you must also add it
to the master list.

How to make this script executable anywhere (on mac or linux):
-----------------------------------------------------
1. Make sure the first line of this script is #!/usr/bin/python
2. Make script executable::

    $ chmod 775 vocab.py

3. Make a link so that the terminal will find this script::

    $ sudo ln -s "$PWD"/vocab.py /usr/bin/vocab

Misc. Notes:
------------
* This code assumes words are always case-sensitive and may include 
    symbols and/or whitespace.
* When searching Dictionary.com for a definitions, spaces are replaced
    by double hyphens.
* Removing a definition from the vocabulary list (with the rm/remove 
    command), does not remove any definition present in the `user-defs` 
    subdirectory.
* The master vocabulary list should be a single column of words. 
    CSV style is fine too (each cell being a word), but this will be 
    converted to a column.

Credit:
-------
This code was created by Andrew Allan Port (AndyAPort@gmail.com).
Definitions are scraped from Dictionary.com.

Licence:
--------
This software is available under the MIT License.  
Copyright (c) 2017 Andrew Allan Port.

"""
from __future__ import print_function
try: input = raw_input 
except: pass

import re, sys, os
from urllib2 import urlopen
from shutil import copyfile
from random import sample


root_dir = os.path.dirname(os.path.realpath(__file__))
user_defs_dir = os.path.join(root_dir, 'user-defs')
word_list_location = os.path.join(root_dir, 'word-list.txt')


def get_word_list():
    with open(word_list_location, 'r') as wl:
        words = []
        for row in wl:
            words += row.split(',')
        words = [w.strip().lower() for w in words]
    return words


def add_word(word):
    with open(word_list_location, 'a') as wl:
        wl.write('\n' + word)


def remove_word(word, backup=True):
    word_list = get_word_list()
    try:
        word_list.remove(word)
    except ValueError:
        print('"{}" not found in word list. '
              'Remember, words are case-sensitive.'.format(word))
        sys.exit(1)

    # create backup (after checking word list opens)
    try:
        copyfile(word_list_location, word_list_location + '.bu')
    except:
        print("="*50)
        print("Unexpected error attempting to backup list, "
              "exiting without overwriting master list.\n\n")
        print("="*50)
        traceback.print_exc()
        sys.exit(1)

    with open(word_list_location, 'w') as wl:
        wl.write('\n'.join(word_list))


def list_words():
    print("\nMaster list location:\n" + word_list_location, '\n')
    for word in get_word_list():
        print(word)
    print()


def get_user_def(word, print_def=True):
    """Get user definition of `word`, or return False if not found."""
    print(os.path.join(user_defs_dir, word))
    try:
        with open(os.path.join(user_defs_dir, word)) as ud:
            user_def = '\n'.join(list(ud))
            if print_def:
                print(user_def)
            return user_def
    except IOError:
        return False


def define(word, print_def=True):
    """Get definition of `word`.

    If not defined by user, scrapes the definition of `word` from 
    dictionary.com.  If not available there, returns False."""

    user_def = get_user_def(word, print_def=print_def)
    if user_def:
        return user_def

    word = word.replace(' ', '--')
    url_to_scrape = "http://dictionary.reference.com/browse/" + word
    try:
        html = urlopen(url_to_scrape).read()
    except:
        print('\nEither this code is out-of-date or dictionary.com '
              'does not know what "{}" means and no user-definition '
              'was found in {} .\n'.format(word, user_defs_dir))
        return False
    items=re.findall('<div class="def-content">\s.*?</div>', html, re.S)
    defs = [re.sub('<.*?>','', x).strip() for x in items]

    web_def = ''
    for i, d in enumerate(defs):
        web_def += '\n' + str(i+1) + '. ' + d

    if print_def:
        print(web_def)
    return web_def


def quiz(n):
    """Quiz user on `n` random words from the master word list."""
    master_list = get_word_list()

    if n is None:
        n = len(master_list)

    for i, word in enumerate(sample(master_list, n)):
        input('\n' + '='*50 + '\n[Q. {}/{}] Define: "{}"  \n'
              '(Press enter when ready for definition.)'
              ''.format(i+1, n, word))
        print('-'*50)
        define(word)


if __name__ == '__main__':
    try:
        if sys.argv[1] in ['add', 'a']:
            add_word(' '.join(sys.argv[2:]))
        elif sys.argv[1] in ['remove', 'rm']:
            remove_word(' '.join(sys.argv[2:]))
        elif sys.argv[1] in ['list', 'ls']:
            list_words()
        elif sys.argv[1] in ['define', 'd']:
            define(sys.argv[2])
        elif sys.argv[1] in ['quiz', 'q']:
            try:
                num_questions = int(sys.argv[2])
            except:
                num_questions = None
            quiz(num_questions)
        elif sys.argv[1] in ['help', 'h']:
            print(__doc__)
        else:
            if len(sys.argv) == 2 and define(sys.argv[1]):
                add_word(sys.argv[1])
            else:
                print("\nFor help, use `vocab help`.\n")

    except Exception as e:
        print("Whoops... something went wrong in an unexpected way:")
        print(e)
        print("\nFor help, use `vocab help`.\n")
    finally:
        sys.exit(0)
