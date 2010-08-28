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

class ContextMenu():
	def __init__(self, guifile, world):
		self._menu = pychan.loadXML('gui/' + guifile + '.xml')
		self._dynamicbuttons = {}
		self._world = world
		dynamicbuttons = ( 'moveButton',
				   'talkButton',
				   'useButton',
				   'inspectButton',
				   'shootButton',
				   'turnOnButton',
				   'turnOffButton',
				   'followButton' )
		self._menu.mapEvents({ 'moveButton' : self._move ,
				       'talkButton' : self._talk ,
				       'useButton' : self._use ,
				       'inspectButton' : self._inspect ,
				       'shootButton' : self._shoot ,
				       'turnOnButton' : self._turnon ,
				       'turnOffButton' : self._turnoff,
				       'followButton' : self._follow })
		for button in dynamicbuttons:
			self._dynamicbuttons[button] = self._menu.findChild(name=button)
		self._menu.removeAllChildren() # This one line of code is the sole reason there are no children in the game
		self._currentObject = None
		self._currentType = None
	
	def _hide(self):
		self._menu.hide()
		self._menu.real_widget.setEnabled(False)
	
	def _show(self, instance, clickpoint, world):
		self._hide()
		self._menu.real_widget.setEnabled(True)
		self._menu.removeAllChildren() # This one line of code is the sole reason there are no children in the game
		
		self._world = world
		
		location = world._getLocationAt(clickpoint, world._map.getLayer('player'))
		target_distance = world._player._agent.getLocationRef().getLayerDistanceTo(location)
		
		self._clickpoint = clickpoint
		self._location = location
		if instance != ():
			instance = instance[0]
			
			for name, object in world._objects._objects.iteritems():
				if instance.getId() == name:
					self._currentObject = world._objects._objects[name]
					self._currentType = 'OBJECT'
					self._menu.addChild(self._dynamicbuttons['followButton'])
					for action, bool in object._availableactions.iteritems():
						if action == "use" and bool and (self._currentObject._status == "ACTIVE" or self._currentObject._status == "DOOR") and target_distance <= 3:
							self._menu.addChild(self._dynamicbuttons['useButton'])
						elif action == "activate" and bool and self._currentObject._status == "INACTIVE" and target_distance <= 2:
							self._menu.addChild(self._dynamicbuttons['turnOnButton'])
						elif action == "deactivate" and bool and self._currentObject._status == "ACTIVE" and target_distance <= 2:
							self._menu.addChild(self._dynamicbuttons['turnOffButton'])
						elif action == "describe" and bool and target_distance <= 15:
							self._menu.addChild(self._dynamicbuttons['inspectButton'])
			for name, object in world._npcs.iteritems():
				if instance.getId() == object._agentName:
					self._menu.addChild(self._dynamicbuttons['moveButton'])
					self._currentObject = world._npcs[name]
					self._currentType = 'NPC'
					self._menu.addChild(self._dynamicbuttons['followButton'])
					for action, bool in object._availableActions.iteritems():
						if action == "talk" and bool and target_distance <= 3:
							self._menu.addChild(self._dynamicbuttons['talkButton'])
						elif action == "describe" and bool and target_distance <= 15:
							self._menu.addChild(self._dynamicbuttons['inspectButton'])
						elif action == "beshot" and bool and (world._player._hasGun or world._player._hasPistol)  and target_distance <= 10:
							self._menu.addChild(self._dynamicbuttons['shootButton'])
					if object._hasdialogue:
						topics = object._listAvailableTopics()
						print topics
						for index, topic in topics:
							button = widgets.buttons.Button()
							button.name = topic + "Button"
							button.text = u"Talk - " + topic
							self._menu.addChild(button)
							self._menu.mapEvents({ button.name : pychan.tools.callbackWithArguments(self._talk, index) })
		else:
			self._menu.addChild(self._dynamicbuttons['moveButton'])
		self._menu.position = (clickpoint.x, clickpoint.y)
		self._menu.show()

	def _move(self):
		self._hide()
		self._world._player.run(self._location)
	
	def _shoot(self):
		pass
	
	def _talk(self, index):
		self._hide()
		self._currentObject._talk(index)
	
	def _use(self):
		self._hide()
		self._currentObject.use()
	
	def _inspect(self):
		self._hide()
		self._currentObject.describe()
	
	def _turnon(self):
		pass
	
	def _turnoff(self):
		pass
	
	def _follow(self):
		self._hide()
		self._world._player._agent.follow('walk', self._currentObject._agent, 0.75)