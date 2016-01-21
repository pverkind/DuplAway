# general libraries
import sys, re, os, itertools

# comparison libraries
import difflib, fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


#==============================================================
# http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/
def reportRatio(var1, var2):
    ratio = fuzz.ratio(var1,var2)
    partial_ratio = fuzz.partial_ratio(var1,var2)
    token_sort_ratio = fuzz.token_sort_ratio(var1,var2)
    token_set_ratio = fuzz.token_set_ratio(var1,var2)

    mean = (ratio+partial_ratio+token_sort_ratio+token_set_ratio)/4

    print("=====================")
    print("fuzz.ratio: %d" % ratio)
    print("fuzz.partial_ratio: %d" % partial_ratio)
    print("fuzz.token_sort_ratio: %d" % token_sort_ratio)
    print("fuzz.token_set_ratio: %d" % token_set_ratio)
    print("=====================")
    print("mean: %d" % mean)

#==============================================================
# check if duplicatedata file exists; if yes - loads it; if no - creates an empty dic
def duplicateDataLoader(filename):
    resultsFile = filename.split(".")[0]+"_duplData.csv"
    if os.path.isfile(resultsFile):
        print("Some results already exits; incrementing...")
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
            
  

#==============================================================
# 1. saves duplicate data on exit;
# 2. should generate the file with approves duplicates on
# the same line, divided with \t
def duplicateDataSaver(filename, pairDic, clusDic):
    resultsFile = filename.split(".")[0]+"_duplData.csv"
    clusterFile = filename.split(".")[0]+"_clusData.csv"
    
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
def processing(filename, threshold):
    os.system('clear')
    pairDic, clusDic = duplicateDataLoader(filename)

    with open(filename, "r", encoding="utf8") as f1:
        testList = f1.read().split("\n")

        for i in testList:
            i1 = i.split("\t")[0]
            #print(i1)
            if len(i1.split()) >= 2: # to avoid comparing a shorter line against a longer one
                for ii in testList:
                    ii1 = ii.split("\t")[0]
                    if i1 != ii1:
                        testKey = "\t".join(sorted([i1, ii1]))
                        if testKey in pairDic:
                            if pairDic[testKey] == "y":
                                pass
                        else:
                            # other fuzz strategies can be used
                            if fuzz.token_set_ratio(i1, ii1) > threshold:
                                #os.system('clear') # commands clears the screen
                                print("=====================")
                                print(i)
                                print("=====================")
                                print(ii)
                                reportRatio(i1, ii1)
                                choice = input("Type 'y', 'n', 'm', or 'stop': ")
                                if choice in ['y','n','m']:
                                    pairDic[testKey] = choice
                                    if choice == 'y':
                                        clusDicUpdate(clusDic, [i1, ii1])
                                        clusDicSelfUpdate(clusDic)
                                        updatePairDic(pairDic, clusDic)
                                elif choice == "stop":
                                    break
                                else:
                                    input("Wrong choice: %s" % choice)
                                    break
                                os.system('clear') # commands clears the screen

                else:
                    continue
                break
                    
        duplicateDataSaver(filename, pairDic, clusDic)

#==============================================================
def main():
    if len(sys.argv) != 3:
        #print(len(sys.argv))
        print("Usage: python3 duplAway.py threshold file.csv")
        print("NB: fuzzywuzzy must be installed")
    else:
        #print(len(sys.argv))
        processing(sys.argv[2], int(sys.argv[1]))

main()
        

