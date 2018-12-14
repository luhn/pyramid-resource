"""
An example of how an application might utilize a dynamic resource tree.

>>> curl localhost:8080/widget/
> {"widget_urls": ["/widget/1/", "/widget/2/"]}

>>> curl localhost:8080/widget/1/
> Hello Widget 1!

>>> curl localhost:8080/widget/2/
> Hello Widget 2!

>>> curl localhost:8080/widget/1/foo
> Hello Widget 1!

>>> curl localhost:8080/widget/foo
> Hello world!

"""
from wsgiref.simple_server import make_server
from pyramid.decorator import reify
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid_resource import Resource


class MockDatabase:
    DATA = {
        1: 'Widget 1',
        2: 'Widget 2',
    }

    def exists(self, id):
        return id in self.DATA

    def find(self, id):
        return self.DATA[id]

    def __iter__(self):
        return iter(self.DATA.keys())


class Foo(Resource):
    pass


class WidgetContainer(Resource):
    __children__ = {
        'foo': Foo,
    }

    def get_child(self, key):
        try:
            id = int(key)
        except ValueError:
            raise KeyError

        if self.request.db.exists(id):
            return Widget, {'widget_id': id}


class Widget(Resource):
    __children__ = {
        'foo': Foo,
    }

    @reify
    def widget(self):
        return self.request.db.find(self.widget_id)


class Root(Resource):
    __children__ = {
        'widget': WidgetContainer,
    }


def list_widgets(context, request):
    urls = []
    for widget_id in request.db:
        urls.append(request.resource_path(context[widget_id]))
    return {
        'widget_urls': urls,
    }


def get_widget(context, request):
    if hasattr(context, 'widget_id'):
        return Response('Hello {}!\n'.format(context.widget))
    else:
        return Response('Hello world!\n')


if __name__ == '__main__':
    with Configurator() as config:
        config.set_root_factory(Root)
        config.add_request_method(
            lambda _: MockDatabase(),
            'db',
            property=True,
        )
        config.add_view(list_widgets, context=WidgetContainer, renderer='json')
        config.add_view(get_widget, context=Widget)
        config.add_view(get_widget, context=Foo)
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
