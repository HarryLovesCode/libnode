assert __name__ == "__main__"

import sys
import os
import shutil
import subprocess
import glob

from . import config



nodeSrcFolder = 'node-{}'.format(config.nodeVersion)
resultFolder = 'libnode'

libFolder = os.path.join(resultFolder, 'lib')

shutil.rmtree(resultFolder, ignore_errors=True)

os.mkdir(resultFolder)
os.mkdir(libFolder)


def filterLibFile(filename):
    return 'gtest' not in filename and 'v8_nosnapshot' not in filename

if sys.platform == 'win32':
    for libFile in os.scandir(nodeSrcFolder + '\\out\\Release\\lib'):
        if libFile.is_file() and libFile.name.endswith('.lib') and filterLibFile(libFile.name):
            print('Copying', libFile.name)
            shutil.copy(libFile.path, libFolder)
elif sys.platform == 'darwin':
    for libFile in os.scandir(nodeSrcFolder + '/out/Release'):
        if libFile.is_file() and libFile.name.endswith('.a') and filterLibFile(libFile.name):
            print('Copying', libFile.name)
            shutil.copy(libFile.path, libFolder)
            print('Striping', libFile.name)
            subprocess.check_call(['strip', '-x', os.path.join(libFolder, libFile.name)])
elif sys.platform == 'linux':
    for dirname, _, basenames in os.walk(nodeSrcFolder + '/out/Release/obj'):
        for basename in basenames:
            if basename.endswith('.a') and filterLibFile(basename):
                subprocess.run(
                    'ar -t {} | xargs ar rs {}'.format(
                        os.path.join(dirname, basename),
                        os.path.join(libFolder, basename)
                    ),
                    check=True, shell=True
                )

additional_obj_glob = nodeSrcFolder + '/out/Release/obj/src/node_mksnapshot.*.o'
if sys.platform == 'win32':
    additional_obj_glob = nodeSrcFolder + '/out/Release/obj/node_mksnapshot/*.obj'
for obj_path in glob.glob(additional_obj_glob):
    shutil.copy(obj_path, libFolder)

shutil.copytree(os.path.join(nodeSrcFolder, 'include'), os.path.join(resultFolder, 'include'))
shutil.copyfile('CMakeLists.txt', os.path.join(resultFolder, 'CMakeLists.txt'))

with open(os.path.join(resultFolder, 'dummy.c'), "w") as dummy_c_file:
    print("void libnode_dummy_func() { }", file=dummy_c_file)
