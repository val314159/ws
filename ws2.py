from geventwebsocket import WebSocketError
from geventwebsocket import WebSocketServer
import bottle, json

@bottle.route('/')
def handle_index():
    return '''
<!DOCTYPE html>
<html>
<head>
<script type="text/javascript">
var ws = new WebSocket("ws://localhost:8080/websocket");
ws.onopen = function() {
  ws.send("Hello, world");
};
ws.onmessage = function (evt) {
  alert(evt.data);
};
</script>
</head>
</html>'''

@bottle.route('/websocket')
def handle_websocket():
    wsock = bottle.request.environ.get('wsgi.websocket')
    if not wsock:
        bottle.abort(400, 'Expected WebSocket request.')

    try:
        while True:
            message = wsock.receive()
            wsock.send("Your message was: %r" % message)
    except WebSocketError:
        pass # break
    pass

WebSocketServer(("", 8080), bottle.app()).serve_forever()
