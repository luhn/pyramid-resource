# pyramid-resource

Pyramid's URL traversal is a powerful feature, but unfortunately Pyramid does
not provide any framework for creating a resource tree.  Although you can make
a resource tree using only dicts, this leaves some of the more interesting
traversal features on the table.  Creating a more functional resource tree is
relatively easy, but is unnecessary boilerplate that this project aims to
eliminate.

## Basic usage

First, of course, you need to add `pyramid-resource` to your project using your
package manager of choice.  e.g.: `pip install pyramid-resource`

Make sure you're familiar with
[URL traversal](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html).

You can create a new resource by subclassing `pyramid_resource.Resource`.  You
can make a resource the root of the tree by setting it as your root factory.
For example, here's a simple application that has a resource tree with only
a root.

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

You can define child resources by setting the `__children__` property to a
dictionary.  The key corresponds the URL segment and the value should be a
resource subclass.  pyramid-resource will automatically make the resources
location-aware.

```python
class Child(Resource):
    pass


class Root(Resource):
    __children__ = {
        'child': Child,
    }
```

You can see the full example
[here](https://github.com/luhn/pyramid-resource/blob/master/examples/02_children.py).

## Dynamic resource trees

One of the more interesting features of URL traversal is that trees can be
created on the fly.  This allows for dynamic traversal trees that can the
application state, such as objects in a database.

pyramid-resource enables this by providing a `get_child` method for you to
override.  The method takes in a single key argument and is invoked if no child
resource can be found in `__children__`.   By default it returns `None`,
indicating no child resource exists with the given key.  You can also raise a
KeyError to indicate the same.  You can return a `Resource` subclass and it
will be used to create a child resource on the fly.

```python
class Child(Resource):
    pass


class Root(Resource):
    def get_child(self, key):
        if exists_in_db(key):
            return Child
```

The current request is accessible via `self.request`.

Of course, this isn't particularly useful if you can't attach information to
the child resource.  `get_child` can also return a two-tuple of a `Resource`
subclass and a dictionary of attributes that will be attached to the resulting
child.

```python
class Child(Resource):
    pass


class Root(Resource):
    def get_child(self, key):
        if exists_in_db(key):
            return Child, {'id': key}
```

You can access the ID in your view through `context.id`.  **Resources will
proxy the attributes of their parent**, so `context.id` will also be accessible
in views further down the tree.

## An example

Here's an example that demonstrates how a real application might utilize
pyramid-resource.

```python
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
```

The resulting application will behave like this:

```
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
```

## Hacking

Developing against pyramid-resource is simple, thanks to Poetry:

* [Install Poetry](https://poetry.eustace.io/docs/#installation) if you haven't
  done so already
* Clone the repository
* Run `poetry install`
* Run the test suite with `make test`

## Prior art

The
[pyramid_traversalwrapper](https://github.com/Pylons/pyramid_traversalwrapper)
project proxies a location-ignorant resource tree to make it resource aware.
