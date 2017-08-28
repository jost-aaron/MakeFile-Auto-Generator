MakeFile-Auto-Generator
=======================
Generates a makeFile for a C++ source file which includes other source files and headers from different directories. 

Requirements:
-----------------------------
- Python 3.x
- Python 2.x is NOT supported as some odd behaviors occur during makefile generation.
- g++ (GCC) 7.1.1 20170630 (Others will most likely work but have not been tested).
- (Optional) Nuitka for compiling into a slightly faster and more portable binary.


Usage:
----------
usage: makeGen.py [flags]

Flag Definitions:
-----------------
<kbd>Flag</kbd> | <kbd>Definition</kbd>
--- | ---
<kbd>-C </kbd> | <p><kbd><strong><u>Target to Compile:</u></strong></kbd></p> <mark> - Required Peramiter! </mark> <br>Set the file we want to compile all of our code into.<br> Example: ```-C main.cpp ```
<kbd>-o</kbd>| <p><kbd><strong><u>Output executable name:</u></strong></kbd></p>Set the name of the output executable the makefile will generate.<br> Example: ```-o a.out```
<kbd>-l</kbd> |<p><kbd><strong><u>Libraries:</u></strong></kbd></p> Set the name of the librarys you would like to link the executable to at compile time. <br> Example: ` -l  "GL GLEW GLU"`
<kbd>-L</kbd> | <p><kbd><strong><u>Library Directories:</u></strong></kbd></p>Give the compiler a Directory to look for librarys in. <br> Example: `-L "path/to/lib_1 path/to/lib_2"`
<kbd>-I</kbd> | <p><kbd><strong><u>Include Directories:</u></strong></kbd></p>Give the compiler a Directory to look for includes in. <br> Example: `-I "path/to/include_1 path/to/include_2"`
<kbd>-V</kbd> | <p><kbd><strong><u>Verbose output mode:</u></strong></kbd></p>This enables printing out information about what librarys are.
<kbd>-O</kbd> | <p><kbd><strong><u>Compiler optimization level:</u></strong></kbd></p> This sets the optimization level of the compiler for compilation.  Any valid selected compiler optimization level can be used. <br>**Usage:**<br>  + For no Optimization dont use this flag  **1-3** (1 being little optimization, 3 being full optimization) <br>**+ g** (No optimization and add debugging symbols in the binary for debugging) <br> Examples: `-O 1` `-O 2` `-O 3` `-O g`
<kbd>-W</kbd> | Disable selected compiler compiler warnings.
<kbd>-std</kbd> |  Set the C++ standard used for the compiler. <br> Example: `-std c++11.`
