MakeFile-Auto-Generator
=======================
Generates a makeFile for a C++ source file which includes other source files and headers from different directories. 

Requirements:
=============
- Python 3.x
- Python 2.x is NOT supported as some odd behaviors occur during makefile generation.
- g++ (GCC) 7.1.1 20170630 (Others will most likely work but have not been tested).
- (Optional) Nuitka for compiling into a slightly faster and more portable binary.

Usage:
======
	usage: makeGen  [-h | --help] [-C | --CompileTarget File.cpp] [-l | --Libs "LibNames"]
		[-L | --LibDirectories "LibPaths"] [-I | --IncludeDirectories "IncludePaths"] [-V | --Verbose]
		[-O | --CompilerOptimization level] [-W | --CompilerWarnings] [--Clang] [--gcc] [-std value]
		[-o | --outFile name]




Flag Definitions:
-----------------

	Compile Target:	(REQUIRED!)
	- Set the file we want to compile all of our code into.
	- Example: main.cpp

   	Out File:
	- Set the name of the output executable the makefile will generate.
	- Example: -o a.out

   	Libs:
	- Set the name of the librarys you would like to link the
	    executable to at compile time.
	- Example: "GL GLEW GLU"

  	 Lib Directory(s):
	- Give the compiler a Directory to look for librarys in.
	- Example: -L "path/to/lib_1 path/to/lib_2"

   	Includes:
	- Give the compiler a Directory to look for includes in.
	- Example: -I "path/to/include_1 path/to/include_2"

  	 Verbose:
	- This enables printing out information about what librarys are
	    being linked and what object files are being generated.

   	Compiler Optimization:
	- This sets the optimization level of selected compiler for compilation.
	- Any valid selected compiler optimization level can be used.
	- Usage:
		+ For no Optimization dont use this flag
		+ 1-3 (1 being little optimization, 3 being full optimization)
		+ g (No optimization and add debugging symbols in the
		    binary for debugging)

  	 Compiler Warnings:
	- Disable selected compiler compilation warnings.

   	Compiler Choices:
	- (C++ Compilers)
	    + g++ (Default)
	    + Clang
	- (C Compiler)
	    + gcc

  	 Compiler Standard:
	- Set the standart used for the compiler.
	- Example: -std c++11.

