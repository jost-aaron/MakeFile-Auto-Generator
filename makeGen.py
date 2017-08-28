 # Compile with nuitka to executable

# Goals for Version 0.3:
# - Add suppert for include directorys
# - Add support for library directorys
# - Add support for exporting shared librarys.
# - Add a makefile.metadata to support faster rebuilding of makefiles.
#       This will contain information about the current make file so it dosent
#       need to be pased and stuff.
# - Add feature which will export a build.sh file to run the makefile.
#   This build.sh file will be able to access a hidden mode called Recursive
#   mode which allows for updating the build.sh file after being called from
#   that script

import sys
import os
import subprocess
import datetime
import difflib

# DataBase stuff
headerFiles = []
sourceFiles = []
directoryMacrosDictionary = dict()
fileDic = dict()
filesProcessedDic = set([])

# User Defined variables
compiler_flags = ""
fileToCompile = ""
outputFileName = "out"
selectedCompiler = "g++"
usingLibrariesString = ""
libraryDirectories = ""
includeDirectories = ""
VerboseMode = False
QuickCompile = False
compilerStandard = ""


DebugMode = False
Version = "0.2"


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
    current_task = ""
    lastPrintLength = 0



    def __init__(self,bar_size,total_num,title=None):


        self.bar_length = bar_size
        self.total = total_num
        if title is not None:
            self.bar_title = title
        self.build_str()

    def update(self,new_val,current_task=None):
        self.current_percent = int((new_val*100)/self.total)
        if(current_task is not None):
            self.current_task = current_task
        self.build_str()

    def build_str(self):


        # If this is not the same as the last one print a new one
        if (self.current_percent is not self.current_progress_num and not self.done):

            # Calculate the number of blank spaces
            self.current_progress_num = int((self.current_percent/100)*self.bar_length)
            num_blank = self.bar_length - self.current_progress_num

            print_str = "\r " + self.bar_title +": "
            # print_str += "#"*(self.current_progress_num)

            print_str += "◼"*(self.current_progress_num)

            print_str += "▱"*(num_blank-1) + " " + str(self.current_percent) + "% (" + self.current_task + ")"
            # print_str += "-"*(num_blank-1) + " " + str(self.current_percent) + "%"

            numAdded = 0
            if(self.lastPrintLength == 0):
                self.lastPrintLength = len(print_str)

            else:
                if(self.lastPrintLength > len(print_str)):
                    print_str += " "*(self.lastPrintLength - len(print_str))
                    numAdded = (self.lastPrintLength - len(print_str))

            self.lastPrintLength = len(print_str) - numAdded

            sys.stdout.write(print_str + "\r")

            if (num_blank-1 <= 0):
                self.done = 1

        if (self.done == 1):
            print_str = "\r" + self.bar_title +": Done" + " "*((self.current_progress_num)+1) + " "*(4+ len(self.current_task))+ "\n"
            sys.stdout.write(print_str)
            self.done = 2

# Run the usage menue
def runArgsMenue():
    print("usage: makeGen  [-h | --help] [-C | --CompileTarget File.cpp] [-l | --Libs \"LibNames\"]")
    print("\t\t[-L | --LibDirectories \"LibPaths\"] [-I | --IncludeDirectories \"IncludePaths\"] [-V | --Verbose]")
    print("\t\t[-O | --CompilerOptimization level] [-W | --CompilerWarnings] [--Clang] [--gcc] [-std value]")
    print("\t\t[-o | --outFile name]")
