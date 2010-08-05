import sys, os, re, math, random, shutil, time

#Tell Python where to find FIFE
fife_path = os.path.join('engine','python')
if os.path.isdir(fife_path) and fife_path not in sys.path:
	sys.path.insert(0,fife_path)

# Load the XML Serialiser:
from fife.extensions.serializers.simplexml import SimpleXMLSerializer

print """ ____  _  ____  _____  _  ____  _  ____ _____ 
| _) \| |/ (__`|_   _|| || ===|| || ===|| () )
|____/|_|\____)  |_|  |_||__|  |_||____||_|\_\

Python Dict to FIFE XML Serial Format Converter
"""

filename = raw_input("XML Filename: ")
xml = SimpleXMLSerializer(filename)

dict = {}
loop = True

while loop:
    key = raw_input("Key: ")
    dict[key] = raw_input("Value: ")
    print "Add more? Y/n"
    if raw_input() == "n":
        loop = False
        
dictstore = xml._serializeDict(dict)
xml.set(raw_input("Module: "), raw_input("Name: "), dictstore)
xml.save(filename)
print filename + " has been updated with the new dict entry. Press enter to end this python shell"
raw_input()