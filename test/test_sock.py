from easy_pyoc import network_util


def test_send_WOL():
    network_util.send_WOL('001122334455')
