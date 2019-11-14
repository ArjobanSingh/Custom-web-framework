from api import API

app = API()

@app.route("/home")
def home(request, response):
    #we don't need to return response, because it is object and is mutable, so its text is getting changed
    response.text = "Hello from the home page"

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
