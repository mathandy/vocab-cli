#!/usr/bin/env python
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

3. Make a link so that the terminal will find this script:

    $ sudo mkdir /usr/local/bin  # likely already exists
    $ sudo ln -s "$PWD"/vocab.py /usr/local/bin/vocab

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
import re, sys, os
from shutil import copyfile
from random import sample

try:
    from PyDictionary import PyDictionary as pyd
    use_pydictionary = True

    # adhoc fix to prevent warnings cause by PyDictionary
    import warnings
    warnings.filterwarnings("ignore")
except ImportError:
    from warnings import warn
    warn("For better results, please install PyDictionary.  On most "
         "systems, this can be done using the terminal/command-prompt "
         "by entering the command:\n\tpip install PyDictionary\n")
    use_pydictionary = False


if sys.version_info < (3, 0):  # if using Python 2
    input = raw_input
    from urllib2 import urlopen
else:
    from urllib.request import urlopen


root_dir = os.path.dirname(os.path.realpath(__file__))
user_defs_dir = os.path.join(root_dir, 'user-defs')
word_list_location = os.path.join(root_dir, 'word-list.txt')


def open_file(filepath):
    import subprocess, os, platform
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))


def single_spaced(s, convert_tabs_to_spaces=True):
    """Removes redundant whitespace."""
    new_s = s.replace('\t', ' ') if convert_tabs_to_spaces else s
    new_s = [c for i, c in enumerate(new_s[:-1])
             if not c == new_s[i+1] == ' ']
    return new_s + new_s[-1]


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
        import traceback
        traceback.print_exc()
        sys.exit(1)

    with open(word_list_location, 'w') as wl:
        wl.write('\n'.join(word_list))


def list_words(*vargs, **kwargs):
    print("\nMaster list location:\n" + word_list_location, '\n')
    for word in get_word_list():
        print(word)
    print()


def get_user_def(word):
    """Get user definition of `word`, or return False if not found."""
    try:
        with open(os.path.join(user_defs_dir, word)) as ud:
            user_def = ''.join(list(ud))
            return user_def
    except IOError:
        return False


def get_pydict_def(word):
    """Returns string definition using PyDictionary."""
    pydict_def = ''
    for part_of_speech, def_list in pyd().meaning(word).items():
        pydict_def += part_of_speech
        for i, d in enumerate(def_list):
            pydict_def += '\n\t' + str(i+1) + '. ' + d
        pydict_def += '\n'
    if pydict_def:
        return pydict_def


def scrape_web_def(word):
    """Scrapes definitions from Dictionary.com."""
    word = word.replace(' ', '--')
    url_to_scrape = "https://dictionary.reference.com/browse/" + word
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

    web_def = single_spaced(web_def)
    return web_def


def define(word, print_def=True):
    """Get definition of `word`.

    If not defined by user, scrapes the definition of `word` from
    dictionary.com and/or PyDictionary.  If definition not available,
    returns False."""

    definition = get_user_def(word)
    if definition:
        return definition

    if use_pydictionary:
        definition = get_pydict_def(word)
        if definition:
            return definition

    definition = scrape_web_def(word)
    if print_def:
        print('\n' + definition)
    return definition


def quiz(n):
    """Quiz user on `n` random words from the master word list."""
    master_list = get_word_list()
    n = int(n) if n else len(master_list)
    for i, word in enumerate(sample(master_list, n)):
        input('\n' + '='*50 + '\n[Q. {}/{}] Define: "{}"  \n'
              '(Press enter when ready for definition.)'
              ''.format(i+1, n, word))
        print('-'*50)
        define(word)


def add_user_def(word):
    from pathlib import Path
    fp = os.path.join(user_defs_dir, word)
    Path(fp).touch()
    open_file(fp)


def add_and_define(word):
    """if definition is available, add and define"""
    definition = define(word, print_def=True)
    if definition and word not in get_word_list():
        add_word(word)


commands = {
    'add': add_word,
    'remove': remove_word,
    'list': list_words,
    'define': define,
    'add_user_def': add_user_def,
    'quiz': quiz,
    'help': help,
}

shortcuts = {
    'a': commands['add'],
    'rm': commands['remove'],
    'ls': commands['list'],
    'd': commands['define'],
    'u': commands['add_user_def'],
    'q': commands['quiz'],
    'h': commands['help'],
}

commands.update(shortcuts)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('option', nargs='?', default=None)
    args = parser.parse_args()

    if args.command not in commands.keys():
        args.option = args.command
        args.command = 'define'
    commands[args.command](args.option)
