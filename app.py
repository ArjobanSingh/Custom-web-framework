from api import API

app = API()

@app.route("/home")
def home(request, response):
    #we don't need to return response, because it is object and is mutable, so its text is getting changed 
    response.text = "Hello from the home page"

@app.route("/about")
def about(request, response):
    response.text = "Hello from about page"
