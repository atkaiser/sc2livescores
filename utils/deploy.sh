git add -p
git commit
git push origin master

# ssh and setup environ
ssh sc2ls-dev@sc2ls.mooo.com /bin/bash << EOF
  source /home/sc2ls-dev/.bash_profile
  ps aux | grep runserver | sed 's/\s\+/ /g' | cut -d' ' -f2 | xargs kill
  ps aux | grep update_state.py | sed 's/\s\+/ /g' | cut -d' ' -f2 | xargs kill
  cd /home/sc2ls-dev/dev/sc2livescores
  git pull
  nohup python manage.py runserver 0.0.0.0:3000 > logs/server.out 2> logs/server.err < /dev/null &
  cd sc2game/utils
  nohup python update_state.py > ../../update.log 2> ../../update.err < /dev/null &
EOF

