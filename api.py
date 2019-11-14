import os
from jinja2 import Environment, FileSystemLoader
from webob import Request, Response
from parse import parse
import inspect
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter
from whitenoise import WhiteNoise
from middleware import Middleware

class API:

    def __init__(self, templates_dir="templates", static_dir="static"):
        self.routes={}
        self.templates_env = Environment(loader=FileSystemLoader(os.path.abspath(templates_dir)))
        self.exception_handler = None
        #wrapped our wsgi app with WhiteNoise and gave it path to static folder
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)
        self.middleware = Middleware(self)

    def add_middleware(self, middleware_cls):
        self.middleware.add(middleware_cls)

    def wsgi_app(self, environ, start_response):
        #response_body = b"Hello, World! Class"
        #status = "200 OK"
        #start_response(status, headers=[])
        #return iter([response_body])
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)

    def template(self, template_name, context=None):
        if context is None:
            context={}

        return self.templates_env.get_template(template_name).render(**context)

    #django way of adding handlers with paths
    def add_route(self, path, handler):
        assert path not in self.routes, "Such route already exists"
        """
        #same functionality as above
        if path in self.routes:
            raise AssertionError("Such route already exists.")
        """

        self.routes[path] = handler

    #flask way of adding routes or paths with handlers using decorators
    def route(self, path):
        def wrapper(handler):
            self.add_route(path, handler)
            return handler

        return wrapper

    def __call__(self, environ, start_response):
        path_info = environ["PATH_INFO"]

        if path_info.startswith("/static"):
            environ['PATH_INFO'] = path_info[len("/static"):]
            return self.whitenoise(environ, start_response)
            
        return self.middleware(environ, start_response)

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                #if no params will be there, this will parse empty {}
                return handler, parse_result.named
        return None, None

    def default_response(self, response):
        response.status_code = 404
        response.text="Not found."

    def handle_request(self, request):

        response = Response()

        handler, kwargs = self.find_handler(request_path=request.path)
        #print(kwargs)
        try:
            if handler is not None:
                #check if handler a class or function
                if inspect.isclass(handler):
                    #first param as object instance, second param will \
                    #return get(function or method of this class) if request\
                    # is GET and post if request POST and None(which is third param)\
                    #if something else
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise AttributeError("Method not allowed", request.method)

                handler(request, response, **kwargs)
            else:
                self.default_response(response)
        except Exception as e:
            #if someone doesn't provide custom exception handler, tham original error will be shown on screen
            if self.exception_handler is None:
                raise e
            else:
                self.exception_handler(request, response, e)

        return response

    def test_session(self, base_url="http://testserver"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session

    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler
