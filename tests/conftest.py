# -*- coding: utf-8 -*-
import os
import pytest

from mailproc import Mailproc


@pytest.fixture(scope="session")
def app():
    app = Mailproc("test_app")
    return app

@pytest.fixture()
def static_dir():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "static")
