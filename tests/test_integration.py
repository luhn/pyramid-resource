import pytest
from pyramid.config import Configurator
from webtest import TestApp as _TestApp


@pytest.fixture(scope="session")
def widget_app():
    config = Configurator()
    config.include("tests.pkgs.widgetapp")
    return _TestApp(config.make_wsgi_app())


def test_get_widget_id(widget_app):
    assert widget_app.get("/widget/5/id").text == "5"


def test_get_widget(widget_app):
    assert widget_app.get("/widget/5/").text == "mywidget:5"


def test_get_widget_not_found(widget_app):
    widget_app.get("/widget/15/", status=404)


def test_get_widget_bad_id(widget_app):
    widget_app.get("/widget/not-an-int/", status=404)


def test_get_widget_list(widget_app):
    assert widget_app.get("/widget/").json == {
        "widget_urls": [
            "/widget/1/",
            "/widget/2/",
            "/widget/5/",
        ],
    }
