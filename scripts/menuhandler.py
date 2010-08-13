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

class MenuHandler():
	def __init__(self, guifile, world):
		self._world = world
		self._menuicons = {}
		self._hud = pychan.loadXML("gui/menu.xml")
		self._dynamicbuttons = ( 'newbutton' ,
					 'loadbutton' ,
					 'savebutton' ,
					 'settingsbutton' ,
					 'aboutbutton' ,
					 'exitbutton' )
		self._menu = self._hud.findChild(name='menu')
		self._menu.mapEvents({ 'newbutton/mousePressed' : self._new ,
				      'newbutton/mouseEntered' : pychan.tools.attrSetCallback(image="gui/icons/buttons/new.png", do__adaptLayout=True) ,
				      'newbutton/mouseExited' : pychan.tools.attrSetCallback(image="gui/icons/buttons/new2.png", do__adaptLayout=True) ,
				      'loadbutton/mousePressed' : self._load ,
				      'loadbutton/mouseEntered' : pychan.tools.attrSetCallback(image="gui/icons/buttons/load.png", do__adaptLayout=True) ,
				      'loadbutton/mouseExited' : pychan.tools.attrSetCallback(image="gui/icons/buttons/load2.png", do__adaptLayout=True) ,
				      'savebutton/mousePressed' : self._save ,
				      'savebutton/mouseEntered' : pychan.tools.attrSetCallback(image="gui/icons/buttons/save.png", do__adaptLayout=True) ,
				      'savebutton/mouseExited' : pychan.tools.attrSetCallback(image="gui/icons/buttons/save2.png", do__adaptLayout=True) ,
				      'settingsbutton/mousePressed' : self._settings,
				      'settingsbutton/mouseEntered' : pychan.tools.attrSetCallback(image="gui/icons/buttons/settings.png", do__adaptLayout=True) ,
				      'settingsbutton/mouseExited' : pychan.tools.attrSetCallback(image="gui/icons/buttons/settings2.png", do__adaptLayout=True) ,
				      'aboutbutton/mousePressed' : self._about ,
				      'aboutbutton/mouseEntered' : pychan.tools.attrSetCallback(image="gui/icons/buttons/about.png", do__adaptLayout=True) ,
				      'aboutbutton/mouseExited' : pychan.tools.attrSetCallback(image="gui/icons/buttons/about2.png", do__adaptLayout=True) ,
				      'exitbutton/mousePressed' : self._exit ,
				      'exitbutton/mouseEntered' : pychan.tools.attrSetCallback(image="gui/icons/buttons/exit.png", do__adaptLayout=True) ,
				      'exitbutton/mouseExited' : pychan.tools.attrSetCallback(image="gui/icons/buttons/exit2.png", do__adaptLayout=True) })
		for button in self._dynamicbuttons:
			self._menuicons[button] = self._menu.findChild(name=button)
		self._menu.removeAllChildren()
	
	def show(self):
		if self._world._gamestate == 'LEVEL':
			self._menu.addChild(self._menuicons['savebutton'])
			self._menu.addChild(self._menuicons['loadbutton'])
		else:	
			self._menu.addChild(self._menuicons['newbutton'])
			self._menu.addChild(self._menuicons['loadbutton'])
		self._menu.addChild(self._menuicons['settingsbutton'])
		self._menu.addChild(self._menuicons['aboutbutton'])
		self._menu.addChild(self._menuicons['exitbutton'])
		self._world._gamestate == 'MENU'
		self._hud.show()
		menu = self._hud.findChild(name="container")
		autoposition.placeWidget(menu, 'right:top')

	def hide(self):
		self._hud.hide()
		self._menu.removeAllChildren()


	def _new(self):
		pass
	
	def _load(self):
		pass
	
	def _save(self):
		pass
	
	def _settings(self):
		pass
	
	def _about(self):
		pass
	
	def _exit(self):
		self._world._quit = True
	
