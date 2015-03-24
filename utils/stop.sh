ps aux | grep uwsgi | sed 's/\s\+/ /g' | cut -d' ' -f2 | xargs kill -9
ps aux | grep update_state.py | sed 's/\s\+/ /g' | cut -d' ' -f2 | xargs kill -9
