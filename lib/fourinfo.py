#xml functions
import xml.dom.minidom
from xml.dom.minidom import Node
#------
#url functions
import urllib
from urlparse import urlparse
#------


BASE_URL = 'http://test-gateway.4info.net/'

def unescape(s):
	s = s.replace("&lt;", "<")
	s = s.replace("&gt;", ">")
	s = s.replace("%2F", "-")
	s = s.replace("+", " ")
	s = s.replace("%26", "&")
	# this has to be last:
	s = s.replace("&amp;", "&")
	return s


def get_list_of_carriers():
	url = BASE_URL + "list"
	xmldoc = xml.dom.minidom.parse(urllib.urlopen(url))
	mapping = {}
	for node in xmldoc.getElementsByTagName('carrier'):
		id = node.getAttribute('id')
		carrier = unescape(node.firstChild.data)
		mapping[id] = carrier
	return mapping
		
def get_headers(url, request_type, content_type, content_length):
	o = urlparse(url)
	port = o.port or "80"
	headers = request_type + " " + o.path + " HTTP/1.1\n HOST: " + o.hostname + ":" + port + "\nContent-Type: " + content_type + "\nConnection: close\nContent-Length: " + content_length + "\n\n"		
	return headers

class FourInfo:
	def __init__(self, carrier_id, phonenumber):
		self.carrier_id = carrier_id
		self.phonenumber = phonenumber
		
	def validate_number(self):
		url = BASE_URL + "/msg"
		validation_xml = self.create_validation_request("5")
		content_length = len(validation_xml.toxml())
		headers = get_headers(url, "POST", "text/xml", str(content_length))
		f = urllib.urlopen(url, headers + validation_xml.toxml())
		print str(f)
		response = f.read()
		f.close
		return response
		
	#---methods
	
	def create_validation_request(self,mytype):
		doc = xml.dom.minidom.Document()
		request = doc.createElement("request")
		doc.appendChild(request)
		request.setAttribute("clientId", "123")
		request.setAttribute("clientKey","32IFJ23OFIJIWR")
		request.setAttribute("type", "VALIDATION")
		validation = doc.createElement("validation")
		request.appendChild(validation)
		recipient = doc.createElement("recipient")
		validation.appendChild(recipient)
		the_type = doc.createElement("type")
		recipient.appendChild(the_type)
		typetext = doc.createTextNode(mytype)
		the_type.appendChild(typetext)
		id = doc.createElement("id")
		recipient.appendChild(id)
		idtext = doc.createTextNode(self.phonenumber)
		id.appendChild(idtext)
		print doc.toprettyxml(indent="	")
		return doc
	