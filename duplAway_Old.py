# general libraries
import sys, re, os, itertools, random

# comparison libraries
import difflib, fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#=R1 and R2===================================================
# string comparison routines using fuzzywuzzy
# http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/
def reportRatio(var1, var2):
    ratio = fuzz.ratio(var1,var2)
    partial_ratio = fuzz.partial_ratio(var1,var2)
    token_sort_ratio = fuzz.token_sort_ratio(var1,var2)
    token_set_ratio = fuzz.token_set_ratio(var1,var2)

    mean = (ratio+partial_ratio+token_sort_ratio+token_set_ratio)/4

    print("=====================")
    print("Comparing: %s" % var1)
    print("     with: %s" % var2)
    print("=====================")
    print("[1] fuzz.ratio: %d" % ratio)
    print("[2] fuzz.partial_ratio: %d" % partial_ratio)
    print("[3] fuzz.token_sort_ratio: %d" % token_sort_ratio)
    print("[4] fuzz.token_set_ratio: %d" % token_set_ratio)
    print("=====================")
    #print("mean: %d" % mean)

def getRatio(var1, var2, alg):
    if int(alg) in [1,2,3,4]:
        if int(alg) == 1:
            ratio = fuzz.ratio(var1,var2)
        if int(alg) == 2:
            ratio = fuzz.partial_ratio(var1,var2)
        if int(alg) == 3:
            ratio = fuzz.token_sort_ratio(var1,var2)
        if int(alg) == 4:
            ratio = fuzz.token_set_ratio(var1,var2)
    else:
        reportRatio(var1,var2)
        print("=====================")
        print("Choose 1, 2, 3, or 4 to to use a specific comparison algorithm...")
        print("For more details on differences, check:\n\thttp://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/")
        sys.exit()
    return(ratio)

#=R1 and R2======================================================
# check if duplicatedata file exists; if does > loads it;
# if doesn't > creates two empty dictionaries
def duplicateDataLoader(resultsFile):
    if os.path.isfile(resultsFile):
        print("Some results already exist; incrementing...")
        pairDic = {}
        clusDic = {}
        with open(resultsFile, "r", encoding="utf8") as f1:
            f1 = f1.read().split("\n")
            print("\tadding to %s processed items" % "{:,}".format(len(f1)))
            for line in f1:
                line = line.split("\t")
                if line[2] in ["y", "n", "m"]:
                    val = line[2]
                else:
                    val = int(line[2])
                pairDic[line[0]+"\t"+line[1]] = val
                
                if line[2] == "y":
                    clusDicUpdate(clusDic, [line[0], line[1]])
        #input(clusDic)
        clusDicSelfUpdate(clusDic)
        updatePairDic(pairDic, clusDic)
        # update pairDic from clusDic
    else:
        print("No results yet; creating new results variable...")
        pairDic = {}
        clusDic = {}
    return(pairDic, clusDic)


#=R1 and R2======================================================
# list: remove duplicates and sort (for comparison)
def fixList(l):
    return(sorted(list(set(l))))

#=R1 and R2: clustedDic updating=================================
def clusDicUpdate(clusDic, listVal):
    for v in listVal:
        if v in clusDic:
            clusDic[v].extend(listVal)
            clusDic[v] = fixList(clusDic[v])

            for d in clusDic[v]:
                if d in clusDic:
                    clusDic[d].extend(clusDic[v])
                    clusDic[d] = fixList(clusDic[d])
                else:
                    clusDic[d] = clusDic[v]
        else:
            clusDic[v] = listVal

def clusDicSelfUpdate(clusDic):
    for k,v in clusDic.items():
        for d in v:
            clusDic[d].extend(v)
            clusDic[d] = fixList(clusDic[d])

#=R1 and R2======================================================
# if A=B and B=C, then A=C; the function does A=C
def updatePairDic(pairDic, clusDic):
    print()
    print("==============================")
    print("PairDic Length: %s" % "{:,}".format(len(pairDic)))
    for k,v in clusDic.items():
        pairs = list(itertools.combinations(v, 2))
        for p in pairs:
            key = "\t".join(sorted(list(p)))
            if key in pairDic:
                pass
            else:
                pairDic[key] = "y"
    print("Updated PairDic Length: %s" % "{:,}".format(len(pairDic)))
    print("==============================")

