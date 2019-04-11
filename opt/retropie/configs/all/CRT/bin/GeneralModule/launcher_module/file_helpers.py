#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
file_helpers.py.

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2019 -krahs- - https://github.com/krahsdevil/
Copyright (C)  2019 dskywalk - http://david.dantoine.org

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 2 of the License, or (at your option) any
later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import os
import hashlib

def remove_line(p_sFile, p_sRemoveMask):
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile,"r+") as f:
        new_file = f.readlines()
        f.seek(0) # rewind
        for line in new_file:
            if p_sRemoveMask not in line:
                f.write(line) # valid line
        f.truncate() # remove everything after the last write
        return True

def modify_line(p_sFile, p_sLineToFind, p_sNewLine, p_bEndLine = True):
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile, "r+") as f:
        new_file = f.readlines()
        f.seek(0) # rewind
        for line in new_file:
            if p_sLineToFind in line:
                line = p_sNewLine
                if p_bEndLine:
                    line += "\n"
            f.write(line) # new line
        f.truncate() # remove everything after the last write
        return True

def add_line(p_sFile, p_sNewLine, p_bEndLine = True):
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile, "a") as f:
        line = p_sNewLine
        if p_bEndLine:
            line += "\n"
        f.write(line)

def ini_get(p_sFile, p_sFindMask):
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile, "r") as f:
        for line in f:
            line = line.strip().replace('=',' ').split(' ')
            if p_sFindMask == line[0].strip():
                return line[-1].strip()

def md5_file(p_sFile):
    hasher = hashlib.md5()
    with open(p_sFile, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()


def remove_file(p_sFile):
    try:
        os.remove(p_sFile)
    except OSError:
        pass
