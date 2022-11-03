# VM in Container

Run preinstalled kvm os[xml + qcow2 files] in container

Obviously you need run container with --privileged, and mount bus peripherals.   
And because of docker cgroup limitation, there is not a easy way run systemd with docker image, so I switch to podman

# Prerequisite

1. KVM capable host with podman installed
2. Preinstalled qcow2 file(s) + virsh dumped xml in same dir, lisk this:

    win11/  
    ├── OVMF_CODE_4M.ms.fd
    ├── win11.qcow2
    ├── win11_VARS.fd
    └── win11.xml

3. And then run this image with mounted os dir to container /vms

# Usage

With podman installed and then run:

    podman run \
    --privileged \
    -d --name vmic \
    -v /dev/kvm:/dev/kvm \
    -v /dev/bus/usb:/dev/bus/usb \
    -v /data/vms/macos12:/vms \
    -p 5900:5900 \
    novice/vmic

If need pci or usb passthrough plus port forwarding to guest, run it like this:

    sudo podman run \
    --privileged \
    -e PCI='01:00.0 01:00.1' \
    -e USB='8087:0a2a 04f2:b512' \
    -e PORT='22,3389' \
    -d --name vmic \
    -v /dev/kvm:/dev/kvm \
    -v /dev/bus/usb:/dev/bus/usb \
    -v /data/vms/win11:/vms \
    -p 2222:22 \
    -p 3389:3389 \
    -p 5900:5900 \
    novice/vmic

and then use vnc viewer connect to host 5900 port

# Show start logs

    podman exec -it vmic journalctl -u init

    