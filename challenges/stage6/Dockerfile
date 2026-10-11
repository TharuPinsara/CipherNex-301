FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    sudo \
    bash \
    coreutils \
    procps \
    nano \
    curl \
    iproute2 \
    sed \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/sshd

RUN useradd -m -s /bin/bash ground-user && \
    echo "ground-user:SatTrack#2024!Ops" | chpasswd

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

COPY flag.txt /root/flag.txt
RUN chown root:root /root/flag.txt && chmod 0400 /root/flag.txt

COPY orbital-sync.service /etc/systemd/system/orbital-sync.service
COPY orbital-sync.timer /etc/systemd/system/orbital-sync.timer
RUN chmod 644 /etc/systemd/system/orbital-sync.*

# Decoy timers
RUN mkdir -p /lib/systemd/system && \
    touch /lib/systemd/system/logrotate.service /lib/systemd/system/logrotate.timer \
          /lib/systemd/system/apt-daily.service /lib/systemd/system/apt-daily.timer \
          /lib/systemd/system/motd-news.service /lib/systemd/system/motd-news.timer \
          /lib/systemd/system/fstrim.service /lib/systemd/system/fstrim.timer \
          /lib/systemd/system/systemd-tmpfiles-clean.timer && \
    chmod 644 /lib/systemd/system/*

RUN mkdir -p /opt/orbital-sync
COPY sync_job.sh /opt/orbital-sync/sync_job.sh
COPY systemctl /usr/local/bin/systemctl
COPY entrypoint.sh /entrypoint.sh

# CRITICAL FIX: Strip any Windows carriage returns (\r) automatically
RUN sed -i 's/\r$//' /entrypoint.sh /usr/local/bin/systemctl /opt/orbital-sync/sync_job.sh && \
    chmod 755 /entrypoint.sh /usr/local/bin/systemctl && \
    chmod 777 /opt/orbital-sync/sync_job.sh

EXPOSE 22

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
