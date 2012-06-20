
_VERSION = "2.5"

import socket
import select
import re
import struct
import random
import sys
import time

import thread
import threading


TOC_SERV_AUTH = ("login.oscar.aol.com", 29999 )
TOC_SERV = ( "toc.oscar.aol.com", 9898 )

class TOCError(Exception): 
	pass

class TOCDisconnectError(Exception): 
	pass

class TocTalk:
	def __init__(self,nick,passwd):
			self._nick = nick
			self._passwd = passwd
			self._agent = "TIC:PY-TOC"
			self._info = "IZEABOT"
			self._seq = random.randint(0,65535)
			self._logfd = sys.stdout
			self._debug = 1
			self._running = 0
			self._ignore = 0
			self._tsem = threading.Semaphore()
			self.build_funcs()


	def build_funcs(self):
		self._dir = []
		for item in dir(self.__class__):
			if ( type( eval("self.%s" % item)) == type(self.__init__) and
			(item[:3] == "on_" or
			item[:4] == "cmd_" )):
				self._dir.append(item)

			
	def go(self):
		self.connect()
		self._running = 1
		self.process_loop()

	def start(self):
		pass

	def connect(self):
		#create the socket object
		try:
			self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except:
			raise TOCError, "FATAL:  Couldn't create a socket"

		# make the connection
		try:
			self._socket.connect( TOC_SERV )
		except:
			raise TOCDisconnectError, "FATAL: Could not connect to TOC Server"
		
		buf  = "FLAPON\r\n\r\n"
		bsent = self._socket.send(buf)
		
		if bsent <> len(buf):
			raise TOCError, "FATAL: Couldn't send FLAPON!"

	def start_log_in(self):
		ep = self.pwdenc()
		self._normnick = self.normalize(self._nick)
		msg = struct.pack("!HHHH",0,1,1,len(self._normnick)) + self._normnick
		self.flap_to_toc(1,msg)

		sn = ord(self._normnick[0]) - 96
		pw = ord(self._passwd[0]) - 96
		d = sn * 7696 + 738816
		e = sn * 746512
		f = pw * d
		g = f - d + e + 71665152
		self._upcode = g

		#now, login
		loginstr = "toc2_login %s %s %s %s english %s 160 US \"\" \"\" 3 0 30303 -kentucky -utf8 %s" % (TOC_SERV_AUTH[0],TOC_SERV_AUTH[1],self._normnick,ep,self.encode(self._agent),self._upcode)
		self.flap_to_toc(2,loginstr )

		
	def normalize(self,data):
		return  re.sub("[^A-Za-z0-9]","",data).lower()

	def encode(self,data):
		for letter in "\\(){}[]$\"":
			data = data.replace(letter,"\\%s"%letter)
		return '"' + data + '"'
	
	def flap_to_toc(self,ftype,msg):
		if ftype == 2:
			msg = msg + struct.pack("!B", 0)
		ditems = []
		ditems.append("*")
		ditems.append(struct.pack("!BHH",ftype,self._seq,len(msg)))
		ditems.append(msg)


		data = "".join(ditems)

		if len(data) >= 2048:
			raise TOCError, "TOC data with protocol overhead cannot exceed 2048 bytes."

		self.derror( "SEND : \'%r\'" % data )
		

		# in case we're threading
		self._tsem.acquire()
		bsent = self._socket.send(data)
		self._tsem.release()


		if bsent <> len(data):
			#maybe make less severe later
			# I've never seen this happen.. have you??
			raise TOCError, "FATAL: Couldn't send all data to TOC Server\n"

		self._seq = self._seq + 1

	def pwdenc(self):
		lookup = "Tic/Toc"
		ept = []

		x = 0
		for letter in self._passwd:
			ept.append("%02x" % ( ord(letter) ^ ord( lookup[x % 7]) ) )
			x = x + 1
		return "0x" + "".join(ept)
	
	def process_loop(self):
		# the "main" loop
		while 1:
			event = self.recv_event()
			if not event:
				continue
			self.handle_event(event)

	def handle_event(self,event):

		self.derror( "RECV : %r" % event[1] )

		#else, fig out what to do with it
		#special case-- login
		if event[0] == 1:
			self.start_log_in()
			return

		if not event[1].count(":"):
			data = ""
			id = "NOID"

		else:
			ind = event[1].find(":")
			id = event[1][:ind].upper()
			data = event[1][ind+1:]

		#handle manually now
		if id == "SIGN_ON":
			self.c_SIGN_ON(id,data)
			return

		if id == "ERROR":
			self.c_ERROR(id,data)
			return

		#their imp
		if ("on_%s" % id ) in self._dir:
			exec ( "self.on_%s(data)" % id )

		else:
			self.werror("INFO : Received unimplemented '%s' id\nData: %s" % (id,data))

	def recv_event(self):
		header = self._socket.recv(6) 

		if header == "":
			self.err_disconnect()
			return

		while len(header) < 6:
			print "Header incomplete--%s of 6 bytes received. Waiting for more." % len(header)
			f = open('incomplete-headers.dat', 'a')
			f.write("Incomplete header: '%s'\n" % header)
			more_header = self._socket.recv(6 - len(header))
			if more_header == "":
				self.err_disconnect()
				return
			header = header + more_header
			f.write("       updated to: '%s'\n" % header)
			f.close()

		try:
			(marker,mtype,seq,buflen) = struct.unpack("<sBhh",header)
		except:
			f = open('bad-header.dat', 'w')
			f.write(header)
			f.close
			print "Unpack error in header. Bad data written to bad-header.dat"

		#get the info
		dtemp = self._socket.recv(buflen)
		data = dtemp
		while len(data) != buflen:
			if dtemp == "":
				self.err_disconnect()
				return
			dtemp = self._socket.recv(buflen - len(data))
			data = data + dtemp

		return (mtype, data)

	def thread_recv_events(self):
		while self._running:
			rfd,dc,dc = select.select([self._socket],[],[])
			if rfd == []:
				continue
			try:
				header = self._socket.recv(6) 
			except:
				self.err_disconnect()

			if header == "":
				self.err_disconnect()

			while len(header) < 6:
				print "Header incomplete--%s of 6 bytes received. Waiting for more." % len(header)
				f = open('incomplete-headers.dat', 'a')
				f.write("Incomplete header: '%s'\n" % header)
				try:
					more_header = self._socket.recv(6 - len(header))
				except:
					self.err_disconnect()
					break
				if more_header == "":
					self.err_disconnect()
					break
				header = header + more_header
				f.write("       updated to: '%s'\n" % header)
				f.close()

			try:
				(marker,mtype,seq,buflen) = struct.unpack("!sBhh",header)
			except:
				f = open('bad-header.dat', 'w')
				f.write(header)
				f.close
				print "Unpack error in header. Bad data written to bad-header.dat"

			#get the info
			dtemp = self._socket.recv(buflen)
			data = dtemp
			while len(data) != buflen:
				if dtemp == "":
					self.err_disconnect()
				dtemp = self._socket.recv(buflen - len(data))
				data = data + dtemp

			if not self._ignore:
				self.handle_event([mtype,data])

	def err_disconnect(self):
		self.werror( "INFO: Disconnected!\n" )
		raise TOCDisconnectError, "FATAL: We seem to have been disconnected from the TOC server.\n"

	# our event handling
	def c_ERROR(self,id,data):
		# let's just grab the errors we care about!

		#still more fields
		if data.count(":"): 
			dt = int (data[:data.find(":")])
		else:
			dt = int(data) # let's get an int outta it
		
		if dt == 980:
			raise TOCError, "FATAL: Couldn't sign on; Incorrect nickname/password combination"

		elif dt == 981:
			raise TOCError, "FATAL: Couldn't sign on; The AIM service is temporarily unavailable"

		elif dt == 982:
			raise TOCError, "FATAL: Couldn't sign on; Your warning level is too high"

		elif dt == 983:
			raise TOCError, "FATAL: Couldn't sign on; You have been connecting and disconnecting too frequently"

		elif dt == 989:
			raise TOCError, "FATAL: Couldn't sign on; An unknown error occurred"

		# ... etc etc etc
		else:
			# try to let further implementation handle it
			if ("on_%s" % id ) in self._dir:
				exec ( "self.on_%s(data)" % id )
			else:
				self.werror("ERROR: The TOC server sent an unhandled error string: %s" % data)

	def c_SIGN_ON(self,type,data):
		self.flap_to_toc(2,"toc_init_done")
		self.flap_to_toc(2,"toc2_set_pdmode 1")
		self.flap_to_toc(2,"toc_set_info %s" % self.encode(self._info) )
		self.start()

	def strip_html(self,data):
		return re.sub("<[^>]*>","",data)

	def normbuds(self,buddies):
		nbuds = []
		for buddy in buddies:
			nbuds.append(self.normalize(buddy))
		return " ".join(nbuds)
	
	#actions--help the user w/common tasks

	def do_RAW_TOC(self,command):
		self.flap_to_toc(2,command)

	#the all-important
	def do_SEND_IM(self,user,message,autoaway=0):
		sendmessage = "toc2_send_im %s %s" % ( self.normalize(user), self.encode(message) )
		if autoaway:
			sendmessage = sendmessage + " auto"
		self.flap_to_toc(2, sendmessage)
	
	#Permit/Deny Functions
	def do_SET_PDMODE(self,value):
		self.flap_to_toc(2,"toc2_set_pdmode %s" % int(self.value) )		

	def do_ADD_PERMIT(self,buddies):
		self.flap_to_toc(2,"toc2_add_permit %s" % self.normbuds(buddies) )

	def do_REMOVE_PERMIT(self,buddies):
		self.flap_to_toc(2,"toc2_remove_permit %s" % self.normbuds(buddies) )

	def do_ADD_DENY(self,buddies):
		self.flap_to_toc(2,"toc2_add_deny %s" % self.normbuds(buddies) )

	def do_REMOVE_DENY(self,buddies):
		self.flap_to_toc(2,"toc2_remove_deny %s" % self.normbuds(buddies) )

	#Buddylist Management

	def do_ADD_GROUP(self,group):
		self.flap_to_toc(2,"toc2_add_group \"%s\"" % group)

	def do_REMOVE_GROUP(self,group):
		self.flap_to_toc(2,"toc2_del_group \"%s\"" % group)

	def do_ADD_BUDDY(self,buddies):
		self.flap_to_toc(2,"toc_add_buddy %s" % self.normbuds(buddies))

	def do_NEW_BUDDIES(self,buddies):
		cmdstring = ""
		prevgroup = ""
		for buddyinfo in buddies:
			if len(buddyinfo) == 2 or len(buddyinfo) == 3:
				group = buddyinfo[0]
				if group == "":
					group = "Buddies"
				sn = self.normalize(buddyinfo[1])
				if sn == "":
					self.werror("Malformed buddylist list.")
					return
				if group != prevgroup:
					cmdstring = cmdstring + "g:%s\n" % group
					prevgroup = group
				cmdstring = cmdstring + "b:%s" % sn
				if len(buddyinfo) == 3:
					cmdstring = cmdstring + ":%s" % buddyinfo[2]
				cmdstring = "{" + cmdstring + "}\n"
			else:
				self.werror("Malformed buddylist list.")
				return
		print cmdstring
		self.flap_to_toc(2,"toc2_new_buddies %s" % cmdstring)

	def do_REMOVE_BUDDY(self,buddies):
		self.flap_to_toc(2,"toc_remove_buddy %s" % self.normbuds(buddies) )

	def do_SET_IDLE(self,itime):
		self.flap_to_toc(2,"toc_set_idle %d" % itime )

	def do_SET_AWAY(self,awaymess):
		if awaymess == "":
			self.flap_to_toc(2,"toc_set_away")
			return

		self.flap_to_toc(2,"toc_set_away %s" % self.encode(awaymess) )
		
	def do_GET_INFO(self,user):
		self.flap_to_toc(2,"toc_get_info %s" % self.normalize(user) )

	def do_SET_INFO(self,info):
		self.flap_to_toc(2,"toc_set_info %s" % self.encode(info) )

	# warning capability
	def do_EVIL(self,user,anon=0):
		if anon:
			acode = "anon"
		else:
			acode = "norm"
			
		self.flap_to_toc(2,"toc_evil %s %s" % (self.normalize(user), acode) )

	#chat
	def do_CHAT_INVITE(self,room,imess,buddies):
		self.flap_to_toc(2,"toc_chat_invite %s %s %s" % (self.normalize(room),
		self.encode(imess), self.normbuds(buddies) ) )

	def do_CHAT_ACCEPT(self, id):
		self.flap_to_toc(2,"toc_chat_accept %s" % id)

	def do_CHAT_LEAVE(self,id):
		self.flap_to_toc(2,"toc_chat_leave %s" % id)
		
	def do_CHAT_WHISPER(self,room,user,message):
		self.flap_to_toc(2,"toc_chat_whisper %s %s %s" % (room, 
		self.normalize(user), self.encode(message) ) )

	def do_CHAT_SEND(self,room,message):
		self.flap_to_toc(2,"toc_chat_send %s %s" % (room, 
		self.encode(message) ) )
		
	def do_CHAT_JOIN(self,roomname):
		self.flap_to_toc(2,"toc_chat_join 4 %s" % roomname)

	def do_SET_CONFIG(self,configstr):
		self.flap_to_toc(2,"toc_set_config \"%s\"" % configstr)

	# error funcs
	def werror(self,errorstr):
		if self._debug:
			self._logfd.write("(%s) %s\n"% (self._nick,errorstr))

	def derror(self,errorstr):
		if self._debug > 1:
			self._logfd.write("(%s) %s\n"% (self._nick,errorstr))

