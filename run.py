#!/usr/bin/env python

# -*- coding: utf-8 -*-

import sys, os, re, math, random, shutil

fife_path = os.path.join('..','..','engine','python')
if os.path.isdir(fife_path) and fife_path not in sys.path:
	sys.path.insert(0,fife_path)

from fife import fife
print "Using the FIFE python module found here: ", os.path.dirname(fife.__file__)

from fife.extensions.fife_settings import Setting

TDS = Setting(app_name="zsc-demo-1",
              settings_file="./settings.xml", 
              settings_gui_xml="")
