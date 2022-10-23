#!/usr/bin/env bash

kvm-ok
if [ $? -ne 0 ]; then
    echo "host machine is kvm incapable, abort..."
    exit 1
fi

# for virbr0 bridge
virsh net-start default
mx=tmp
sleep 1
for x in *.xml; do 
    /cp.py "$x" $mx
    virsh define $mx
done
rm -f $mx
for i in $(virsh list --name --all); do 
    echo "start vm $i"
    virsh start $i; 
done
echo "----------list vms----------"
virsh list --all

source /pf.sh