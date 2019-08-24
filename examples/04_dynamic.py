"""
An example of how an application might utilize a dynamic resource tree.

>>> curl localhost:8080/widget/
> /widget/1/
> /widget/2/

>>> curl localhost:8080/widget/1/
> Hello Widget 1!

>>> curl localhost:8080/widget/2/
> Hello Widget 2!

"""
from wsgiref.simple_server import make_server
from pyramid.decorator import reify
from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid_resource import Resource


class Widget(Resource):
    """
    A resource representing a widget in the mock database.

    """
    @reify
    def widget(self):
        """
        Lookup the widget from the database.

        """
        return self.request.widget_db.find(self.widget_id)


class WidgetContainer(Resource):
    """
    A resource containing the Widget resources.

    """
    def get_child(self, key):
        """
        Return a child resource if the widget exists in the database.

        """
        try:
            id = int(key)
        except ValueError:
            raise KeyError

        if self.request.widget_db.exists(id):
            return Widget, {'widget_id': id}


class Root(Resource):
    __children__ = {
        'widget': WidgetContainer,
    }


@view_config(context=WidgetContainer, renderer='string')
def list_widgets(context, request):
    """
    GET /widget/

    List the URLs of all widgets.

    """
    urls = []
    for widget_id in request.widget_db:
        urls.append(request.resource_path(context[widget_id]))
    return '\n'.join(urls) + '\n'


@view_config(context=Widget, renderer='string')
def get_widget(context, request):
    """
    GET /widget/{id}/

    Greet the current widget.

    """
    return 'Hello {}!\n'.format(context.widget)


class MockDatabase:
    """
    An imitation of a widget database.

    """
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


if __name__ == '__main__':
    with Configurator() as config:
        config.set_root_factory(Root)
        config.add_request_method(
            lambda _: MockDatabase(),
            'widget_db',
            property=True,
        )
        config.scan()
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
