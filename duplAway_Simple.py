# general libraries
import sys, re, os, itertools, random

# comparison libraries
import difflib, fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#================================================================================
# CONFIGURATION =================================================================
#================================================================================
filename = "AraCorpus_NewBiblio_TriCollection.csv" # this is the file you will analyze
saveMode = "all"         # variants: all, man[ually tagged]
alg   = "[50,0,0,50]"    # algorithm threshold above which results are shown
ID    = "[1]"            # the number of the column whenre the IDs are
comp  = "[4,8]"          # columns for comparison (divided by commas)
disp  = "[1,3,4,6,8,13]" # columns for display (divided by commas)
verb  = "Books"          # this is the infix that will be added to the name of the file with results
interSave = 1000         # saving .tmp results every X iterations
saveCounter = 25         # saving .results every X manually added results
#================================================================================

# results are to be saved into
# fName_ID_Comp_Verb_TimeStamp.results
# format: ID > ID > Key (y, n, m)
# fName_ID_Comp_Verb.clusters
# format: ID ID ID ID ID

import time
def timeStamp():
    timestr = time.strftime("%Y%m%d%H%M%S")
    return(timestr)

timeStampVal = timeStamp()

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
    print("Comparing: %s" % var1.strip())
    print("     with: %s" % var2.strip())
    print("=====================")
    print("[1] fuzz.ratio: %d" % ratio)
    print("[2] fuzz.partial_ratio: %d" % partial_ratio)
    print("[3] fuzz.token_sort_ratio: %d" % token_sort_ratio)
    print("[4] fuzz.token_set_ratio: %d" % token_set_ratio)
    print("=====================")
    #print("mean: %d" % mean)

def allRatioResults(var1, var2):
    alg1 = fuzz.ratio(var1,var2)
    alg2 = fuzz.partial_ratio(var1,var2)
    alg3 = fuzz.token_sort_ratio(var1,var2)
    alg4 = fuzz.token_set_ratio(var1,var2)
    return([alg1, alg2, alg3, alg4])

#=R1 and R2======================================================
# check if duplicatedata file exists; if does > loads it;
# if doesn't > creates empty dictionaries
def duplicateDataLoader(resultsFile):
    lof = os.listdir()
    count = 0
    results = []
    for f in lof:
        if f.startswith(resultsFile) and f.endswith(".results"):
            with open(f, "r", encoding="utf8") as f1:
                f1 = f1.read().split("\n")
                results += f1
                print(f)
                print("\t%d" % len(results))
                
    if len(results) > 0:
        print("\t\tSome results already exist; incrementing...")
        pairDic = {}
        clusDic = {}

        try:
            with open(resultsFile+".tmp", "r", encoding="utf8") as f2:
                f2 = f2.read().split("\n")
                results += f2
            print("\tadding to %s processed items" % "{:,}".format(len(f1)))
        except:
            print("No temporary results to load...")

        results = list(set(results))
                
        for line in results:
            line = line.split("\t")

            key = "\t".join(sorted([line[0],line[1]]))

            # generating value
            if line[2] in choiceList:
                val = line[2]
            elif "," in line[2]:
                val = line[2].split(",")
                val = list(map(int, val))
            else:
                # other results are to be ignored
                input(line)

            # updating pairDic
            if key in pairDic:
                if type(pairDic[key]) is list:
                    if val in choiceList:
                        pairDic[key] = val
                else:
                    if pairDic[key] != val:
                        del pairDic[key]
                        # y will override m, n
                        # m and n will be equally removed
            else:
                pairDic[key] = val

            if line[2] == "y":
                clusDicUpdate(clusDic, [line[0], line[1]])
        
        clusDicSelfUpdate(clusDic)
        updatePairDic(pairDic, clusDic, "y")

        # save a new timestamped file with updated results
        saveCollectedPairs(pairDic, resultsFile, saveMode)

        
        # delete old timestamp files
        for f in lof:
            if f.startswith(resultsFile) and f.endswith(".results"):
                os.remove(f)

    else:
        print("No results yet; creating new results variable...")
        pairDic = {}
        clusDic = {}
        
    return(pairDic, clusDic)


