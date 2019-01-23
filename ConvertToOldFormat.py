#################################################################################################
# @author Anthony Abouhassan
# @date 07-29-18
# @purpose
#   this script was created to fix the change obg did with tax rates
#   it will find the tax rate element and check to see if the value is greater than 1.
#   if it is, it will divide that value by 100 and continue creating a new 
#   MTM file. 
# @error code definitions
#   Use this section to determine where the program went wrong
#   exit code   description
#   0           Successful completion
#   1           File does not exist
#   2           Date doesn't match date format
#   3           Tax rate is below 1% for a city
#   4           No ORG file exists
#   5		Manually quit because .org file already exists
# @revision history
#  user     date        change
#  AAB      07-25-18    initial programming
#  AAB      07-27-18    move to production
#  AAB      08-06-18	made warning about previous file more clear
#
#################################################################################################
from __future__ import division
import glob
import argparse
import sys
import os
import datetime
from shutil import copyfile
from decimal import Decimal

#update this if we get a city below .75% tax rate
MIN_TAX_RATE = .74
OBG_FILE_LOCATION = "/sybdisk10/production/sybbatch_pgms/nacha_obg/"

#custom exit 
def quitout(_code):
    print('error code: ' + str(_code))
    print('')
    print('')
    print('####################################')
    print('Failing out of ConvertToOldFormat.py ')
    print('####################################')
    print('')
    print('')
    exit(_code)


#go through the line
def ConvertTaxRates(_splitstring, maxValue):
    #loop through to get every tax rate
    while maxValue < len(_splitstring):
        #divide rate by 100
        if Decimal(_splitstring[maxValue]) > MIN_TAX_RATE:
            correctedRate = Decimal(_splitstring[maxValue]) / 100
            _splitstring[maxValue] = str(correctedRate)
            #move to the next rate position
            maxValue+=21
        else:
            print("tax rate too low on this line")
            print(str('|').join(_splitstring))
            print("at this position:")
            print(maxValue)
            print("quitting")
            quitout(3)
    #join the string back together with the correct deliminator 
    return str('|').join(_splitstring)

#create backup files
def CreateBackups(_filename):
    if os.path.exists(_filename.replace('.txt', '.org')):
        print("******************** WARNING ************************")
        print("backup already exists for this date - if this date was inaccurate at the initial run then you'll need to delete the .org file for this date when the corrected files are uploaded.")
    else:
        print("backing up file")
        copyfile(_filename, _filename.replace('.txt', '.org'))
    
#read the file passed and out a new file
def ConvertOldFile(_filename):
    print("I've entered the ConvertOldFile method")
    newfile = ""
    MWMFile = open(_filename, "r")
    if MWMFile.mode == "r":
        print("reading contents")
        contents = MWMFile.readlines()  
    for line in contents:
        #go line by line to replace the taxrate with the corrected tax rate
        _splitLine = line.split("|")

        #make sure there's atleast one tax rate
        if len(_splitLine) > 22:
            newfile += ConvertTaxRates(_splitLine, 22)
        else:
            newfile += line
    MWMFile.close()
    print("i'm returning the newfile")
    return newfile

def main():
    print('')
    print('')
    print('##############################')
    print('Entering ConvertToOldFormat.py')
    print('##############################')
    print('')
    print('')
    #get date from script
    parser=argparse.ArgumentParser()
    parser.add_argument('date_1')
    parser.add_argument('date_2')
    args=parser.parse_args()
    #convert date to the correct format
    try:
        _oldDateFormat = '%m%d%y'
        _correctDateFormat = datetime.datetime.strptime(args.date_1, _oldDateFormat).strftime('%Y%m%d')
    except:
        print("incorrect date format - quitting")
        quitout(2)
    
    filName = "12001.MWM" + _correctDateFormat  + '*.txt'
    #search for files matching
    fileResult = glob.glob(OBG_FILE_LOCATION + filName)
    
    #take the newest result
    if fileResult:
        filName=fileResult[0]
    else:
        print("No File exists")
        quitout(1)
    
    print("I'm converting: " + filName)
    
    #create backups
    CreateBackups(filName)
    orgFilName = "12001.MWM" + _correctDateFormat  + '*.org'
    #search for files matching
    orgFileResult = glob.glob(OBG_FILE_LOCATION + orgFilName)
    #take the newest result
    if orgFileResult:
        orgFilName=orgFileResult[0]
    else:
        print("No ORG File exists")
        quitout(4)   
    #generate a string with the new file data
    newFileData = ConvertOldFile(orgFilName)
    print("completed creating new data")

    #write the new file
    newFile = open(filName, 'w')
    newFile.write(newFileData)
    newFile.close()
    print('')
    print('')
    print('#############################')
    print('Exiting ConvertToOldFormat.py')
    print('#############################')
    print('')
    print('')
    exit(0)

if __name__ == "__main__":
    main()
