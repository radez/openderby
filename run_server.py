from cherrypy import wsgiserver
from openderby import app

app.debug = True
d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8080), d)


if __name__ == '__main__':
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
