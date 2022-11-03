#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import os
import sys
import re
from jinja2 import Environment, FileSystemLoader

if len(sys.argv) != 3:
    print("Need in/out xml file name to process")
    sys.exit(1)
PCI, USB, PORT = None, None, None
env = open('/proc/1/environ', 'r')
for e in env.read().split("\0"):
    kv = e.split('=')
    # print(kv)
    if kv[0] == 'PCI':
        PCI = kv[1]
        print("PCI=" + PCI)
    if kv[0] == 'USB':
        USB = kv[1]
        print("USB=" + USB)
    if kv[0] == 'PORT':
        PORT = kv[1]
        print("PORT=" + PORT)
env.close()

vm_path = "/vms/"
tree = ET.parse(sys.argv[1])
root = tree.getroot()

to_del = ['uuid', 'devices/interface/mac']
for x in to_del:
    for d in root.findall(x):
        print("clear--->%s" %  (d.text or d.get('address')) )
        d.clear()
        # root.remove(d)

to_mod = ['loader', 'nvram']
for xp in to_mod:
    for p in root.iter(xp):
        to_path = vm_path + os.path.basename(p.text)
        print("%s--->%s" % (p.text, to_path))
        p.text = to_path


for d in root.findall('./devices/disk/source'):
    to_path = vm_path + os.path.basename(d.get('file'))
    print("%s--->%s" % (d.get('file'), to_path))
    d.set('file', to_path)

nic = root.find('devices/interface')
if nic is not None:
    print("%s--->%s" % (nic.get('type'), 'bridge'))
    nic.set('type', 'bridge')

br = root.find('devices/interface/source')
if br is not None:
    print("%s--->%s" % (br.get('bridge'), 'virbr0'))
    br.set('bridge', 'virbr0')

devices = root.find('devices')
for d in root.findall('./devices/hostdev'):
    devices.remove(d)

for c in devices:
    # ga stand for guest address
    ga = c.find('address')
    if ga is not None:
        c.remove(ga)

environment = Environment(loader=FileSystemLoader("/tmpl/"))
# -e PCI='01:00.0.on 01:00.1' -e USB='8087:0a2a 04f2:b512'
# PCI = os.getenv('PCI')
if PCI is not None:
    tmpl = environment.get_template("pci.xml")
    for p in PCI.split():
        pc = re.split(r':|\.', p)
        pci_host_dev = tmpl.render(
            bus = pc[0],
            slot = pc[1],
            func = pc[2],
            mf = 'on' if len(pc) > 3 and pc[3] == 'on' else 'off'
        )
        print(pci_host_dev)
        devices.append(ET.XML(pci_host_dev))

# USB = os.getenv('USB')
if USB is not None:
    tmpl = environment.get_template("usb.xml")
    for u in USB.split():
        usb = re.split(r':|\.|\s', u)
        pci_host_dev = tmpl.render(
            vendor = usb[0],
            product= usb[1]
        )
        print(pci_host_dev)
        devices.append(ET.XML(pci_host_dev))

tree.write(sys.argv[2])
pf_script = "/pf.sh"
if PORT is None:
    PORT = '22'
tmpl = environment.get_template("pf.sh")
nft = tmpl.render( ports = PORT )   
f = open(pf_script, "w")
f.write(nft)
f.close()
os.chmod(pf_script, 0o755)