class BotManagerError(Exception):
	pass

class BotManager:
	def __init__(self):
		self.bots = {}

	def addBot(self,bot,botref,go=1,reconnect=1,delay=30):
		if self.bots.has_key(botref):
			raise BotManagerError, "That botref is already registered"

		self.bots[botref] = bot
		self.bots[botref]._reconnect = reconnect
		self.bots[botref]._delay = delay
		if go:
			self.botGo(botref)

	def botGo(self,botref):
		if not self.bots.has_key(botref):
			raise BotManagerError, "That botref has not been registered"
		thread.start_new_thread(self._dispatcher,(self.bots[botref],))

	def botStop(self,botref):
		if not self.bots.has_key(botref):
			raise BotManagerError, "That botref has not been registered"
		self.bots[botref]._running = 0
		self.bots[botref]._socket.close()

	def botPause(self,botref,val=1):
		if not self.bots.has_key(botref):
			raise BotManagerError, "That botref has not been registered"
		self.bots[botref]._ignore = val

	def getBot(self,botref):
		if not self.bots.has_key(botref):
			raise BotManagerError, "That botref has not been registered"
		return self.bots[botref]
		

	def _dispatcher(self,bot):
		while 1:
			try:
				bot.connect()
				bot._running = 1
				bot.thread_recv_events()
			except TOCDisconnectError:
				if not bot._reconnect or not bot._running:
					break
				bot._running = 0
				time.sleep(bot._delay) # then we reconnect
			else:
				break
		thread.exit()

	def wait(self):
		while 1:
			time.sleep(2000000) # not coming back from this...
