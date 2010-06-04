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

import sys, os, re

# Tell the interpreter where to find the engine
fife_path = os.path.join('..','..','engine','python')
if os.path.isdir(fife_path) and fife_path not in sys.path:
	sys.path.insert(0,fife_path)

# Import the engine
from fife import fife

# Import misc. libraries
import copy
import math, random

# Import FIFE libraries
from fife.extensions import pychan
from fife.extensions.pychan import widgets
from fife.extensions.soundmanager import SoundManager

# Import eventListenerBase and the maploader
from scripts.common.eventlistenerbase import EventListenerBase
from fife.extensions.loaders import loadMapFile, loadImportFile

class World(EventListenerBase):
	def __init__(self, app, engine, setting):
		super(World, self).__init__(engine, regKeys=True, regCmd=False, regMouse=True)

		self._applictaion = app
		self._engine = engine
		self._setting = setting
		self._timemanager = engine.getTimeManager()
		self._eventmanager = engine.getEventManager()
		self._model = engine.getModel()
		self._filename = ''
		self._keystate = { 'UP': False, 
		                   'DOWN': False, 
		                   'LEFT': False, 
		                   'RIGHT': False, 
		                   'CTRL': False, 
		                   'SPACE': False,
				   'Q': False,
				   'E': False,} 
		self._pump_ctr = 0
		self._map = None
		self._scene = None
		self._paused = True
		self._pausedtime = 0
		self._starttime = 0
		self._gamestate = 'STOPPED'
		
		pychan.init(self._engine)
		
		self._hud = None
		self._mainmenu = None
		self._pausemenu = None
		self._loadingmenu = None
		
		self._soundmanager = SoundManager(self._engine)
		
	def _loadGui(self, type, guifile):
		if type == 'MAIN':
			self._mainmenu = pychan.loadXML('gui/' + guifile + '.xml')
			guiinit = __import__('scripts.gui.' + guifile)
			guiinit.run()
		elif type == 'HUD':
			self._hud = pychan.loadXML('gui/' + guifile + '.xml')
			guiinit = __import__('scripts.gui.' + guifile)
			guiinit.run()
		elif type == 'PAUSE':
			self._pause = pychan.loadXML('gui/' + guifile + '.xml')
			guiinit = __import__('scripts.gui.' + guifile)
			guiinit.run()
		elif type == 'LOAD':
			self._loadingmenu = pychan.loadXML('gui/' + guifile + '.xml')
			guiinit = __import__('scripts.gui.' + guifile)
			guiinit.run()
		else:
			pass
	
	def _hideAllGuis(self):
		if self._hud != None:
			self._hud.hide()
		if self._mainmenu != None:
			self._mainmenu.hide()
		if self._pausemenu != None:
			self._pausemenu.hide()
		if self._loadingmenu != None:
			self._loadingmenu.hide()

	def _loadLevelMapCallback(self, action, percentdone):
		if percentdone == 1:
			self._gamestate = 'LOADED'
			self._hideAllGuis()
			if self._hud != None:
				self._hud.show()
		else:
			print str(percentdone) + "% loaded"
	
	def _loadMenuMapCallback(self, action, percentdone):
		if percentdone == 1:
			self._gamestate = 'LOADED'
			self._hideAllGuis()
			if self._mainmenu != None:
				self._mainmenu.show()
		else:
			print str(percentdone) + "% loaded"

	def _loadMap(self, filename, purpose):
		self._model.deleteMap(self._map)
		self._map = None
		
		if purpose == 'LEVEL':
			self._map = loadMapFile(filename, self._engine, self._loadLevelMapCallback)
			self._hideAllGuis()
			if self._loadingmenu != None:
				self._loadingmenu.show()
		elif purpose == 'MENU':
			self._map = loadMapFile(filename, self._engine, self._loadMenuMapCallback)
			self._hideAllGuis()
			if self._loadingmenu != None:
				self._loadingmenu.show()
		
		self._cameras = {}
		for cam in self._map.getCameras():
			camera_id = cam.getId()
			self._cameras[camera_id] = cam
			cam.resetRenderers()
