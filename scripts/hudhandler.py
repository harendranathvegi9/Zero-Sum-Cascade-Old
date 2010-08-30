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

class HUDHandler():
	def __init__(self, guifile, world):
		self._world = world
		self._menuicons = {}
		self._hud = pychan.loadXML("gui/hud.xml")
		self._dynamicbuttons = ( 'menuicon' ,
					 'mapicon' ,
					 'zscicon' )
		self._hud.mapEvents({ 'menuicon/mousePressed' : self._showmenu ,
				      'menuicon/mouseEntered' : pychan.tools.attrSetCallback(image="gui/icons/menuui.png", do__adaptLayout=True) ,
				      'menuicon/mouseExited' : pychan.tools.attrSetCallback(image="gui/icons/menuui2.png", do__adaptLayout=True) ,
				      'mapicon/mousePressed' : self._showmap ,
				      'mapicon/mouseEntered' : pychan.tools.attrSetCallback(image="gui/icons/mapui.png", do__adaptLayout=True) ,
				      'mapicon/mouseExited' : pychan.tools.attrSetCallback(image="gui/icons/mapui2.png", do__adaptLayout=True) ,
				      'zscicon/mousePressed' : self._togglezsc ,
				      'zscicon/mouseEntered' : pychan.tools.attrSetCallback(image="gui/icons/zscui.png", do__adaptLayout=True) ,
				      'zscicon/mouseExited' : pychan.tools.attrSetCallback(image="gui/icons/zscui2.png", do__adaptLayout=True) })
		for button in self._dynamicbuttons:
			self._menuicons[button] = self._hud.findChild(name=button)
		self._hud.removeAllChildren()
	
	def show(self):
		self._hud.addChild(self._menuicons['menuicon'])
		if self._world._player._hasMap:
			self._hud.addChild(self._menuicons['mapicon'])
		if self._world._player._hasZSC:
			self._hud.addChild(self._menuicons['zscicon'])
		self._hud.show()
		hud = self._hud.findChild(name="hud")
		autoposition.placeWidget(hud, 'center:bottom-25')

	def hide(self):
		self._hud.hide()
		self._hud.removeAllChildren()

	def _showmenu(self):
		self.hide()
		self._world._mainmenu.show()
	
	def _showmap(self):
		if self._world._player._hasMap:
			self._world._imageviewer.show(self._world._mapimage)
			self.hide()
	
	def _togglezsc(self):
		pass