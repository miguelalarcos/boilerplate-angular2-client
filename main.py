import tornado.ioloop
import tornado.web
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado import gen
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
                if payload['role'] == role:
                    return f(self, *args)
                else:
                    raise Exception('not role ', role)
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

class JSONHandler(tornado.web.RequestHandler):
    def rjson(self, ret):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(ret, default=json_dumps_helper))
        self.finish()

class DateHandler(JSONHandler):
    @gen.coroutine    
    @has_role('admin')
    @types(int, date)
    def get(self, year, d):
        self.rjson({'year': year, 'd': d})

class LoginHandler(JSONHandler):
    @gen.coroutine    
    def get(self, token):
        url = "https://www.googleapis.com/oauth2/v1/userinfo?access_token=" + token
        request = HTTPRequest(url=url, method="GET")
        response = yield AsyncHTTPClient().fetch(request)
        
        if response.code == 200:
            data = json.loads(str(response.body, 'utf-8'))
            jwt_ = jwt.encode({'role': 'admin', 'email': data['email']}, 'secret', algorithm='HS256')
            self.rjson({'jwt': jwt_.decode("utf-8")})
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
    application = tornado.web.Application([
        (r'/', MainHandler),
        (r"/login/(.+)", LoginHandler),
        (r"/(\d{4})/(\d\d-\d\d-\d\d\d\d)", DateHandler),
        (r'/(.*)', NoCacheStaticFileHandler, {'path': './dist'}),
    ], debug=True)
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()