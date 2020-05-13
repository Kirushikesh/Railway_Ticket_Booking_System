from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from flask_login import LoginManager

app=Flask(__name__)

app.config['MYSQL_USER'] = '4U7D6CjWLc'
app.config['MYSQL_PASSWORD']='CMkRdUSFBP'
app.config['MYSQL_HOST']='remotemysql.com'
app.config['MYSQL_DB']='4U7D6CjWLc'
app.config['MYSQL_CURSORCLASS']='DictCursor'

app.config['SECRET_KEY']='dbacc137b9ee97d9b616fa4bcd4ce30a'
mysql=MySQL(app)

bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view ='login'

from railwaysystem import routes