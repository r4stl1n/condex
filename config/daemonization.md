## Daemonization
This assumes Ubuntu installation. Instructions will vary based on distribution

### Celery Configuration File
1. put the condex.celery file somewhere on your filesystem *not* in the working copy.
2. edit condex.celery and replace the token in `CELERY_BIN` to the path inside of your virtual environment where you've installed celery

### Condex Service File
1. copy the condex.service file to `/etc/systemd/system`
2. edit the token `EnvironmentFile` to be the path where you placed the condex.celery file earlier
3. edit the token `WorkingDirectory` to be the path where you cloned Condex
4. as a sudoer run `sudo systemctl daemon-reload`. You'll need to run this step any time you modify the condex.service file

### Starting the Daemon
`sudo systemctl start condex`

### Stopping the Daemon
`sudo systemctl stop condex`

### Restarting the Daemon
`sudo systemctl restart condex`

