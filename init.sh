#!/usr/bin/env bash

kvm-ok
if [ $? -ne 0 ]; then
    echo "host machine is kvm incapable, abort..."
    exit 1
fi
# start libvirt services
dbus-uuidgen > /var/lib/dbus/machine-id
mkdir -p /var/run/dbus
dbus-daemon --config-file=/usr/share/dbus-1/system.conf --print-address

source /etc/default/virtlogd
/usr/sbin/virtlogd $VIRTLOGD_ARGS &
source /etc/default/virtlockd
/usr/sbin/virtlockd $VIRTLOCKD_ARGS &
source /etc/default/libvirtd
/usr/sbin/libvirtd $LIBVIRTD_ARGS &
# for virbr0 bridge
# virsh net-start default
mx="tmp_xml"
sleep 1
for x in *.xml; do 
    /cp.py "$x" $mx
    virsh define $mx
done
rm -f $mx
for i in $(virsh list --name --all); do 
    echo "starting vm $i , please wait ..."
    virsh start $i; 
done
echo "----------list vms----------"
virsh list --all

[ -z "$BRIDGE" ] && source /pf.sh

while [ 1 ]; do
    sleep 2
    SERVICE="/usr/sbin/libvirtd"
    if ! pidof "$SERVICE" >/dev/null; then
        echo "$SERVICE stopped. restart it"
        "$SERVICE" &
    fi
done