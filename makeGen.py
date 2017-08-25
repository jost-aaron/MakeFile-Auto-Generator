# Compile with nuitka to executable

import sys

import os
import subprocess
import datetime
import difflib

fileToCompile = ""
listOfcppFiles = []

usingLibrariesString = ""
compiler_flags = ""

VerboseMode = False
DebugMode = False

Version = "0.1"

# Progrss bar class
class progressBar():


    """docstring for progressBar.

        This class requires sys to be included

        Usage:

        name=progressBar(bar_size,total_num)
        lable will default to Progress

        optional: (This will give the progressBar a custom lable other than the default)

        name=progressBar(bar_size,total_num,title=new_title_str)

    """

    indicator_char = "#"
    current_percent = 0
    current_progress_num = 0
    done = 0
    bar_title = "Progress"


    def __init__(self,bar_size,total_num,title=None):


        self.bar_length = bar_size
        self.total = total_num
        if title is not None:
            self.bar_title = title
        self.build_str()

    def update(self,new_val):
        self.current_percent = int((new_val*100)/self.total)
        self.build_str()

    def build_str(self):


        # If this is not the same as the last one print a new one
        if (self.current_percent is not self.current_progress_num and not self.done):

            # Calculate the number of blank spaces
            self.current_progress_num = int((self.current_percent/100)*self.bar_length)
            num_blank = self.bar_length - self.current_progress_num

            print_str = "\r" + self.bar_title +": "
            # print_str += "#"*(self.current_progress_num)

            print_str += "◼"*(self.current_progress_num)

            print_str += "▱"*(num_blank-1) + " " + str(self.current_percent) + "%"
            # print_str += "-"*(num_blank-1) + " " + str(self.current_percent) + "%"

            sys.stdout.write(print_str)

            if (num_blank-1 <= 0):
                self.done = 1

        if (self.done == 1):
            print_str = "\r" + self.bar_title +": Done" + " "*((self.current_progress_num)+1) + "\n"
            sys.stdout.write(print_str)
            self.done = 2

# Print the help menue for the program
def runHelpMenue():
    print("usage: makeGen  [-h | --help] [-C | --CompileTarget File.cpp] [-L | --Libs \"LibNames\"] [-V | --Verbose]")
    print("\t\t[-O | --CompilerOptimization level] [-W | --CompilerWarnings]")
    print()
    print("Description:\n" + "\t- MakeGen v" + Version + "\n" +"\t- This program automatically generates a makefile for a specified C++ Source file.")
    print("\tDependacies:")
    tabLen = " "*3
    print("\t" + tabLen + "\t- g++ Compiler")
    print("\nFlag Definitions:")

    # Print Descritions for compile target flag
    print("\tCompile Target:\t(REQUIRED!)")
    print("\t" + tabLen + "\t- Set the file we want to compile all of our code into.")
    print("\t" + tabLen + "\t- Example: main.cpp")
    print()

    print("\tLibs:")
    print("\t" + tabLen + "\t- Set the name of the librarys you would like to link the")
    print("\t" + tabLen + "\t    executable to at compile time.")
    print("\t" + tabLen + "\t- Example: \"GL GLEW GLU\"")
    print()

    print("\tVerbose:")
    print("\t" + len(tabLen)*" " + "\t- This enables printing out information about what librarys are")
    print("\t" + len(tabLen)*" " + "\t    being linked and what object files are being generated.")
    print()

    print("\tCompiler Optimization:")
    print("\t" + len(tabLen)*" " + "\t- This sets the optimization level of g++ for compilation.")
    print("\t" + len(tabLen)*" " + "\t- Any valid g++ optimization level can be used.")
    print("\t" + len(tabLen)*" " + "\t- Usage:")
    print("\t" + len(tabLen)*" " + "\t\t* For no Optimization dont use this flag")
    print("\t" + len(tabLen)*" " + "\t\t* 1-3 (1 being little optimization, 3 being full optimization)")
    print("\t" + len(tabLen)*" " + "\t\t* g (No optimization and add debugging symbols in the")
    print("\t" + len(tabLen)*" " + "\t\t    binary for debugging)")

    print("\tCompiler Warnings:")
    print("\t" + len(tabLen)*" " + "\t- Disable g++ compilation warnings.")

