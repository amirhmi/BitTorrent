ip netns add h1
ip netns add h2
ip netns add h3
ovs-vsctl add-br s1
ovs-vsctl add-br s2
ip link add s1-eth1 type veth peer name h1-eth1
ip link add s1-eth2 type veth peer name h2-eth1
ip link add s1-eth3 type veth peer name s2-eth1
ip link add s2-eth2 type veth peer name h3-eth1
ip link set h1-eth1 netns h1
ip link set h2-eth1 netns h2
ip link set h3-eth1 netns h3
ovs-vsctl add-port s1 s1-eth1
ovs-vsctl add-port s1 s1-eth2
ovs-vsctl add-port s1 s1-eth3
ovs-vsctl add-port s2 s2-eth1
ovs-vsctl add-port s2 s2-eth2
ovs-vsctl set-controller s1 tcp: 127.0.0.1
ovs-vsctl set-controller s2 tcp: 127.0.0.1
ifconfig s1-eth1 up
ifconfig s1-eth2 up
ifconfig s1-eth3 up
ifconfig s2-eth1 up
ifconfig s2-eth2 up
ip netns exec h1 ifconfig h1-eth1 10.0.0.1
ip netns exec h1 ifconfig lo up
ip netns exec h2 ifconfig h2-eth1 10.0.0.2
ip netns exec h2 ifconfig lo up
ip netns exec h3 ifconfig h3-eth1 10.0.0.3
ip netns exec h3 ifconfig lo up