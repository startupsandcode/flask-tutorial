# My Flask Project
## build sass
```
pip install Flask-Scss
```
add it to __init__.py
and put your scss files in the assets directory.
```
from flask_scss import Scss
Scss(app,static_dir='app/static', asset_dir='app/assets')

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
