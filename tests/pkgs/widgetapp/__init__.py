from pyramid_resource import Resource


def includeme(config):
    config.set_root_factory(Root)
    config.add_view(list_widgets, context=WidgetContainer, renderer="json")
    config.add_view(get_widget, context=Widget, renderer="string")
    config.add_view(
        get_widget_id, context=Widget, name="id", renderer="string"
    )
    Root.resolve_children(config)


class Root(Resource):
    __children__ = {
        "widget": ".WidgetContainer",
    }


class WidgetContainer(Resource):
    def get_child(self, key):
        try:
            int_key = int(key)
        except ValueError:
            raise KeyError

        if int_key not in range(10):
            raise KeyError

        return Widget, {"widget_id": int_key}


class Widget(Resource):
    @property
    def widget(self):
        # Perhaps a DB lookup
        return "mywidget:{}".format(self.widget_id)


def list_widgets(context, request):
    urls = []
    for widget_id in [1, 2, 5]:
        urls.append(request.resource_path(context[widget_id]))
    return {
        "widget_urls": urls,
    }


def get_widget_id(context, request):
    assert isinstance(context.widget_id, int)
    return context.widget_id


def get_widget(context, request):
    return context.widget
