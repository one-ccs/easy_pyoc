from easy_pyoc import Logger


def test_logger():
    logger1 = Logger()
    logger2 = Logger()
    logger3 = Logger(name='test', formatter='%(message)s')

    assert logger1 is logger2
    assert logger1 is not logger3
    assert logger2 is not logger3
