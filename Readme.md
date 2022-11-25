# This is for kvm+libvirt virtual machine running in docker container

Run preinstalled kvm os[xml + qcow2 files] in container

Obviously you need run container with --privileged, and mount bus peripherals.   


# Prerequisite

1. KVM capable host with docker installed
2. Preinstalled qcow2 file(s) + virsh dumped xml in same dir, lisk this:

    win11/  
    ├── OVMF_CODE_4M.ms.fd  
    ├── win11.qcow2  
    ├── win11_VARS.fd  
    └── win11.xml  

3. And then run this image with mounted os dir to container /vms

# Usage

    docker run \
    --pull always \
    --privileged \
    -d --name vmic \
    --cgroupns=host \
    -v /run/udev:/run/udev:ro \
    -v /dev/kvm:/dev/kvm \
    -v /dev/bus/usb:/dev/bus/usb \
    -v /data/github/vmic/win7x64:/vms \
    -p 5900:5900 \
    novice/vmic

If need pci or usb passthrough plus port forwarding to guest, run it like this:

    docker run \
    --privileged \
    -e PCI='01:00.0 01:00.1' \
    -e USB='8087:0a2a 04f2:b512' \
    -e PORT='22,3389' \
    -d --name vmic \
    --cgroupns=host \
    -v /run/udev:/run/udev:ro \
    -v /dev/kvm:/dev/kvm \
    -v /dev/bus/usb:/dev/bus/usb \
    -v /data/vms/win11:/vms \
    -p 2222:22 \
    -p 3389:3389 \
    -p 5900:5900 \
    novice/vmic

If need passthrough Intel GVT-g or nvidia vGPU, and set cpu or memory capacity, or spice|vnc password  
run command some thing like this:

    docker run \
    --privileged \
    -e CPU='8' \
    -e RAM='8G' \
    -e VGPU='79e66c46-b15e-4f21-9431-007c23c1cf9e' \
    -e PASS='letmein' \
    -d --name vmic \
    --cgroupns=host \
    -v /run/udev:/run/udev:ro \
    -v /dev/kvm:/dev/kvm \
    -v /dev/bus/usb:/dev/bus/usb \
    -v /data/vms/win11:/vms \
    -p 5900:5900 \
    novice/vmic

FYI. ram unit can be G | M | K, e.g. 8G or 8192M or 8388608K

and then use vnc/remote viewer connect to host 5900 port

# Show start logs

    docker logs vmic 

# There are some prepacked os container  

- novice/vmic:winxp_zh
- novice/vmic:win7x86_en
- novice/vmic:win7x64_zh
- novice/vmic:win11_en 
- novice/vmic:ubdt      *ubuntu 22.04 desktop* 

default username/password: novice/nv

you can run it without mount /vms directory, some thing like this:

    docker run \
    --privileged \
    -e CPU='2' \
    -e RAM='2G' \
    -e PORT='3389' \
    -d --name winxp \
    --cgroupns=host \
    -v /run/udev:/run/udev:ro \
    -v /dev/kvm:/dev/kvm \
    -v /dev/bus/usb:/dev/bus/usb \
    -p 5900:5900 \
    -p 3389:3389 \
    novice/vmic:winxp_zh

And then vnc/rdp (default: 5900/3389) into it