def verboseModePrint(inputString):
        if(VerboseMode):
            print("-",inputString)

# Paser and run a system command and return the output of the command
def getCommandLineArgs():
    # Allow for fileToCompile to be written to
    global fileToCompile
    global usingLibrariesString
    global VerboseMode
    global compiler_flags

    argsFound = sys.argv

    if (".py" in argsFound[0]):
        argsFound.pop(0)


    # Check if --help was called or no arguments were given
    if("-h" in argsFound or "--help" in argsFound or len(argsFound) == 0):
        runHelpMenue()
        exit(0)

    # Set the verbosity mode
    if("-V" in argsFound or "--Verbose" in argsFound):
        VerboseMode = True

    if("-W" in argsFound or "--CompilerWarnings" in argsFound):
        compiler_flags+= "-w"
        verboseModePrint("Compiler Warnings Disabled")

    # Dealing with Compile target assignment
    # Make sure the compile target file was specified and done correctly
    if("-C" in argsFound or "--CompileTarget" in argsFound):

        # Find the index of the compile target flag and add 1 to it to find the arguemnts location
        indexOfCompileFileArg = None
        if ("-C" in argsFound):
            indexOfCompileFileArg = argsFound.index("-C")+1
        elif("--CompileTarget" in argsFound):
            indexOfCompileFileArg = argsFound.index("--CompileTarget")+1

        # TODO: Add an additional check if the indexOfCompileFileArg is still None. Is kind of redundant through

        # Check if there is a .cpp file after the flag

        if(indexOfCompileFileArg > len(argsFound)-1):
            print("Error: No source file (file.cpp) was given after --CompileTarget or -C.")
            exit(1)

        # Make sure the next thing is not a flag
        if("-" != argsFound[indexOfCompileFileArg][0]):

            if (".cpp" in argsFound[indexOfCompileFileArg][-4:]):
                fileToCompile = argsFound[indexOfCompileFileArg]
            else:
                print("Error: File name: " + argsFound[indexOfCompileFileArg] + " is not a C++ source file (Example: file.cpp)")
                exit(1)
        else:
            print("Error: No source file (file.cpp) was given after --CompileTarget or -C.")
            exit(1)
        # if the file we found eariler does not exist error out
        if(not os.path.isfile(fileToCompile)):
            print("Error: " + fileToCompile + " could not be found in directory:", os.getcwd() + "/")
            # Make a sugestion on files they could have ment
            possableFiles = os.listdir(".")
            possableFiles = [ x for x in possableFiles if "." in x ]
            sugestions = difflib.get_close_matches(fileToCompile,possableFiles)
            if(len(sugestions) > 0):
                print("Did you mean " + sugestions[0] + "?")
            elif(len(sugestions) > 1):
                print("Did you mean " + sugestions[0] + " or " + sugestions[1] + "?")
            exit(1)
    else:
        print("Error: Compile Target not specified with -C or --CompileTarget.")
        exit(1)


    # Check if any librarys have been specified
    if ("-L" in argsFound or "--Libs" in argsFound):
        indexOfLibsArg = None
        if("-L" in argsFound):
            indexOfLibsArg = argsFound.index("-L")+1
        elif("--Libs" in argsFound):
            indexOfLibsArg = argsFound.index("--Libs")+1

        # TODO: Add an additional check if the indexOfCompileFileArg is still None. Is kind of redundant through

        #  Do some Checks to make sure there is an argument given after the flag
        if (indexOfLibsArg > len(argsFound)-1):
            print("Error:  No arguments found for -L or --Libs Flag!")
            exit(1)
        if("-" == argsFound[indexOfLibsArg][0]):
            print("Error: No arguments found for -L or --Libs Flag!")
            exit(1)

        # Parse the input string into a list of librarys
        libsString = ""
        unformatedLibStrings = argsFound[indexOfLibsArg]

        # If multiple librarys were specified
        if(" " in unformatedLibStrings):
            # Split up the librarys into a list
            unformatedLibStrings = unformatedLibStrings.split(" ")

            # Add -l to all of the libNames so they are in the correct format for g++ when linking
            for lib in unformatedLibStrings:
                # If we are in verbose mode tell the user a library was added to the link list
                verboseModePrint("Library Added: "+lib)
                libsString += "-l" + lib + " "

            # Take away the last space which was added in the last itteration
            libsString.strip()

        # If a single library was specified
        else:
            # If we are in verbose mode tell the user a library was added to the link list
            verboseModePrint("Library Added: "+unformatedLibStrings)
            libsString = "-l" + unformatedLibStrings

        usingLibrariesString = libsString

    # Process command line inputs for compiler optimization level
    if ("-O" in argsFound or "--CompilerOptimization" in argsFound):

        # Check for the index of each type of optimization flag then add 1 to get the arguments location
        indexOfCompileFileArg = None
        if("-O" in argsFound):
            indexOfOptimizationLevel = argsFound.index("-O")+1
        elif("--CompilerOptimization" in argsFound):
            indexOfOptimizationLevel = argsFound.index("--CompilerOptimization")+1

        #  Do some Checks to make sure there is an argument given after the flag
        if (indexOfOptimizationLevel > len(argsFound)-1):
            print("Error: No Optimization Level found after -O or --CompilerOptimization flag!")
            exit(1)
        if("-" == argsFound[indexOfOptimizationLevel][0]):
            print("Error: No Optimization Level found after -O or --CompilerOptimization flag!")
            exit(1)

        if (argsFound[indexOfOptimizationLevel] == "g"):
            compiler_flags += " -g"
            verboseModePrint("Compiler Optimization Set to: g")
        elif (argsFound[indexOfOptimizationLevel] == "1" or argsFound[indexOfOptimizationLevel] == "2" or argsFound[indexOfOptimizationLevel] == "3"):
            compiler_flags += " -O" + argsFound[indexOfOptimizationLevel]
            verboseModePrint("Compiler Optimization Set to: " + "-O" + argsFound[indexOfOptimizationLevel])
        else:
            print("Warning: Optimization Level: " + argsFound[indexOfOptimizationLevel] + " is an unrecognised input.")
            ans = input("Would you like to override? (y or n) ")
            if(ans != "y" and ans != "yes"):
                print("exiting...")
                exit(1)
            else:
                compiler_flags += "-O" + argsFound[indexOfOptimizationLevel]
                verboseModePrint("Compiler Optimization Set to: " + "-O" + argsFound[indexOfOptimizationLevel])

