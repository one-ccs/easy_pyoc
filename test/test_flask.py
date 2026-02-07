from unittest.mock import MagicMock
from easy_pyoc import flask_util


def test_quick_data():
    mock_flask = MagicMock()
    mock_flask.request.args.to_dict.return_value = {'id': '123'}
    mock_flask.request.values.to_dict.return_value = {}
    mock_flask.request.form.to_dict.return_value = {'coords[longitude]': '45.0', 'coords[latitude]': '90.0'}
    mock_flask.request.files.to_dict.return_value = {}
    mock_flask.request.get_json.return_value = {'extra': 'data'}

    # Patch the flask module in flask_util
    flask_util.flask = mock_flask

    # Test extracting data
    result = flask_util.quick_data('id', ('coords[longitude]', float), ('coords[latitude]', float))
    assert result == ('123', 45.0, 90.0)

    # Test extracting with default value
    result = flask_util.quick_data(('missing_key', int, 0))
    assert result == 0

    # Test extracting entire data
    result = flask_util.quick_data()
    expected_data = {
        'id': '123',
        'coords[longitude]': '45.0',
        'coords[latitude]': '90.0',
        'extra': 'data'
    }
    assert result == expected_data
