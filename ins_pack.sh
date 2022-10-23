#!/usr/bin/env bash

apt-get update
apt-get install -y \
systemd systemd-sysv \
qemu-kvm libvirt-daemon-system libvirt-clients \
cpu-checker nftables python3-pip

pip3 install Jinja2

sed -i '/user = "root"/s/^#//;/group = "root"/s/^#//;s/^#remember_owner = 1/remember_owner = 0/;' \
/etc/libvirt/qemu.conf 
# optional
# apt-get install -y \
# lsb-release sudo wget curl gnupg2 \
# libguestfs-tools libosinfo-bin \
# virtinst bridge-utils

tee /etc/systemd/system/init.service << END
[Unit]
Description=my init script
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/vms
ExecStart=/init.sh

[Install]
WantedBy=multi-user.target
END

systemctl enable init.service
# journalctl -u init
rm -- "$0"