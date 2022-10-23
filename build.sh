#!/usr/bin/env bash

podman build -t docker.io/novice/vmic .

# podman tag localhost/novice/vmic docker.io/novice/vmic
podman push docker.io/novice/vmic