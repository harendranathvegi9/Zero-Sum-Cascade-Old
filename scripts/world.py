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
from scripts import musicmanager, npc, eventtracker, objectmanager, contextmenu
from scripts import hudhandler, menuhandler, settingshandler, abouthandler
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
		self._gamestate = 'NONE'
		self._quit = False
		self._player = None
		self._eventtracker = None
		self._objects = {}
		self._contextmenu = contextmenu.ContextMenu('rightclickmenu', self)
		self._mouseMoved = False
		
		# Start pychan
		pychan.init(self._engine)
		
		# Set all GUI types to empty
		self._hud = None
		self._mainmenu = None
		self._pausemenu = None
		self._loadingmenu = None
		self._settingsmenu = None
		self._aboutmenu = None
		
		# Start the sound manager
		self._soundmanager = SoundManager(self._engine)
		self._sounds = musicmanager.MusicManager(self._engine, self._soundmanager, self._timemanager)
		
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
			self._mainmenu = menuhandler.MenuHandler(guifile, self)
		elif type == 'HUD':
			self._hud = hudhandler.HUDHandler(guifile, self)
		elif type == 'SETTINGS':
			self._settingsmenu = settingshandler.SettingsHandler(guifile, self)
		elif type == 'ABOUT':
			self._aboutmenu = abouthandler.AboutHandler(guifile, self)
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
		if self._settingsmenu != None:
			self._settingsmenu.hide()
		if self._aboutmenu != None:
			self._aboutmenu.hide()

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
			self._hideAllGuis()
		# Otherwise set the loading screens percentage label
		else:
			loaded = self._loadingmenu.findChild(name="loading")
			loaded.text = str(math.floor(percentdone * 100)) + u'% Loaded'			
	
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
			self._hideAllGuis()
			if self._mainmenu != None:
				self._mainmenu.show()
		# Otherwise set the loading screens percentage label
		else:
			loaded = self._loadingmenu.findChild(name="loading")
			loaded.text = str(math.floor(percentdone * 100)) + u'% Loaded'

	def _loadMap(self, filename, purpose, port=False, location=None, direction=None):
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
		self._eventtracker = None
		
		
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
			
		if purpose == 'LEVEL':
			# Start the player character
			self._startPlayerActor()
			if location != None:
				self._player._agent.setLocation(location)
			if direction != None:
				self._player._agent.setFacingLocation(direction)
			if self._hud != None:
				self._hud.show()
			
			self._loadLevelMapCallback("", 0.775)
		
		# Start the floating text renderer
		renderer = fife.FloatingTextRenderer.getInstance(self._cameras['main'])
		textfont = self._engine.getGuiManager().createFont('fonts/rpgfont.png', 0, str(self._setting.get("FIFE", "FontGlyphs")))
		renderer.changeDefaultFont(textfont)
		renderer.setDefaultBackground(0,0,0,0)
		renderer.setDefaultBorder(0,0,0,0)
		renderer.activateAllLayers(self._map)
		renderer.setEnabled(True)
		
		if purpose == 'LEVEL':
			self._loadLevelMapCallback("", 0.8)
		else:
			self._loadMenuMapCallback("", 0.8)
	
		if self._mapsettings.get("map", "usewaypoints", False):
			self._waypoints = self._mapsettings._deserializeList(self._mapsettings.get("map", "waypoints", ""))
		else:
			self._waypoints = None

		if purpose == 'LEVEL':
			self._loadLevelMapCallback("", 0.825)
		else:
			self._loadMenuMapCallback("", 0.825)
		
		if self._mapsettings.get("map", "useobjects", False):
			self._objects = objectmanager.ObjectManager(self)
			objlist = self._mapsettings._deserializeList(self._mapsettings.get("map", "objectlist", False))
			for file in objlist:
				self._objects._loadObjects(file)
		
		if purpose == 'LEVEL':
			self._loadLevelMapCallback("", 0.85)
		else:
			self._loadMenuMapCallback("", 0.85)
		
		if self._mapsettings.get("map", "dynamicnpcs", False):
			self._npclist = self._mapsettings._deserializeDict(self._mapsettings.get("map", "npclist", False))
			if self._npclist != False:
				for id, name in self._npclist.iteritems():
					self._npcs[name] = npc.NPC(self._setting, self._model, id, self._map.getLayer('player'), self, True, name)
		
		if purpose == 'LEVEL':
			self._loadLevelMapCallback("", 0.9)
		else:
			self._loadMenuMapCallback("", 0.9)
		
		self._eventtracker = eventtracker.EventTracker(self._engine, self._model, self._sounds, self)
		if self._mapsettings.get("map", "useevents", False):
			eventlist = self._mapsettings._deserializeList(self._mapsettings.get("map", "eventslist", ""))
			for file in eventlist:
				self._eventtracker._addEvent(file)
				
		if purpose == 'LEVEL':
			self._loadLevelMapCallback("", 0.95)
		else:
			self._loadMenuMapCallback("", 0.95)
			
		self._drift = {}
		self._drift = self._mapsettings._deserializeDict(self._mapsettings.get("map", "drift", "use : False"))
		if self._drift["use"] == "True":
			self._drift["use"] = True
			self._drift["x"] = float(self._drift["x"])
			self._drift["y"] = float(self._drift["y"])

			start = self._drift["start"].partition(",")
			loc = fife.Location(self._map.getLayer('player'))
			loc.setExactLayerCoordinates(fife.ExactModelCoordinate(float(start[0]), float(start[2])))
			self._cameras['main'].setLocation(loc)
		else:
			self._drift["use"] = False
		
		self._gamestate = purpose
			
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
	
	def _getInstancesAt(self, clickpoint, layer):
		"""
		Query the main camera for instances on a given layer.
		"""
		return self._cameras['main'].getMatchingInstances(clickpoint, layer)
			
	def mousePressed(self, evt):
		if evt.isConsumedByWidgets() or self._gamestate != 'LEVEL':
			return
		clickpoint = fife.ScreenPoint(evt.getX(), evt.getY())
		playerinstance = self._getInstancesAt(clickpoint, self._map.getLayer('player'))
		playerinstance = playerinstance + self._getInstancesAt(clickpoint, self._map.getLayer('waypoints'))
		if (evt.getButton() == fife.MouseEvent.LEFT):
			self._player.run(self._getLocationAt(clickpoint, self._map.getLayer('player')))
			self._contextmenu._hide()
		elif (evt.getButton() == fife.MouseEvent.RIGHT):
			self._contextmenu._show(playerinstance, clickpoint, self)
		evt.consume()
			
	def mouseMoved(self, evt, ext=False, cursor=None):
		self._mouseMoved = True
		if self._map == None or self._gamestate != 'LEVEL':
			return
		
		renderer = fife.InstanceRenderer.getInstance(self._cameras['main'])
		renderer.removeAllOutlines()
	
		if ext:
			pt = fife.ScreenPoint(cursor.getX(), cursor.getY())
		else:
			pt = fife.ScreenPoint(evt.getX(), evt.getY())
		instances = self._getInstancesAt(pt, self._map.getLayer('player'))
		instances = instances + self._getInstancesAt(pt, self._map.getLayer('waypoints'))
		for i in instances:
			for name, object in self._objects._objects.iteritems():
				if i.getId() == name:
					renderer.addOutlined(i, random.randint(20,255), random.randint(20,255), random.randint(20,255), 1)
			for name, object in self._npcs.iteritems():
				if i.getId() == object._agentName:
					renderer.addOutlined(i, random.randint(20,255), random.randint(20,255), random.randint(20,255), 1)

	def _keyPressed(self, evt):
		keyval = evt.getKey().getValue()
		keystr = evt.getKey().getAsString().lower()
		#if keyval = 

	def _startPlayerActor(self):
		self._player = Player(self._setting, self._model, "actor-pc", self._map.getLayer('player'))
		self._cameras['main'].setLocation(self._player._agent.getLocation())
		self._cameras['main'].attach(self._map.getLayer('player').getInstance("actor-pc"))
		if self._cameras['main'].getAttached() == None:
			print "Attach Failed"
	
	def cameraDrift(self):
		if self._drift["use"]:
			oldloc = self._cameras['main'].getLocation().getExactLayerCoordinates()
			border = self._drift["end"].partition(",")
			if oldloc.x < float(border[0]):
				self._drift["x"] = (self._drift["x"] + random.randint(-1, 1) * 0.025) * -1
				print str(self._drift["x"]) + "," + str(self._drift["y"])
			if oldloc.y < float(border[2]):
				self._drift["y"] = (self._drift["y"] + random.randint(-1, 1) * 0.025) * -1
				print str(self._drift["x"]) + "," + str(self._drift["y"])
			border2 = self._drift["start"].partition(",")
			if oldloc.x > float(border2[0]):
				self._drift["x"] = (self._drift["x"] + random.randint(-1, 1) * 0.025) * -1
				print str(self._drift["x"]) + "," + str(self._drift["y"])
			if oldloc.y > float(border2[2]):
				self._drift["y"] = (self._drift["y"] + random.randint(-1, 1) * 0.025) * -1
				print str(self._drift["x"]) + "," + str(self._drift["y"])
			delta = self._timemanager.getTimeDelta() / 100.0
			loc = fife.Location(self._map.getLayer('player'))
			deltax = round(oldloc.x + self._drift["x"] * delta, 2)
			deltay = round(oldloc.y + self._drift["y"] * delta, 2)
			loc.setExactLayerCoordinates(fife.ExactModelCoordinate(deltax, deltay))
			self._cameras['main'].setLocation(loc)
