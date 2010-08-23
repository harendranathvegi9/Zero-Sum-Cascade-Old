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

from scripts.agentbase import Agent

_STATE_NONE, _STATE_IDLE, _STATE_RUN, _STATE_ACTION, _STATE_TALK = xrange(5)

class NPC(Agent):
	def __init__(self, settings, model, agentName, layer, world, uniqInMap=True, name=""):
		super(NPC, self).__init__(settings, model, agentName, layer, uniqInMap)
		self._state = _STATE_NONE
		self._name = name
		self._agentName = agentName
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
					   'glitch': False,
					   'describe' : True}
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
				 'glitch': self.glitch,
				 'decribe' : self.describe }
		self._world = world
		self._loadNPC(self._name)
		
	def _loadNPC(self, name):
		self._npcFile = SimpleXMLSerializer(filename="npcs/" + name + ".xml")
		actionstr = self._npcFile.get("npc", "actions", None)
		actions = self._npcFile._deserializeDict(actionstr)
		for action, bool in actions.iteritems():
			if bool == "True":
				self._availableActions[action] = True
			else:
				self._availableActions[action] = False
		self._actionchance = self._npcFile.get("npc", "actionchance", 0)
		self._description = self._npcFile.get("npc", "description", "I can see a mysterious figure,\n but I can't quite make them out.")
		self._autowalk = self._npcFile.get("npc", "autowalk", True)
		self._hasdialogue = self._npcFile.get("npc", "hasdialogue", False)
		self._autowalk = self._npcFile.get("npc", "autowalk", True)
		self._loadDialogue()
		self._idle()
	
	def _loadDialogue(self):
		if not self._hasdialogue:
			return
		self._dialogue = {}
		self._idledialogue = []
		index = []
		index = self._npcFile._deserializeList(self._npcFile.get("dialogue", "index", ""))
		for line in index:
			self._dialogue[line] = self._npcFile._deserializeDict(self._npcFile.get("dialogue", line, ""))
		idleindex = self._npcFile._deserializeList(self._npcFile.get("dialogue", "idleindex", ""))
		for line in idleindex:
			self._idledialogue.append(self._dialogue[line])
	
	def _listAvailableTopics(self):
		returninglist = []
		if not self._hasdialogue:
			return returninglist
		for index, dialogue in self._dialogue.iteritems():
			if dialogue["requires"] in self._world._player._plots or dialogue["requires"] == '0' and dialogue not in self._idledialogue:
				returninglist.append((index, dialogue["topic"]))
		return returninglist
	
	def _talk(self, index):
		if self._world._gamestate == 'LEVEL' and index not in self._world._player._plots:
			self._world._player._plots.append(index)
		self._agent.say(self._dialogue[index]["text"], 5000)
	
	def onInstanceActionFinished(self, instance, action):
		self._idle()
		
	def _idle(self):
		self._state = _STATE_IDLE
		if self._autowalk:
			chance = random.randint(0,100)
			if chance < self._actionchance:
				self._waypointmove()
			else:
				self._agent.act('walk', self._agent.getFacingLocation())
			chance = random.randint(0,100)
			if chance < self._actionchance / 2 and self._hasdialogue:
				self.talk()
		
	def _waypointmove(self):
		no = random.randint(0, len(self._world._waypoints) - 1)
		point = self._world._waypoints[no]
		x, point, y = point.partition(',')
		location = fife.Location()
		location.setLayer(self._layer)
		location.setExactLayerCoordinates(fife.ExactModelCoordinate(int(x) + random.randint(-1,1), int(y) + random.randint(-1,1)))
		self.run(location)
		
	def run(self, location):
		self._state = _STATE_RUN
		self._agent.move('walk', location, 0.75)
		
	def walk(self):
		pass
		
	def talk(self):
		chance = random.randint(0, len(self._idledialogue) - 1)
		self._talk(self._idledialogue[chance]["index"])
	
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

	def describe(self):
		self._world._player._agent.say(self._description, 5000)