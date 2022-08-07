from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.response import Response

from pyramid_resource import Resource


class Root(Resource):
    __children__ = {
        "child": ".dotted_names.Child",
    }


class Child(Resource):
    pass


def link(context, request):
    return Response(request.resource_path(context["child"]))


def child(context, request):
    return Response("Hello!\n")


def make_app():
    config = Configurator()
    config.set_root_factory(Root)
    config.add_view(link, context=Root)
    config.add_view(child, context=Child)
    config.scan(".dotted_names")
    return config.make_wsgi_app()


if __name__ == "__main__":
    app = make_app()
    server = make_server("0.0.0.0", 8080, app)
    server.serve_forever()
