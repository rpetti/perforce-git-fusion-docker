FROM oraclelinux:7.9

RUN rpm --import https://package.perforce.com/perforce.pubkey
COPY perforce.repo /etc/yum.repos.d/perforce.repo
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm \
    && yum install -y git git-lfs openssh-server cronie git helix-git-fusion-2017.2 \
    && yum install -y patch \
    && yum clean all \
    && rm -rf /var/cache/yum

COPY patches /tmp/patches

RUN bash -c "for p in /tmp/patches/*.patch; do patch -p0 <\$p; done"

VOLUME /opt/perforce/git-fusion/home/perforce-git-fusion
VOLUME /etc/ssh

EXPOSE 22
EXPOSE 8080

COPY entrypoint.sh /entrypoint.sh

ENV GITFUSION_SERVER_ID=git-fusion
ENV TZ=UTC
ENV GITFUSION_UNKNOWN_USER=reject
ENV GITFUSION_READONLY=false
ENV GITFUSION_ALLOWINSENSITIVE=false
ENV GITFUSION_P4PASSWD=""
ENV P4PORT=perforce:1666
ENV P4SUPERUSER=""
ENV P4SUPERPASSWD=""
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/perforce/git-fusion/bin:/opt/perforce/git-fusion/libexec
ENV LANG=en_US.UTF-8

ENTRYPOINT ["/entrypoint.sh"]
