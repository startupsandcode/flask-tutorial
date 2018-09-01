# My Flask Project
## build sass
```
python setup.py build_sass
```
## deploy to heroku
```
git push heroku deploy:master
```
## db changes
```
flask db migrate -m "Your migration note"
flask db upgrade
```