#=R1 and R2 - saving collected pairs============================
def saveCollectedPairs(pairDic, resultsFile, saveMode):
    print("Saving updated results into a file...")
    lResults = []
    if saveMode == "all":
        for k,v in pairDic.items():
            # for saving in file (loadable with duplicateDataLoader())
            lResults.append(k+"\t"+str(v))
    elif saveMode == "man":
        for k,v in pairDic.items():
            if pairDic[k] in ["y", "n", "m"]:
                lResults.append(k+"\t"+str(v))
    else:
        sys.exit("Wrong key for saving results (must be 'all' or 'man')")

    duplRes = "\n".join(lResults)
    if duplRes != "":    
        with open(resultsFile, "w", encoding="utf8") as f9:
            f9.write(duplRes)
        print("================")
        print("%s duplicate pairs saved into %s" % ("{:,}".format(len(lResults)), resultsFile))
        print("================")
    else:
        print("================")
        print("No duplicate pairs; nothing saved...")
        print("================")

#=R1 and R2 - saving clusters==================================
def saveClusteredResults(clusDic, clusterFile):
    clusters = []
    for k,v in clusDic.items():
        val = v
        val = fixList(val)
        val = "\t".join(val)
        clusters.append(val)

    clusters = fixList(clusters)
    with open(clusterFile, "w", encoding="utf8") as f9:
        f9.write("\n".join(clusters))
    print("================")
    print("%s clusters saved into %s" % ("{:,}".format(len(clusters)), clusterFile))
    print("================")

def choiceCollector():
    print("=====================")
    print("   y --- for 'yes'   (true match)")
    print("   n --- for 'no'    (no match)")
    print("   m --- for 'maybe' (maybe a match; requires manual checking)")
    print("=====================")    
    print("stop --- to save the results and exit")
    print("=====================")
    choice = input("Type 'y', 'n', 'm', or 'stop': ")
    return(choice)

#==============================================================
# Routine for TSV of anylength ================================
#==============================================================
def routine2Report(loop1, loop2, testListLen, nump, i, ii):
    print("=====================")
    print("ITEMS TO REVIEW:")
    print("Items reviewed with current settings:") #'{:20,.2f}'.format(f)
    rep1 = '{: 10,.2f}%'.format((loop1 / testListLen)*100)
    print("\t%s (%s out of %s items)" % (rep1, "{:,}".format(loop1), "{:,}".format(testListLen)))
    rep2 = '{: 10,.2f}%'.format((loop2 / nump)*100)
    print("\t%s (%s out of %s pairs have been compaired)" % (rep2, "{:,}".format(loop2), "{:,}".format(nump)))
    reportRatio(i[0], ii[0])
    print("=====================")
    print(i[1])
    print("=====================")
    print(ii[1])
    print("=====================")

