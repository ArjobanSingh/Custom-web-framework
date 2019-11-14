import pytest

from api import API

#@pytest.fixture
#def api():
#    return API()

def test_basic_route(api):
    @api.route("/home")
    def home(req, resp):
        resp.text = "YOLO"

    with pytest.raises(AssertionError):
        @api.route("/home")
        def home2(req, resp):
            resp.text = "YOLO"

def test_arjoban_test_client_can_send_requests(api, client):
    RESPONSE_TEXT = "THIS IS COOL"

    @api.route("/hey")
    def cool(req, resp):
        resp.text = RESPONSE_TEXT

    assert client.get("http://testserver/hey").text == RESPONSE_TEXT

def test_parameterized_route(api, client):
    @api.route("/{name}")
    def hello(req, resp, name):
        resp.text = f"hey {name}"

    assert client.get("http://testserver/arjoban").text == "hey arjoban"
    assert client.get("http://testserver/Brahm").text == "hey Brahm"

def test_default_404_response(client):
    response = client.get("http://testserver/doesnotexist")

    assert response.status_code == 404
    assert response.text == "Not found."

def test_class_based_handler(api, client):

    @api.route("/classTest")
    class Class_test:
        def get(self, req, resp):
            resp.text = "your order"

        def post(self, req, resp):
            resp.text = "posted"

    assert client.get('http://testserver/classTest').text == "your order"
    assert client.post('http://testserver/classTest').text == "posted"

def test_alternative_route(api, client):
    response_text = "Alternative way to add route"

    def home(req,resp):
        resp.text = response_text

    api.add_route("/alternative", home)

    assert client.get("http://testserver/alternative").text  == response_text
