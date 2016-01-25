# DuplAway
Routine to identify duplicates in fuzzy data (such as, for example, bibliographical records)

# Running the script:
   - works of Python 3
   - [fuzzywuzzy library](http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/) must be installed

# Routine 2:
 - uses TSV with any number of columns; works best for comparing
   complex items (bibliographical records)
## Parameters are as follows:

 - **file** : the name of a data file for processing (must be in the same folder as the script)
 - **thr**[eshold] : the lowest comparison ratio to consider
 - **alg**[orithm] : chooses one of the 4 fuzzywuzzy routines
  - [1] `fuzz.ratio`
  - [2] `fuzz.partial_ratio`
  - [3] `fuzz.token_sort_ratio`
  - [4] `fuzz.token_set_ratio`
  - [Detailed descriptions of these algorithms.](http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/)
 - **len**[gth]    : the length (in words) of the first comparison string; works better when comparing longer strings with shorter ones
 - **sav**[e Mode] : 'all', or 'man'
   - all - saves all: + works faster on restart; - creates really large result files (dupl)
     - a) if you don't mind extra space, restarting is much faster with 'all', since the script does have to calculate anew
     - b) re-running with 'man' will remove all irrelevant results, keeping only manually tagged ones ('y', 'n', 'm', and other supported choices)
 - **id** : column with unique identifiers --- required column!
 - **comp**[are] : columns to use for comparison (separated by commas); for example, [author] and [title] for identifying bibliographical records for the same works
 - **disp**[lay] : columns to use for showing during the decision stage (separated by commas); for example, [author], [title], [editor], etc. for bibliographical records
 - **verb**[al]: a word that will be added as an infix into a file with results; makes it easier to understand what kind of data the file contains; for example, the same dataset can be used for different purposes, and while it will be reflected in the infix, where the the column numbers are given, it is not very readable. Adding a simple verbal marker should be helpful (so, verb=Authors > analyzing Authors' names; verb=Book --- book titles, etc.)

*NB*: arguments (i.e., everything after 'python3 duplAway.py') can be given in any order; do not change the name of the script, since it will break the argument analysis logic

## example command for Routine 2
```
$ python3 duplAway.py file=AraCorpus_NewBiblio_TriCollection.tsv thr=90 alg=4 len=5 id=[4] comp=[4] disp=[4,6] verb=Authors sav=all
```

- the script will analyze file 'AraCorpus_NewBiblio_TriCollection.tsv',
- using algorithm 4 and showing only results with 90% likelihood
- comparing longer strings with shorter ones seems to work better, hence the lower limit is set to 5 [words]; you may want to experiment with this parameter (increase it, if you get stuck);
- it will use column 4 for ids
- it will also use values from col 4 for comparison;
- it will show also data from cols 4 and 6, which should help to make the finals decision whether this is a true of false match
- it will add 'Authors' to the name of the file (for readability) this essentially means that we are comparing names of authors
- it will also save ALL results on exit

```
$ python3 duplAway.py file=AraCorpus_AuthorNames.tsv thr=90 alg=4 len=5 id=[1] comp=[2] disp=[2,3,4] verb=Authors sav=all
```

```
$ python3 duplAway.py file=AraCorpus_NewBiblio_TriCollection.tsv thr=90 alg=4 len=5 id=[1] comp=[4,8] disp=[1,3,4,6,8,13] verb=Books sav=all
```

# Config file
Using a config file is a more convenient option: all parameters are stored in a file > shorter command

Example for Routine 2 (include the following 11 lines into a file > configFile2.txt); everything after '#' is a comment

```
============================
~duplAway.py           # do not change
~file = AraCorpus_NewBiblio_TriCollection.tsv # this is the file you will analyze
~sav  = all            # variants: all, man[ually tagged]
~thr  = 98             # number between 1 and 100 (100 is usually a very close match [depends of the algorithm])
~alg  = 1              # one of the 4 fuzzywuzzy routines 
~len  = 5              # the shortest length of string (in words) to run comparison on
~id   = [1]            # the number of the column whenre the IDs are
~comp = [4,8]          # the numbers of columns strings from which should be compared (divided by commas)
~disp = [1,3,4,6,8,13] # the numbers of columns strings from which should be printed on the screen (divided by commas)
~verb = Books          # this is the infix that will be added to the name of the file with results  
============================
```

The command to run the script then becomes:

```
$ python3 duplAway.py configFile2.txt
```

# Some thoughts and suggestions
 1. fuzzywuzzy Library has 4 algorithms that have different level of tolerance, so it make sense to start with algorithm 1 and threshold 100, gradually lowering until too many wrong suggestions start to appear; after that, repeating this for algorithms 2, 3, and 4.
   - [1] `fuzz.ratio`
   - [2] `fuzz.partial_ratio`
   - [3] `fuzz.token_sort_ratio`
   - [4] `fuzz.token_set_ratio`
   - [Detailed descriptions of these algorithms.](http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/)
 2. Using `sav=all` is likely to result in large files, but this will make it faster to restart if you need to; when you think that you are done, you can rerun the script with `sav=man`, which will remove all irrelevant results, saving only `man`ual decisions
 3. The `len=XX` parameter (number of words): the comparison of longer strings with shorter ones gives better results in the workflow, so you may want to up this parameter if the script gets stuck on an inconclusive string.

