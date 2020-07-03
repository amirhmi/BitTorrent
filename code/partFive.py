from mininet.topo import Topo

class Part5Topo( Topo ):

    def __init__( self ):
	n = 5
        Topo.__init__( self )

	s = self.addSwitch('s1')
	h = []
	for i in range(n):
		h.append(self.addHost('h' + (i + 1).__str__()))
	for i in range(n):
		self.addLink(h[i], s, delay='40ms', max_queue_size=100)

topos = { 'part5topo': ( lambda: Part5Topo() ) }