# Print the help menue for the program
def runHelpMenue():
    runArgsMenue()
    print()
    print("Description:\n" + "\t- MakeGen v" + Version + "\n" +"\t- This program automatically generates a makefile for a specified C/C++ Source file.")
    print("\tDependacies:")
    tabLen = " "*0
    print("\t" + "\t- One or more of the following. (g++,Clang,gcc)")
    print("\nFlag Definitions:")

    # Print Descritions for compile target flag
    print("   Compile Target:\t(REQUIRED!)")
    print("\t- Set the file we want to compile all of our code into.")
    print("\t- Example: main.cpp")
    print()

    print("   Out File:")
    print("\t- Set the name of the output executable the makefile will generate.")
    print("\t- Example: -o a.out")
    print()

    print("   Libs:")
    print("\t- Set the name of the librarys you would like to link the")
    print("\t    executable to at compile time.")
    print("\t- Example: \"GL GLEW GLU\"")
    print()

    print("   Lib Directory(s):")
    print("\t- Give the compiler a Directory to look for librarys in.")
    print("\t- Example: -L \"path/to/lib_1 path/to/lib_2\"")
    print()

    print("   Includes:")
    print("\t- Give the compiler a Directory to look for includes in.")
    print("\t- Example: -I \"path/to/include_1 path/to/include_2\"")
    print()

    print("   Verbose:")
    print("\t- This enables printing out information about what librarys are")
    print("\t    being linked and what object files are being generated.")
    print()

    print("   Compiler Optimization:")
    print("\t- This sets the optimization level of selected compiler for compilation.")
    print("\t- Any valid selected compiler optimization level can be used.")
    print("\t- Usage:")
    print("\t\t+ For no Optimization dont use this flag")
    print("\t\t+ 1-3 (1 being little optimization, 3 being full optimization)")
    print("\t\t+ g (No optimization and add debugging symbols in the")
    print("\t\t    binary for debugging)\n")

    print("   Compiler Warnings:")
    print("\t- Disable selected compiler compilation warnings.\n")

    print("   Compiler Choices:")
    print("\t- (C++ Compilers)")
    print("\t    + g++ (Default)")
    print("\t    + Clang")
    print("\t- (C Compiler)")
    print("\t    + gcc\n")

    print("   Compiler Standard:")
    print("\t- Set the standart used for the compiler.")
    print("\t- Example: -std c++11.\n")

def verboseModePrint(inputString):
    if(VerboseMode):
        print("[MakeGen]:",inputString)

