#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xml.etree.ElementTree import Element, fromstring


class XMLUtil(object):

    @staticmethod
    def element_to_dict(element: Element, default: any = ...) -> dict:
        """将 xml.etree.ElementTree.Element 转换为字典

        Args:
            element (Element): xml.etree.ElementTree.Element 对象
            default (any, optional): 当 xml 中某个节点没有值时, 使用 default 填充, 当 default 为 `...` 时, 则不填充. Defaults to ....

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
    def xml_to_dict(xml: str, default: any = ...) -> dict:
        """将 xml 字符串转换为字典

        Args:
            xml (str): xml 字符串
            default (any, optional): 当 xml 中某个节点没有值时, 使用 default 填充, 当 default 为 `...` 时, 则不填充. Defaults to `...`.

        Returns:
            dict: 解析后的字典
        """
        return XMLUtil.element_to_dict(fromstring(xml), default)
