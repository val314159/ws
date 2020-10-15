import bottle, hashlib, jinja2, json
from collections import defaultdict
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketServer

loader = jinja2.FileSystemLoader("tmpl")
escape = jinja2.select_autoescape(['html', 'xml'])
env = jinja2.Environment(autoescape=escape, loader=loader)

def md5(s): return hashlib.md5(s.encode()).hexdigest()
def g(s):   return "https://gravatar.com/gravatar/"+md5(s)
def render_file(name, data):
    return env.get_template(name).render(data)

env.filters['md5'] = md5
env.filters['g'] = g

@bottle.get('/')
def index():
    raise bottle.redirect('/static/index.html')

@bottle.get('/static/<path:path>')
def serve_static(path):
    return bottle.static_file(path, 'static')

@bottle.get('/tmpl/<path:path>')
def serve_template(path):
    data = dict(
        arr = [ "xx", "yy", "zz" ]
    )
    return render_file(path, data)

connections = []
channels = defaultdict(list)
channels['main']
channels['request']
channels['response']

def publish(ch, data):
    j = json.dumps(data)
    for w in channels[ch]:
        try:
            w.send(j)
        except WebSocketError as e:
            print("EEEEE", e)
            pass
        except Exception as e:
            print("XXXXX", e)
            pass
        pass
    pass

def find_wsock(uuid):
    for c in connections:
        if id(c) == uuid:
            return c

@bottle.put('/ps/pub/<ch>')
def pub(ch, uuid=''):
    uuid = bottle.request.query('uuid', uuid)
    data = bottle.request.body.read(-1)
    wsock = find_wsock(uuid)
    publish(ch, data)
    return "{}\n"

@bottle.get('/ps/sub/<ch>')
def sub(ch, uuid=''):
    uuid = bottle.request.query('uuid', uuid)
    wsock = find_wsock(uuid)
    channels[ch].append(wsock)
    return "{}\n"

@bottle.get('/ps/uns/<ch>')
def uns(ch, uuid=''):
    uuid = bottle.request.query('uuid', uuid)
    wsock = find_wsock(uuid)
    channels[ch].remove(wsock)
    return "{}\n"

@bottle.get('/websocket')
def handle_websocket():
    wsock = bottle.request.environ.get('wsgi.websocket')
    if not wsock:
        raise bottle.abort(400, 'Expected WebSocket request.')
    connections.append(wsock)
    try:
        def send(action, **kw):
            wsock.send(json.dumps(dict(action=action,**kw)))
            return
        send("hello", uuid=id(wsock))
        message = wsock.receive()
        while message:
            data = json.loads(message)
            send("echo", data=message)
            message = wsock.receive()
            pass
    except WebSocketError as e:
        print("E", e)
    except Exception as e:
        print("X", e)
        pass
    connections.remove(wsock)
    pass

app = bottle.default_app()
WebSocketServer(("0.0.0.0", 8080), app).serve_forever()
