#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
PI2JAMMA hardware detection

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2020 -krahs- - https://github.com/krahsdevil/
Copyright (C)  2020 dskywalk - http://david.dantoine.org

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
import sys, keyboard

iPressed = 0
for i in range(0, 900):
    try:
        if keyboard.is_pressed('&'):
            iPressed += 1
    except:
        sys.exit(50)

if iPressed > 0: sys.exit(100)
sys.exit(0)