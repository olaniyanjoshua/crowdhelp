from distutils.log import debug
from pkg import app

if __name__=="__main__":
   # app.config["SECRET_KEY"]="abubu25hbu2747862k&t3y87hdb#$3UHjs"
   # app.config["ADMIN_EMAIL"]= "admin@personal.com"
   #app.config.from_pyfile("config.py")
   #app.run(debug=True)
   app.run(debug=True,port=8100)