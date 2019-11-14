from api import API
from middleware import Middleware

app = API()

class SimpleCustomMiddleware(Middleware):
    def process_request(self, request):
        print("Processing request", request.url)

    def process_response(self, request, response):
        print("processing response", request.url)

app.add_middleware(SimpleCustomMiddleware)        

def custom_exception_handler(request, response, exception_cls):
    #whenever any exception will occur, this msg will popup on user screen
    response.text = "Oops! Something went wrong. Please contact us at **********"

app.add_exception_handler(custom_exception_handler)

@app.route("/home")
def exception_throwing_handler_at_home(request, response):
    #we don't need to return response, because it is object and is mutable, so its text is getting changed
    #response.text = "Hello from the home page"
    raise AssertionError("This handler should not be used")

@app.route("/about")
def about(request, response):
    response.text = "Hello from about page"

@app.route("/hello/{name}")
def greeting(request, response, name):
    response.text = f"Hello, {name}"

@app.route("/tell/{age:d}")
def age(request, response, age):
    response.text = f"your age={age}"

@app.route("/book")
class BooksResource:
    def get(self, req, resp):
        resp.text = "Books Page"

    def post(self, req, resp):
        resp.text = "post worked"

#encoding unicode string to bytes
def template_handler(req, resp):
    resp.body = app.template("index.html", {"name": "Arjoban", "title": "Best Framework"}).encode()

app.add_route("/template", template_handler)
