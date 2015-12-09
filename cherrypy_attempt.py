from cherrypy import wsgiserver as wsgi
from app import create_app, db
import os

dow = create_app(os.getenv('FLASK_CONFIG') or 'default')

d = wsgi.WSGIPathInfoDispatcher({'/': dow})
server = wsgi.CherryPyWSGIServer(('0.0.0.0', 80), d)

if __name__ == '__main__':
   try:
      server.start()
   except KeyboardInterrupt:
      server.stop()