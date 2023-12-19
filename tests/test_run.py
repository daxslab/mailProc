# -*- coding: utf-8 -*-
import os


def test_service_run(app):
    pid_file = app._get_pid_file_path()
    assert os.path.isfile(pid_file)