#=R2======================================================
# list: remove duplicates and sort (for comparison)
def fixList(l):
    return(sorted(list(set(l))))

#=R2: clustedDic updating=================================
def clusDicUpdate(setDic, listVal):
    for v in listVal:
        if v in setDic:
            setDic[v].extend(listVal)
            setDic[v] = fixList(setDic[v])

            for d in setDic[v]:
                if d in setDic:
                    setDic[d].extend(setDic[v])
                    setDic[d] = fixList(setDic[d])
                else:
                    setDic[d] = setDic[v]
        else:
            setDic[v] = listVal

def clusDicSelfUpdate(setDic):
    for k,v in setDic.items():
        for d in v:
            setDic[d].extend(v)
            setDic[d] = fixList(setDic[d])

#=R2======================================================
# if A=B and B=C, then A=C; the function does A=C
def updatePairDic(pairDic, setDic, tag):
    print()
    print("==============================")
    print("PairDic Length: %s" % "{:,}".format(len(pairDic)))
    for k,v in setDic.items():
        pairs = list(itertools.combinations(v, 2))
        for p in pairs:
            key = "\t".join(sorted(list(p)))
            if key in pairDic:
                pass
            else:
                pairDic[key] = tag
    print("Updated PairDic Length: %s" % "{:,}".format(len(pairDic)))
    print("==============================")

#=R2 - saving collected pairs============================
def saveCollectedPairs(pairDic, resultsFile, saveMode):
    print("Saving updated results into a file...")
    lResults = []
    if saveMode == "all":
        # Temp / all results
        lResults = []
        for k,v in pairDic.items():
            if type(v) is list:
                v1 = ",".join(map(str, v))
                lResults.append(k+"\t"+v1)
                print(v)
                input(v1)
            else:
                lResults.append(k+"\t"+v)
        saveListResultsIntoFile(lResults, resultsFile+".tmp")

        # Manual / only manually tagged
        lResults = []
        for k,v in pairDic.items():
            if pairDic[k] in choiceList:
                lResults.append(k+"\t"+v)
        saveListResultsIntoFile(lResults, resultsFile+"_"+timeStampVal+".results")

    elif saveMode == "man":
        for k,v in pairDic.items():
            if pairDic[k] in choiceList:
                lResults.append(k+"\t"+str(v))
        saveListResultsIntoFile(lResults, resultsFile+"_"+timeStampVal+".results")

    else:
        sys.exit("Wrong key for saving results (must be 'all' or 'man')")


def saveListResultsIntoFile(lResults, resultsFile):
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

#=R2 - saving clusters==================================
def saveClusteredResults(clusDic, clusterFile):
    clusters = []
    for k,v in clusDic.items():
        val = v
        val = fixList(val)
        val = "\t".join(val)
        clusters.append(val)

    clusters = fixList(clusters)
    clusterFile = clusterFile+".clusters"
    with open(clusterFile, "w", encoding="utf8") as f9:
        f9.write("\n".join(clusters))
    print("================")
    print("%s clusters saved into %s" % ("{:,}".format(len(clusters)), clusterFile))
    print("================")

choiceList = ["y", "n", "m"]

def choiceCollector():
    print("=====================")
    print("   y --- for `yes`, a true match, the same item (or parts that make the same item)")
    print("   n --- for `no`, not a match, different items")
    print("   m --- for `maybe` a match, requires manual checking")
    print("=====================")    
    print("   stop --- to save the results and exit")
    print("=====================")
    choice = input("Type one of the choices: ")
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

def listToList(varList, testList):
    test = 0
    testResult = 'n'
    for i in range(0,4,1):
        if varList[i] >= testList[i]:
            test += 1
    if test == 4:
        testResult = 'y'
    return(testResult)

