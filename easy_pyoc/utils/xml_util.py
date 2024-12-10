#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, Any, Literal
from xml.etree.ElementTree import Element, fromstring, tostring

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

from .path_util import PathUtil


class XMLUtil(object):
    """XML 工具类"""

    @staticmethod
    def loads(xml: str, default: Any = ...) -> dict:
        """将 xml 字符串转换为字典

        Args:
            xml (str): xml 字符串
            default (Any, optional): 当 xml 中某个节点没有值时, 使用 default 填充, 当 default 为 `...` 时, 则不填充. 默认为 `...`.

        Returns:
            dict: 解析后的字典
        """
        return XMLUtil.xml_to_dict(xml, default)

    @staticmethod
    def dumps(data: dict, encoding: str = 'unicode', *, tag: str = 'root', deep: int = ..., method: str = 'xml') -> str | bytes:
        """将字典转换为 xml 字符串

        如果 encoding 为 `unicode`, 则返回字符串, 否则返回字节串

        Args:
            data (dict): 字典数据
            encoding (str, optional): 编码格式. 默认为 `unicode`.
            tag (str, optional): 根节点标签. 默认为 `root`.
            deep (int, optional): 递归深度, 当 deep 为 `...` 时, 则不限制递归深度. 默认为 `...`.
            method (str, optional): 输出方法, 可选 `xml` | `html` | `text` | `c14n`. 默认为 `xml`.

        Returns:
            str | bytes: xml 字符串
        """
        return XMLUtil.dict_to_xml(data, encoding, tag=tag, deep=deep, method=method)

    @staticmethod
    def load(fp: 'FileDescriptorOrPath', default: Any = ..., encoding: str = 'utf-8') -> dict:
        """读取文件 xml 文件并转换为字典

        Args:
            xml (str): xml 字符串
            default (Any, optional): 当 xml 中某个节点没有值时, 使用 default 填充, 当 default 为 `...` 时, 则不填充. 默认为 `...`.

        Returns:
            dict: 解析后的字典
        """
        with PathUtil.open(fp, 'r', encoding=encoding) as f:
            return XMLUtil.xml_to_dict(f.read(), default)

    @staticmethod
    def dump(fp: 'FileDescriptorOrPath', data: dict, *, xml_encoding: str = 'unicode', file_encoding: str = 'utf-8', tag: str = 'root', deep: int = ..., method: str = 'xml') -> None:
        """将字典写入文件 xml 文件

        Args:
            fp (FileDescriptorOrPath): 文件路径
            data (dict): 字典数据
            xml_encoding (str, optional): xml 编码格式. 默认为 `unicode`.
            file_encoding (str, optional): 文件编码格式. 默认为 `utf-8`.
            tag (str, optional): 根节点标签. 默认为 `root`.
            deep (int, optional): 递归深度, 当 deep 为 `...` 时, 则不限制递归深度. 默认为 `...`.
            method (str, optional): 输出方法, 可选 `xml` | `html` | `text` | `c14n`. 默认为 `xml`.
        """
        with PathUtil.open(fp, 'w', encoding=file_encoding) as f:
            f.write(XMLUtil.dict_to_xml(data, xml_encoding, tag=tag, deep=deep, method=method))

    @staticmethod
    def element_to_dict(element: Element, default: Any = ...) -> dict:
        """将 xml.etree.ElementTree.Element 转换为字典

        Args:
            element (Element): xml.etree.ElementTree.Element 对象
            default (Any, optional): 当 xml 中某个节点没有值时, 使用 default 填充, 当 default 为 `...` 时, 则不填充. 默认为 `...`.

        Returns:
            dict: 解析后的字典
        """
        result = {}

        for child in element:
            if len(child) == 0:
                if not child.text:
                    if default is not ...:
                        value = default
                        result[child.tag] = value
                    continue

                try:
                    value = int(child.text)
                except ValueError:
                    try:
                        value = float(child.text)
                    except ValueError:
                        value = child.text

                if isinstance(value, str) and value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'

                result[child.tag] = value
            else:
                result[child.tag] = XMLUtil.element_to_dict(child)
        return result

    @staticmethod
    def xml_to_dict(xml: str, default: Any = ...) -> dict:
        """将 xml 字符串转换为字典

        Args:
            xml (str): xml 字符串
            default (Any, optional): 当 xml 中某个节点没有值时, 使用 default 填充, 当 default 为 `...` 时, 则不填充. 默认为 `...`.

        Returns:
            dict: 解析后的字典
        """
        return XMLUtil.element_to_dict(fromstring(xml), default)

    @staticmethod
    def dict_to_element(data: dict, *, tag: str = 'root', deep: int = ...) -> Element:
        """将字典转换为 xml.etree.ElementTree.Element 对象

        Args:
            data (dict): 字典数据
            tag (str, optional): 根节点标签. 默认为 `root`.
            deep (int, optional): 递归深度, 当 deep 为 `...` 时, 则不限制递归深度. 默认为 `...`.

        Returns:
            Element: xml.etree.ElementTree.Element 对象
        """
        element = Element(tag)
        deep = deep - 1 if deep is not ... else deep

        if not isinstance(data, dict):
            return element

        for key, value in data.items():
            key = str(key)

            if deep is not ... and deep <= 0:
                child = Element(key)
                child.text = str(value)
            elif isinstance(value, dict):
                child = XMLUtil.dict_to_element(value, tag=key, deep=deep)
            elif isinstance(value, list):
                for item in value:
                    child = XMLUtil.dict_to_element(item, tag=key, deep=deep)
                    element.append(child)
                continue
            else:
                child = Element(key)
                child.text = str(value)
            element.append(child)

        return element

    @staticmethod
    def element_to_xml(element: Element, encoding: str = 'unicode', *, method: str = 'xml') -> str | bytes:
        """将 xml.etree.ElementTree.Element 对象转换为 xml 字符串

        如果 encoding 为 `unicode`, 则返回字符串, 否则返回字节串

        Args:
            element (Element): xml.etree.ElementTree.Element 对象
            encoding (str, optional): 编码格式. 默认为 `unicode`.
            method (str, optional): 输出方法, 可选 `xml` | `html` | `text` | `c14n`. 默认为 `xml`.

        Returns:
            str | bytes: xml 字符串
        """
        return tostring(element, encoding, method)

    @staticmethod
    def dict_to_xml(data: dict, encoding: str = 'unicode', *, tag: str = 'root', deep: int = ..., method: str = 'xml') -> str | bytes:
        """将字典转换为 xml 字符串

        如果 encoding 为 `unicode`, 则返回字符串, 否则返回字节串

        Args:
            data (dict): 字典数据
            encoding (str, optional): 编码格式. 默认为 `unicode`.
            tag (str, optional): 根节点标签. 默认为 `root`.
            deep (int, optional): 递归深度, 当 deep 为 `...` 时, 则不限制递归深度. 默认为 `...`.
            method (str, optional): 输出方法, 可选 `xml` | `html` | `text` | `c14n`. 默认为 `xml`.

        Returns:
            str | bytes: xml 字符串
        """
        return XMLUtil.element_to_xml(XMLUtil.dict_to_element(data, tag=tag, deep=deep), encoding, method=method)
