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
		self._objectmanifest = SimpleXMLSerializer(file)
		objstr = self._objectfile.get("object", "actions", None)
		obj = self._objectfile._deserializeList(objstr)
		for object in obj.iteritems():
			tmp = InteractiveObject(self, self._world._model, 'objects/' + object)
			self._objects[tmp._agentName] = tmp

class InteractiveObject(fife.InstanceActionListener):
	def __init__(self, objectmanager, model, file):
		fife.InstanceActionListener.__init__(self)
		self._manager = objectmanager
		self._model = model
		self._objectFile = SimpleXMLSerializer(file)
		self._agentName = self._objectFile.get("object", "agentname", "dummy")
		self._layer = self._manager._world._map._getLayer(self._objectFile.get("object", "layer", "player"))
		self._agent = layer.getInstance(agentName)
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
		
		actionstr = self._objectfile.get("object", "actions", None)
		actions = self._objectfile._deserializeDict(actionstr)
		for action, bool in actions.iteritems():
			self._availableactions[action] = bool
	
	def onInstanceActionFinished(self, instance, action):
		if self._status == 'ON':
			self._agent.act('on', self._agent.getFacingLoaction)
		elif self._status == 'OFF':
			self._agent.act('off', self._agent.getFacingLoaction)
		elif self._status == 'DESTROYED':
			self._agent.act('dead', self._agent.getFacingLoaction)
		elif self._status == 'GLITCHED':
			self._agent.act('glitch', self._agent.getFacingLoaction)
	
	def use(self):
		if self._status == 'ON':
			self._agent.act('on', self._agent.getFacingLoaction)

	def destroy(self):
		self._agent.act('die', self._agent.getFacingLoaction)
		self._status = 'DESTROYED'
	
	def activate(self):
		self._agent.act('turnon', self._agent.getFacingLoaction)
		self._status = 'ON'
	
	def deactivate(self):
		self._agent.act('turnoff', self._agent.getFacingLoaction)
		self._status = 'OFF'
	
	def explode(self):
		self._agent.act('explode', self._agent.getFacingLoaction)
		self._status = 'DESTROYED'
	
	def describe(self):
		pass # Will pass description to the HUD
	
	def glitch(self):
		self._agent.act('glitch', self._agent.getFacingLoaction)
		self._status = 'GLITCHED'