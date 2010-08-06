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
from fife.extensions.pychan import autoposition
from fife.extensions.pychan import widgets
from fife.extensions.soundmanager import SoundManager
from fife.extensions.fife_settings import Setting


# Import eventListenerBase, agentbase and the maploader
from scripts.common.eventlistenerbase import EventListenerBase
from scripts import agentbase
from scripts.agents.player import Player
from scripts import musicmanager, npc
from fife.extensions.loaders import loadMapFile, loadImportFile
from fife.extensions.serializers.simplexml import SimpleXMLSerializer

# World class. Starts the world.
class World(EventListenerBase):
	"""
	World Class
	Sets up the map, gui, soundmanager and calls the Actor class to deal with actors
	
	Keyword Arguments
	EventListenerBase - World inherits from EventListenerBase
	"""
	def __init__(self, app, engine, setting):
		"""
		__init__ Function
		Starts an instance of the World class
		
		Keyword Arguments
		app - A pointer to the main application
		engine - A pointer to fife.engine
		setting - A pointer to a fife settings XML file
		"""
		super(World, self).__init__(engine, regKeys=True, regCmd=False, regMouse=True)

		# Throw values into their variables
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
		self._cameras = {}
		self._npcs = {}
		self._npclist = None
		self._pump_ctr = 0
		self._map = None
		self._scene = None
		self._paused = True
		self._pausedtime = 0
		self._starttime = 0
		self._gamestate = 'STOPPED'
		self._player = None
		
		# Start pychan
		pychan.init(self._engine)
		
		# Set all GUI types to empty
		self._hud = None
		self._mainmenu = None
		self._pausemenu = None
		self._loadingmenu = None
		
		# Start the sound manager
		self._soundmanager = SoundManager(self._engine)
		self._sounds = musicmanager.MusicManager(self._engine, self._soundmanager)
		
	def _loadGui(self, type, guifile, imports):
		"""
		_loadGui Function
		Loads a pychan GUI file to one of the four GUI slots, then loads a python package to run to initilise the gui
		
		Keyword Arguments
		type - String, the type of GUI being loaded
		guifile - String, name of the pychan file being loaded
		imports - Boolean
		"""
		if type == 'MAIN':
			self._mainmenu = pychan.loadXML('gui/' + guifile + '.xml')
			if imports:
				guiinit = __import__('scripts.gui.' + guifile)
				guiinit.run()
		elif type == 'HUD':
			self._hud = pychan.loadXML('gui/' + guifile + '.xml')
			if imports:
				guiinit = __import__('scripts.gui.' + guifile)
				guiinit.run()
		elif type == 'PAUSE':
			self._pause = pychan.loadXML('gui/' + guifile + '.xml')
			if imports:
				guiinit = __import__('scripts.gui.' + guifile)
				guiinit.run()
		elif type == 'LOAD':
			self._loadingmenu = pychan.loadXML('gui/' + guifile + '.xml')
			if imports:
				guiinit = __import__('scripts.gui.' + guifile)
				guiinit.run()
		else:
			pass
	
	def _hideAllGuis(self):
		"""
		_hideAllGuis Function
		Hides any active GUI elements
		"""
		if self._hud != None:
			self._hud.hide()
		if self._mainmenu != None:
			self._mainmenu.hide()
		if self._pausemenu != None:
			self._pausemenu.hide()
		if self._loadingmenu != None:
			self._loadingmenu.hide()

	def _loadLevelMapCallback(self, action, percentdone):
		"""
		_loadLevelMapCallback Function
		Acts as a callback for level loading.
		
		Keyword Arguments
		action - String, what has just been loaded
		percentdone - Float, percentage loaded
		"""
		# You have to pump the engine, else it doesn't render anything
		# until the map has loaded
		self._engine.pump()
		
		# If it's loaded, hide the loading screen and load the HUD
		if percentdone == 1:
			self._gamestate = 'LOADED'
			self._hideAllGuis()
			if self._hud != None:
				self._hud.show()	
		# Otherwise set the loading screens percentage label
		else:
			print str(percentdone) + "% loaded"
			loaded = self._loadingmenu.findChild(name="loading")
			loaded.text = str(math.floor(percentdone * 100)) + '% Loaded'			
	
	def _loadMenuMapCallback(self, action, percentdone):
		"""
		_loadMenuMapCallback Function
		Acts as a callback for level loading.
		
		Keyword Arguments
		action - String, what has just been loaded
		percentdone - Float, percentage loaded
		"""
		# You have to pump the engine, else it doesn't render anything
		# until the map has loaded
		self._engine.pump()
		
		# If it's loaded, hide the loading screen and load the menu
		if percentdone == 1:
			self._gamestate = 'LOADED'
			self._hideAllGuis()
			if self._mainmenu != None:
				self._mainmenu.show()
		# Otherwise set the loading screens percentage label
		else:
			print str(percentdone) + "% loaded"
			loaded = self._loadingmenu.findChild(name="loading")
			loaded.text = str(math.floor(percentdone * 100)) + '% Loaded'

	def _loadMap(self, filename, purpose):
		"""
		_loadMap Function
		Deletes the old map and loads a new one. Also initilises cameras.
		
		Keyword Arguments
		filename - String, path to the map file
		purpose - String, LEVEL or MENU
		"""
		self._model.deleteMap(self._map)
		self._map = None
		self._npcs = {}
		self._npclist = False
		self._mapsettings = SimpleXMLSerializer(filename=filename +".config")
		
		
		
		if purpose == 'LEVEL':
			# Hide any active GUIs
			self._hideAllGuis()
			
			# Pump the engine to force it to move to a new frame
			self._engine.pump()
			
			# If the loading menu is loaded, show it
			if self._loadingmenu != None:
				self._loadingmenu.show()
				loadwindow = self._loadingmenu.findChild(name="loadwindow")
				autoposition.placeWidget(loadwindow, 'automatic')
			
			# Load the map
			self._map = loadMapFile(filename, self._engine, self._loadLevelMapCallback)
			
		elif purpose == 'MENU':
			# Hide any active GUIs
			self._hideAllGuis()
			
			# Pump the engine to force it to move to a new frame
			self._engine.pump()
			
			# If the loading menu is loaded, show it
			if self._loadingmenu != None:
				self._loadingmenu.show()
				loadwindow = self._loadingmenu.findChild(name="loadwindow")
				autoposition.placeWidget(loadwindow, 'automatic')
				
			# Load the map
			self._map = loadMapFile(filename, self._engine, self._loadMenuMapCallback)
		
		# Start (or clear) the camera array
		self._cameras = {}
		
		# For each camera in the map
		for cam in self._map.getCameras():
			# Get the camera ID
			camera_id = cam.getId()
			# Add the camera with that ID to the array
			self._cameras[camera_id] = cam
			# Reset the camera
			cam.resetRenderers()
			
		# Start co-ordinate renderer
		renderer = self._cameras['main'].getRenderer('CoordinateRenderer')
		renderer.clearActiveLayers()
		renderer.addActiveLayer(self._map.getLayer("coords"))
			
		if self._mapsettings.get("map", "usewaypoints", False):
			self._waypoints = self._mapsettings._deserializeList(self._mapsettings.get("map", "waypoints", ""))
		else:
			self._waypoints = None
		
		if self._mapsettings.get("map", "dynamicnpcs", False):
			self._npclist = self._mapsettings._deserializeDict(self._mapsettings.get("map", "npclist", False))
			if self._npclist != False:
				for id, name in self._npclist.iteritems():
					self._npcs[name] = npc.NPC(self._setting, self._model, id, self._map.getLayer('player'), self, True, name)
		
			
	def _getLocationAt(self, clickpoint, layer):
		"""
		Query the main camera for the Map location (on the agent layer)
		that a screen point refers to.
		"""
		target_mapcoord = self._cameras['main'].toMapCoordinates(clickpoint, False)
		target_mapcoord.z = 0
		location = fife.Location(layer)
		location.setMapCoordinates(target_mapcoord)
		return location
			
	def mousePressed(self, evt):
		if evt.isConsumedByWidgets():
			return
		clickpoint = fife.ScreenPoint(evt.getX(), evt.getY())
		if (evt.getButton() == fife.MouseEvent.LEFT):
			self._player.run(self._getLocationAt(clickpoint, self._map.getLayer('player')))
			
	def _startPlayerActor(self):
		self._player = Player(self._setting, self._model, "actor-pc", self._map.getLayer('player'))
		self._cameras['main'].setLocation(self._player._agent.getLocation())
		self._cameras['main'].attach(self._map.getLayer('player').getInstance("actor-pc"))
		if self._cameras['main'].getAttached() == None:
			print "Attach Failed"
