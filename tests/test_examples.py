from webtest import TestApp

from examples import child_resources, dotted_names, dynamic, root_only


def test_root_only():
    app = TestApp(root_only.make_app())
    assert app.get("/").text == "Hello!\n"


def test_child_resources():
    app = TestApp(child_resources.make_app())
    assert app.get("/child/").text == "Hello!\n"


def test_dotted_names():
    app = TestApp(dotted_names.make_app())
    assert app.get("/child/").text == "Hello!\n"


def test_dynamic():
    app = TestApp(dynamic.make_app())
    assert app.get("/widget/").text == "/widget/1/\n/widget/2/\n"
    assert app.get("/widget/1/").text == "Hello Widget 1!\n"
