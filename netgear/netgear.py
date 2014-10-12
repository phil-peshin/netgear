from __future__ import print_function

__author__ = "Philip Peshin"
__copyright__ = "Copyright 2014, Philip Peshin"
__license__ = "GPL"
__version__ = "0.0.1"
__email__ = "phil.peshin@gmail.com"

import requests, os, re
from optparse import OptionParser

class Netgear:

    def __init__(self, options):
        self.options = options

    def check_result(self, response):
        error_message = re.findall(r'<INPUT.*NAME="err_msg".*VALUE="\s*(.*)\s">', response.text)
        error_flag = re.findall(r'<INPUT.*NAME="err_flag".*VALUE="(.*)">', response.text)
        if len(error_flag) > 0 and int(error_flag[0]) != 0:
            print(error_message[0])
            exit(error_flag[0])

    def login(self):
        self.session = requests.Session()
        response = self.session.post('http://{host}/base/main_login.html'.format(**self.options.__dict__), dict(pwd=self.options.password))

    def vlan_cfg(self):
        response = self.session.get('http://{host}/switching/dot1q/vlan_cfg.html'.format(**self.options.__dict__))
        vlanIds = dict(re.findall(r'<INPUT.*NAME="(\d*.\d*.\d*).vlanId".*VALUE="(\d*)">', response.text))
        vlanNames = dict(re.findall(r'<INPUT.*NAME="(\d*.\d*.\d*).vlanName".*VALUE="(.*)".*>', response.text))
        vlans = dict()
        for position, id in vlanIds.items():
            vlans[id] = dict(name=vlanNames[position], position=position)
        return vlans

    def vlan_list(self):
        result = dict()
        cfg = self.vlan_cfg()
        for id in sorted(cfg.keys(), key=lambda x: int(x)):
            print("{id} {name}".format(id=id.ljust(4), name=cfg[id]['name']))
        return result

    def vlan_add(self, ids, name=None):
        for id in ids.split(','):
            if not name:
                name = 'vlan-' + id.zfill(4)
            response = self.session.post('http://{host}/switching/dot1q/vlan_cfg.html'.format(**self.options.__dict__),
                              dict(add=16, vlan_id=id, vlan_name=name, vlan_type='Static'))
            self.check_result(response)

    def vlan_del(self, ids):
        self.vlan_delete(ids)

    def vlan_delete(self, ids):
        cfg = self.vlan_cfg()
        params = dict(delete=16)
        for id in ids.split(','):
            if id not in cfg:
                print('No such VLAN: ' + id)
                exit(1)
            params[cfg[id]['position'] + '.CBox_1'] = 'checkbox'
            params[cfg[id]['position'] + '.vlanId'] = id
        response = self.session.post('http://{host}/switching/dot1q/vlan_cfg.html'.format(**self.options.__dict__), params)
        self.check_result(response)

    def vlan_membership_set(self, ids, value):
        decode = {'.': '3', 'U': '2', 'T': '1'}
        line = ''
        for c in value:
            line += decode[c]
            line += ','
        line += '3,3,3,3'
        for id in ids.split(','):
            response = self.session.post('http://{host}/switching/dot1q/vlan_port_cfg_rw.html'.format(**self.options.__dict__),
                                         dict(submt=16, vlanid=id, hiddenMem=line))
            self.check_result(response)


    def vlan_membership_get(self, id):
        response = self.session.post('http://{host}/switching/dot1q/vlan_port_cfg_rw.html'.format(**self.options.__dict__),
                                     dict(submt=0, vlanid=id))
        self.check_result(response)
        membership = dict(re.findall(r'toggleImage\(this,(\d),0,\'img_unit1\'\).*\/base\/images\/grey_(.).gif', response.text))
        result = ''
        decode = dict(b='.', u='U', t='T')
        for port in sorted(membership.keys(), key=lambda x: int(x)):
            result += decode[membership[port]]
        return result

    def vlan_membership(self, ids=None, membership=None):
        if ids:
            if membership:
                self.vlan_membership_set(ids, membership)
            else:
                for id in ids.split(','):
                    print("{vlan} {membership}".format(vlan=id.ljust(4), membership=self.vlan_membership_get(id)))
            return
        cfg = self.vlan_cfg()
        for id in sorted(cfg.keys(), key=lambda x: int(x)):
            print("{vlan} {membership}".format(vlan=id.ljust(4), membership=self.vlan_membership_get(id)))

    def vlan_pvid(self, ports=None, vlan=None, type='all'):
        if not ports:
            response = self.session.get('http://{host}/switching/dot1q/qnp_port_cfg_rw.html'.format(**self.options.__dict__))
            pvid = re.findall(r'>g(\d)<.*\s*.*>(\d*)<.*\s*.*>(\d*)<.*\s*.*>(.*)<', response.text)
            decode = {'VLAN Only': 'vlan', 'Admit All': 'all'}
            for port, vlan_new, vlan_current, mode in pvid:
                print("{port} {vlan} {mode}".format(port=port, vlan=vlan_current.rjust(4), mode=decode[mode]))
        else:
            port_list = ports.split(',')
            selectedPorts = ''
            for port in port_list:
                selectedPorts += 'g{port};'.format(port=port)
            response = self.session.post('http://{host}/switching/dot1q/qnp_port_cfg_rw.html'.format(**self.options.__dict__),
                                         dict(submt=16, selectedPorts=selectedPorts, pvid=vlan, ftype=type, multiple_ports=len(port_list)))
            self.check_result(response)

def main():
    parser = OptionParser(usage='''
Netgear GS108T management utility
---------------------------------

List all VLANs:
    netgear vlan list

Add VLAN(s):
    netgear vlan add <comma separated VLAN ids> [<VLAN name>]

Delete VLAN(s):
    netgear vlan del <comma separated VLAN ids>

Print VLAN membership for all VLANs:
    netgear vlan membership

Print VLAN membership for VLANs:
    netgear vlan membership <comma separated VLAN ids>

Set VLAN membership for VLANs:
    netgear vlan membership <comma separated VLAN ids> <input>
Membership input format:
    . - removed
    U - untagged
    T - tagged
Example:
    netgear vlan membership 100,101 U....TTT
Untag port #1; remove ports 2,3,4,5; Tag ports 6,7,8 on VLANs 100 and 101

List PVID:
    netgear vlan pvid

Set PVID
    netgear vlan pvid <Comma separated ports, starting with 1> <VLAN> <mode vlan | all>
Examples:
    netgear vlan pvid 4,6,8 30 all
    netgear vlan pvid 3,4,5 40 vlan

    ''')
    parser.add_option("", "--host", default=os.getenv('NETGEAR_HOST', None), help="Netgear hostname or IP")
    parser.add_option("-p", "--password", default=os.getenv('NETGEAR_PASSWORD', 'password'), help="Netgear password")
    (options, args) = parser.parse_args()
    if not options.host:
        print('use --host or NETGEAR_HOST environment variable to specify Netgear hostname or IP address')
        exit(1)
    if len(args) == 0:
        parser.print_help()
        exit(1)

    nergear = Netgear(options)
    nergear.login()
    getattr(nergear, args[0] + "_" + args[1])(*args[2:])

if __name__ == "__main__":
    main()