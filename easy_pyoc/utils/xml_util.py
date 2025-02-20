#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, Optional, Union
from xml.etree.ElementTree import (
    ParseError,
    XMLParser,
    Element,
    fromstring,
    tostring,
)

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

from .path_util import PathUtil


class XMLUtil(object):
    """XML 工具类"""

    @staticmethod
    def auto_type(text: Optional[str]) -> Optional[Union[str, int, float, bool]]:
        """自动类型转换"""
        if text is None:
            return None
        elif text.isdigit():
            return int(text)
        elif text.replace('.', '', 1).isdigit():
            return float(text)
        elif text.lower() in ['true', 'false']:
            return text.lower() == 'true'
        else:
            return text

    @staticmethod
    def loads(xml: str, *, parser: Optional[XMLParser] = None) -> dict:
        """将 xml 字符串转换为字典

        Args:
            xml (str): xml 字符串
            parser (XMLParser, optional): xml 解析器, 当为 `None` 时, 使用标准解析器. 默认为 `None`.

        Returns:
            dict: 解析后的字典
        """
        return XMLUtil.xml_to_dict(xml, parser=parser)

    @staticmethod
    def dumps(data: dict, *, tag: str = 'root', deep: int = ..., encoding: str = 'unicode', method: str = 'xml') -> str | bytes:
        """将字典转换为 xml 字符串

        如果 encoding 为 `unicode`, 则返回字符串, 否则返回字节串

        Args:
            data (dict): 字典数据
            tag (str, optional): 根节点标签. 默认为 `root`.
            deep (int, optional): 递归深度, 当 deep 为 `...` 时, 则不限制递归深度. 默认为 `...`.
            encoding (str, optional): 编码格式. 默认为 `unicode`.
            method (str, optional): 输出方法, 可选 `xml` | `html` | `text` | `c14n`. 默认为 `xml`.

        Returns:
            str | bytes: xml 字符串
        """
        return XMLUtil.dict_to_xml(data, encoding, tag=tag, deep=deep, method=method)

    @staticmethod
    def load(fp: 'FileDescriptorOrPath', *, parser: Optional[XMLParser] = None, encoding: str = 'utf-8') -> dict:
        """读取文件 xml 文件并转换为字典

        Args:
            fp (FileDescriptorOrPath): 文件路径
            parser (XMLParser, optional): xml 解析器, 当为 `None` 时, 使用标准解析器. 默认为 `None`.
            encoding (str, optional): 文件编码格式. 默认为 `utf-8`.

        Returns:
            dict: 解析后的字典
        """
        with PathUtil.open(fp, 'r', encoding=encoding) as f:
            return XMLUtil.xml_to_dict(f.read(), parser=parser)

    @staticmethod
    def dump(fp: 'FileDescriptorOrPath', data: dict, *, tag: str = 'root', xml_encoding: str = 'unicode', file_encoding: str = 'utf-8', deep: int = ..., method: str = 'xml') -> None:
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
    def element_to_dict(element: Element) -> dict:
        """将 xml.etree.ElementTree.Element 转换为字典

        Args:
            element (Element): xml.etree.ElementTree.Element 对象

        Returns:
            dict: 解析后的字典
        """
        result, text, tail = ({element.tag: {}}), element.text or '', ''

        # 设置属性
        for k, v in element.attrib.items():
            result[element.tag][f'@{k}'] = XMLUtil.auto_type(v)

        # 设置子节点
        for child in element:
            tail += child.tail or ''

            if child.tag in result[element.tag]:
                if isinstance(result[element.tag][child.tag], list):
                    result[element.tag][child.tag].append(XMLUtil.element_to_dict(child)[child.tag])
                else:
                    result[element.tag][child.tag] = [
                        result[element.tag][child.tag],
                        XMLUtil.element_to_dict(child)[child.tag],
                    ]
            else:
                result[element.tag].update(XMLUtil.element_to_dict(child))

        # 设置文本
        if not result[element.tag]:
            result[element.tag] = XMLUtil.auto_type((element.text or '').strip() or None)
        else:
            if text.lstrip() and tail.rstrip():
                result[element.tag]['#text'] = text.lstrip() + tail.rstrip()
            elif text.strip():
                result[element.tag]['#text'] = text.strip()
            elif tail.strip():
                result[element.tag]['#text'] = tail.strip()
        return result

    @staticmethod
    def xml_to_element(xml: str, *, parser: Optional[XMLParser] = None) -> Element:
        """将 xml 字符串转换为 xml.etree.ElementTree.Element 对象

        Args:
            xml (str): xml 字符串
            parser (XMLParser, optional): xml 解析器, 当为 `None` 时, 使用标准解析器. 默认为 `None`.

        Returns:
            Element: xml.etree.ElementTree.Element 对象
        """
        try:
            return fromstring(xml, parser)
        except ParseError:
            raise ValueError('XML 格式有误')

    @staticmethod
    def xml_to_dict(xml: str, *, parser: Optional[XMLParser] = None) -> dict:
        """将 xml 字符串转换为字典

        Args:
            xml (str): xml 字符串
            parser (XMLParser, optional): xml 解析器, 当为 `None` 时, 使用标准解析器. 默认为 `None`.

        Returns:
            dict: 解析后的字典
        """
        return XMLUtil.element_to_dict(
            XMLUtil.xml_to_element(
                xml,
                parser=parser,
            ),
        )

    @staticmethod
    def element_to_xml(element: Element, *, encoding: str = 'unicode', method: str = 'xml') -> str | bytes:
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
    def dict_to_element(data: dict, *, tag: str = 'root', deep: int = ..., indent: int = 4) -> Element:
        """将字典转换为 xml.etree.ElementTree.Element 对象

        Args:
            data (dict): 字典数据
            tag (str, optional): 根节点标签. 默认为 `root`.
            deep (int, optional): 递归深度, 当 deep 为 `...` 时, 则不限制递归深度. 默认为 `...`.
            indent (int, optional): 缩进空格数. 默认为 `4`.

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
    def dict_to_xml(data: dict, *, tag: str = 'root', deep: int = ..., indent: int = 4, encoding: str = 'unicode', method: str = 'xml') -> str | bytes:
        """将字典转换为 xml 字符串

        如果 encoding 为 `unicode`, 则返回字符串, 否则返回字节串

        Args:
            data (dict): 字典数据
            tag (str, optional): 根节点标签. 默认为 `root`.
            deep (int, optional): 递归深度, 当 deep 为 `...` 时, 则不限制递归深度. 默认为 `...`.
            indent (int, optional): 缩进空格数. 默认为 `4`.
            encoding (str, optional): 编码格式. 默认为 `unicode`.
            method (str, optional): 输出方法, 可选 `xml` | `html` | `text` | `c14n`. 默认为 `xml`.

        Returns:
            str | bytes: xml 字符串
        """
        return XMLUtil.element_to_xml(
            XMLUtil.dict_to_element(
                data,
                tag=tag,
                deep=deep,
                indent=indent,
            ),
            encoding=encoding,
            method=method,
        )
