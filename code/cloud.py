
"""
	A pure python ping implementation using raw sockets.

	Note that ICMP messages can only be send from processes running as root
	
"""


import os
import select
import struct
import sys
import time
import socket,sys
from impacket import ImpactPacket
from random import randint



if sys.platform.startswith("win32"):
	# On Windows, the best timer is time.clock()
	default_timer = time.clock
else:
	# On most other platforms the best timer is time.time()
	default_timer = time.time


# ICMP parameters
ICMP_ECHOREPLY = 0 # Echo reply (per RFC792)
ICMP_ECHO = 8 # Echo request (per RFC792)
ICMP_MAX_RECV = 2048 # Max size of incoming buffer

MAX_SLEEP = 1000
NUMBER_OF_NODES = 5

class file_breaker:
	def __init__(self, fn, ps = 20):
		self.return_mode = False
		self.file_name = fn
		self.part_size = ps
		self.check = []
		self.parts = []
	def breakfile(self):
		ret = []
		with open(self.file_name, "rb") as f:
			count = 0
			byte = f.read(1)
			ret.append(b"")
			while byte:
				if count >= 20:
					ret.append(b"")
					count = 0
				ret[-1] += byte
				count += 1
				byte = f.read(1)
		return ret, ret.__len__()
	def initConstruct(self, number):
		print("file " + self.file_name.__str__() + " breaked to " + number.__str__() + " parts")
		self.part_number = number
		for i in range(number):
			self.check.append(False)
			self.parts.append(b"")
	def addForConstruct(self, part_ind, part):
		if not self.return_mode:
			return False
		print("received file " + self.file_name.__str__() + " part " + part_ind.__str__())
		self.check[part_ind] = True
		self.parts[part_ind] = part
		for i in range(self.part_number):
			if self.check[i] == False:
				return True
		with open("rcv_" + self.file_name, "wb") as f:
			for part in self.parts:
				f.write(part)
		print("download done")
		return True
	def isForFile(self, filename):
		return (filename == self.file_name)
	def returnHome(self):
		self.return_mode = True

def is_valid_ip4_address(addr):
	parts = addr.split(".")
	if not len(parts) == 4:
		return False
	for part in parts:
		try:
			number = int(part)
		except ValueError:
			return False
		if number > 255 or number < 0:
			return False
	return True

def to_ip(addr):
	if is_valid_ip4_address(addr):
		return addr
	return socket.gethostbyname(addr)


class Response(object):
	def __init__(self):
		self.max_rtt = None
		self.min_rtt = None
		self.avg_rtt = None
		self.packet_lost = None
		self.ret_code = None
		self.output = []

		self.packet_size = None
		self.timeout = None
		self.source = None
		self.destination = None
		self.destination_ip = None

