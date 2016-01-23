# general libraries
import sys, re, os, itertools, random

# comparison libraries
import difflib, fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#==============================================================
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

#==============================================================
# check if duplicatedata file exists; if does > loads it;
# if doesn't > creates two empty dictionaries
def duplicateDataLoader(filename):
    resultsFile = filename.split(".")[0]+"_duplData.tsv"
    if os.path.isfile(resultsFile):
        print("Some results already exist; incrementing...")
        pairDic = {}
        clusDic = {}
        with open(resultsFile, "r", encoding="utf8") as f1:
            f1 = f1.read().split("\n")
            print("\tadding to %d processed items" % len(f1))
            for line in f1:
                line = line.split("\t")
                pairDic[line[0]+"\t"+line[1]] = line[2]
                
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


#==============================================================
# list: remove duplicates and sort (for comparison)
def fixList(l):
    return(sorted(list(set(l))))

#==============================================================
# clustedDic updating
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

#==============================================================
# if A=B and B=C, then A=C; the function does A=C
def updatePairDic(pairDic, clusDic):
    print()
    print("==============================")
    print("PairDic Length: %d" % len(pairDic))
    for k,v in clusDic.items():
        pairs = list(itertools.combinations(v, 2))
        for p in pairs:
            key = "\t".join(sorted(list(p)))
            if key in pairDic:
                pass
            else:
                pairDic[key] = "y"
    print("Updated PairDic Length: %d" % len(pairDic))
    print("==============================")

#==============================================================
# 1. saves duplicate data on exit;
# 2. should generate the file with approves duplicates on
# the same line, divided with \t
def duplicateDataSaver(filename, pairDic, clusDic):
    resultsFile = filename.split(".")[0]+"_duplData.tsv"
    clusterFile = filename.split(".")[0]+"_clusData.txt"
    
    print("Saving updated results into a file...")
    lResults = []
    for k,v in pairDic.items():
        # for saving in file (loadable with duplicateDataLoader())
        lResults.append(k+"\t"+v)
            
    with open(resultsFile, "w", encoding="utf8") as f9:
        f9.write("\n".join(lResults))
    print("================")
    print("%d duplicate pairs saved" % len(lResults))
    print("================")

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
    print("%d clusters saved" % len(clusters))
    print("================")

#==============================================================
# main processing function
def routine1(filename, threshold, length, alg):
    os.system('clear')    
    pairDic, clusDic = duplicateDataLoader(filename)
    print("\tStarting processing...")   
    #os.system('clear')

    with open(filename, "r", encoding="utf8") as f1:
        testList = f1.read().split("\n")
        random.shuffle(testList)

        loop1 = 0
        loop2 = 0
        counter = 0

        for i in testList:
            loop1 += 1
            if loop1 % 50 == 0:
                print("% 9d" % loop1)
                
            i1 = i.split("\t")[0]

            if len(i1.split()) >= int(length): # to avoid comparing a shorter line against a longer one
                for ii in testList:
                    loop2 += 1
                    if loop2 % 10000 == 0:
                        print("\t% 9d" % loop2)
                        
                    ii1 = ii.split("\t")[0]
                    if i1 != ii1:
                        testKey = "\t".join(sorted([i1, ii1]))
                        if testKey in pairDic:
                            if pairDic[testKey] == "y":
                                pass
                        else:
                            # other fuzz strategies can be used
                            if getRatio(i1, ii1, int(alg)) > int(threshold):
                                os.system('clear') # commands clears the screen
                                reportRatio(i1, ii1)
                                print("=====================")
                                print(i)
                                print("=====================")
                                print(ii)
                                print("=====================")
                                choice = input("Type 'y', 'n', 'm', or 'stop': ")
                                if choice in ['y','n','m']:
                                    pairDic[testKey] = choice
                                    if choice == 'y':
                                        clusDicUpdate(clusDic, [i1, ii1])
                                        clusDicSelfUpdate(clusDic)
                                        updatePairDic(pairDic, clusDic)
                                    # save results every 10 records
                                    counter += 1
                                    if counter % 10 == 0:
                                        print("\nSAVING RESULTS...")
                                        print("\t%d results processed...\n" % counter)
                                        duplicateDataSaver(filename, pairDic, clusDic)
                                elif choice == "stop":
                                    break
                                else:
                                    input("Wrong choice: %s" % choice)
                                    break
                                print("\nMoving on...")
                                #os.system('clear') # commands clears the screen

                else:
                    continue
                break
                    
        duplicateDataSaver(filename, pairDic, clusDic)

#==============================================================
annotation = """
# Running the script:
#   - works of Python 3
#   - fuzzywuzzy library must be installed
#     (see: http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/)
# Routine 1:
# - uses 2 columns TSV; best for grouping one-line descriptions of the same entities (names or book titles)
#   Col1 - values for comparison
#   Col2 - values for display
# Running: python3 duplAway.py file=filename thr=90 alg=4 len=4
#   where:
#       file        : the name of a data file for processing (must be in the same folder as the script)
#       thr[eshold] : the lowest comparioson ratio to consider
#       alg[orithm] : chooses one of the 4 fuzzywuzzy routines
#       len[gth]    : the length (in words) of the first comparison string;
#                     works better when comparing longer strings with shorter ones
# Routine 2:
# - uses TSV with any number of columns; best for comparing complex items (bibliographical records)
# Running: python3 duplAway.py file=filename thr=90 alg=4 len=4 id=[1] comp=[1,2,3,4] disp=[1,2,3,4,5,6]
#   where:
#       file        : the name of a data file for processing (must be in the same folder as the script)
#       thr[eshold] : the lowest comparioson ratio to consider
#       alg[orithm] : chooses one of the 4 fuzzywuzzy routines
#       len[gth]    : the length (in words) of the first comparison string;
#                     works better when comparing longer strings with shorter ones
#       id          : column with unique identifiers --- required column!
#       comp[are]   : columns to use for comparison (separated by commas);
#                     for example, [author] and [title] for bibliographical records
#       disp[lay]   : columns to use for showing during the decision stage (separated by commas);
#                     for example, [author], [title], [editor], etc. for bibliographical records
# NB: arguments (i.e., everything after 'python3 duplAway.py') can be given in any order;
#     do not change the name of the script, since it will break the argument analysis logic
"""

def arg(var):
    return(var.split("=")[1])

def main():
    # run Routine 1
    if len(sys.argv) == 5:
        os.system('clear')
        # analyze arguments
        a = sorted(sys.argv)
        #python3 duplAway.py file=authorsNames_3Collections.txt thr=90 alg=4 len=4
        #['alg=4', 'duplAway.py', 'file=filename', 'len=4', 'thr=90']
        #routine1(filename, threshold, length, alg)
        routine1(arg(a[2]), arg(a[4]), arg(a[3]), arg(a[0]))
        #print(args)
        
    # run Routine 2
    elif len(sys.argv) == 8:
        os.system('clear')
        # analyze arguments
        # ['alg=4', 'comp=[1,2,3,4]', 'disp=[1,2,3,4,5,6]', 'duplAway.py', 'file=filename', 'id=[1]', 'len=4', 'thr=90']
        args = sorted(sys.argv)
        print(args)

    # exit
    else:
        os.system('clear')
        print(sorted(sys.argv))
        print(annotation)

main()
        

