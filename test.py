import pytest
from webtest import TestApp as _TestApp
from pyramid.config import Configurator
from pyramid_resource import Resource


def test_resolve_names():
    class MyResource(Resource):
        pass


def test_default_lookup():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        __children__ = {
            'sub': SubResource,
        }

    root = MyResource('request')
    sub = root['sub']
    assert isinstance(sub, SubResource)
    assert sub.request == 'request'
    assert sub.__name__ == 'sub'
    assert sub.__parent__ is root

    with pytest.raises(KeyError):
        root['sub2']


def test_custom_lookup_subclass():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        def get_child(self, key):
            assert key == 'sub'
            return SubResource

    root = MyResource('request')
    sub = root['sub']
    assert isinstance(sub, SubResource)
    assert sub.request == 'request'
    assert sub.__name__ == 'sub'
    assert sub.__parent__ is root


def test_custom_lookup_tuple():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        def get_child(self, key):
            assert key == 'sub'
            return SubResource, {'foo': 'bar'}

    root = MyResource('request')
    sub = root['sub']
    assert isinstance(sub, SubResource)
    assert sub.request == 'request'
    assert sub.__name__ == 'sub'
    assert sub.__parent__ is root
    assert sub.foo == 'bar'


def test_getattr():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        subfoo = 'subbar'

        @property
        def prop(self):
            return 'myprop'

    parent = MyResource('request')
    child = SubResource('request', 'sub', parent, foo='bar')
    grandchild = SubResource('request', 'sub', child)
    with pytest.raises(AttributeError):
        assert parent.foo
    assert parent.subfoo == 'subbar'
    assert parent.prop == 'myprop'
    assert child.foo == 'bar'
    assert child.subfoo == 'subbar'
    assert child.prop == 'myprop'
    assert grandchild.foo == 'bar'
    assert grandchild.subfoo == 'subbar'
    assert grandchild.prop == 'myprop'


# Integration tests


@pytest.fixture
def app():
    class WidgetContainer(Resource):
        def get_child(self, key):
            try:
                int_key = int(key)
            except ValueError:
                raise KeyError

            if int_key not in range(10):
                raise KeyError

            return Widget, {'widget_id': int_key}

    class Widget(Resource):
        @property
        def widget(self):
            # Perhaps a DB lookup
            return 'mywidget:{}'.format(self.widget_id)

    class Root(Resource):
        __children__ = {
            'widget': WidgetContainer,
        }

    def list_widgets(context, request):
        urls = []
        for widget_id in [1, 2, 5]:
            urls.append(request.resource_path(context[widget_id]))
        return {
            'widget_urls': urls,
        }

    def get_widget_id(context, request):
        assert isinstance(context.widget_id, int)
        return context.widget_id

    def get_widget(context, request):
        return context.widget

    with Configurator(settings={}) as config:
        config.set_root_factory(Root)
        config.add_view(list_widgets, context=WidgetContainer, renderer='json')
        config.add_view(get_widget, context=Widget, renderer='string')
        config.add_view(get_widget_id, context=Widget, name='id',
                        renderer='string')
    return _TestApp(config.make_wsgi_app())


def test_get_widget_id(app):
    assert app.get('/widget/5/id').text == '5'


def test_get_widget(app):
    assert app.get('/widget/5/').text == 'mywidget:5'


def test_get_widget_not_found(app):
    assert app.get('/widget/15/', status=404)


def test_get_widget_bad_id(app):
    assert app.get('/widget/not-an-int/', status=404)


def test_get_widget_list(app):
    assert app.get('/widget/').json == {
        'widget_urls': [
            '/widget/1/',
            '/widget/2/',
            '/widget/5/',
        ],
    }


# Test resolution


class ResolverRoot(Resource):
    __children__ = {
        'foo': '.ToResolve',
    }


class ToResolve(Resource):
    pass


def test_resolve_children():

    def hello(context, request):
        return 'Hello world!'

    with Configurator(settings={}) as config:
        config.set_root_factory(ResolverRoot)
        config.add_view(hello, context=ToResolve, renderer='string')
        config.scan()
    app = _TestApp(config.make_wsgi_app())

    assert app.get('/foo').text == 'Hello world!'
