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

# Tell the interpreter where to find the engine
fife_path = os.path.join('..','..','engine','python')
if os.path.isdir(fife_path) and fife_path not in sys.path:
	sys.path.insert(0,fife_path)

# Import the engine
from fife import fife

# Import misc. libraries

# Import FIFE libraries
#from fife.extensions.soundmanager import SoundManager

class MusicManager():
	def __init__(self, engine, soundmanager):
		self._soundmanager = soundmanager
		
		self._emitters = {}
		
	def _setAmbient(self, file, play):
		self._emitters['ambient'] = self._soundmanager.createSoundEmitter(file)
		self._emitters['ambient']._setLooping(True)
		if play:
			self._emitters['ambient'].play()
			
	def _setMusic(self, file, play):
		self._emitters['music'] = self._soundmanager.createSoundEmitter(file)
		self._emitters['ambient']._setLooping(True)
		if play:
			self._emitters['music'].play()
		
	def _startClip(self, clip):
		if self._emitters[clip] != None:
			self._emitters[clip].play()
	
	def _stopClip(self, clip):
		if self._emitters[clip] != None:
			self._emitters[clip].stop()
		
	def _stopAllClips(self):
		for sound in self._emitters:
			self._stopClip(sound)

	def _loadClip(self, clip, file, looping, play):
		self._emitters[clip] = self._soundmanager.createSoundEmitter(file)
		self._emitters[clip]._setLooping(looping)
		if play:
			self._emitters[clip].play()
	
class ThreePartMusic():
	def __init__(self, intro, loop, end, load, soundmanager):
		self._soundmanager = soundmanager
		if load:
			self._intro = self._soundmanager.createSoundEmitter(intro)
			self._intro._setCallback(startLoop)
			self._loop = self._soundmanager.createSoundEmitter(loop)
			self._loop._setLooping(True)
			self._end = self._soundmanager.createSoundEmitter(end)
			self._intro._setCallback(_fullStop)
		else:
			self._intro = intro
			self._intro._setCallback(_startLoop)
			self._loop = loop
			self._loop._setLooping(True)
			self._end = end
			self._intro._setCallback(_fullStop)
		self._status = 'STOPPED'
		
	def _start(self):
		self._intro.play()
		self._status = 'INTRO'
		
	def _startLoop(self):
		self._intro.stop()
		self._loop.play()
		self._status = 'LOOP'
		
	def _stop(self, stop):
		if stop:
			self._intro.stop()
			self._loop.stop()
			self._end.stop()
			self._status = 'STOPPED'
		else:
			self._loop.stop()
			self._end.start()
			self._status = 'ENDING'
	def _fullStop(self):
		self._intro.stop()
		self._loop.stop()
		self._end.stop()
		self._status = 'STOPPED'