# REQUIRES: ID column, COMPARE columns, DISPLAY columns
# file=filename thr=90 alg=4 len=4 id=[1] comp=[1,2,3,4] disp=[1,2,3,4,5,6] verb=CompCategory
def routine2(filename, threshold, length, alg, ID, comp, disp, verb, saveMode):        
    # generating info on columns and the suffix
    id1   = int(ID[1:-1])
    comp1 = sorted(list(map(int, comp[1:-1].split(","))))
    disp1 = sorted(list(map(int, disp[1:-1].split(","))))

    compS = "".join(list(map(str, comp1)))
    dispS = "".join(list(map(str, disp1)))
    suf   = "_%s_ID%s_Comp%s_Disp%s" % (verb, ID[1:-1], compS, dispS)

    resultsFile = filename.split(".")[0]+suf+"_duplicIDs.tsv"
    clusterFile = filename.split(".")[0]+suf+"_clusIDs.tsv"

    # start processing data                   
    os.system('clear')    
    pairDic, clusDic = duplicateDataLoader(resultsFile)
    print("\tStarting processing...")

    def valGen(row, index, conn):
        row = row.split("\t")
        valList = []
        for i in index:
            valList.append(row[i-1])
        return(conn.join(valList))

    with open(filename, "r", encoding="utf8") as f1:
        f1 = f1.read()
        # FOR ARABIC COLLECTIONS METADATA #
        f1 = f1.replace("NOTGIVEN", "")
                
        initList = f1.split("\n")
        # generate testList from the original one, simplifying it to 3 basic columns: COMPARE, DISPLAY, ID
        testList = []
        for r in initList:
            compVal = valGen(r, comp1, " :: ")
            dispVal = valGen(r, disp1, "\n")
            idVal   = r.split("\t")[id1-1]
            testList.append("\t".join([compVal, dispVal, idVal]))

        testList = fixList(testList)                 
        #random.shuffle(testList)
        testListLen = len(testList)
        nump = testListLen*testListLen
        numRec = len(initList)
        numRecNew = len(testList)

        loop1 = 0
        loop2 = 0
        counter = 0
        
        for i in testList:
            i = i.split("\t")
             
            loop1 += 1
            if loop1 % 100 == 0:
                print("% 9s" % "{:,}".format(loop1))
                if len(pairDic) < loop2 and saveMode == "all":
                    print("\nSAVING RESULTS...")
                    print("\t%s results processed...\n" % "{:,}".format(len(pairDic)))
                    saveCollectedPairs(pairDic, resultsFile, saveMode)
                    saveClusteredResults(clusDic, clusterFile)
                
            if len(i[0].split()) >= int(length): # to avoid comparing a shorter line against a longer one
                for ii in testList:
                    ii = ii.split("\t")

                    loop2 += 1
                    if loop2 % 100000 == 0:
                        print("\t% 9s" % "{:,}".format(loop2))
                        
                    if i[0] != ii[0]:
                        testKey = "\t".join(sorted([i[2], ii[2]])) # testKey = sorted([id1,id2])
                        if testKey in pairDic:
                            if pairDic[testKey] in ['y','n','m']:
                                pass
                            #elif pairDic[testKey] < int(threshold):
                            #    pass
                            elif pairDic[testKey] >= int(threshold):
                                os.system('clear') # commands clears the screen
                                routine2Report(loop1, loop2, testListLen, nump, i, ii)
                                choice = choiceCollector()
                                #choice = input("Type 'y', 'n', 'm', or 'stop': ")
                                if choice in ['y','n','m']:
                                    pairDic[testKey] = choice
                                    if choice == 'y':
                                        clusDicUpdate(clusDic, [i[2], ii[2]])
                                        clusDicSelfUpdate(clusDic)
                                        updatePairDic(pairDic, clusDic)
                                    # save results every 10 records
                                    counter += 1
                                    if counter % 10 == 0:
                                        print("\nSAVING RESULTS...")
                                        print("\t%d results processed...\n" % counter)
                                        saveCollectedPairs(pairDic, resultsFile, saveMode)
                                        saveClusteredResults(clusDic, clusterFile)
                                elif choice == "stop":
                                    break
                                else:
                                    input("Wrong choice...")
                                    continue
                                print("\nMoving on...")
                                #os.system('clear') # commands clears the screen
                            else:
                                pass
                                
                        else:
                            testThreshold = getRatio(i[0], ii[0], int(alg))
                            # other fuzz strategies can be used
                            if testThreshold >= int(threshold):
                                os.system('clear') # commands clears the screen
                                routine2Report(loop1, loop2, testListLen, nump, i, ii)
                                choice = choiceCollector()
                                #choice = input("Type 'y', 'n', 'm', or 'stop': ")
                                if choice in ['y','n','m']:
                                    pairDic[testKey] = choice
                                    if choice == 'y':
                                        clusDicUpdate(clusDic, [i[2], ii[2]])
                                        clusDicSelfUpdate(clusDic)
                                        updatePairDic(pairDic, clusDic)
                                    # save results every 10 records
                                    counter += 1
                                    if counter % 10 == 0:
                                        print("\nSAVING RESULTS...")
                                        print("\t%d results processed...\n" % counter)
                                        saveCollectedPairs(pairDic, resultsFile, saveMode)
                                        saveClusteredResults(clusDic, clusterFile)
                                elif choice == "stop":
                                    break
                                else:
                                    input("Wrong choice...")
                                    continue
                                print("\nMoving on...")
                                #os.system('clear') # commands clears the screen
                            elif testThreshold < int(threshold):
                                pairDic[testKey] = testThreshold
                            else:
                                pass
                else:
                    continue
                break

        # Saving results
        saveCollectedPairs(pairDic, resultsFile, saveMode)
        saveClusteredResults(clusDic, clusterFile)

