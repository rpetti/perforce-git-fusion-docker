# Perforce Git Fusion docker container

## Container Info

### Environment Variables and Defaults

```bash
# server id to use for the git fusion server
GITFUSION_SERVER_ID=git-fusion

# time zone of the Perforce server
TZ=UTC

# how to treat git commits from users that do not map to perforce users
#  reject - block the push
#  pusher - corresponding p4 change will be authored by the pusher
#  unknown - corresponding p4 change will be authored by a special "unknown" user
GITFUSION_UNKNOWN_USER=reject

# whether git fusion repos are read only
GITFUSION_READONLY=false

# allows case-insensitive perforce servers
GITFUSION_ALLOWINSENSITIVE=false

# password to use for git fusion accounts, random if empty
GITFUSION_P4PASSWD=""

# Perforce connection details
P4PORT=perforce:1666
P4SUPERUSER=""
P4SUPERPASSWD=""
```

### Exposed Ports

- 22 - SSH

### Volumes

- `/etc/ssh` - for persisting SSH host keys
- `/opt/perforce/git-fusion/home/perforce-git-fusion` - git-fusion config and data

## Post-install actions

Git Fusion requires some triggers to be installed on the Perforce server, but the install script that's run on first startup doesn't bother doing this. The following needs to be done on the Perforce server after it's completed:

- Install python on the Perforce server
- Copy the `p4gf_submit_trigger*` files to a folder on the Perforce server
- Run `python p4gf_submit_trigger.py --install <P4PORT> <P4USER> <P4PASSWD>`

## Repo and user setup

Refer to the [User Documentation](git-fusion.pdf) for Git Fusion.
