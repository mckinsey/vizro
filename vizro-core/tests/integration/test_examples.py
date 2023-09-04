from vizro import Vizro


def test_default_dashboard(dash_duo, default_dashboard):
    """Test if default example dashboard starts and has no errors in logs."""
    app = Vizro().build(default_dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []


def test_dict_dashboard(dash_duo, dict_dashboard):
    """Test if dictionary example dashboard starts and has no errors in logs."""
    app = Vizro().build(dict_dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []


def test_json_dashboard(dash_duo, json_dashboard):
    """Test if json example dashboard starts and has no errors in logs."""
    app = Vizro().build(json_dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []


def test_yaml_dashboard(dash_duo, yaml_dashboard):
    """Test if yaml example dashboard starts and has no errors in logs."""
    app = Vizro().build(yaml_dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []
