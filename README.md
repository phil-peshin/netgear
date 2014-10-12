netgear
=======

Netgear GS108T management utilities

Netgear GS108T is an inexpensive managed switch with VLAN support, but unfortunately you can only manage it thru Web GUI.
So I decided to create a command line utility to manage VLANs. 

How to use
----------

INSTALLATION
sudo python setup.py install


PREPARE ENVIRONMENT
Though you can pass everything in arguments, I find it conenient to set enviromnent variables

export NETGEAR_HOST=192.168.1.200
export NETGEAR_PASSWORD=password

EXAMPLES

# list all VLANs
$ netgear vlan list
1    Default
2    Voice VLAN
3    Auto-Video
10   external
20   internal
30   data

# add 3 VLANs
$ netgear vlan add 111,112,113

# delete 3 VLANs
$ netgear vlan del 111,112,113

# add VLAN 111 with a name 'data'
$ netgear vlan add 111 data

# print all VLAN membership. Port positions left to right, legend . = removed, U = untagged, T = tagged
$ netgear vlan membership
1    U.......
2    ........
3    ........
10   .UU.....
20   ...U.U.U
30   ....U.U.
100  ...T.T.T
101 

# set VLANs 102,103,104 membership, tagged ports #4,6,8
$ netgear vlan membership 102,103,104 ...T.T.T

# print PVID
$ netgear vlan pvid
1    1 all
2   10 all
3   10 all
4   20 all
5   30 all
6   20 all
7   30 all
8   20 all

# set VLAN #100 for ports 2,3,4 allowing 'all' traffic (tagged and untagged)
$ netgear vlan pvid 2,3,4 100 all

# set VLAN #200 for ports 5,6,7 allowing only 'vlan' traffic
$ netgear vlan pvid 5,6,7 200 vlan



(c) Philip Peshin, phil.peshin@gmail.com
October 12, 2014