# Paser and run a system command and return the output of the command
def getCommandLineArgs():
    # Allow for fileToCompile to be written to
    global fileToCompile,usingLibrariesString,VerboseMode,compiler_flags,outputFileName
    global DebugMode,selectedCompiler,compilerStandard,includeDirectories,libraryDirectories

    argsFound = sys.argv

    if(len(argsFound) == 1):
        runArgsMenue()
        exit(1)

    # Check if --help was called or no arguments were given
    if("-h" in argsFound or "--help" in argsFound):
        runHelpMenue()
        exit(1)

    # Check if -Debug was called to put the program in debug mode
    if("-Debug" in argsFound):
        DebugMode = True

    # Set the verbosity mode
    if("-V" in argsFound or "--Verbose" in argsFound):
        VerboseMode = True

    # Set the filename
    if("-o" in argsFound or "--outFile" in argsFound):
        indexOfOutFileFlag = argsFound.index("-o")
        if(indexOfOutFileFlag == len(argsFound)-1):
            print("Error: name requred after using -o or --outFile.")
            exit(1)
        if("-" in argsFound[indexOfOutFileFlag+1]):
            print("Error: name requred after using -o or --outFile.")
            exit(1)
        outputFileName = argsFound[indexOfOutFileFlag+1]

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

            if (".cpp" == argsFound[indexOfCompileFileArg][-4:]):
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
    if ("-l" in argsFound or "--Libs" in argsFound):
        indexOfLibsArg = None
        if("-l" in argsFound):
            indexOfLibsArg = argsFound.index("-l")+1
        elif("--Libs" in argsFound):
            indexOfLibsArg = argsFound.index("--Libs")+1

        # TODO: Add an additional check if the indexOfCompileFileArg is still None. Is kind of redundant through

        #  Do some Checks to make sure there is an argument given after the flag
        if (indexOfLibsArg > len(argsFound)-1):
            print("Error:  No arguments found for -l or --Libs Flag!")
            exit(1)
        if("-" == argsFound[indexOfLibsArg][0]):
            print("Error: No arguments found for -l or --Libs Flag!")
            exit(1)

        # Parse the input string into a list of librarys
        libsString = ""
        unformatedLibStrings = argsFound[indexOfLibsArg]

        # If multiple librarys were specified
        if(" " in unformatedLibStrings):
            # Split up the librarys into a list
            unformatedLibStrings = unformatedLibStrings.split(" ")

            verboseModePrint("Adding Libraries")
            stringToPrint = "  + "
            # Add -l to all of the libNames so they are in the correct format for selected compiler when linking
            for lib in unformatedLibStrings:
                # If we are in verbose mode tell the user a library was added to the link list
                # print("  + "+lib)
                stringToPrint += lib
                if (unformatedLibStrings.index(lib) != len(unformatedLibStrings)-1):
                    stringToPrint += ","


                libsString += "-l" + lib + " "
            if (VerboseMode):
                print(stringToPrint)
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

    # Other compiler has been selected
    if ("--Clang" in argsFound and "--gcc" not in argsFound):
        selectedCompiler = "clang"
    elif ("--gcc" in argsFound and "--Clang" not in argsFound):
        selectedCompiler = "gcc"
    elif ("--gcc" not in argsFound and "--Clang" not in argsFound):
        pass
    else:
        print("Error: Only one compiler can be chosen at once.")
        exit(1)

    # Set the c++ standard
    if ("-std" in argsFound):

        indexOfStdArg = argsFound.index("-std")
        if(indexOfStdArg == len(argsFound)-1):
            print("Error: No C++ standard given with -std flag.")
            exit(1)

        stdFound = argsFound[indexOfStdArg+1]
        if ("-" in stdFound):
            print("Error: No C++ standard given with -std flag.")
            exit(1)
        if("c++" not in stdFound and "C++" not in stdFound):
            print("Error: Incorrectly formated C++ standard!")
            print("Correct exaple: -std c++11 or -std C++11")
            print("Given:",stdFound)
            exit(1)
        verboseModePrint("Compiler Standard Set to: " + stdFound)
        compiler_flags += " -std="+stdFound

    # Add library directories
    if ("-L" in argsFound or "--LibDirectories" in argsFound):
        indexOfLibDirsArg = argsFound.index("-L")
        if (indexOfLibsArg == len(argsFound)-1):
            print("Error: Library Directories must be specified when using -L")
            exit(1)
        if("-" in argsFound[indexOfLibDirsArg+1]):
            print("Error: Library Directories must be specified when using -L")
            exit(1)
        if("/" not in argsFound[indexOfLibDirsArg+1]):
            print("Warning: The input directories for -L dont contain any \"/\" and therefore might be incorrect.")
            print("Given:",argsFound[indexOfLibDirsArg+1])
            ans = input("Continue anyway? (y or n) ")
            if("y" not in ans):
                print("exiting...")
                exit(1)
        libraryDirectories = "".join([" -L "+x for x in argsFound[indexOfLibDirsArg+1].split(" ")])
        verboseModePrint("Adding Library Directories:")
        if(VerboseMode):
            for incDir in argsFound[indexOfLibDirsArg+1].split(" "):
                print("  +",incDir)
        compiler_flags +=  libraryDirectories

    # Add include directories
    if ("-I" in argsFound or "--IncludeDirectories" in argsFound):
        indexOfIncDirsArg = argsFound.index("-I")
        if (indexOfIncDirsArg == len(argsFound)-1):
            print("Error: Include Directories must be specified when using -L")
            exit(1)
        if("-" in argsFound[indexOfIncDirsArg+1]):
            print("Error: Include Directories must be specified when using -L")
            exit(1)
        if("/" not in argsFound[indexOfIncDirsArg+1]):
            print("Warning: The input directories for -I dont contain any \"/\" and therefore might be incorrect.")
            print("Given:",argsFound[indexOfIncDirsArg+1])
            ans = input("Continue anyway? (y or n) ")
            if("y" not in ans):
                print("exiting...")
                exit(1)
        includeDirectories = "".join([" -I "+x for x in argsFound[indexOfIncDirsArg+1].split(" ")])

        verboseModePrint("Adding Include Directories:")
        if(VerboseMode):
            for incDir in argsFound[indexOfIncDirsArg+1].split(" "):
                print("  +",incDir)

        compiler_flags +=  includeDirectories

    # Set the name of the output executable
    if ("-o" in argsFound or "--outFile" in argsFound):

        return 0

# Run a system command ie Bash and return its result
def runSysCmd(commandString):
    splitStr = commandString.split()
    return str(subprocess.check_output(splitStr))

# Use selected compiler -MM to generate a list of dependancies for the file
def getMakeLine(fileName):
    # If this fails and throws an exception that means selected compiler threw an error which needs to be fixed
    try:
        # Get the make dependancies from selected compiler -MM
        completeLine = runSysCmd("" + selectedCompiler + " -MM " + fileName)

        # Get rid of some artifacts that selected compiler throws out
        completeLine = str(completeLine).replace("\\n","").replace("\\ ","").replace("b\'","").replace("\'","").replace("\\","").replace("  "," ")
        return completeLine
    except:
        exit(1)

 # Write information about the make file into it

