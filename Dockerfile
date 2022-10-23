FROM ubuntu:22.04
LABEL maintainer="Novice <novice79@126.com>"


ENV DEBIAN_FRONTEND noninteractive   
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8
COPY ins_pack.sh /ins_pack.sh
COPY init.sh /init.sh
COPY pf.sh /pf.sh
COPY cp.py /cp.py
COPY tmpl /tmpl
RUN /ins_pack.sh


WORKDIR /vms
# COPY macos12 .
EXPOSE 22 5900

ENTRYPOINT ["/lib/systemd/systemd"]