# Run a system command ie Bash and return its result
def runSysCmd(commandString):
    splitStr = commandString.split()
    return str(subprocess.check_output(splitStr))

# Generate a list of all of the cpp files in the project directory
def findCppFiles(dirName=None):

    # Make listOfcppFiles writable
    global listOfcppFiles

    # List of all of the cpp files we have
    fileNames = []

    # A list of all the directories in the current directory
    directorysToVisit = []

    # Get a list of all of the files and folders in the current directory
    if(dirName is not None):
        dirList = os.listdir(dirName)
    else:
        dirList = os.listdir(".")


    dirListSorted = []


    # Sort all of the .cpp files into the dirListSorted
    for item in dirList:
        if (".cpp" in item):
            dirListSorted.append(item)

    # Sort all of the directorys into dirListSorted
    for item in dirList:
        if (dirName is not None):
            if(os.path.isdir(dirName + "/" + item)):
                dirListSorted.append(item)
        else:
            if(os.path.isdir(item)):
                dirListSorted.append(item)

    # Go through all of the items in the current directory
    for item in dirListSorted:

        # Check if we are in a sub directory. If so use the path from currend working directory
        if (dirName is not None):
            # If the item is a directory add it to the list of directorys
            if(os.path.isdir(dirName + "/"+ item)):
                directorysToVisit.append(item)
            # If it is a C++ source file and it is not the main file we are compiling add it to the list of files
            elif(".cpp" in item and item != fileToCompile):
                fileNames.append(dirName+"/"+item)

        else:

            # If the item is a directory add it to the list of directorys
            if(os.path.isdir(item)):
                directorysToVisit.append(item)
            # If it is a C++ source file and it is not the main file we are compiling add it to the list of files
            elif(".cpp" in item and item != fileToCompile):
                fileNames.append(item)

    if(len(directorysToVisit) > 0):
        # Go through all of the directories we found and find all of their files and directories
        for directory in directorysToVisit:
            # Get all of the files from the below directory
            if (dirName is not None):
                prevFiles = findCppFiles(dirName=dirName + "/" + directory)
            else:
                prevFiles = findCppFiles(dirName=directory)
            # Add each file to the file list
            for fileFound in prevFiles:
                fileNames.append(fileFound)

    listOfcppFiles = fileNames
    return fileNames

