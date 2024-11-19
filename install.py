import os
import argparse

def parse_args():
    cwd = os.getcwd()
    vs_default = os.path.join(cwd, "vs")
    cmake_default = os.path.join(cwd, "cmake")
    qt_default = os.path.join(cwd, "qt")

    parser = argparse.ArgumentParser(
        prog='OpenCascade Builder',
        description='This script is for downloading and installing any dependencies for building OpenCascade for Windows, as well as building OpenCascade for Windows',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    vs_group = parser.add_mutually_exclusive_group()
    vs_group.add_argument('--existing-vs-dir', type=existing_vs_dir, help='Root directory of an existing Visual Studio installation. Throws an error if DIR/VC/Auxiliary/Build/vcvarsall.bat doesn\' exist.')
    vs_group.add_argument('--new-vs-dir', type=new_vs_dir, default=vs_default, help='Target directory for new Visual Studio installation. If supplied path is "C:/" then Visual Studio will be installed in "C:/vs".')

    cmake_group = parser.add_mutually_exclusive_group()
    cmake_group.add_argument('--existing-cmake-dir', type=existing_cmake_dir, help='Root directory of an existing cmake installation. Throws an error if DIR/bin/cmake.exe doesn\'t exist.')
    cmake_group.add_argument('--new-cmake-dir', type=new_cmake_dir, default=cmake_default, help='Target directory for new cmake installation. If supplied path is "C:/" then cmake will be installed in "C:/cmake".')

    qt_group = parser.add_mutually_exclusive_group()
    qt_group.add_argument('--existing-qt-dir', type=existing_qt_dir, help='Root directory of an existing QT installation. Throws an error if DIR/bin/qmake.exe doesn\'t exist.')
    qt_group.add_argument('--new-qt-dir', type=new_qt_dir, default=qt_default, help='Target directory for new QT installation. If supplied path is "C:/" then cmake will be installed in "C:/qt".')
    qt_group.add_argument('--no-qt', action="store_true", help='If you have no need for QT then this flag will remove QT from the build process')
    
    return parser.parse_args()

def getOrInstallDependencies(args, src_dir):
    if(args.existing_vs_dir == None):
        os.system(f'curl -L https://aka.ms/vs/17/release/vs_community.exe -o "{os.path.join(src_dir, "vs_community.exe")}"')
        os.system(f'{os.path.join(src_dir, "vs_community.exe")} --installPath "{args.new_vs_dir}" --channelId VisualStudio.17.Release.LTSC.17.0 --productId Microsoft.VisualStudio.Product.Community --add Microsoft.VisualStudio.Workload.NativeDesktop;includeRecommended --add Microsoft.VisualStudio.Component.VC.v141.x86.x64')
        vs_dir = os.path.join(args.new_vs_dir, "VC", "Auxiliary", "Build")
    else:
        vs_dir = args.existing_vs_dir

    if(args.existing_cmake_dir == None):
        os.system(f'curl -L https://github.com/Kitware/CMake/releases/download/v3.31.0-rc2/cmake-3.31.0-rc2-windows-x86_64.msi -o "{os.path.join(src_dir, "cmake-3.31.0-rc2-windows-x86_64.msi")}"')
        os.system(f'{os.path.join(src_dir, "cmake-3.31.0-rc2-windows-x86_64.msi")} INSTALL_ROOT="{args.new_cmake_dir}" ADD_CMAKE_TO_PATH=System')
        # https://gitlab.kitware.com/cmake/cmake/-/tree/v3.31.0-rc2/Utilities/Release/WiX?ref_type=tags for cmake.msi params
        cmake_dir = os.path.join(args.new_cmake_dir, "bin")
    else:
        cmake_dir = args.existing_cmake_dir

    if(not args.no_qt):
        if(args.existing_qt_dir == None):
            os.system(f'curl -L https://d13lb3tujbc8s0.cloudfront.net/onlineinstallers/qt-online-installer-windows-x64-4.8.1.exe -o "{os.path.join(src_dir, "qt-online-installer-windows-x64-4.8.1.exe")}"')
            os.system(f'{os.path.join(src_dir, "qt-online-installer-windows-x64-4.8.1.exe")} --root "{args.new_qt_dir}" --accept-licenses --accept-obligations --default-answer --confirm-command install qt.qt5.5152.win64_msvc2019_64 qt.qt5.5152.debug_info')
            qt_dir = os.path.join(args.new_qt_dir, "5.15.2", "msvc2019_64", "bin")
        else:
            qt_dir = args.existing_qt_dir

    return vs_dir, cmake_dir, qt_dir

def install():
    args = parse_args()

    root_dir = os.getcwd()
    src_dir = os.path.join(root_dir, "src")
    third_party_dir = os.path.join(root_dir, "third_party")
    os.system(f"mkdir {src_dir}")
    os.system(f"mkdir {third_party_dir}")

    vs_dir, cmake_dir, qt_dir = getOrInstallDependencies(args, src_dir)

    tcltk_install_dir = os.path.join(third_party_dir, "tcltk-install")
    freetype_install_dir = os.path.join(third_party_dir, "freetype-install")
    freeimage_install_dir = os.path.join(third_party_dir, "freeimage-install")

    install_tcl(tcltk_install_dir, src_dir, vs_dir)
    install_tk(tcltk_install_dir, src_dir, vs_dir)
    install_freetype(freetype_install_dir, src_dir, vs_dir)
    install_freeimage(freeimage_install_dir, src_dir, vs_dir)
    install_opencascade(root_dir, src_dir, third_party_dir, cmake_dir, qt_dir, tcltk_install_dir, freetype_install_dir, freeimage_install_dir, args.no_qt)

def install_opencascade(root_dir, src_dir, third_party_dir, cmake_dir, qt_dir, tcltk_install_dir, freetype_install_dir, freeimage_install_dir, no_qt):
    print("Installing OpenCascade...")

    occt_filename = "opencascade-7.8.1.zip"
    occt_install_dir = "OCCT-7_8_1-install"
    os.system(f"curl -L https://github.com/Open-Cascade-SAS/OCCT/archive/refs/tags/V7_8_1.zip -o {os.path.join(src_dir, occt_filename)}")
    os.system(f"tar -xf {os.path.join(src_dir, occt_filename)}")

    # For directly downloading precompiled third party libraries
    # occt3rd_filename = "opencascade-thirdparty-7.8.0.zip"
    # os.system(f'curl -L https://github.com/Open-Cascade-SAS/OCCT/releases/download/V7_8_0/3rdparty-vc14-64.zip -o {occt3rd_filename}')
    # os.system(f'tar -xf {occt3rd_filename}')
    cmake_exe = os.path.join(cmake_dir, "cmake.exe")

    os.system(f'\
        cd OCCT-7_8_1 & \
        mkdir build & \
        {cmake_exe} \
            -D3RDPARTY_DIR={third_party_dir} \
            -DBUILD_FORCE_RelWithDebInfo=True \
            -DBUILD_WITH_DEBUG=True \
            -DUSE_FREETYPE=True \
            -DUSE_FREEIMAGE=True \
            -DUSE_TK=True \
            -DUSE_OPENGL=True \
            -DINSTALL_DIR={os.path.join(root_dir, occt_install_dir)} \
            -DINSTALL_FREETYPE=True \
            -DINSTALL_FREEIMAGE=True \
            -DINSTALL_TCL=True \
            -DINSTALL_TK=True \
            {"-DBUILD_SAMPLES_QT=True" if not no_qt else ""} \
            {"-DINSTALL_SAMPLES=True" if not no_qt else ""} \
            {"-DINSTALL_Qt5=True" if not no_qt else ""} \
            {f"-D3RDPARTY_QT_DIR={os.path.abspath(os.path.join(qt_dir, ".."))}" if not no_qt else ""} \
            -D3RDPARTY_FREETYPE_DIR={freetype_install_dir} \
            -D3RDPARTY_FREETYPE_LIBRARY_DIR={os.path.join(freetype_install_dir, "lib")} \
            -D3RDPARTY_FREETYPE_INCLUDE_DIR_ft2build={os.path.join(freetype_install_dir, "include")} \
            -D3RDPARTY_FREETYPE_INCLUDE_DIR_freetype2={os.path.join(freetype_install_dir, "include", "freetype", "config")} \
            -D3RDPARTY_FREETYPE_DLL_DIR={os.path.join(freetype_install_dir, "bin")} \
            -DFREETYPE_LIBRARY_RELEASE={os.path.join(freetype_install_dir, "lib", "freetype.lib")} \
            -DFREETYPE_LIBRARY_DEBUG={os.path.join(freetype_install_dir, "libd", "freetype.lib")} \
            -D3RDPARTY_FREEIMAGE_DIR={freeimage_install_dir} \
            -D3RDPARTY_FREEIMAGE_INCLUDE_DIR={os.path.join(freeimage_install_dir, "include")} \
            -D3RDPARTY_FREEIMAGE_DLL_DIR_freeimage={os.path.join(freeimage_install_dir, "bin")} \
            -D3RDPARTY_FREEIMAGE_LIBRARY_DIR_freeimage={os.path.join(freeimage_install_dir, "lib")} \
            -D3RDPARTY_TCL_DIR={tcltk_install_dir} \
            -D3RDPARTY_TK_DIR={tcltk_install_dir} \
            {f"-DQt5_DIR={qt_dir}" if not no_qt else ""} \
            -S . -B build & \
        {cmake_exe} --build build -j {os.environ['NUMBER_OF_PROCESSORS']} & \
        {cmake_exe} --build build --config Release -j {os.environ['NUMBER_OF_PROCESSORS']} & \
        {cmake_exe} --install build & \
        {cmake_exe} --install build --config Debug\
    '.replace("\\", "/"))
    # Use of .replace("\\", "/") is because some of the opencascade cmake files check paths using regex which can misbehave with backslashes

    # -D3RDPARTY_FREEIMAGE_DIR={os.path.join(cwd, "FreeImage")} \
    # -D3RDPARTY_FREEIMAGE_INCLUDE_DIR={os.path.join(cwd, "FreeImage", "Source")} \
    # -D3RDPARTY_FREEIMAGE_DLL_DIR_freeimage={os.path.join(cwd, "FreeImage", "x64", "Release")} \
    # -D3RDPARTY_FREEIMAGE_LIBRARY_DIR_freeimage={os.path.join(cwd, "FreeImage", "x64", "Release")} \
            
def install_tcl(install_dir, src_dir, vs_dir):
    print("Installing tcl...")

    tcl_filename = "tcl8615-src.zip"
    os.system(f"""\
        cd {src_dir} & \
        curl -L http://prdownloads.sourceforge.net/tcl/{tcl_filename} -o "{tcl_filename}" & \
        tar -xf {tcl_filename} & \
        cd tcl8.6.15\\win & \
        set CL=/MP  & \
        {os.path.join(vs_dir, "vcvarsall.bat")} amd64 & \
        nmake -f makefile.vc INSTALLDIR={install_dir} & \
        nmake -f makefile.vc install INSTALLDIR={install_dir} """)
    os.system(f'copy "{os.path.join(install_dir,"bin", "tclsh86t.exe")}" "{os.path.join(install_dir,"bin", "tclsh.exe")}"')
    os.system(f'copy "{os.path.join(install_dir,"bin", "tcl86t.dll")}" "{os.path.join(install_dir,"bin", "tcl86.dll")}"')

def install_tk(install_dir, src_dir, vs_dir):
    print("Installing tk...")

    tk_filename = "tk8615-src.zip"
    os.system(f"""\
        cd {src_dir} & \
        curl -L http://prdownloads.sourceforge.net/tcl/{tk_filename} -o "{tk_filename}" & \
        tar -xf {tk_filename} & \
        cd tk8.6.15\\win & \
        set CL=/MP & \
        {os.path.join(vs_dir, "vcvarsall.bat")} amd64 & \
        nmake -f makefile.vc INSTALLDIR={install_dir} TCLDIR={os.path.join(src_dir, "tcl8.6.15")} & \
        nmake -f makefile.vc install INSTALLDIR={install_dir} TCLDIR={os.path.join(src_dir, "tcl8.6.15")}""")
    os.system(f'copy "{os.path.join(install_dir,"bin", "wish86t.exe")}" "{os.path.join(install_dir,"bin", "wish.exe")}"')
    os.system(f'copy "{os.path.join(install_dir,"bin", "tk86t.dll")}" "{os.path.join(install_dir,"bin", "tk86.dll")}"')

def install_freetype(install_dir, src_dir, vs_dir):
    print("Installing freetype...")
    freetype_filename = "ft2133.zip"
    os.system(f"""\
        cd {src_dir} & \
        curl -L https://sourceforge.net/projects/freetype/files/freetype2/2.13.3/{freetype_filename}/download -o "{freetype_filename}" & \
        tar -xf {freetype_filename} & \
        cd freetype-2.13.3 & \
        {os.path.join(vs_dir, "vcvarsall.bat")} amd64 & \
        devenv MSBuild.sln /Build Release & \
        devenv MSBuild.sln /Build """)
    os.system(f'mkdir {os.path.join(install_dir,"lib")}')
    os.system(f'mkdir {os.path.join(install_dir,"libd")}')
    os.system(f'mkdir {os.path.join(install_dir,"bin")}')
    os.system(f'mkdir {os.path.join(install_dir,"bind")}')
    os.system(f'mkdir {os.path.join(install_dir,"include")}')
    os.system(f'copy "{os.path.join(src_dir,"freetype-2.13.3", "objs", "x64", "Release", "freetype.lib")}" "{os.path.join(install_dir,"lib", "freetype.lib")}"')
    os.system(f'copy "{os.path.join(src_dir,"freetype-2.13.3", "objs", "x64", "Release", "freetype.dll")}" "{os.path.join(install_dir,"bin", "freetype.dll")}"')
    os.system(f'copy "{os.path.join(src_dir,"freetype-2.13.3", "objs", "x64", "Debug", "freetype.lib")}" "{os.path.join(install_dir,"libd", "freetype.lib")}"')
    os.system(f'copy "{os.path.join(src_dir,"freetype-2.13.3", "objs", "x64", "Debug", "freetype.dll")}" "{os.path.join(install_dir,"bind", "freetype.dll")}"')
    os.system(f'robocopy "{os.path.join(src_dir,"freetype-2.13.3", "include")}" "{os.path.join(install_dir,"include")}" /s /e')

def install_freeimage(install_dir, src_dir, vs_dir):
    print("Installing freeimage...")
    
    freeimage_filename = "FreeImage3180.zip"
    os.system(f"""\
        cd {src_dir} & \
        curl -L https://sourceforge.net/projects/freeimage/files/Source%20Distribution/3.18.0/{freeimage_filename}/download -o "{freeimage_filename}" & \
        tar -xf {freeimage_filename} & \
        cd FreeImage & \
        {os.path.join(vs_dir, "vcvarsall.bat")} amd64 & \
        msbuild FreeImage.2017.vcxproj /p:WindowsTargetPlatformVersion=10.0.22621.0 /p:Configuration=Release -maxcpucount """)
    os.system(f'mkdir {os.path.join(install_dir,"lib")}')
    os.system(f'mkdir {os.path.join(install_dir,"bin")}')
    os.system(f'mkdir {os.path.join(install_dir,"include")}')
    os.system(f'copy "{os.path.join(src_dir,"FreeImage", "x64", "Release", "FreeImage.lib")}" "{os.path.join(install_dir, "lib", "FreeImage.lib")}"')
    os.system(f'copy "{os.path.join(src_dir,"FreeImage", "x64", "Release", "FreeImage.dll")}" "{os.path.join(install_dir, "bin", "FreeImage.dll")}"')
    os.system(f'copy "{os.path.join(src_dir,"FreeImage", "Source", "FreeImage.h")}" "{os.path.join(install_dir, "include", "FreeImage.h")}"')

def existing_vs_dir(path):
    return file_exists(os.path.join(path, "VC", "Auxiliary", "Build"), "vcvarsall.bat")

def existing_cmake_dir(path):
    return file_exists(os.path.join(path, "bin"), "cmake.exe")

def existing_qt_dir(path):
    return file_exists(os.path.join(path, "bin"), "qmake.exe")
    
def file_exists(path, filename):
    path = os.path.abspath(path)
    if os.path.isfile(os.path.join(path, filename)):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} does not contain {filename}.")

def new_vs_dir(path):
    return valid_dir(path, suffix="vs")

def new_cmake_dir(path):
    return valid_dir(path, suffix="cmake")

def new_qt_dir(path):
    return valid_dir(path, suffix="qt")

def valid_dir(path, suffix=""):
    path = os.path.abspath(path)
    if(os.path.split(path)[1] != suffix):
        path = os.path.join(path, suffix)
    if os.access(os.path.dirname(path), os.W_OK):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")
    
if __name__ == "__main__":
    install()

