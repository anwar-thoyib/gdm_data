#!/usr/bin/python
#v1a2
import sys
import time
import datetime
import re
import os

##############################################################################
class License:
    Contact = "ricky.yusrihadi@optiva.com"

    def __init__(self, mystr):
        self.SW_Ver     = mystr
        self.Warning    = "20/10/2020"
        self.Expired    = "30/10/2020"
        self.TS_Now     = time.time()
        self.TS_Warning = self.date2timestamp(self.Warning)
        self.TS_Expired = self.date2timestamp(self.Expired)
        self.Help       = []

    def date2timestamp(self, mydate):
        return(time.mktime(datetime.datetime.strptime(mydate, "%d/%m/%Y").timetuple()))

    def setSWVer(self, mystr):
        self.SW_Ver = mystr

    def addHelp(self, mystr):
        self.Help.append(mystr);

    def addLibrary(self, mystr):
        self.Library.append(mystr);

    def setWarning(self, mystr):
        self.Warning = mystr
        self.TS_Warning = self.date2timestamp(self.Warning)

    def setExpired(self, mystr):
        self.Expired = mystr
        self.TS_Expired = self.date2timestamp(self.Expired)

    def checkExpired(self):
        if len(sys.argv) > 1:
            if sys.argv[1] == "--version":
                self.showVersion()
                return True

            if sys.argv[1] == "--help":
                self.showHelp()
                return True

        if self.TS_Expired <= self.TS_Now:
            print("!!!ERROR: The license already expired!")
            exit(0)

    def showVersion(self):
        print(self.SW_Ver)
#        if self.Library:
#            tmp = "Using Library:"
#            for mylib in self.Library:
#                tmp += "\n  " + mylib
#                print(tmp)

        exit(0)

    def showHelp(self):
        print(self.SW_Ver)
        for myline in self.Help: print(myline)
        exit(0)

    def getNumericList(self, mystr):
        tmp   = []
        aline = re.search("^(\d+)$", mystr)
        if aline:
            tmp.append(mystr)
        else:
            fp = open(mystr)
            for line in fp:
                cust = str(line.splitlines()).strip('[]').strip('\'')
                tmp.append(cust)

        return tmp

    def getFileList(self, mystr):
        tmp = []
        if os.path.exists(mystr):
            fp = open(mystr)
            for line in fp:
                rline = re.search('^(\w+)$', line)
                if rline:
                    tmp.append(rline.group(1))
            fp.close()
        else:
            tmp.append(mystr)
            
        return tmp
        
    def __del__(self):
        if self.TS_Warning <= self.TS_Now:
            if self.TS_Expired > self.TS_Now: print("Warning!: The license will be expired at " + self.Expired)

            print("please contact: " + self.Contact)

