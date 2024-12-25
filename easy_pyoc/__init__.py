#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .logger import Logger as Logger

from .sock.server_socket import ServerSocket as ServerSocket
from .sock.client_socket import ClientSocket as ClientSocket

from .utils import not_this_module
from .utils.crc_util import CRCUtil as CRCUtil
from .utils.datetime_util import DateTimeUtil as DateTimeUtil
from .utils.json_util import JSONUtil as JSONUtil
from .utils.knx_util import KNXUtil as KNXUtil
from .utils.network_util import NetworkUtil as NetworkUtil
from .utils.object_util import ObjectUtil as ObjectUtil
from .utils.path_util import PathUtil as PathUtil
from .utils.string_util import StringUtil as StringUtil
from .utils.thread_util import ThreadUtil as ThreadUtil
from .utils.xml_util import XMLUtil as XMLUtil

try:
    from .utils.flask_util import FlaskUtil as FlaskUtil
except ImportError as e:
    FlaskUtil = not_this_module('FlaskUtil', e.msg)

try:
    from .utils.toml_util import TOMLUtil as TOMLUtil
except ImportError as e:
    TOMLUtil = not_this_module('TOMLUtil', e.msg)

try:
    from .utils.yaml_util import YAMLUtil as YAMLUtil
except ImportError as e:
    YAMLUtil = not_this_module('YAMLUtil', e.msg)

from .classes.magic import Magic as Magic
from .classes.config import Config as Config


__version__ = '0.8.1'
__author__ = 'one-ccs'
__email__ = 'one-ccs@foxmail.com'

__all__ = [
    'Logger',

    'ServerSocket',
    'ClientSocket',

    'CRCUtil',
    'DateTimeUtil',
    'FlaskUtil',
    'JSONUtil',
    'KNXUtil',
    'NetworkUtil',
    'ObjectUtil',
    'PathUtil',
    'StringUtil',
    'TOMLUtil',
    'XMLUtil',
    'YAMLUtil',

    'Magic',
    'Config',
]
