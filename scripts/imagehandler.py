# -*- coding: utf-8 -*-

# ####################################################################
#  Copyright (C) 2010 Minstry of Plenty
# 
#  This file is part of the Lohkan Library
#
#  Lohkan is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published 
#  by the Free Software Foundation, either version 3 of the License,
#  or (at your option) any later version.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this program.  If not, see
#  <http://www.gnu.org/licenses/>.
# ####################################################################

import sys, os, re, math, random

# Import the engine
from fife import fife

# Import Pychan
from fife.extensions import pychan
from fife.extensions.pychan import autoposition
from fife.extensions.pychan import widgets

from fife.extensions.serializers.simplexml import SimpleXMLSerializer

class ImageHandler():
	def __init__(self, guifile, world):
		self._world = world
		self._menuicons = {}
		self._window = pychan.loadXML("gui/imageviewer.xml")
		self._dynamicbuttons = [ 'image' ]
		self._window.mapEvents({ 'image/mousePressed' : self._hide })
		for button in self._dynamicbuttons:
			self._menuicons[button] = self._window.findChild(name=button)
	
	def show(self, displayimage="gui/icons/images/error.png"):
		self._menuicons['image'].image = displayimage
		print displayimage
		self._window.show()
		autoposition.placeWidget(self._window, 'center:center')

	def hide(self):
		self._window.hide()

	def _hide(self):
		self.hide()
		self._world._hud.show()