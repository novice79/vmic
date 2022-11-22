#!/usr/bin/env bash

echo "get guest vm nat ip address, please wait ..."
while [ 1 ]; do
    sleep 1
    vm_ip=$(virsh net-dhcp-leases default | awk 'FNR == 3 {print $5}')
    if [[ -n "$vm_ip" ]]; then
        vm_ip=${vm_ip%/*}
        nft add table novice
        nft add chain novice pre { type nat hook prerouting priority dstnat\; }
        # nft add rule novice pre tcp dport { 22, 80, 443, 1024-5899, 5910-65534 } dnat to $vm_ip
        nft add rule novice pre tcp dport { {{ports}} } dnat to $vm_ip
        nft delete table ip filter
        nft list ruleset | grep -A 5 novice
        break
    fi
done

if [ $sd -eq 1 ]; then
    echo "todo: ssh or winrm into guest to execute mount samba path command"
fi