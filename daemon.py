
	
#Copyright (C) 2009 Nikitas Stamatopoulos
	
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
	
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
	
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.



import dbus, re, os, SocketServer, socket,sys
import signal

if len(sys.argv) == 2:
	port = int(sys.argv[1])
else:
	port = 8484

def on_exit(sig, func=None):
	print "exiting Rhythmote daemon"
	server_socket.shutdown(1)
	server_socket.close()

signal.signal(signal.SIGTERM, on_exit)	




bus = dbus.SessionBus()
rbox = bus.get_object( 'org.gnome.Rhythmbox', '/org/gnome/Rhythmbox/Player')
rboxs = bus.get_object( 'org.gnome.Rhythmbox', '/org/gnome/Rhythmbox/Shell')
rboxp = bus.get_object( 'org.gnome.Rhythmbox', '/org/gnome/Rhythmbox/PlaylistManager')
player = dbus.Interface(rbox, 'org.gnome.Rhythmbox.Player')
shell = dbus.Interface(rboxs, 'org.gnome.Rhythmbox.Shell')
playlist = dbus.Interface(rboxp, 'org.gnome.Rhythmbox.PlaylistManager')

volume = 0
home = os.environ['HOME']
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.settimeout(None)
server_socket.bind(("", port))
server_socket.listen(5)
test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
test_socket.connect(('google.de',0))
ip = test_socket.getsockname()[0]
test_socket.close()
client_socket = None
print 'Started Rhythmote on port %s' % (port)
print 'Your IP is %s' % (ip)
while 1:
	client_socket, address = server_socket.accept()
	received = client_socket.recv(512)
	action, var = received.split('/')

	if action == "coverImage":
		try:
			cover = open(shell.getSongProperties(player.getPlayingUri())['rb:coverArt-uri'] )
			reply=cover.read()
			cover.close()
		except IOError:
			reply=""
			
		client_socket.send(reply)

	if action == "coverExists":
		if shell.getSongProperties(player.getPlayingUri()).has_key('rb:coverArt-uri'):
			coverExists="true"
			artwork_path = shell.getSongProperties(player.getPlayingUri())['rb:coverArt-uri'] 
			if os.path.isfile(artwork_path):
				size = int(os.path.getsize(artwork_path))
				if size > 200000:
					coverExists="false"
			else:
				coverExists="false"
		client_socket.send(reply)
		
	if action == "playPause":
		player.playPause(1)

	if action == "next":
		player.next()

	if action == "prev":
		player.previous()

	if action == "volumeDown":
		currVol = player.getVolume()
		currVol = currVol-0.1
		if currVol < 0:
			currVol=0
		player.setVolume(currVol)
		
	if action == "volumeUp":
		player.setVolume(player.getVolume()+0.1)

	if action == "mute":
	    if player.getMute() == True:
	        player.setMute(False)
	    else:
	        player.setMute(True)

	if action == "status":
		if player.getPlaying():
			reply = "playing"
		else:
			reply = "paused"
		client_socket.send(reply.encode('utf-8'))

	if action == "album":
		reply = str(shell.getSongProperties(player.getPlayingUri())["album"])
		client_socket.send(reply.encode('utf-8'))
		
	if action == "artist":
		reply = str(shell.getSongProperties(player.getPlayingUri())["artist"])
		client_socket.send(reply.encode('utf-8'))
		
	if action == "title":
		reply = str(shell.getSongProperties(player.getPlayingUri())["title"])
		client_socket.send(reply.encode('utf-8'))
		
	if action == "trackCurrentTime":
		reply = str(int(player.getElapsed()))
		client_socket.send(reply)
		
	if action == "trackTotalTime":
		reply = str(int(shell.getSongProperties(player.getPlayingUri())['duration']))
		client_socket.send(reply)
		
	if action == "seek":
		player.setElapsed(int(var))

	if action == "shuffle":
		pass

	if action == "repeat":
		pass
			
		
	if action == "all":
		try:
			if player.getPlaying():
				status = "playing"
			else:
				status = "paused"
			album = str(shell.getSongProperties(player.getPlayingUri())["album"])
			artist = str(shell.getSongProperties(player.getPlayingUri())["artist"])
			title = str(shell.getSongProperties(player.getPlayingUri())["title"])
			trackCurrentTime = str(int(player.getElapsed()))
			trackTotalTime = str(int(shell.getSongProperties(player.getPlayingUri())['duration']))
			coverExists="false"
			if shell.getSongProperties(player.getPlayingUri()).has_key('rb:coverArt-uri'):
				coverExists="true"
				artwork_path = shell.getSongProperties(player.getPlayingUri())['rb:coverArt-uri'] 
				if os.path.isfile(artwork_path):
					size = int(os.path.getsize(artwork_path))
					if size > 200000:
						coverExists="false"
				else:
					coverExists="false"
			sep = '/'
			reply=status+sep+album+sep+artist+sep+title+sep+trackCurrentTime+sep+trackTotalTime+sep+coverExists
			client_socket.send(reply.encode('utf-8'))
		
		except Exception as e:
			lala=1
		
	client_socket.close()
		
		
### DEBUG ###
# code to get all methods
#from dbus import SessionBus, Interface
#from dbus._expat_introspect_parser import process_introspection_data

def introspect_object(named_service, object_path):
	'''This is debug output function'''
	obj = SessionBus().get_object(named_service, object_path)
	iface = Interface(obj, 'org.freedesktop.DBus.Introspectable')
	return process_introspection_data(iface.Introspect())

#introspect_object('org.gnome.Rhythmbox', '/org/gnome/Rhythmbox/Shell')


