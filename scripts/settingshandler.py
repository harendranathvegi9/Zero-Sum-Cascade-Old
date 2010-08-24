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

class SettingsHandler():
	def __init__(self, guifile, world):
		self._world = world
		self._options = {}
		self._popupoptions = {}
		self._window = pychan.loadXML("gui/settings.xml")
		self._popup = pychan.loadXML("gui/settingspopup.xml")
		self._dynamicbuttons = [ "resolutionDrop" ,
					 "fullscreenButton" ,
					 "windowedButton" ,
					 "openGLButton" ,
					 "SDLButton" ,
					 "soundonButton" ,
					 "soundoffButton" ,
					 "applyButton" ,
					 "closeButton" ]
		self._popupbuttons = [ "okButton" ,
				       "cancelButton" ]
		for button in self._dynamicbuttons:
			self._options[button] = self._window.findChild(name=button)
		for button in self._popupbuttons:
			self._popupoptions[button] = self._popup.findChild(name=button)
		self._options["resolutionDrop"].items = [ u"640x480" ,
							 u"800x480" ,
							 u"800x600" ,
							 u"1024x600" ,
							 u"1024x768" ,
							 u"1280x768" ,
							 u"1440x900" ,
							 u"1280x960" ]
		i = 0
		self._resolution = 0
		for resolution in self._options["resolutionDrop"].items:
			if self._world._setting.get("FIFE", "ScreenResolution", "800x600") == resolution:
				self._options["resolutionDrop"]._setSelected(i)
				self._resolution = i
				break
			else:
				i = i + 1
		if self._world._setting.get("FIFE", "FullScreen", True):
			self._options["fullscreenButton"].toggled = True
			self._fullscreen = True
		else:
			self._options["windowedButton"].toggled = True
			self._fullscreen = False
		if self._world._setting.get("FIFE", "RenderBackend", "OpenGL") == "OpenGL":
			self._options["openGLButton"].toggled = True
			self._openGL = True
		else:
			self._options["SDLButton"].toggled = True
			self._openGL = False
		if self._world._setting.get("FIFE", "PlaySounds", True):
			self._options["soundonButton"].toggled = True
			self._sound = True
		else:
			self._options["soundoffButton"].toggled = True
			self._sound = False
		
		self._window.mapEvents({ "closeButton" : self._apply })
		self._popup.mapEvents({ "okButton" : self._popupOkay ,
				        "closeButton" : self._popupCancel })
	
	def show(self):
		self._window.show()

	def hide(self):
		self._window.hide()
		self._popup.hide()

	def _apply(self):
		self.hide()
		if (self._options["soundonButton"].toggled and self._sound) or (not self._options["soundonButton"].toggled and not self._sound):
			if (self._options["openGLButton"].toggled and self._openGL) or (not self._options["openGLButton"].toggled and not self._openGL):
				if (self._options["fullscreenButton"].toggled and self._fullscreen) or (not self._options["fullscreenButton"].toggled and not self._fullscreen):
					if self._options["resolutionDrop"].selected == self._resolution:
						self._world._mainmenu.show()
						return
		self._window.hide()
		self._popup.show()
	
	def _popupOkay(self):
		self._world._setting.set("FIFE", "PlaySounds", self._options["soundonButton"].toggled)
		self._world._setting.set("FIFE", "FullScreen", self._options["fullscreenButton"].toggled)
		if self._options["openGLButton"].toggled:
			self._world._setting.set("FIFE", "RenderBackground", "OpenGL")
		else:
			self._world._setting.set("FIFE", "RenderBackground", "SDL")
		self._world._setting.set("FIFE", "ScreenResolution", self._options["resolutionDrop"]._getSelectedItem())
		self._world._setting.saveSettings()
		self._world._quit = True
	
	def _popupCancel(self):
		i = 0
		for resolution in self._options["resolutionDrop"].items:
			if self._world._setting.get("FIFE", "ScreenResolution", "800x600") == resolution:
				self._options["resolutionDrop"]._setSelected(i)
				break
			else:
				i = i + 1
		if self._world._setting.get("FIFE", "FullScreen", True):
			self._options["fullscreenButton"].toggled = True
			self._fullscreen = True
		else:
			self._options["windowedButton"].toggled = True
			self._fullscreen = False
		if self._world._setting.get("FIFE", "RenderBackend", "OpenGL") == "OpenGL":
			self._options["openGLButton"].toggled = True
			self._openGL = True
		else:
			self._options["SDLButton"].toggled = True
			self._openGL = False
		if self._world._setting.get("FIFE", "PlaySounds", True):
			self._options["soundonButton"].toggled = True
			self._sound = True
		else:
			self._options["soundoffButton"].toggled = True
			self._sound = False
		self._popup.hide()
		self._world._mainmenu.show()

