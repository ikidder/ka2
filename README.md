# ka2


This repo contains a side project. 
 
Corey Schafer's flask videos were tremendously helpful: https://www.youtube.com/channel/UCCezIgC97PvUuR4_gbFUs5g

---

### Connecting to the Heroku db
```
(.venv) $ heroku run python
>>> import socket, os
>>> socket.gethostname()
>>> for key in os.environ.keys():
...     print(key, os.environ[key])
... 
>>> from kamagape import *
>>> app = Flask(__name__)
>>> app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://{username}}:{password}@{server}:5432/{database}'
```

### Heroku Postgres backup and rollback
[Manual Backup and download](https://devcenter.heroku.com/articles/heroku-postgres-backups#creating-a-backup)

[Recovery after critical data loss](https://devcenter.heroku.com/articles/heroku-postgres-rollback#common-use-case-recovery-after-critical-data-loss)


### Postgres permission
GRANT ALL PRIVILEGES ON DATABASE {db} TO {user}


### Alembic bash commands
Set the env var used by alembic/env.py
```
export DATABASE_URL=''
```

Autogenerate an upgrade script:
```
alembic revision --autogenerate -m "comment"
```
Run the upgrade:
```
alembic upgrade head
```

### Generating a SECRET_KEY

os.urandom(24).hex()