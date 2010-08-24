#!/usr/bin/env python

# -*- coding: utf-8 -*-

import sys, os, re, math, random, shutil, time, getopt

# Check to see if the user wants to supply FIFE themselves
argv = sys.argv[1:]
local = False
try:
	opts, args = getopt.getopt(argv, "l", "use-local")
except:
	pass
for opt, arg in opts:
	if opt in ("-l", "--use-local"):
		local = True
	else:
		local = False


# Import FIFE
if local:
	try:
		from fife import fife
	except:
		fife_path = os.path.join('engine','python')
		if os.path.isdir(fife_path) and fife_path not in sys.path:
			sys.path.insert(0,fife_path)
		from fife import fife
else:
	fife_path = os.path.join('engine','python')
	if os.path.isdir(fife_path) and fife_path not in sys.path:
		sys.path.insert(0,fife_path)
	from fife import fife

print "Using the FIFE python module found here: ", os.path.dirname(fife.__file__)
from fife.extensions.basicapplication import ApplicationBase
from scripts.common.eventlistenerbase import EventListenerBase

# Import the world library
from scripts import world
from scripts.musicmanager import ThreePartMusic

# Import the settings library
from fife.extensions.fife_settings import Setting

# Import the settings file and name the application
TDS = Setting(app_name="zsc-demo-1",
              settings_file="./settings.xml", 
              settings_gui_xml="")

class ApplicationListener(EventListenerBase):
	"""
	ApplicationListener Class
	Inherits from EventListenerBase, handles keypresses, commands and the console.
	"""
	def __init__(self, engine, world):
		"""
		__init___ Function
		Starts the application listener
		
		Keyword Arguments
		engine - A pointer to fife.engine
		world - A World object
		"""
		super(ApplicationListener, self).__init__(engine,regKeys=True,regCmd=True, regMouse=False, regConsole=True, regWidget=True)
		self._engine = engine
		self._world = world
		self._quit = False
		self._console = self._engine.getGuiManager().getConsole
		
	def keyPressed(self, evt):
		"""
		keyPressed Function
		Handles keypresses (simple, ain't it?)
		"""
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
			evt.consume()
		else:	
			self._world._keyPressed(evt)

	def onConsoleCommand(self, command):
		"""
		onConsoleCommand Function
		Takes the input from the user from the console and checks it for a command
		
		Keyword Arguments
		command - String, a command
		"""
		result = ''
		if command.lower() in ('quit', 'exit'):
			self._quit = True
			result = 'quitting'
		elif command.lower() in ('hide'):
			self._console().toggleShowHide()
		elif command.lower() in ('close'):
			self._console().clear()
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
			# Takes the current timestamp and makes a filename from it
			filename = 'screenshot' + str(time.time()) + '.png'
			self._engine.getRenderBackend().captureScreen('screenshots/' + filename)
			result = 'Screenshot ' + filename + ' taken'
		elif command.lower() in ('clear', 'empty'):
			self._console().clear()
			result = 'Console cleared'
		elif command.lower() in ('stopsounds'):
			self._world._sounds._stopAllClips()
			result = 'Sounds stopped'
		elif command.lower() in ('startambient'):
			self._world._sounds._startClip('ambient')
			result = 'ambient music started'
		elif command.lower() in ('startmusic'):
			self._world._sounds._startClip('music')
			result = 'ambient music started'
		else:
			result = 'Command not found'
		return result
	
	def onCommand(self, command):
		self._quit = (command.getCommandType() == fife.CMD_QUIT_GAME)
		if self._quit:
			command.consume()

class mainApplication(ApplicationBase):
	"""
	mainApplication Class
	The game it's self. Starts everything.
	"""
	def __init__(self):
		super(mainApplication,self).__init__()
		
		# Start a new instance of a World object
		self._world = world.World(self, self.engine, TDS)
		
		# Start a new listener object
		self._listener = ApplicationListener(self.engine, self._world)
		
		# Load GUI
		self._world._loadGui('LOAD', 'loading-1', False)
		self._world._loadGui('HUD', 'hud', False)
		self._world._loadGui('MAIN', 'menu', False)
		self._world._loadGui('SETTINGS', 'settings', False)
		self._world._loadGui('ABOUT', 'about', False)
		
		
		
		# TODO: Add loading a map based on the settings file.
		# Load a map
		self._world._loadMap('maps/zsc-test-6.xml', 'MENU')
		
		self._world._sounds._loadClip("beep", "sounds/beep.ogg", False, False)
		
		#self._world._sounds._loadClip('ambient', 'music/forestAmbient1.ogg', True, False)
		#self._world._sounds._startClip('ambient', True)
		
		self._testsound = ThreePartMusic('music/other/title/start.ogg', 'music/other/title/loop.ogg', 'music/other/title/end.ogg', True, self._world._soundmanager)
		self._testsound._start()
		

	def createListener(self):
		pass # already created in constructor

	def _pump(self):
		"""
		_pump Function
		Overwrites the default _pump function and is executed every frame.
		"""
		# Check to see if anything tried to quit
		if self._listener._quit or self._world._quit:
			self.breakRequested = True
		
		self._world._mouseMoved = False
		
		self._world._eventtracker._evaluateEvents()
		self._world._sounds._fade()
		
		if not self._world._mouseMoved:
			self._world.mouseMoved(None, True, self.engine.getCursor())
def main():
	"""
	main Function
	Runs when the script is started. Simply starts mainApplication.
	"""
	app = mainApplication()
	app.run()
if __name__ == '__main__':
	main()
