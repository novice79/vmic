# VM in Container

Obviously you need run container with --privileged, and mount bus peripherals. And because of docker cgroup limitation, there is not a easy way run systemd with docker image, so I switch to podman

# Prerequisite

KVM capable host with podman installed

# Usage

install podman and then run:

    podman run \
    --privileged \
    -d --name vmic \
    -v /dev/kvm:/dev/kvm \
    -v /dev/bus/usb:/dev/bus/usb \
    -v /data/github/vmic/macos12:/vms \
    -p 5900:5900 \
    novice/vmic

if need pci or usb passthrough, run it like this:

    podman run \
    --privileged \
    -e PCI='01:00.0 01:00.1' \
    -e USB='8087:0a2a 04f2:b512' \
    -d --name vmic \
    -v /dev/kvm:/dev/kvm \
    -v /dev/bus/usb:/dev/bus/usb \
    -v /data/github/vmic/macos12:/vms \
    -p 5900:5900 \
    novice/vmic

and then use vnc viewer connect to host 5900 port

# Show start logs

    podman exec -it vmic journalctl -u init

    