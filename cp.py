#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import os
import sys
import re
from jinja2 import Environment, FileSystemLoader

if len(sys.argv) != 3:
    print("Need in/out xml file name to process")
    sys.exit(1)
PCI, USB, PORT, CPU, RAM, VGPU = None, None, None, None, None, None
PASS = None
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
    if kv[0] == 'CPU':
        CPU = kv[1]
        print("CPU=" + CPU)
    if kv[0] == 'RAM':
        RAM = kv[1]
        print("RAM=" + RAM)
    if kv[0] == 'VGPU':
        VGPU = kv[1]
        print("VGPU=" + VGPU)
    if kv[0] == 'PASS':
        PASS = kv[1]
        print("PASS=" + PASS)
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
if CPU is not None and CPU.isnumeric():
    root.find('vcpu').text = CPU
    root.remove(root.find("cpu"))
    cpu = f"""
    <cpu mode='host-passthrough' check='none' migratable='on'>
        <topology sockets='1' dies='1' cores='1' threads='{CPU}'/>
    </cpu>
    """
    root.append(ET.XML(cpu))
if RAM is not None:
    for i in range(0, 1):
        m, v = root.find('memory'), None
        if RAM[-1] == "G" or RAM[-1] == "M" or RAM[-1] == "K":
            unit = RAM[-1]
            v = m.text = RAM[:-1]
        elif RAM.isnumeric():
            unit = 'G'
            v = m.text = RAM
        else:
            break
        m.set('unit', f'{unit}iB')
        m = root.find('currentMemory')
        m.text = v
        m.set('unit', f'{unit}iB')
if VGPU is not None:
    tmpl = environment.get_template("vgpu.xml")
    vg = tmpl.render( uuid = VGPU )
    print(vg)
    devices.append(ET.XML(vg))

if PASS is not None:
    devices.find('graphics').set('passwd', PASS)
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