# REQUIRES: ID column, COMPARE columns, DISPLAY columns
#def routine2(filename, ID, comp, disp, verb, saveMode):
def routine2():
    length = 2
    
    # generating info on columns and the suffix
    id1   = int(ID[1:-1])
    comp1 = sorted(list(map(int, comp[1:-1].split(","))))
    disp1 = sorted(list(map(int, disp[1:-1].split(","))))

    algTest = list(map(int, alg[1:-1].split(",")))

    compS = "".join(list(map(str, comp1)))
    dispS = "".join(list(map(str, disp1)))
    suf   = "_%s_ID%s_Comp%s" % (verb, ID[1:-1], compS)

    resultsFile = filename.split(".")[0]+suf
    clusterFile = filename.split(".")[0]+suf

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
        random.shuffle(testList)
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
            if loop1 % 200 == 0:
                print("% 9s %s processed..." % ("{:,}".format(loop1), verb))
            if loop1 % interSave == 0:
                if len(pairDic) < loop2 and saveMode == "all":
                    print("\nSAVING RESULTS...")
                    print("\t%s results processed...\n" % "{:,}".format(len(pairDic)))
                    saveCollectedPairs(pairDic, resultsFile, saveMode)
                
            if len(i[0].split()) >= int(length): # to avoid comparing a shorter line against a longer one
                for ii in testList:
                    ii = ii.split("\t")

                    loop2 += 1
                    if loop2 % 100000 == 0:
                        print("\t% 9s" % "{:,}".format(loop2))
                        
                    if i[0] != ii[0]:
                        testKey = "\t".join(sorted([i[2], ii[2]])) # testKey = sorted([id1,id2])
                        if testKey in pairDic:
                            if pairDic[testKey] in choiceList:
                                pass

                            elif type(pairDic[testKey]) is list:
                                if listToList(val, algTest) == "y":
                                    os.system('clear') # commands clears the screen
                                    routine2Report(loop1, loop2, testListLen, nump, i, ii)
                                    choice = choiceCollector()
                                    #choice = input("Type 'y', 'n', 'm', or 'stop': ")
                                    if choice in choiceList:
                                        pairDic[testKey] = choice
                                        if choice == 'y':
                                            clusDicUpdate(clusDic, [i[2], ii[2]])
                                            clusDicSelfUpdate(clusDic)
                                            updatePairDic(pairDic, clusDic, 'y')

                                        # save results every saveCounter records
                                        counter += 1
                                        if counter % saveCounter == 0:
                                            print("\nSAVING RESULTS...")
                                            print("\t%d results processed...\n" % counter)
                                            saveCollectedPairs(pairDic, resultsFile, saveMode)
                                            saveClusteredResults(clusDic, clusterFile, 'y')
                                    elif choice == "stop":
                                        break
                                    else:
                                        input("Wrong choice...")
                                        continue
                                    print("\nMoving on...")
                                else:
                                    pass
                            else:
                                pass
                        else:
                            val = allRatioResults(i[2], ii[2])                            
                            if listToList(val, algTest) == "y":
                                os.system('clear') # commands clears the screen
                                routine2Report(loop1, loop2, testListLen, nump, i, ii)
                                choice = choiceCollector()
                                #choice = input("Type 'y', 'n', 'm', or 'stop': ")
                                if choice in choiceList:
                                    pairDic[testKey] = choice
                                    if choice == 'y':
                                        clusDicUpdate(clusDic, [i[2], ii[2]])
                                        clusDicSelfUpdate(clusDic)
                                        updatePairDic(pairDic, clusDic, 'y')

                                    # save results every saveCounter records
                                    counter += 1
                                    if counter % saveCounter == 0:
                                        print("\nSAVING RESULTS...")
                                        print("\t%d results processed...\n" % counter)
                                        saveCollectedPairs(pairDic, resultsFile, saveMode)
                                        saveClusteredResults(clusDic, clusterFile, 'y')
                                elif choice == "stop":
                                    break
                                else:
                                    input("Wrong choice...")
                                    continue
                                print("\nMoving on...")
                            else:
                                pairDic[testKey] = val

                else:
                    continue
                break

        # Saving results
        saveCollectedPairs(pairDic, resultsFile, saveMode)
        saveClusteredResults(clusDic, clusterFile)

routine2()
