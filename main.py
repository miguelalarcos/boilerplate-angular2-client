import tornado.ioloop
import tornado.web
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

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @has_role('admin')
    @types(int, date)
    @rjson
    def get(self, year, d):        
        return {'year': year, 'd': d}        

if __name__ == "__main__":
    print('init')
    print(jwt.encode({'rol': 'admin'}, 'secret', algorithm='HS256'))
    application = tornado.web.Application([
        (r"/(\d{4})/(\d\d-\d\d-\d\d\d\d)", MainHandler),
    ], debug=True)
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()