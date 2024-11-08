# General Info
The purpose of this script is to download/compile the tools needed for Open Cascade C++ development on Windows.
Over the past 3/4 years I've had a reinstall Open Cascade multiple times for various reasons and this script aims to simplify this process.

## Dependencies
The only dependency is Python. The script should download and install everything needed when used appropriately.
Could I have written this script as a batch or powershell script? Yes, but the python argparse module makes handling different configurations a breeze.

## Usage
There are three main parts to the script:
1. Download and install dependencies: CMake and Visual Studio (and maybe Qt).
2. Compile third party libraries from sources (tcl, tk, freeimage, freetype).
3. Compile Open Cascade from sources.

Qt is not a strict dependency but comes in useful when developing applications with a GUI and is necessary to compile the Open Cascade Qt samples.

The following command lists the usage of the script:
`python install.py --help`

If you're on a fresh Windows install without CMake, Visual Studio or Qt then the following command will install everything in the specified directories:
`python install.py --new-cmake-dir C:\\cmake --new-vs-dir C:\\visualstudio --new-qt-dir C:\\qt`

If you have an existing installation of CMake, Visual Studio or Qt then you can supply the relevant directory using the --existing-cmake-dir, --existing-vs-dir or --existing-qt-dir arguments.

If you supply no arguments, then CMake, Visual Studio and Qt will be installed in the current working directory.

## Note
If your Open Cascade build is failing, you may need to change OCCT-7_8_1\src\StdPrs\StdPrs_BRepFont.cxx line 460 from 'char' to 'auto'. This is a bug in Open Cascade 7.8.1 and should be fixed in the next release.