from .classes.logger import Logger as Logger
from .classes.magic import Magic as Magic
from .classes.config import Config as Config
from .classes.color import AnsiColor as AnsiColor

from .sock.server import ServerSocket as ServerSocket
from .sock.client import ClientSocket as ClientSocket

from .utils import data_util as data_util
from .utils import datetime_util as datetime_util
from .utils import exception_util as exception_util
from .utils import func_util as func_util
from .utils import json_util as json_util
from .utils import knx_util as knx_util
from .utils import network_util as network_util
from .utils import object_util as object_util
from .utils import package_util as package_util
from .utils import path_util as path_util
from .utils import string_util as string_util
from .utils import thread_util as thread_util
from .utils import xml_util as xml_util
from .utils import not_this_module

try:
    from .utils import toml_util as toml_util
except ImportError as e:
    toml_util = not_this_module('toml_util', e.msg)

try:
    from .utils import yaml_util as yaml_util
except ImportError as e:
    yaml_util = not_this_module('yaml_util', e.msg)

try:
    from .utils import flask_util as flask_util
except ImportError as e:
    flask_util = not_this_module('flask_util', e.msg)



__version__ = package_util.get_version('easy_pyoc')
__author__ = 'one-ccs'
__email__ = 'one-ccs@foxmail.com'

__all__ = [
    'Logger',
    'Magic',
    'Config',
    'AnsiColor',

    'ServerSocket',
    'ClientSocket',

    'data_util',
    'datetime_util',
    'exception_util',
    'func_util',
    'json_util',
    'knx_util',
    'network_util',
    'object_util',
    'package_util',
    'path_util',
    'string_util',
    'thread_util',
    'xml_util',
    'toml_util',
    'yaml_util',
    'flask_util',
]
