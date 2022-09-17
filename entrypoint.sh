#!/bin/sh
set -e

if [ ! -f ~git/is_configured ]; then

    if [ "$GITFUSION_READONLY" = "true" ]; then
        READONLYOPT="--readonly"
    else
        READONLYOPT=""
    fi

    if [ "$GITFUSION_ALLOWINSENSITIVE" = "true" ]; then
        ALLOWINSENSITIVEOPT="--allow-insensitive"
    else
        ALLOWINSENSITIVEOPT=""
    fi

    if [ -z "$GITFUSION_P4PASSWD" ]; then
        GITFUSION_P4PASSWD=$(date +%s | sha256sum | base64 | head -c 32)
    fi

    /opt/perforce/git-fusion/libexec/configure-git-fusion.sh -n -m --server remote \
        $READONLYOPT --super "$P4SUPERUSER" --superpassword "$P4SUPERPASSWD" \
        --gfp4password "$GITFUSION_P4PASSWD" \
        --id "$GITFUSION_SERVER_ID" --p4port "$P4PORT" --timezone "$TZ" \
        --unknownuser "$GITFUSION_UNKNOWN_USER" \
        $ALLOWINSENSITIVEOPT

    touch ~git/is_configured
fi

ssh-keygen -A

#sshd
/usr/sbin/sshd -D -o ListenAddress=0.0.0.0 &
#cron
/usr/sbin/crond -n &
#TODO: graceful shutdown
wait