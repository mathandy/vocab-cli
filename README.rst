A CLI to define, create a list of, and quiz you on vocabulary words.

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
