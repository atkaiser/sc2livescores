ps aux | grep runserver | sed 's/\s\+/ /g' | cut -d' ' -f2 | xargs kill
ps aux | grep update_state.py | sed 's/\s\+/ /g' | cut -d' ' -f2 | xargs kill