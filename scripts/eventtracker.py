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

class Event(self):
	def __init__(self, eventfile, tracker):
		self._file = SimpleXMLSerializer(filename=eventfile)
		self._eventname = self._file.get("event", "name", len(tracker._events))
		self._status = 'INACTIVE'
		self._type = self._file.get("event", "type", "dummy")
		
		if self._type == "dummy":
			pass
			self._status = 'FULFILLED'
		if self._type == "trip":
			self._target = self._file.get("event", "target", None)
			self._location = fife.Location('player')
			self._location.setMapCoordinates(fife.ModelCoodinate(self._file.get("event", "x", 0),self._file.get("event", "y", 0), 0))
		if self._type == "areatrip":
			self._target = self._file.get("event", "target", None)
			self._xmin = self._file.get("event", "xmin", 0)
			self._xmax = self._file.get("event", "xmax", 0)
			self._ymin = self._file.get("event", "ymin", 0)
			self._ymax = self._file.get("event", "ymax", 0)
		if self._type == "door":
			self._target = self._file.get("event", "target", None)
			self._location = fife.Location('player')
			self._location.setMapCoordinates(fife.ModelCoodinate(self._file.get("event", "x", 0),self._file.get("event", "y", 0), 0))
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
		
		self._action = self._file.get("event", "action", _eventfufilled)

class EventTracker(self):
	def __init__(self, engine, model, musicmanager):
		self._events = {}
		self._engine = engine
		self._model = model
		self._musicmanager = musicmanager
		self._eventmusic = {}
	
	def _addEvent(self, eventfile):
		temp = Event(eventfile, self)
		self._events[temp._eventname] = temp
	
	def _deleteEvent(self, event):
		del self._events[event]