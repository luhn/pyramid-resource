from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.response import Response

from pyramid_resource import Resource


class Root(Resource):
    pass


def hello_world(request):
    return Response("Hello!\n")


def make_app():
    config = Configurator()
    config.set_root_factory(Root)
    config.add_view(hello_world, context=Root)
    return config.make_wsgi_app()


if __name__ == "__main__":
    app = make_app()
    server = make_server("0.0.0.0", 8080, app)
    server.serve_forever()
