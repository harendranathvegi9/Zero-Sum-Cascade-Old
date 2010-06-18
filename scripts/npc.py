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
from scripts.agentbase import Agent

_STATE_NONE, _STATE_IDLE, _STATE_RUN, _STATE_ACTION, _STATE_TALK = xrange(5)

class NPC(Agent):
	def __init__(self, settings, model, agentName, layer, uniqInMap=True, exists=False, location=None):
		if exists:
			super(Player, self).__init__(settings, model, agentName, layer, uniqInMap)
		else:
			super(Player, self).__init__(settings, model, agentName, layer)
			self._fifeobject = self._model.getObject(agentName, "ZSC:DyanamicAgentModels")
			self._agent = self._layer.createInstance(self._fifeobject, location, agentName)
			fife.InstanceVisual.create(self._agent)
			self._agent.thisown = 0
		self._state = _STATE_NONE