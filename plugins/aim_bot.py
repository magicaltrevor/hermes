from lib.toc import *

class Aim(TocTalk):
	def __init__(self,login,password,message,to_address=None,from_address=None):
		self.login = login
		self.nick = login
		self.passwd = password
		self.to_address = to_address
		self.from_address = from_address
		self.message = message
		
	def send_message(self):
		return 'Sending message through AIM: ' + self.message