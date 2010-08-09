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

# ####################################################################
# This file may contain code taken from the FIFE Library
# Code taken from FIFE (c) 2005-2010 the FIFE team
# ####################################################################

import sys, os, re, math, random

# Import the engine
from fife import fife

class Agent(fife.InstanceActionListener):
	def __init__(self, settings, model, agentName, layer, uniqInMap=True):
		fife.InstanceActionListener.__init__(self)
		self._settings = settings
		self._model = model
		self._agentName = agentName
		self._layer = layer
		if uniqInMap:
			self._agent = layer.getInstance(agentName)
			self._agent.addActionListener(self)
			
	def onInstanceActionFinished(self, instance, action):
		pass

	def start(self):
		pass