import sys, re, os, difflib, fuzzywuzzy, tabulate
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


# check if duplicatedata file exists; if yes - loads it; if no - creates empty dic
def duplicateDataLoader(filename):
    resultsFile = filename.split(".")[0]+"_duplData.csv"
    if os.path.isfile(resultsFile):
        print("Some results already exits; incrementing...")
        dic = {}
        with open(resultsFile, "r", encoding="utf8") as f1:
            f1 = f1.read().split("\n")
            print("\tadding to %d processed items" % len(f1))
            for line in f1:
                line = line.split("\t")
                dic[line[0]+"\t"+line[1]] = line[2]
    else:
        print("No results yet; creating new results variable...")
        dic = {}
    return(dic)

# saves duplicate data on exit; generates the file with approves duplicates on
# the same line, divided with \t
def duplicateDataSaver(filename, dic):
    resultsFile = filename.split(".")[0]+"_duplData.csv"
    print("Saving updated results into a file...")
    lResults = []
    conflated = {}
    for k,v in dic.items():
        # for saving in file (loadable with duplicateDataLoader())
        lResults.append(k+"\t"+v)
            
    with open(resultsFile, "w", encoding="utf8") as f9:
        f9.write("\n".join(lResults))
    print("================")
    print("%d duplicate pairs saved" % len(lResults))
    print("================")


# main processing function
def processing(filename, threshold):
    results = duplicateDataLoader(filename)

    with open(filename, "r", encoding="utf8") as f1:
        testList = f1.read().split("\n")

        for i in testList:
            i1 = i.split("\t")[0]
            for ii in testList:
                ii1 = ii.split("\t")[0]
                if i1 != ii1:
                    testKey = "\t".join(sorted([i1, ii1]))
                    if testKey in results:
                        if results[testKey] == "y":
                            pass
                    else:
                        # other fuzz strategies can be used
                        if fuzz.token_set_ratio(i1, ii1) > threshold:
                            os.system('clear') # commands clears the screen
                            print("=====================")
                            print(i)
                            print("=====================")
                            print(ii)
                            reportRatio(i1, ii1)
                            choice = input("Type 'y', 'n', 'm', or 'stop': ")
                            if choice in ['y','n','m']:
                                results[testKey] = choice
                                pass
                            elif choice == "stop":
                                break
                            else:
                                input("Wrong choice: %s" % choice)
                                break
            else:
                continue
            break
                    
        duplicateDataSaver(filename, results)


def main():
    if len(sys.argv) != 3:
        #print(len(sys.argv))
        print("Usage: python3 duplAway.py threshold file.csv")
        print("NB: fuzzywuzzy must be installed")
    else:
        #print(len(sys.argv))
        processing(sys.argv[2], int(sys.argv[1]))

main()
        

