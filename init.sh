#!/usr/bin/env bash

kvm-ok
if [ $? -ne 0 ]; then
    echo "host machine is kvm incapable, abort..."
    exit 1
fi
# if mount samba directory to /data?
[ -d "/data" ] && sd=1 || sd=0
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
echo "sambauser=${sambauser:=novice}"
echo "sambapass=${sambapass:=nv}"
useradd -m -d /data $sambauser
chpasswd <<<"$sambauser:$sambapass"
usermod -aG sambashare $sambauser
echo -e "$sambapass\n$sambapass" |smbpasswd -a -s -U $sambauser
cat > /etc/samba/smb.conf << END
[global]
workgroup = WORKGROUP
log file = /var/log/samba/log.%m
max log size = 1000
logging = file
server role = standalone server
obey pam restrictions = yes
unix password sync = yes
passwd program = /usr/bin/passwd %u
passwd chat = *Enter\snew\s*\spassword:* %n\n *Retype\snew\s*\spassword:* %n\n *password\supdated\ssuccessfully* .
pam password change = yes
map to guest = bad user
[vmic-data]
path = /data
writeable=Yes
browseable = yes
create mask=0644
directory mask=0755
public=yes
END
/usr/sbin/smbd --daemon --no-process-group
while [[ ! -S /var/run/libvirt/libvirt-sock ]]; do
    sleep 2
    echo "wait for libvirt service starting ..."
done
# for virbr0 bridge
# virsh net-start default
mx="tmp_xml"
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
export sambauser sambapass sd
[ -z "$BRIDGE" ] && source /pf.sh

while [ 1 ]; do
    sleep 2
    SERVICE="/usr/sbin/libvirtd"
    if ! pidof "$SERVICE" >/dev/null; then
        echo "$SERVICE stopped. restart it"
        "$SERVICE" &
    fi
done