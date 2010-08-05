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

from scripts.agentbase import Agent

_STATE_NONE, _STATE_IDLE, _STATE_RUN, _STATE_ACTION, _STATE_TALK = xrange(5)

class NPC(Agent):
	def __init__(self, settings, model, agentName, layer, map, uniqInMap=True, name=""):
		super(NPC, self).__init__(settings, model, agentName, layer, uniqInMap)
		self._state = _STATE_NONE
		self._name = name
		self._layer = layer
		self._availableActions = { 'walk': False,
					   'run': False,
					   'talk': False,
					   'die': False,
					   'explode': False,
					   'holdgun': False,
					   'firegun': False,
					   'beshot': False,
					   'walkgun': False,
					   'rungun': False,
					   'diegun': False,
					   'beshotgun': False,
					   'holdpistol': False,
					   'aimpistolleft': False,
					   'aimpistolright': False,
					   'firepistolleft': False,
					   'firepistolright': False,
					   'walkpistol': False,
					   'runpistol': False,
					   'diepistol': False,
					   'beshotpistol': False,
					   'teleportstart': False,
					   'teleportend': False,
					   'glitch': False }
		self._action = { 'walk': self.walk,
				 'run': self.run,
				 'talk': self.talk,
				 'die': self.die,
				 'explode': self.explode,
				 'holdgun': self._idle,
				 'firegun': self.fire,
				 'beshot': self.beshot,
				 'walkgun': self.walk,
				 'rungun': self.run,
				 'diegun': self.die,
				 'beshotgun': self.beshot,
				 'holdpistol': self._idle,
				 'aimpistolleft': self.aimleft,
				 'aimpistolright': self.aimright,
				 'firepistolleft': self.fireleft,
				 'firepistolright': self.fireright,
				 'walkpistol': self.walk,
				 'runpistol': self.run,
				 'diepistol': self.die,
				 'beshotpistol': self.beshot,
				 'teleportstart': self.teleportstart,
				 'teleportend': self.teleportend,
				 'glitch': self.glitch }
		self._map = map
		self._loadNPC(self._name)
		
	def _loadNPC(self, name):
		self._npcFile = SimpleXMLSerializer(filename="npcs/" + name + ".xml")
		actionstr = self._npcFile.get("npc", "actions", None)
		actions = self._npcFile._deserializeDict(actionstr)
		print actions
		for action, bool in actions.iteritems():
			self._availableActions[action] = bool
		self._actionchance = self._npcFile.get("npc", "actionchance", 0)
		self._idle()
			
	def onInstanceActionFinished(self, instance, action):
		self._idle()
		
	def _idle(self):
		self._state = _STATE_IDLE
		self._waypointmove()
		
	def _waypointmove(self):
		no = random.randint(0, len(self._map._waypoints) - 1)
		point = self._map._waypoints[no]
		x, point, y = point.partition(',')
		location = fife.Location()
		location.setLayer(self._layer)
		location.setExactLayerCoordinates(fife.ExactModelCoordinate(x + random.randint(-1,1), y + random.randint(-1,1)))
		self.run(location)
		
	def run(self, location):
		self._state = _STATE_RUN
		print self._name + " is running"
		self._agent.move('walk', location, 1)
		
	def walk(self):
		pass
		
	def talk(self):
		pass
	
	def die(self):
		pass
	
	def explode(self):
		pass
	
	def beshot(self):
		pass
	
	def aimleft(self):
		pass
	
	def aimright(self):
		pass
	
	def fire(self):
		pass
	
	def fireleft(self):
		pass
	
	def fireright(self):
		pass
	
	def teleportstart(self):
		pass
	
	def teleportend(self):
		pass
	
	def glitch(self):
		pass
