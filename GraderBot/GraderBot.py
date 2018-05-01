import re
import sys

def checkpage(pagetext, report):
    tokens = []
    tk = pagetext.split('\n')
    for t in tk:
        if t:
            if t[0] == '*':
                tokens.append(t)

    grade = 6.0

    grade -= checkentries(tokens, report)

    if len(tokens) <= 10:
        return 0.0

    if checksource(tokens, report) > 0:
        grade -= 0.5



    return max(grade, 0)


def checksource(tokens, report):
    r = '\*.*\[https?:\/\/w?w?w?\.?letemps[^\]]*\].*'
    p = re.compile(r)
    badsourced = 0
    index = 0

    for t in tokens:
        match = p.match(t)
        if not match:
            badsourced += 1
            report.write("Bad source at entry #" + str(index) + " : " + t + "\n")
        index +=1


    return badsourced


def checkentries(tokens, report):
    malus = 0
    malus += max(15 - len(tokens), 0)

    if (len(tokens) < 15):
        report.write("Only " + str(len(tokens)) + " entries when at least 15 are expected\n")

    dates_isolator_expr = ['\* \[\[(.*)\]\] \/', '\*\[\[(.*)\]\]\:', '\*\[\[(.*)\]\]\/', '\*\[\[(.*)\]\] \/']

    hyperword_count = 0
    chrono_count    = 0
    for t in tokens:
        didmatch = False

        hyperword_count += t.count("[[")

        for i in dates_isolator_expr:
            d = re.compile(i)
            match = d.match(t)
            if match:
                didmatch = True
        if not didmatch:
            chrono_count += 1

    malus += max(4 - hyperword_count, 0) * 0.5
    malus += round(chrono_count/2)/4.0

    if hyperword_count <= 4:
        report.write("Insufficient use of hyperwords\n")

    if chrono_count > 0:
        report.write(str(chrono_count) + " entries did not have a chronology\n")

    return min(malus, 4)


argc = len(sys.argv)

if argc < 3:
    read_file  = open("LouiseMichel.txt", "r")
    write_file = open("report.txt", "w")
else:
    read_file  = open(sys.argv[1], "r")
    write_file = open(sys.argv[2], "w")

grade = checkpage(read_file.read(), write_file)
if grade > 5.95:
    write_file.write("No relevant error found.\n")
write_file.write("\n\nFINAL GRADE : " + str(grade) + " / 6.0\n")