# Use g++ -MM to generate a list of dependancies for the file
def getMakeLine(fileName):
    # If this fails and throws an exception that means g++ threw an error which needs to be fixed
    try:
        # Get the make dependancies from g++ -MM
        completeLine = runSysCmd("g++ -MM " + fileName)
        # If
        if(VerboseMode):
            verboseOFileName = fileName.split("/")[-1].split(".cpp")[0] + ".o"
            verboseModePrint("Object file Added: " + verboseOFileName)
        # Get rid of some artifacts that g++ throws out
        completeLine = str(completeLine).replace("\\n","").replace("\\ ","").replace("b\'","").replace("\'","").replace("\\","")
        return completeLine
    except:
        exit(1)

# Write information about the make file into it
def writeMakeFileInformation(f):

    currentDate = datetime.datetime.now()

    f.write("# This file was autogenerated by makeGen v" + Version + "\n")
    f.write("# Author: Aaron Jost\n")
    f.write("# Date Generated: " + str(currentDate.day) + "/" + str(currentDate.month) + "/" + str(currentDate.year) + " @ " + str(currentDate.hour) + ":" + str(currentDate.minute) + "\n\n" )


    return 0;

# Write the make file
def genMakeFile():
    # Storage varable for object file information
    # contents [["example.o","exampleDep.cpp exampleDep.hpp ..." ] ... ]
    dotOlines = []

    if(not VerboseMode):
        progress = progressBar(30,len(listOfcppFiles)-1,title="MakeFile Generation")

    # For every cpp file do the following
    for cppFile in listOfcppFiles:
        if(not VerboseMode):
            progress.update(listOfcppFiles.index(cppFile))

        # Generate the make line
        completeLine = getMakeLine(cppFile)

        # Separate the object.o file name and its dependancies
        oFileName = completeLine.split(":")[0]
        oFileDeps = completeLine.split(":")[1].strip()

        # Append the information to the object file information Storage varable
        dotOlines.append([oFileName,oFileDeps])

    # Generate a list of all the object files we need to generate
    objFileList = ""
    for objFiles in dotOlines:
        objFileList += objFiles[0] + " "

    # Storage variable for an unorganized list of all the directories we are pulling source files from
    directorysList = []
    # Organized list of the above list. [cppFiles , ... , directories , ...]
    replaceDirPaths = []

    # Generate a list of all directories
    for currentCppFile in listOfcppFiles:

        # In the current cppFile with path. Get just the path part of it without the cppFile
        indexOfLast = currentCppFile.rfind("/")+1
        dirFound = currentCppFile[0:indexOfLast]

        # If that directory has not been found before add it to the list of directories
        if (dirFound not in directorysList):
            directorysList.append(dirFound)

    # Open a file to write the makefile into
    f = open("makefile","w")

    writeMakeFileInformation(f)

    # Write a variable into the make file with the compiler flags we want
    if(compiler_flags != ""):
        f.write("COMPILER_FLAGS = "+compiler_flags + "\n")

    # Go through all of the directories and see if there are any file paths we can assign to a variable to reduce the length of the makefile code
    for Direct in directorysList:
        # If the number of directories transversed by the path is more than one make it into variable
        if(Direct.count("/") > 1):
            # Take off the last / in the path
            dirsUsed = Direct.split("/")[0:-1]
            # initalize a variable for the reconstructed path
            reconstructed = ""
            # For each directory define a variable for it in the make file
            for item in dirsUsed:
                reconstructed += item + "/"
                replaceDirPaths.append(reconstructed)
            # Write the variable to the make file
            f.write(str((dirsUsed[-1] + "_DIR").upper()) + " = " + reconstructed[0:-1] + "\n")

    f.write("\n")

    # Write the final compilation definition for target file
    f.write("# Does all of the linking and compilation of " + fileToCompile + ".\n")
    f.write("out: " +fileToCompile + " " + objFileList+"\n")
    if (compiler_flags != ""):
        f.write("\tg++ "+ "$(COMPILER_FLAGS)" + " " + fileToCompile + " " + objFileList+"-o out "+ usingLibrariesString+"\n\n")
    else:
        f.write("\tg++ " + fileToCompile + " " + objFileList+"-o out "+ usingLibrariesString+"\n\n")
    # Wrte the cleanup definitions for pre-compiled headers
    f.write("# Used for cleaning up all of the precompiled headers.\n")
    f.write("cleanHeads:\n")
    # Get a list of all the directories in the current folder
    listofDirs = [x[0] for x in os.walk(".")][1:]
    for cleanDir in listofDirs:
        f.write("\trm -rf "+cleanDir+"/*.gch\n")
    f.write("\n")

    # Write the cleanup definitions for the object files
    f.write("# Used for cleaning up all of the object files.\n")
    f.write("cleanObjs:\n")
    f.write("\trm -rf *.o\n\n")

    # Clean up definition for everything
    f.write("# Used for cleaning up everything.\n")
    f.write("clean: cleanObjs cleanHeads\n")





    # Generate code for all of the object files
    lastDir = ""

    for dep in dotOlines:
        objectDefinitionLineElement = dep[1].split()[0]
        indexOfLast = objectDefinitionLineElement.rfind("/")+1
        dirFound = objectDefinitionLineElement[0:indexOfLast]
        currentIndex = dotOlines.index(dep)

        # Check if any of the parts in the directory have been defined as variables to save space
        for replacment in replaceDirPaths:
            if (replacment in dep[1] and dirFound.count("/") > 1 and replacment.count("/") > 1):
                indexOfReplacment = dotOlines.index(dep)
                VarName = replacment.split("/")[-2]
                dotOlines[indexOfReplacment][1] = dotOlines[indexOfReplacment][1].replace(replacment[0:-1],"$("+VarName.upper() + "_DIR)")

        if(dirFound != lastDir or dirFound == ""):
            if(dirFound == ""):
                dirFound = "Souce Directory"
            f.write("\n#" + "-"*27 + "-"*(len(dirFound)-1) + "\n")
            f.write("#------------ " + dirFound + " ------------\n")
            f.write("#" + "-"*27 + "-"*(len(dirFound)-1) + "\n")
            lastDir = dirFound

        f.write(dep[0] + ": "+ dotOlines[currentIndex][1]+"\n")
        if(compiler_flags != ""):
            f.write("\tg++ "+ "$(COMPILER_FLAGS)"+" -c "+ dotOlines[currentIndex][1] +"\n")
        else:
            f.write("\tg++ " +"-c "+ dotOlines[currentIndex][1] +"\n")

    f.close()

getCommandLineArgs()
findCppFiles()
genMakeFile()
