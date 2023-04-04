# -*- coding: utf-8 -*-

__author__ = "Martijn Berger"

import platform
import os
import shutil
from setuptools import find_packages, setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize

if platform.system() == "Linux":
    libraries = ["SketchUpAPI"]
    extra_compile_args = []
    extra_link_args = ["-Lbinaries/sketchup/x86-64"]
elif platform.system() == "Darwin":  # OS x
    libraries = []
    extra_compile_args = ["-mmacosx-version-min=10.9", "-F.", "-std=c++17"]
    extra_link_args = [
        "-std=c++17",
        "-mmacosx-version-min=10.9",
        "-F",
        ".",
        "-framework",
        "SketchUpAPI",
    ]
else:
    libraries = ["SketchUpAPI"]
    extra_compile_args = ["/Zp8", "/std:c++17"]
    extra_link_args = ["/LIBPATH:binaries/sketchup/x64/", "/std:c++17"]

ext_modules = [
    Extension(
        "sketchup",  # name of extension
        ["sketchup.pyx", "support.cpp"],  # filename of our Pyrex/Cython source
        language="c++",  # this causes Pyrex/Cython to create C++ source
        include_dirs=["headers", "."],  # usual stuff
        libraries=libraries,  # ditto
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        embedsignature=True,
    )
]

for e in ext_modules:
    e.cython_directives = {"language_level": "3"}  # all are Python-3


setup(
    name="Sketchup",
    cmdclass={"build_ext": build_ext},
    ext_modules=ext_modules,
)


def find_first_file_of_dir_by_prefix(dir, prefix):
    # os마다 같은 경로에서 생성되는 폴더와 파일명이 달라 공통되는 이름으로 파일을 받기 위한 함수
    # 주어진 이름으로 찾았을 때 폴더인 경우 폴더 내부 첫 번째 파일 경로를 반환
    for (path, dir, files) in os.walk(dir):
        for dir_name in dir:
            if dir_name.startswith(prefix):
                folder_name = os.path.join(path, dir_name)
                file_to_copy = os.listdir(folder_name)
                return os.path.join(folder_name, file_to_copy[0])


build_file = find_first_file_of_dir_by_prefix("./build", "lib.")
cython_file_dest = "../lib"

if platform.system() == "Linux":
    # not supported yet
    pass
else:
    print(f'Copying from "{build_file}" to "{cython_file_dest}"...')
    shutil.copy(build_file, cython_file_dest)
if platform.system() == "Darwin":  # OS x
    os.system(
        "install_name_tool -change '@rpath/SketchUpAPI.framework/Versions/A/SketchUpAPI' '@loader_path/SketchUpAPI.framework/Versions/A/SketchUpAPI' ../lib/sketchup.cpython-39-darwin.so"
    )
print("Process all done. Enjoy!")
