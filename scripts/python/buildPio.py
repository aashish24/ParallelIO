import os
import platform
import sys
import xml.etree.ElementTree as etree
# imports of NCAR scripts
import builder
import parsers
lib_path = os.path.join('scripts/python/contrib/unit_testing')
sys.path.append(lib_path)
from machine_setup import get_machine_name
from query_cesm_config import MachineCompilerSettings

import pprint

def runBuild(args):
    """ run the build and configure.  Call a factory class to
        kick off the appropriate build.
    """
    if args.mach:
        machine_name = args.mach
    else:
        machine_name = resolveName()

    if machine_name is None:
        raise RuntimeError("Could not resolve machine name.")

    machinefilename = args.xmlpath[0]+"/config_machines.xml"
    compilerfilename = args.xmlpath[0]+"/config_compilers.xml"
    
    xmlfile = os.path.abspath(machinefilename)
    if not os.path.isfile(xmlfile):
        raise RuntimeError("Could not find machines file: {0}".format(xmlfile))
    compiler = None
    if args.compiler:    
        compiler = args.compiler[0]    
     
    mtree = etree.parse(xmlfile).getroot()
    mach_tree = mtree.findall(".//machine[@MACH='{0}']/".format(machine_name))

    for e in mach_tree:
        if e.tag == "COMPILERS":
            compiler_list = e.text.split(',')
            # If compiler was not provided use default for machine 
            if compiler is None:
                compiler = compiler_list[0]
            if(compiler not in compiler_list):
                print("ERROR: compiler {0} not supported on machine {1}".format(compiler,machine_name))


    print ("Configure and build for :: %s \n" %
           (machine_name + " " + compiler))
    if args.test:
        print ("And run tests \n" )

    xmlcompiler = MachineCompilerSettings(compiler, compilerfilename, 
                                          machine=machine_name,use_mpi=args.mpi)

    with open('PIO_Macros.cmake', "w") as macros_file:
        xmlcompiler.write_cmake_macros(macros_file,"PIO")

    bld = builder.platformBuilder.factory(machine_name,compiler,args.test,args.mpi,args.debug)
    bld.metaBuild()


def resolveName():
    """ osx requires a Darwin build (for laptops, desktops).
        bigger platforms will usually have a name (yellowstone,
        edison, etc...)
    """
    if platform.system() == "Darwin":
        name = "darwin"
    else:
        name = get_machine_name()
    return name


def main(argv):
    """ everything starts here
    """
    useMsg = ("Build PIO and unit tests outside of the CESM framework."
              "Mostly for development and testing for faster turn-around."
              " >> python scripts/python/buildPio.py <compiler>")

    cliP = parsers.cliParser()
    args = cliP.doCliParse(useMsg)

    runBuild(args)

if __name__ == "__main__":
    main(sys.argv[1:])