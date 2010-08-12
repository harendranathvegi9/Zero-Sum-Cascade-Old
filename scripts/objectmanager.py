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

from fife.extensions.serializers.simplexml import SimpleXMLSerializer

class ObjectManager():
	def __init__(self, world):
		self._objects = {}
		self._objectmanifest = None
		self._world = world
		
	def _loadObjects(self, file):
		tmp = InteractiveObject(self, self._world._model, file)
		self._objects[tmp._agentName] = tmp

class InteractiveObject(fife.InstanceActionListener):
	def __init__(self, objectmanager, model, file):
		fife.InstanceActionListener.__init__(self)
		self._manager = objectmanager
		self._model = model
		self._objectFile = SimpleXMLSerializer(file)
		self._agentName = self._objectFile.get("object", "agentname", "dummy")
		self._layer = self._manager._world._map.getLayer(self._objectFile.get("object", "layer", "player"))
		self._agent = self._layer.getInstance(self._agentName)
		self._agent.addActionListener(self)
		self._status = self._objectFile.get("object", "status", 'INACTIVE')
		
		self._actions = { 'use' : self.use,
				  'destroy' : self.destroy,
				  'turnon' : self.activate,
				  'turnoff' : self.deactivate,
				  'explode' : self.explode,
				  'describe': self.describe,
				  'glitch' : self.glitch }
		self._availableactions = { 'use' : False,
					   'destroy' : False,
					   'turnon' : False,
					   'turnoff' : False,
					   'explode' : False,
					   'describe' : True,
					   'glitch' : False }
		
		actionstr = self._objectFile.get("object", "actions", None)
		actions = self._objectFile._deserializeDict(actionstr)
		for action, bool in actions.iteritems():
			print action + " = " + bool
			if bool in ("True"):
				self._availableactions[action] = True
			else:
				self._availableactions[action] = False
			print action + " = " + str(self._availableactions[action])
		self._description = self._objectFile.get("object", "description", "I can see something, but\n I can't tell what it is")
		self._talk = self._objectFile.get("object", "talk", False)
		self._message = self._objectFile._deserializeList(self._objectFile.get("object", "messages", ""))
		self._usesound = self._objectFile.get("object", "sound", False)
		if self._usesound:
			self._manager._world._sounds._loadclip(self._agentName, self._objectFile.get("object", "soundfile", ""), False, False)
			self._sound = self._manager._world._sounds._emitters[self._agentName]
		self._loadObject()
		self.onInstanceActionFinished(self._agent, "")
	
	def onInstanceActionFinished(self, instance, action):
		if self._status == 'ACTIVE':
			self._agent.act('on', self._agent.getFacingLocation())
		elif self._status == 'INACTIVE':
			self._agent.act('off', self._agent.getFacingLocation())
		elif self._status == 'DESTROYED':
			self._agent.act('dead', self._agent.getFacingLocation())
		elif self._status == 'GLITCHED':
			self._agent.act('glitch', self._agent.getFacingLocation())
	
	def use(self):
		if self._status == 'ACTIVE':
			self._agent.act('use', self._agent.getFacingLocation())
			self._manager._world._player._agent.setFacingLocation(self._agent.getLocation())
			if self._noactioncallbacks == 0:
				self._action()
			elif self._noactioncallbacks == 1:
				self._action(self._actioncallbacks[0])
			elif self._noactioncallbacks == 2:
				self._action(self._actioncallbacks[0], self._actioncallbacks[1])
			elif self._noactioncallbacks == 3:
				self._action(self._actioncallbacks[0], self._actioncallbacks[1], self._actioncallbacks[2])
			elif self._noactioncallbacks == 4:
				self._action(self._actioncallbacks[0], self._actioncallbacks[1], self._actioncallbacks[2], self._actioncallbacks[3])
			elif self._noactioncallbacks == 5:
				self._action(self._actioncallbacks[0], self._actioncallbacks[1], self._actioncallbacks[2], self._actioncallbacks[3], self._actioncallbacks[4])
			if self._talk:
				rand = random.randint(0, len(self._message) - 1)
				self._manager._world._player._agent.say(self._message[rand], 3500)
			if self._usesound:
				self._sound.play()

	def destroy(self):
		self._agent.act('die', self._agent.getFacingLoaction)
		self._status = 'DESTROYED'
	
	def activate(self):
		self._agent.act('turnon', self._agent.getFacingLoaction)
		self._status = 'ACTIVE'
	
	def deactivate(self):
		self._agent.act('turnoff', self._agent.getFacingLoaction)
		self._status = 'INACTIVE'
	
	def explode(self):
		self._agent.act('explode', self._agent.getFacingLoaction)
		self._status = 'DESTROYED'
	
	def describe(self):
		self._manager._world._player._agent.say(self._description, 5000)
	
	def glitch(self):
		self._agent.act('glitch', self._agent.getFacingLoaction)
		self._status = 'GLITCHED'
		
	def noAction(self):
		pass # This function exists purely to act as a void function
		     # for objects that make a pretty light
		
	def _loadObject(self):
		action = self._objectFile.get("object", "action", "none")
		if action == "none":
			self._action = self.noAction
			self._noactioncallbacks = 0
			self._actioncallbacks = {}
		elif action == "door":
			loc1 = fife.Location()
			loc1.setLayer(self._manager._world._map.getLayer('player'))
			loc1.setExactLayerCoordinates(fife.ExactModelCoordinate(self._file.get("event", "newx", 0), self._file.get("event", "newy", 0)))
			
			loc2 = fife.Location()
			loc2.setLayer(self._manager._world._map.getLayer('player'))
			loc2.setExactLayerCoordinates(fife.ExactModelCoordinate(self._file.get("event", "refx", 0), self._file.get("event", "refy", 0)))
			
			self._action = self._manager._world._loadMap
			self._noactioncallbacks = 5
			self._actioncallbakcs = { 0 : self._objectFile.get("object", "mapfile", "") ,
						  1 : 'LEVEL' ,
						  2 : True ,
						  3 : loc1 ,
						  4 : loc2 }
		elif action == "plot":
			self._action = self._manager._world._eventtracker._evaluateItem
			self._noactioncallbacks = 1
			self._actioncallbacks = { 0 : self._agentName }
		elif action == "book":
			pass # Needs GUI manager
		elif action == "computer":
			pass # Needs GUI manager
		elif action == "teleport":
			pass # Needs hooks in the player and NPC classes