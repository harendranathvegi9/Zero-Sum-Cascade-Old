#!/usr/bin/env python

# -*- coding: utf-8 -*-

import sys, os, re, math, random, shutil, time

# Tell Python where to find FIFE
fife_path = os.path.join('..','..','engine','python')
if os.path.isdir(fife_path) and fife_path not in sys.path:
	sys.path.insert(0,fife_path)

# Import FIFE
from fife import fife
print "Using the FIFE python module found here: ", os.path.dirname(fife.__file__)
from fife.extensions.basicapplication import ApplicationBase
from scripts.common.eventlistenerbase import EventListenerBase

# Import the world (yes, all of it)
from scripts import world

# Import the settings library
from fife.extensions.fife_settings import Setting

TDS = Setting(app_name="zsc-demo-1",
              settings_file="./settings.xml", 
              settings_gui_xml="")

class ApplicationListener(EventListenerBase):
	def __init__(self, engine, world):
		super(ApplicationListener, self).__init__(engine,regKeys=True,regCmd=True, regMouse=False, regConsole=True, regWidget=True)
		self._engine = engine
		self._world = world
		self._quit = False
		self._console = self._engine.getGuiManager().getConsole
		
	def keyPressed(self, evt):
		keyval = evt.getKey().getValue()
		keystr = evt.getKey().getAsString().lower()
		consumed = False
		if keyval == fife.Key.ESCAPE:
			self._quit = True
			evt.consume()
		elif keyval == fife.Key.F10:
			self._console().toggleShowHide()
			evt.consume()
		elif keyval == fife.Key.F12:
			self.onConsoleCommand('takescreenshot')
			evt.consume()
		elif keyval == fife.Key.F1:
			self._console().toggleShowHide()
			self.onConsoleCommand('help')

	def onCommand(self, command):
		self._quit = (command.getCommandType() == fife.CMD_QUIT_GAME)
		if self._quit:
			command.consume()

	def onConsoleCommand(self, command):
		result = ''
		if command.lower() in ('quit', 'exit'):
			self._quit = True
			result = 'quitting'
		elif command.lower() in ('close'):
			self._console().toggleShowHide()
		elif command.lower() in ('help'):
			self._console().println(open('misc/help.txt','r').read())
			result = "-- End of help --"
		elif command.lower() in ('help console'):
			self._console().println(open('misc/consolehelp.txt','r').read())
			result = "-- End of help --"
		elif command.lower() in ('help keymap'):
			self._console().println(open('misc/keymaphelp.txt','r').read())
			result = "-- End of help --"
		elif command.lower() in ('help press'):
			self._console().println(open('misc/press.txt','r').read())
			result = "-- End of help --"
		elif command.lower() in ('takescreenshot'):
			filename = 'screenshot' + str(time.time()) + '.png'
			self._engine.getRenderBackend().captureScreen('screenshots/' + filename)
			result = 'Screenshot ' + filename + ' taken'
		else:
			result = 'Command not found'
		return result

class mainApplication(ApplicationBase):
	def __init__(self):
		super(mainApplication,self).__init__()
		
		self._world = world.World(self, self.engine, TDS)
		self._listener = ApplicationListener(self.engine, self._world)
		
		self._world._loadMap('maps/zsc-test-4.xml', 'LEVEL')
		
	def requestQuit(self):
		cmd = fife.Command()
		cmd.setSource(None)
		cmd.setCommandType(fife.CMD_QUIT_GAME)
		self.engine.getEventManager().dispatchCommand(cmd)
		
			
	def createListener(self):
		pass # already created in constructor

	def _pump(self):
		if self._listener._quit:
			self.breakRequested = True
		#else:
		#	self._world.pump()
			
def main():
	app = mainApplication()
	app.run()
if __name__ == '__main__':
	main()