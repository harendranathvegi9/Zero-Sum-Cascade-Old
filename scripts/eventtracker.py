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

# Tell the interpreter where to find the engine
fife_path = os.path.join('..','..','engine','python')
if os.path.isdir(fife_path) and fife_path not in sys.path:
	sys.path.insert(0,fife_path)
#root_dir = os.path.join('..','..')
#if os.path.isdir(root_dir) and root_dir not in sys.path:
#	sys.path.insert(0, root_dir)

# Import the engine
from fife import fife
from fife.extensions.serializers.simplexml import SimpleXMLSerializer
from musicmanager import ThreePartMusic

class Event():
	def __init__(self, eventfile, tracker):
		self._file = SimpleXMLSerializer(filename=eventfile)
		self._eventname = self._file.get("event", "name", len(tracker._events))
		self._status = 'INACTIVE'
		self._type = self._file.get("event", "type", "dummy")
		self._tracker = tracker
		
		if self._file.get("event", "active", False):
			self._status = 'ACTIVE'

		self._repeating = self._file.get("event", "repeating", False)
		
		self._activates = self._file.get("event", "activates", "none")
		
		if self._type == "dummy":
			pass
			self._status = 'FULFILLED'
		if self._type == "trip":
			self._target = self._file.get("event", "target", None)
			self._x = self._file.get("event", "x", 0)
			self._y = self._file.get("event", "y", 0)
		if self._type == "areatrip":
			self._target = self._file.get("event", "target", None)
			self._xmin = self._file.get("event", "xmin", 0)
			self._xmax = self._file.get("event", "xmax", 0)
			self._ymin = self._file.get("event", "ymin", 0)
			self._ymax = self._file.get("event", "ymax", 0)
		if self._type == "item":
			self._item = self._file.get("event", "item", None)
		if self._type == "dialogue":
			self._dialogue = self._file.get("event", "dialogue")
		if self._type == "plot":
			self._subtype = self._file.get("event", "subtype", "dummy")
			if self._subtype == "dummy":
				pass
				self._status = 'FULFILLED'
			if self._subtype == "trip":
				self._target = self._file.get("event", "target", None)
				self._x = self._file.get("event", "x", 0)
				self._y = self._file.get("event", "y", 0)
			if self._subtype == "areatrip":
				self._target = self._file.get("event", "target", None)
				self._xmin = self._file.get("event", "xmin", 0)
				self._xmax = self._file.get("event", "xmax", 0)
				self._ymin = self._file.get("event", "ymin", 0)
				self._ymax = self._file.get("event", "ymax", 0)
			if self._subtype == "item":
				self._item = self._file.get("event", "item", None)
			if self._subtype == "dialogue":
				self._dialogue = self._file.get("event", "dialogue")
		
		action = self._file.get("event", "action", "none")
		if action == "eventmusic":
			self._tracker._eventmusic[self._eventname] = ThreePartMusic(self._file.get("event", "musicintro", ""), self._file.get("event", "musicloop", ""), self._file.get("event", "musicend", ""), True, tracker._musicmanager._soundmanager)
			self._action = self._tracker._eventmusic(self._eventname)._play
			self._noactioncallbacks = 0
			self._actioncallbacks = {}
		elif action == "playsound":
			self._action = self._tracker._musicmanager._startClip
			self._noactioncallbacks = 1
			self._actioncallbacks = {0: self._file.get("event", "clip", "default")}
		elif action == "stopsound":
			self._action = self._tracker._musicmanager._startClip
			self._noactioncallbacks = 1
			self._actioncallbacks = {0: self._file.get("event", "clip", "default")}
		elif action == "swapmap":
			self._action = self._tracker._world._loadMap
			self._noactioncallbacks = 2
			self._actioncallbacks = {0: self._file.get("event", "newmap", ""),
						 1: 'LEVEL'}
		elif action == "movenpc":
			self._action = self._tracker._world._npcs[self._file.get("event", "npc", "")].run
			location = fife.Location()
			location.setLayer(tracker._world._map.getLayer('player'))
			location.setExactLayerCoordinates(fife.ExactModelCoordinate(self._file.get("event", "newx", 0), self._file.get("event", "newy", 0)))
			self._actioncallbacks = {0: location}
		elif action == "moveplayer":
			self._action = self._tracker._world._player.run
			location = fife.Location()
			location.setLayer(tracker._world._map.getLayer('player'))
			location.setExactLayerCoordinates(fife.ExactModelCoordinate(self._file.get("event", "newx", 0), self._file.get("event", "newy", 0)))
			self._actioncallbacks = {0: location}
		elif action == "npcaction":
			reaction = self._file.get("event", "clip", "default")
			if self._tracker._world._npcs[self._file.get("event", "npc", "")]._availableActions[reaction]:
				self._action = self._tracker._world._npcs[self._file.get("event", "npc", "")]._action[reaction]
				self._noactioncallbacks = 0
		elif action == "playeraction":
			reaction = self._file.get("event", "clip", "default")
			if self._tracker._world._player._availableActions[reaction]:
				self._action = self._tracker._world._player._action[reaction]
				self._noactioncallbacks = 0
		elif action == "portnpc":
			self._action = self._tracker._world._npcs[self._file.get("event", "npc", "")]._agent.setLocation
			location = fife.Location()
			location.setLayer(tracker._world._map.getLayer('player'))
			location.setExactLayerCoordinates(fife.ExactModelCoordinate(self._file.get("event", "newx", 0), self._file.get("event", "newy", 0)))
			self._actioncallbacks = {0: location}
		elif action == "portplayer":
			self._action = self._tracker._world._player._agent.setLocation
			self._noactioncallbacks = 1
			location = fife.Location()
			location.setLayer(tracker._world._map.getLayer('player'))
			location.setExactLayerCoordinates(fife.ExactModelCoordinate(self._file.get("event", "newx", 0), self._file.get("event", "newy", 0)))
			self._actioncallbacks = {0: location}
		
	def _evaluate(self, item=None):
		if self._target == "player":
			loc = self._tracker._world._player._agent.getLocation().getExactLayerCoordinates()
		else:
			loc = self._tracker._world._npcs[self._target]._agent.getLocation().getExactLayerCoordinates()
		if self._type == "plot":
			type = self._subtype
			plot = True
		else:
			type = self._type
			plot = False
		if type == "trip":
			if int(loc.x) == self._x and int(loc.y) == self._y:
				if self._noactioncallbacks == 0:
					self._action()
				elif self._noactioncallbacks == 1:
					self._action(self._actioncallbacks[0])
				elif self._noactioncallbacks == 2:
					self._action(self._actioncallbacks[0], self._actioncallbacks[1])
				elif self._noactioncallbacks == 3:
					self._action(self._actioncallbacks[0], self._actioncallbacks[1], self._actioncallbacks[2])
				if self._repeating:
					self._status = 'ACTIVE'
				else:
					self._status = 'FULFILLED'
				if self._activates != "none":
					self._tracker._events[self._activates]._status = 'ACTIVE'
		elif type == "areatrip":
			if loc.x >= self._xmin and loc.x <= self._xmax and loc.y >= self._ymin and loc.y <= self._ymax:
				if self._noactioncallbacks == 0:
					self._action()
				elif self._noactioncallbacks == 1:
					self._action(self._actioncallbacks[0])
				elif self._noactioncallbacks == 2:
					self._action(self._actioncallbacks[0], self._actioncallbacks[1])
				elif self._noactioncallbacks == 3:
					self._action(self._actioncallbacks[0], self._actioncallbacks[1], self._actioncallbacks[2])
				if self._repeating:
					self._status = 'ACTIVE'
				else:
					self._status = 'FULFILLED'
				if self._activates != "none":
					self._tracker._events[self._activates]._status = 'ACTIVE'
		elif type == "item":
			if item != None and item == self._item:
				if self._noactioncallbacks == 0:
					self._action()
				elif self._noactioncallbacks == 1:
					self._action(self._actioncallbacks[0])
				elif self._noactioncallbacks == 2:
					self._action(self._actioncallbacks[0], self._actioncallbacks[1])
				elif self._noactioncallbacks == 3:
					self._action(self._actioncallbacks[0], self._actioncallbacks[1], self._actioncallbacks[2])
				if self._repeating:
					self._status = 'ACTIVE'
				else:
					self._status = 'FULFILLED'
				if self._activates != "none":
					self._tracker._events[self._activates]._status = 'ACTIVE'
		elif type == "dialogue":
			if self._dialogue in self._tracker._world._player._plots:	
				if self._noactioncallbacks == 0:
					self._action()
				elif self._noactioncallbacks == 1:
					self._action(self._actioncallbacks[0])
				elif self._noactioncallbacks == 2:
					self._action(self._actioncallbacks[0], self._actioncallbacks[1])
				elif self._noactioncallbacks == 3:
					self._action(self._actioncallbacks[0], self._actioncallbacks[1], self._actioncallbacks[2])
				if self._repeating:
					self._status = 'ACTIVE'
				else:
					self._status = 'FULFILLED'
				if self._activates != "none":
					self._tracker._events[self._activates]._status = 'ACTIVE'


class EventTracker():
	def __init__(self, engine, model, musicmanager, world):
		self._events = {}
		self._engine = engine
		self._model = model
		self._musicmanager = musicmanager
		self._world = world
		self._eventmusic = {}
	
	def _addEvent(self, eventfile):
		temp = Event(eventfile, self)
		self._events[temp._eventname] = temp
	
	def _deleteEvent(self, event):
		del self._events[event]
		
	def _evaluateEvents(self, all=False):
		for name, event in self._events.iteritems():
			if event._status == 'ACTIVE' or all:
				event._evaluate()
	
				
	def _evaluateEvent(self, event, item=None):
		if self._events[event]._status == 'ACTIVE':
			self._events[event]._evaluate(item)