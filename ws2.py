from gevent import monkey ; monkey.patch_all()
from bottle import request, abort, default_app

app = default_app()

@app.route('/websocket')
def handle_websocket():
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')
    wsock.send("helloooooooo")
    while True:
        try:
            message = wsock.receive()
            wsock.send("Your message was: %r" % message)
        except WebSocketError:
            print("ERR")
            break
        pass
    pass

@app.route('/static/<path:path>')
def statics(path):
    return static_file(path, 'static')

@app.route('/tmpl/<path:path>')
def statics(path):
    return static_file(path, 'tmpl')

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
    <html>
    <head>
    <script type="text/javascript">
    WS=(L,x)=>`ws${L.protocol.substr(4)}//${L.host}`+x;
    var ws = new WebSocket(WS(location,"/websocket"));
    ws.onopen = function() {
    ws.send("Hello, world");
    };
    ws.onmessage = function (evt) {
    alert(evt.data);
    };
    </script>
    </head>
    </html>
'''

from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
server = WSGIServer(("0.0.0.0", 8081), app,
                    handler_class=WebSocketHandler)
server.serve_forever()
