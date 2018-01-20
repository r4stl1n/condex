#!/bin/sh

SESSION='Condex'
WORKER=4
tmux -2 new-session -d -s $SESSION

# Update Latest git repository
tmux send-keys "git pull" C-m

tmux new-window -t $SESSION:1 -n 'Stats'
tmux send-keys 'source .env/bin/activate' C-m
tmux send-keys 'python main.py' C-m
tmux send-keys 'index stop' C-m

# Start Celery
tmux new-window -t $SESSION:2 -n 'Celery'
tmux send-keys 'source .env/bin/activate' C-m
tmux send-keys 'celery -A Tasks worker -B --loglevel=INFO --concurrency=8 -Q Condex-Trade-Queue -n Condex-Trade-Worker' C-m

# Start Celery
tmux new-window -t $SESSION:3 -n 'Celery'
tmux send-keys 'source .env/bin/activate' C-m
tmux send-keys 'celery -A Tasks worker --loglevel=INFO --concurrency=2 -Q Condex-Update-Queue -n Condex-Update-Worker' C-m

#tmux new-window -t $SESSION:3 -n 'MySQL'

# Change to Stats Session
tmux select-window -t $SESSION:1

# Attach to session
tmux -2 attach-session -t $SESSION
