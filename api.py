from webob import Request, Response
from parse import parse
import inspect
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter

class API:

    def __init__(self):
        self.routes={}

    def route(self, path):

        assert path not in self.routes, "Such route already exists"

        """
        #same functionality as above
        if path in self.routes:
            raise AssertionError("Such route already exists.")
            """

        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper

    def __call__(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)
        #response_body = b"Hello, World! Class"
        #status = "200 OK"
        #start_response(status, headers=[])
        #return iter([response_body])

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

        return response

    def test_session(self, base_url="http://testserver"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session
