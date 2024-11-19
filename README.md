# General Info
The purpose of this script is to download/compile the tools needed for Open Cascade C++ development on Windows.

## Dependencies
The only dependency is Python. The script should download and install everything needed when used appropriately.
Could I have written this script as a batch or powershell script? Yes, but the python argparse module makes handling any changes to arguments much simpler.
## Usage
There are three main things this script does:
1. Download and install dependencies: CMake and Visual Studio (and maybe Qt).
2. Compile third party libraries from sources (tcl, tk, freeimage, freetype).
3. Compile Open Cascade from sources.

Qt is not a strict dependency but comes in useful when developing applications with a GUI and is necessary to compile the Open Cascade Qt samples. 
Use the `--no-qt` flag to build without Qt .

The following command lists the usage of the script:
`python install.py --help`

If you're on a fresh Windows install without CMake, Visual Studio or Qt then the following command will install everything in the specified directories:
`python install.py --new-cmake-dir C:\\cmake --new-vs-dir C:\\visualstudio --new-qt-dir C:\\qt`

If you have an existing installation of CMake, Visual Studio or Qt then you can supply the relevant directory using the `--existing-cmake-dir`, `--existing-vs-dir` or `--existing-qt-dir` arguments:
`python install.py --existing-cmake-dir C:\\cmake --existing-vs-dir C:\\visualstudio --existing-qt-dir C:\\qt\\5.15.2\\msvc2019_64`

If you supply no arguments, then CMake, Visual Studio and Qt will be installed in the current working directory.

## Note
- The Open Cascade build will almost certainly be failing right now. You'll have to change OCCT-7_8_1\src\StdPrs\StdPrs_BRepFont.cxx line 460 from 'char' to 'auto'. This is a bug in Open Cascade 7.8.1 with freetype 2.13.3 and will be fixed in the next Open Cascade release. 
- This script doesn't build Qt from sources so if you're not using the `--no-qt` flag you will need to create an account for the Qt installer. As far am I am aware, there isn't a way around this.
- The cmake install will start before the Visual Studio installation has finished. This is because the Visual Studio installer starts another process to do the bulk of the work. It's best to just wait until the Visual Studio installation has finished before starting the cmake install otherwise you run the risk that the script will try to start building tcl/tk before Visual Studio is fully installed.
- I've set up the Qt installation to work without user interaction. The same can be done for Visual Studio with the `--passive` flag and the `/passive` flag for cmake.