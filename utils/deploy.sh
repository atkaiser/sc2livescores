git add -p
git commit
git push origin master

# ssh and setup environ
ssh sc2ls@sc2ls.mooo.com /bin/bash << EOF
  source /home/sc2ls/.bash_profile
  ps aux | grep uwsgi | grep sc2livescores | grep -v grep | sed 's/\s\+/ /g' | cut -d' ' -f2 | xargs kill -9
  ps aux | grep update_state.py | sed 's/\s\+/ /g' | cut -d' ' -f2 | xargs kill -9
  workon sc2ls
  cd /home/sc2ls/dev/sc2livescores
  git pull
  python manage.py collectstatic --noinput
  echo "Starting server ..."
  nohup uwsgi --ini sc2livescores_uwsgi.ini > logs/server.out 2> logs/server.err < /dev/null &
  cd sc2game/utils
  echo "Starting update_state process ..."
  nohup python update_state.py &> ../../logs/update.log < /dev/null &
EOF

echo "Done."
