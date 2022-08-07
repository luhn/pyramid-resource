from pyramid.view import view_config

from pyramid_resource import Resource


def includeme(config):
    config.set_root_factory(Root)
    config.scan(".")


class Root(Resource):
    __children__ = {
        "child": ".Child",
    }


class Child(Resource):
    pass


@view_config(context=Child, renderer="string")
def hello(context, request):
    return "Hello World!"
