import bottle
import jinja2
import hashlib
def md5(s):
    return hashlib.md5(s.encode()).hexdigest()
def g(s):
    return "https://gravatar.com/gravatar/"+md5(s)
loader = jinja2.FileSystemLoader("tmpl")
autoescape = jinja2.select_autoescape(['html', 'xml'])
env = jinja2.Environment(autoescape=autoescape,
                         loader=loader)
env.filters['md5'] = md5
env.filters['g'] = g
def render_file(name, data):
    return env.get_template(name).render(data)
@bottle.get('/')
def index():
    return "index\n"
@bottle.get('/static/<path:path>')
def serve_static(path):
    return bottle.static_file(path, 'static')
@bottle.get('/tmpl/<path:path>')
def serve_template(path):
    data = dict(
        arr = [ "xx", "yy", "zz" ]
    )
    return render_file(path, data)
bottle.run()