class Ping(object):
	def __init__(self, node_num):
		self.filebreakers = []
		self.node_num = node_num
		self.node_ip = "10.0.0." + node_num.__str__()
		self.timeout = 1000
		self.packet_size = 100
		self.socket = self.create_socket()
		self.message = ""
		self.blacklist = []
		self.sender_node()

	#--------------------------------------------------------------------------

	def header2dict(self, names, struct_format, data):
		""" unpack the raw received IP and ICMP header informations to a dict """
		unpacked_data = struct.unpack(struct_format, data)
		return dict(zip(names, unpacked_data))

	#--------------------------------------------------------------------------
	
	def sender_node(self):
		while True:
			if self.receive_and_eval(self.socket):
				mode, filename = self.eval_inp(self.message[:-1])
				if mode == 'up':
					self.send_file(filename)#removing new line character
				elif mode == 'down':
					for fb in self.filebreakers:
						if fb.isForFile(filename):
							rnd1, rnd2 = self.random_ip()
							self.send_message(rnd1, rnd2, self.socket, filename + "/" + self.node_ip, 1, True)
							fb.returnHome()
					print("file " + filename.__str__() + " is in download mode")
				else:
					print("invalid input")

	def eval_inp(self, inp):
		spl = inp.split(' ', 1)
		if spl.__len__() == 2:
			return spl[0], spl[1]
		return "", ""

	def send_file(self, filename):
		"""
		send and receive pings in a loop. Stop if count or until deadline.
		"""

		fb = file_breaker(filename)
		self.filebreakers.append(fb)
		fileparts, count = fb.breakfile()
		fb.initConstruct(count)
		seq_number = 0

		while True:
			rnd1, rnd2 = self.random_ip()
			self.send_message(rnd1, rnd2, self.socket, filename + "/" + fileparts[seq_number], seq_number, False)
			seq_number += 1
			if seq_number >= count:
				break
		print("file " + filename.__str__() + " uploaded")

	def create_socket(self):
		try: 
			current_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
			current_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

		except socket.error, (errno, msg):
			if errno == 1:
				# Operation not permitted - Add more information to traceback
				#the code should run as administrator
				etype, evalue, etb = sys.exc_info()
				evalue = etype(
					"%s - Note that ICMP messages can only be sent from processes running as root." % evalue
				)
				raise etype, evalue, etb
			raise # raise the original error
		return current_socket

	# send an ICMP ECHO_REQUEST packet
	def send_message(self, source_ip, dest_ip, current_socket, msg, seq_number, is_ret):
		
		#Create a new IP packet and set its source and destination IP addresses
		src = source_ip
		dst = dest_ip
		ip = ImpactPacket.IP()
			#print(src.__str__() + " to " + dst.__str__())
		ip.set_ip_src(src)
		ip.set_ip_dst(dst)	

		#Create a new ICMP ECHO_REQUEST packet 
		icmp = ImpactPacket.ICMP()
		icmp.set_icmp_type(icmp.ICMP_ECHO)

		#inlude a small payload inside the ICMP packet
		#and have the ip packet contain the ICMP packet
		icmp.contains(ImpactPacket.Data(msg))
		ip.contains(icmp)


		#give the ICMP packet some ID
		if is_ret:
			icmp.set_icmp_id(0x04)
		else:
			icmp.set_icmp_id(0x03)
		
		#set the ICMP packet checksum
		icmp.set_icmp_cksum(0)
		icmp.auto_checksum = 1
		
		icmp.set_icmp_seq(seq_number)
		self.send_packet(current_socket, ip.get_packet(), dst)
	
	def send_packet(self, current_socket, ip_packet, dst):
		try:
			current_socket.sendto(ip_packet, (dst, 1)) # Port number is irrelevant for ICMP
		except socket.error as e:
			self.response.output.append("General failure (%s)" % (e.args[1]))
			current_socket.close()
		return
	
	def random_ip(self):
		a, b = -1, -1
		while a == b or b == self.node_num:
			a = randint(1, NUMBER_OF_NODES)
			b = randint(1, NUMBER_OF_NODES)
		return "10.0.0." + a.__str__(), "10.0.0." + b.__str__()

	def receive_and_eval(self, current_socket):
		has_data, icmp_header, ip_header, data = self.receive_packet(current_socket)
		if not has_data:
			return False #timeout
		if icmp_header == None:
			return True #stdin data
		icmp_type = (int)(icmp_header["type"])
		if icmp_type == ICMP_ECHO:
			packet_id = (int)(icmp_header["packet_id"])
			if packet_id == 4:
				if not data.split('/', 1) in self.blacklist:
					self.blacklist.append(data.split('/', 1))
				rnd1, rnd2 = self.random_ip()
				self.send_message(rnd1, rnd2, self.socket, data, icmp_header["seq_number"], True)
				return False
			filename = data.split('/', 1)[0]
			for fb in self.filebreakers:
				if fb.isForFile(filename):
					if not fb.addForConstruct(icmp_header["seq_number"] ,data.split('/', 1)[1]):
						rnd1, rnd2 = self.random_ip()
						self.send_message(rnd1, rnd2, self.socket, data, icmp_header["seq_number"], False)
						return False #echo data for me but without return home
					else:
						return False #echo data for me, constructed with no reply
			
			for bl in self.blacklist:
				if bl[0] == filename:
					self.send_message(self.node_ip, bl[1], self.socket, data, icmp_header["seq_number"], False)
					return False #echo data not for me but is in blacklist
			rnd1, rnd2 = self.random_ip()
			self.send_message(rnd1, rnd2, self.socket, data, icmp_header["seq_number"], False)
			return False  #echo data not for me and it's not in black list
		return False #echo reply data
	def receive_packet(self, current_socket):
		inputready, outputready, exceptready = select.select([current_socket, sys.stdin], [], [], self.timeout / 1000.0)
		if inputready == []: # timeout
			return False, None, None, None
		if sys.stdin in inputready:
			self.message = sys.stdin.readline()
			return True, None, None, None

		packet_data, address = current_socket.recvfrom(ICMP_MAX_RECV)
		#packet_data, address = current_socket.recvfrom(ICMP_MAX_RECV)
		#print(packet_data)
		icmp_header = self.header2dict(
			names=[
				"type", "code", "checksum",
				"packet_id", "seq_number"
			],
			struct_format="!BBHHH",
			data=packet_data[20:28]
		)
		ip_header = self.header2dict(
			names=[
				"version", "type", "length",
				"id", "flags", "ttl", "protocol",
				"checksum", "src_ip", "dest_ip"
			],
			struct_format="!BBHHHBBHII",
			data=packet_data[:20]
		)
		packet_size = len(packet_data) - 28
		return True, icmp_header, ip_header, packet_data[28:]

my_num = sys.argv[1]
print("10.0.0." + my_num.__str__())
p = Ping(((int)(my_num)))