def writeMakeFileInformation(f):

    currentDate = datetime.datetime.now()

    f.write("# This file was autogenerated by makeGen v" + Version + "\n")
    f.write("# Author: Aaron Jost\n")
    f.write("# Date Generated: " + str(currentDate.day) + "/" + str(currentDate.month) + "/" + str(currentDate.year) + " @ " + str(currentDate.hour) + ":" + str(currentDate.minute) + "\n\n")

# Write all of the file cleanUp defintions into the makefile
def writeMakeFileCleanUp(f,listofDirs):
    # Wrte the cleanup definitions for pre-compiled headers
    f.write("# Used for cleaning up all of the precompiled headers.\n")
    f.write("cleanHeads:\n")
    f.write("\trm -rf *.gch\n")
    # Get a list of all the directories in the current folder
    for cleanDir in listofDirs:
        macroCleanDir = cleanDir[0:-1]
        try:
            macroCleanDir = directoryMacrosDictionary[macroCleanDir]
        except:
            pass
        f.write("\trm -rf "+macroCleanDir.strip("./")+"/*.gch\n")
    f.write("\n")

    # Write the cleanup definitions for the object files
    f.write("# Used for cleaning up all of the object files.\n")
    f.write("cleanObjs:\n")
    f.write("\trm -rf *.o\n\n")

    # Clean up definition for everything
    f.write("# Used for cleaning up everything.\n")
    f.write("clean: cleanObjs cleanHeads\n")

# Recursive helper function to get all of the dependancies for all of the targets
def getUsedFilesRecursive(currentFile,currentDir):

    findings = {""}
    if (currentFile[-4:] == ".hpp"):
        baseName = currentFile.strip(".hpp")
    elif (currentFile[-2:] == ".h"):
        baseName = currentFile.strip(".h")
    else:
        print()
        print("Error: Non Header file included in:",(currentDir,currentFile))
        if(".cpp" in currentFile or ".c" == currentFile[-2:]):

            print("Source files should be used by including their header file then linked.")
        exit(1)

    if(os.path.isfile(currentDir+baseName + ".cpp")):
        findings.update([baseName+".cpp"])

    thisFilesRequirements = getMakeLine(currentDir+currentFile).split(":")[1].strip().split(" ")[1:]

    for requirement in thisFilesRequirements:
        pathToSearchIn = "".join([n+"/" for n in requirement.split("/")[0:-1]])
        fileWeAreLookingAt = requirement.split("/")[-1]
        if(not filesProcessedDic.issuperset([fileWeAreLookingAt])):
            findings.update(getUsedFilesRecursive(fileWeAreLookingAt,pathToSearchIn))
        filesProcessedDic.update([fileWeAreLookingAt])

    return list(findings)

# Get all of the headers and source files used by the main file we are compiling
def getUsedFiles():

    global headerFiles,sourceFiles,fileDic,filesProcessedDic

    AllowedFiles = {""}

    # Get all of the dependancies for main file
    mainsRequirements = getMakeLine(fileToCompile).split(":")[1].strip().split(" ")[1:]

    filesProcessedDic.update(fileToCompile)

    if(not VerboseMode):
        progress = progressBar(30,len(mainsRequirements),title="Finding Dependacies")
    else:
        print("[MakeGen]: Finding Depandancies: ")
    index = 0
    for dep in mainsRequirements:
        index += 1
        if(not VerboseMode):
            progress.update(index,current_task=dep)
        else:
            print("  +",str(dep))
        # Get the directory path to the file from the full path
        pathToSearchIn = "".join([n+"/" for n in dep.split("/")[0:-1]])
        fileWeAreLookingAt = dep.split("/")[-1]


        AllowedFiles.update([fileWeAreLookingAt])
        AllowedFiles.update(getUsedFilesRecursive(fileWeAreLookingAt,pathToSearchIn))
        filesProcessedDic.update(fileWeAreLookingAt)
        AllowedFiles.discard("")


    fileDictionary = list(AllowedFiles)

    dirStructure = []
    for files in os.walk("./"):
        dirName = files[0]
        filesInDir = files[2]
        for f in filesInDir:
            if(f in fileDictionary):
                newfullPath = dirName
                if (newfullPath[-1] != "/"):
                    newfullPath += "/"
                newfullPath += f
                dirStructure.append(newfullPath)

    for f in dirStructure:
        if(f[-4:] == ".hpp" or f[-2:] == ".h"):
            headerFiles.append(f)
        elif(f[-4:] == ".cpp" or f[-2] == ".c"):
            sourceFiles.append(f)
        else:
            print("Error: found a file which is not a cpp,c,h,or hpp file",f)
            exit(1)

    for header in headerFiles:
        headerFileName = header.split("/")[-1]
        headerPath = header.strip(headerFileName)
        fileDic.update([(headerFileName,headerPath)])

    for source in sourceFiles:
        sourceFileName = source.split("/")[-1]
        sourcePath = source.strip(sourceFileName)
        fileDic.update([(sourceFileName,sourcePath)])

