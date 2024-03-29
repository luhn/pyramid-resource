# pyramid-resource

Pyramid's URL traversal is a powerful tool and personally one of my favorite features of the framework.
Unfortunately, Pyramid doesn't provide any framework or utilities for implementing resource trees.
This project aims to reduce the boilerplate necessary for creating feature-full resource trees.

## Prerequisites

To use this package, you'll first need to be familiar with Pyramid's [URL traversal](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html).

Once you're ready to get started, install pyramid-resource:  `pip install pyramid-resource`

## Basic Usage

You can create a new resource by subclassing `pyramid_resource.Resource`.
For example, here's a simple application that has a resource tree with only a root resource.

```python
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid_resource import Resource


class Root(Resource):
    pass


def hello_world(request):
    return Response('Hello!\n')


if __name__ == '__main__':
    with Configurator() as config:
        config.set_root_factory(Root)
        config.add_view(hello_world, context=Root)
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
```

You can define child resources by setting the `__children__` property to a dictionary.
The key corresponds the URL segment and the value should be a resource subclass.
pyramid-resource will automatically make the resources location-aware.

```python
class Child(Resource):
    pass


class Root(Resource):
    __children__ = {
        'child': Child,
    }
```

You can see the full example [here](https://github.com/luhn/pyramid-resource/blob/master/examples/child_resources.py).

### Name Resolution

For convenience, you can reference children as [dotted name](https://docs.pylonsproject.org/projects/pyramid/en/2.0-branch/glossary.html#term-dotted-Python-name) strings.
This is useful for putting parent resources above child resources in your code, e.g.:

```python
class Root(Resource):
    __children__ = {
        'child': '.Child',
    }


class Child(Resource):
    pass
```

For this to properly function, you will need to run [Configurator.scan](https://docs.pylonsproject.org/projects/pyramid/en/2.0-branch/api/config.html#pyramid.config.Configurator.scan) on the module.
If you prefer not to use `scan`, you can also invoke the resolution manually using `Resource.resolve_children`:

```python
def includeme(config):
    Root.resolve_children(config)
```

This functionality resolves strings using [Configurator.maybe_dotted](https://docs.pylonsproject.org/projects/pyramid/en/2.0-branch/api/config.html#pyramid.config.Configurator.maybe_dotted) and will behave the same.
This means that names *are relative to the configurator,* not necessarily the package that contains the resource.

## Dynamic resource trees

One of the more interesting features of URL traversal is that trees can be created on the fly.
This allows for dynamic resource trees that can mirror the application state, such as objects in a database.

Dynamic resource trees can be created by implementing a `get_child` method on a resource class.
This method should accept a single argument of a URL segment and will be called if no child is found in the `__children__` property.
If the URL segment corresponds to a valid child resource, `get_child` should return a resource class and the child resource will be instanciated from that.
If no corresponding child is found, `None` should be returned or `KeyError` raised, and traversal will be halted.

```python
class Root(Resource):
    def get_child(self, key):
        if exists_in_db(key):
            return Child
        else:
            return None


class Child(Resource):
    pass
```

Of course, this isn't particularly useful if you can't attach information to the child resource.
You can instantiate a resource with additional data as kwargs and return it from `get_child`:

```python
class Root(Resource):
    def get_child(self, key):
        if exists_in_db(key):
            return Child(id=key)


class Child(Resource):
    pass
```

The object ID will now be accessible via `context.id` in views on the child resource.
**Resources will proxy the attributes of their parent**, so `context.id` will also be accessible in views further down the tree.

If you need to access the current request in your `get_child` implementations, it's available via `self.request`.

## An Example

Here's an example that demonstrates how a real application might utilize pyramid-resource.

```python
from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.decorator import reify
from pyramid.view import view_config

from pyramid_resource import Resource


class Root(Resource):
    __children__ = {
        "widget": ".dynamic.WidgetContainer",
    }


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
            return Widget(widget_id=id)


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


@view_config(context=WidgetContainer, renderer="string")
def list_widgets(context, request):
    """
    GET /widget/

    List the URLs of all widgets.

    """
    urls = []
    for widget_id in request.widget_db:
        urls.append(request.resource_path(context[widget_id]))
    return "\n".join(urls) + "\n"


@view_config(context=Widget, renderer="string")
def get_widget(context, request):
    """
    GET /widget/{id}/

    Greet the current widget.

    """
    return "Hello {}!\n".format(context.widget)


class MockDatabase:
    """
    An imitation of a widget database.

    """

    DATA = {
        1: "Widget 1",
        2: "Widget 2",
    }

    def exists(self, id):
        return id in self.DATA

    def find(self, id):
        return self.DATA[id]

    def __iter__(self):
        return iter(self.DATA.keys())


def make_app():
    config = Configurator()
    config.set_root_factory(Root)
    config.add_request_method(
        lambda _: MockDatabase(),
        "widget_db",
        property=True,
    )
    config.scan(".dynamic")
    return config.make_wsgi_app()


if __name__ == "__main__":
    app = make_app()
    server = make_server("0.0.0.0", 8080, app)
    server.serve_forever()
```

The resulting application will behave like this:

```
>>> curl localhost:8080/widget/
> /widget/1/
> /widget/2/

>>> curl localhost:8080/widget/1/
> Hello Widget 1!

>>> curl localhost:8080/widget/2/
> Hello Widget 2!
```

## Prior art

The [pyramid_traversalwrapper](https://github.com/Pylons/pyramid_traversalwrapper) project proxies a location-ignorant resource tree to make it location-aware.
