from mininet.topo import Topo

class Part3Topo( Topo ):

    def __init__( self, test_number):
        switch_num = 2
	if test_number == 8:
		switch_num = 7

        Topo.__init__( self )

        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )

	#creating n switches
	s = []
	for i in range(switch_num):
		s.append(self.addSwitch('s' + i.__str__()))

	#adding links
        self.add_link(h1, s[0], test_number)
        self.add_link(h2, s[switch_num-1], test_number)
	for i in range(switch_num - 1):
		self.add_link(s[i], s[i+1], test_number)

    def add_link(self, a, b, test_number):
	if test_number == 1:
		self.addLink(a, b, delay='20ms');
	elif test_number == 2:
		self.addLink(a, b, delay='90ms');
	elif test_number == 3:
		self.addLink(a, b, delay='10ms', bw=1);
	elif test_number == 4:
		self.addLink(a, b, delay='10ms', bw=15);
	elif test_number == 5:
		self.addLink(a, b, delay='10ms', max_queue_size=1);
	elif test_number == 6:
		self.addLink(a, b, delay='10ms', max_queue_size=15);
	else:
		self.addLink(a, b, delay='10ms');


topos = {'part4topo1': ( lambda: Part3Topo(1) ), 'part4topo2': ( lambda: Part3Topo(2) ),  'part4topo3': ( lambda: Part3Topo(3) ),  'part4topo4': ( lambda: Part3Topo(4) ),  'part4topo5': ( lambda: Part3Topo(5) ),  'part4topo6': ( lambda: Part3Topo(6) ), 'part4topo7': ( lambda: Part3Topo(7) ),  'part4topo8': ( lambda: Part3Topo(8) )}