def writeMakeFile():
    # Open a file to write the makefile into
    f = open("makefile","w")

    writeMakeFileInformation(f)

    # Write a variable into the make file with the compiler flags we want
    if(compiler_flags != ""):
        f.write("COMPILER_FLAGS = "+compiler_flags +  "\n\n")

    dirSet = {""}
    for d in (sourceFiles+headerFiles):
        dirSet.update(["".join([n+"/" for n in d.split("/")[0:-1]])])
    dirSet.discard("")

    # Generate macros for directories which are more that 2 deep
    GeneratedComment = False
    for d in dirSet:
        if (d.count("/") > 2):
            if(not GeneratedComment):
                f.write("# Directory Macros to reduice file size.\n")
                GeneratedComment = True
            macroName = d.split("/")[-2].upper() + "_DIR"
            macroValue = d[0:-1]
            directoryMacrosDictionary.update([(macroValue,"$("+macroName+")")])
            f.write(macroName+" = " + macroValue.strip("./") +"\n")
    f.write("\n")

    # Write the definition for the main file
    f.write("# Make file definition for output file.\n")
    f.write("out: ")

    depsString = fileToCompile + " "

    for cppFile in sourceFiles:
        addition = (cppFile.split("/")[-1][0:-4]+".o ")
        depsString += addition

    f.write(depsString + "\n")




    if (len(compiler_flags) != 0):
        flags = "$(COMPILER_FLAGS)"
    else:
        flags = ""
    f.write("\t" + selectedCompiler + " " + flags + " " + depsString + " " +  usingLibrariesString + " -o " + outputFileName)

    f.write("\n\n")

    # Write cleanUp definitions
    writeMakeFileCleanUp(f,list(dirSet))

    currentFolder = "."
    if(not VerboseMode):
        progress = progressBar(30,len(sourceFiles),title="Generating makefile")
    else:
        print("[MakeGen]: Generating Object File Definitions:")
    p = 0
    for cppFile in sourceFiles:
        p += 1
        if(not VerboseMode):
            progress.update(p,current_task="Generating: " + cppFile.split("/")[-1].strip(".cpp")+".o")
        else:
            print("  +",str(cppFile.split("/")[-1].strip(".cpp")+".o"))
        # print(cppFile)
        fileName = cppFile.split("/")[-1]
        dirName = "".join([n+"/" for n in cppFile.split("/")[:-1]])
        if (dirName != currentFolder):

            currentFolder = dirName

            f.write("\n#"+"-"*12 + "-"*len(dirName+"Directory: ") + "\n")
            f.write("#"+"-"*5 + " "+ "Directory: " + dirName.strip("./") + "/ "+ "-"*5 + "\n")
            f.write("#"+"-"*12 + "-"*len(dirName+"Directory: ") + "\n")

        requirements = ""
        requiredFiles = getMakeLine(cppFile).split(":")[-1].split(" ")
        requiredFiles.remove("")
        for path in requiredFiles:
            lookingForFile = path.split("/")[-1]
            properPath = fileDic[lookingForFile]
            if(properPath.count("/") > 2):
                properPath = directoryMacrosDictionary["."+properPath[:-1]] + "/"
            else:
                properPath = "."+properPath
            requirements+= (properPath+lookingForFile + " ").strip("./")

        f.write(fileName[:-4]+".o: " + requirements + "\n")

        if (len(compiler_flags) != 0):
            flags = "$(COMPILER_FLAGS)"
        else:
            flags = ""
        f.write("\t" + selectedCompiler + " -c " + flags + " " + requirements + "\n")

getCommandLineArgs()
getUsedFiles()
writeMakeFile()
