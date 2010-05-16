#!/usr/bin/env python
# Copyright (C) 2010 robstar.cc  <info at navarin dot de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.


try:
	import os
	import sys
	import subprocess
	import rb
	import gobject
	import gtk, gtk.glade
	import gconf, gnome
except ImportError as e:
	print "Depencies missing:"
	print str(e)


class RhythmotePlugin (rb.Plugin):
	'''Rhythmote's main class.'''

	def __init__(self):
		rb.Plugin.__init__(self)
		path = os.path.abspath( __file__ )
		
		self.daemon = None
		self.cwd = path[:path.rfind("/")]
		self.gconf_keys = {
			'port' : '/apps/rhythmbox/plugins/rhythmote/port'
		}
		self.client = gconf.client_get_default()
		self.port = self.client.get_string(self.gconf_keys["port"]) or "8484"

		

	def activate(self, shell):
		'''Default actication method, automatically called when the plugin is 
		started from within Rhythmbox. It starts a separated process which acts 
		as a daemon and listens to the port, entered in the settings dialog.'''
		
		print "starting Rhythmote"
		self.restart()
		#self.daemon = subprocess.Popen(["/usr/bin/python", self.cwd+"/daemon.py", str(self.port)]);
			

	def deactivate(self, shell):
		'''This method is called automatically, when Ryhthmbox is closed or the 
		plugin is deactivated by the user. It cleans up all objects which are
		not needed anymore and sends a SIGTERM to stop the daemon.'''
		
		print "quitting Rhythmote"
	
		if self.daemon:
			self.daemon.terminate()
			
			
	def create_configure_dialog(self, dialog=None):
		'''creates the configuration dialog using a libglade gui'''
		
		if dialog == None:
		
			self.configure_callback_dic = {
				"rb_rhythmote_port_changed" : lambda w: self.client.set_string(self.gconf_keys['port'], self.port)
			}
		
			gladexml = gtk.glade.XML(self.find_file("rhythmote-prefs.glade"))
			gladexml.signal_autoconnect(self.configure_callback_dic)
			gladexml.get_widget("port").set_text(self.port)
			
			dialog = gladexml.get_widget('preferences_dialog')
			def dialog_response (dialog, response):
				port = gladexml.get_widget("port").get_text()
				try:
					number = int(port)
				except (ValueError, IndexError):
					dialog.hide()
				
				#if port == self.port:
				#	dialog.hide()
				
				self.port = port
				self.client.set_string(self.gconf_keys['port'], self.port)
				self.restart()
				print "Rhythmote now running on port: "+ port
				dialog.hide()
				
			dialog.connect("response", dialog_response)
			
		dialog.present()
		return dialog	
		
		
	def restart(self):
		if self.daemon:
			print "terminating daemon"
			self.daemon.terminate()
		self.daemon = subprocess.Popen(["/usr/bin/python", self.cwd+"/daemon.py", str(self.port)]);



