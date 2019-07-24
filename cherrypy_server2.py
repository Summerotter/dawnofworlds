from cherrypy import wsgiserver as wsgi
#from app import create_app, db
from fyp import fyp_create_app, fyp_db
import os

#dow = create_app(os.getenv('FLASK_CONFIG') or 'default')
fyp = fyp_create_app(os.getenv('FLASK_CONFIG') or 'default')

d = wsgi.WSGIPathInfoDispatcher({'/':fyp,})
server = wsgi.CherryPyWSGIServer(('0.0.0.0', 4999), d)

if __name__ == '__main__':
   try:
      server.start()
   except KeyboardInterrupt:
      server.stop()