#==============================================================
annotation = """
# Running the script:
#   - works of Python 3
#   - fuzzywuzzy library must be installed
#     (see: http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/)
# Routine 2:
# - uses TSV with any number of columns; best for comparing complex items (bibliographical records)
# Parameters are as follows:
#       file        : the name of a data file for processing (must be in the same folder as the script)
#       thr[eshold] : the lowest comparison ratio to consider
#       alg[orithm] : chooses one of the 4 fuzzywuzzy routines
#       len[gth]    : the length (in words) of the first comparison string;
#                     works better when comparing longer strings with shorter ones
#       sav[e Mode] : 'all', or 'man'
#                     all - saves all: + works faster on restart; - creates really large result files (dupl)
#                     a) if you don't mind extra space, restarting is much faster with 'all', since the script does have to calculate anew
#                     b) re-running with 'man' will remove all irrelevant results, keeping only manually tagged ones ('y', 'n', and 'm')
#       id          : column with unique identifiers --- required column!
#       comp[are]   : columns to use for comparison (separated by commas);
#                     for example, [author] and [title] for bibliographical records
#       disp[lay]   : columns to use for showing during the decision stage (separated by commas);
#                     for example, [author], [title], [editor], etc. for bibliographical records
#       verb[al]    : just a word for the category of things that are compared > makes it easier to interpret what is in the file
#                     for example, the same dataset can be used for different purposes, and while it will be reflected in the
#                     suffix, where the the colund numbers are given, this suffix is not very readable, so adding a simple verbal
#                     marker should be helpful (so, verb=Authors > analyzing Authors' names; verb=Book --- book titles, etc.
# NB: arguments (i.e., everything after 'python3 duplAway.py') can be given in any order;
#     do not change the name of the script, since it will break the argument analysis logic
#
#==========================================================
## example command for Routine 2
#==========================================================

$ python3 duplAway.py file=AraCorpus_NewBiblio_TriCollection.tsv thr=90 alg=4 len=5 id=[4] comp=[4] disp=[4,6] verb=Authors sav=all
    - the script will analyze file 'AraCorpus_NewBiblio_TriCollection.tsv',
    - using algorithm 4 and showing only results with 90% likelihood
    - comparing longer strings with shorter ones seems to work better,
      hence the lower limit is set to 5 [words]; you may want to
      experiment with this parameter (increase it, if you get stuck);
    - it will use column 4 for ids
    - it will also use values from col 4 for comparison;
    - it will show also data from cols 4 and 6, which should help to
      make the finals decision whether this is a true of false match
    - it will add 'Authors' to the name of the file (for readability)
      this essentially means that we are comparing names of authors
    - it will also save ALL results on exit
$ python3 duplAway.py file=AraCorpus_AuthorNames.tsv thr=90 alg=4 len=5 id=[1] comp=[2] disp=[2,3,4] verb=Authors sav=all
$ python3 duplAway.py file=AraCorpus_NewBiblio_TriCollection.tsv thr=90 alg=4 len=5 id=[1] comp=[4,8] disp=[1,3,4,6,8,13] verb=Books sav=all

# Config file is a more convenient option: keep all parameters in a file and load it with a script > shorter command
# Example for Routine 1 (include the following 11 lines into a file > configFile2.txt); everything after '#' is a comment
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
# The command to run the script then becomes:

$ python3 duplAway.py configFile2.txt

#==========================================================
# Some suggestions
#==========================================================
# 1. fuzzywuzzy Library has 4 algorithms that have different level of tolerance, so it make sense to start with
#    algorithm 1 and threshold 100, gradually lowering until too many wrong suggestions start to appear;
#    after that, repeating this for algorithms 2, 3, and 4.
    [1] fuzz.ratio
    [2] fuzz.partial_ratio
    [3] fuzz.token_sort_ratio
    [4] fuzz.token_set_ratio
#    Details on these algorithms: http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/
# 2. Using sav=all will save large files, but will make it faster to restart if you need to; when you think that
#    you are done, rerun the script with sav=man, which will remove all irrelevant results, saving only 'man'ual decisions
# 3. The len=XX parameter: the comparison of longer lines with shorter gives better results in the workflow, so you may want to up
#    this parameterif the script gets stuck on an inconclusive string.
"""

def arg(var):
    return(var.split("=")[1])

def main():
    # run Routine 2 with the config file (Routine 1 is deprecated...)
    if len(sys.argv) == 2:
        print("Starting Routine 2 with a config file...")
        # loading with config file
        with open(sys.argv[1], "r", encoding="utf8") as f1:
            a = []
            for i in f1:
                if i[0] == "~":
                    i = re.sub("#.*| +|\n", "", i)
                    a.append(i)
                
            a = sorted(a)
            print("=====================")
            for i in a:
                print("arg(a[%d])\t%s" % (a.index(i), i))
            print("=====================")
            
            routine2(arg(a[4]),\
                     # filename
                     arg(a[8]),\
                     # threshold
                     arg(a[6]),\
                     # length
                     arg(a[0]),\
                     # alg
                     arg(a[5]),\
                     # ID
                     arg(a[1]),\
                     # comp
                     arg(a[2]),\
                     # disp
                     arg(a[9]),\
                     # verb
                     arg(a[7])\
                     # saveMode
                     )
        
    # run Routine 2 with arguments (Routine 1 is deprecated...)
    elif len(sys.argv) == 10:
        os.system('clear')
        print("Starting Routine 2 with arguments...")
        # analyze arguments
        a = sorted(sys.argv)
        print("=====================")
        print(a)
        print("=====================")
        for i in a:
            print("arg(a[%d])\t%s" % (a.index(i), i))

        routine2(arg(a[4]),\
                 # filename
                 arg(a[8]),\
                 # threshold
                 arg(a[6]),\
                 # length
                 arg(a[0]),\
                 # alg
                 arg(a[5]),\
                 # ID
                 arg(a[1]),\
                 # comp
                 arg(a[2]),\
                 # disp
                 arg(a[9]),\
                 # verb
                 arg(a[7])\
                 # saveMode
                 )

    else:
        os.system('clear')
        print("Wrong number of arguments...")
        print(sorted(sys.argv))
        print(annotation)

main()
