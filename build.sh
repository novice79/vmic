#!/usr/bin/env bash

docker build --pull -t novice/vmic .

docker push novice/vmic:latest