import tornado.ioloop
import tornado.web
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import json
from datetime import datetime
import jwt
 
def has_role(role):
    def decorator(f):
        def helper(self, *args):
            try:
                auth = self.request.headers.get('Authorization', None)
                token = auth.split()[1]
                payload = jwt.decode(token, 'secret', algorithms=['HS256'])
                if payload['rol'] == '':
                    return f(self, *args)
                else:
                    raise Exception('no tiene rol ', role)
            except Exception as e:
                self.send_error(401, msg='my error')
        return helper
    return decorator

def json_dumps_helper(doc):
    if(isinstance(doc, datetime)):
        return {'$date': doc.timestamp()*1000}
    else:
        return doc


def date(arg):
    return datetime.strptime(arg, '%d-%m-%Y')

def rjson(f):
    def helper(self, *args):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(f(self, *args), default=json_dumps_helper))
        self.finish()
    return helper

def types(*ts):
    def decorator(f):
        def helper(self, *args):
            args_ = []
            try:
                for t, arg in zip(ts, args):
                    args_.append(t(arg))
            except Exception as e:
                print(e)
            return f(self, *args_)
        return helper
    return decorator

class DateHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @has_role('admin')
    @types(int, date)
    @rjson
    def get(self, year, d):        
        return {'year': year, 'd': d}    

class LoginHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @types(str)
    @rjson
    def get(self, token):
        url = "https://www.googleapis.com/oauth2/v1/userinfo?access_token=" + token
        request = HTTPRequest(url=url, method="GET")
        response = yield AsyncHTTPClient().fetch(request)

        if response.code == 200:
            data = json.loads(str(response.body, 'utf-8'))
            jwt_ = jwt.encode({'rol': 'admin', 'email': data['email']}, 'secret', algorithm='HS256')
            return {'jwt': jwt_}
        else:
            self.send_error(401, msg='my error')     

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("dist/index.html")


class NoCacheStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")

if __name__ == "__main__":
    print('init')
    print(jwt.encode({'rol': 'admin'}, 'secret', algorithm='HS256'))
    application = tornado.web.Application([
        (r'/', MainHandler),
        (r"/login/(.+)", LoginHandler),
        (r"/(\d{4})/(\d\d-\d\d-\d\d\d\d)", DateHandler),
        (r'/(.*)', NoCacheStaticFileHandler, {'path': './dist'}),
    ], debug=True)
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()