#!/usr/bin/env bash

apt-get update
apt-get install -y \
qemu-kvm libvirt-daemon-system libvirt-clients \
cpu-checker nftables python3-pip samba

pip3 install Jinja2
# pip3 install pywinrm

sed -i '/user = "root"/s/^#//;/group = "root"/s/^#//;s/^#remember_owner = 1/remember_owner = 0/;' \
/etc/libvirt/qemu.conf 

rm -- "$0"