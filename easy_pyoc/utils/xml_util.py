"""XML 工具"""

from typing import TYPE_CHECKING, Optional, Union
from xml.dom.minidom import parseString
from xml.etree.ElementTree import (
    ParseError,
    XMLParser,
    Element,
    fromstring,
    tostring,
)

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath

from . import path_util


ATTR_PREFIX = '@'
"""属性节点前缀"""

CONTENT_KEY = '#text'
"""内容节点键"""


def auto_type(text: Optional[str]) -> Optional[Union[str, int, float, bool]]:
    """自动类型转换, 用于将 xml 字符串转换为字典时, 自动将字符串转换为数字或布尔类型"""
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


def loads(xml: str, *, parser: Optional[XMLParser] = None) -> dict:
    """将 xml 字符串转换为字典

    Args:
        xml (str): xml 字符串
        parser (XMLParser, optional): xml 解析器, 当为 `None` 时, 使用标准解析器. 默认为 `None`.

    Returns:
        dict: 解析后的字典
    """
    return xml_to_dict(xml, parser=parser)


def dumps(data: dict, *, tag: Optional[str] = None, deep: int = -1, encoding: str = 'unicode', method: str = 'xml') -> str | bytes:
    """将字典转换为 xml 字符串

    如果 encoding 为 `unicode`, 则返回字符串, 否则返回字节串

    Args:
        data (dict): 字典数据
        tag (Optional[str], optional): 根节点标签. 默认为 `root`.
        deep (int, optional): 递归深度, 当 deep 为 `-1` 时, 则不限制递归深度. 默认为 `-1`.
        encoding (str, optional): 编码格式. 默认为 `unicode`.
        method (str, optional): 输出方法, 可选 `xml` | `html` | `text` | `c14n`. 默认为 `xml`.

    Returns:
        str | bytes: xml 字符（节）串
    """
    return dict_to_xml(data, tag=tag, deep=deep, encoding=encoding, method=method)


def load(fp: 'FileDescriptorOrPath', *, parser: Optional[XMLParser] = None, encoding: str = 'utf-8') -> dict:
    """读取文件 xml 文件并转换为字典

    Args:
        fp (FileDescriptorOrPath): 文件路径
        parser (XMLParser, optional): xml 解析器, 当为 `None` 时, 使用标准解析器. 默认为 `None`.
        encoding (str, optional): 文件编码格式. 默认为 `utf-8`.

    Returns:
        dict: 解析后的字典
    """
    with path_util.open(fp, 'r', encoding=encoding) as f:
        return xml_to_dict(f.read(), parser=parser)


def dump(fp: 'FileDescriptorOrPath', data: dict, *, tag: Optional[str] = None, xml_encoding: str = 'unicode', file_encoding: str = 'utf-8', deep: int = -1, method: str = 'xml') -> None:
    """将字典写入文件 xml 文件

    Args:
        fp (FileDescriptorOrPath): 文件路径
        data (dict): 字典数据
        xml_encoding (str, optional): xml 编码格式. 默认为 `unicode`.
        file_encoding (str, optional): 文件编码格式. 默认为 `utf-8`.
        tag (Optional[str], optional): 根节点标签. 默认为 `root`.
        deep (int, optional): 递归深度, 当 deep 为 `-1` 时, 则不限制递归深度. 默认为 `-1`.
        method (str, optional): 输出方法, 可选 `xml` | `html` | `text` | `c14n`. 默认为 `xml`.
    """
    with path_util.open(fp, 'w', encoding=file_encoding) as f:
        f.write(dict_to_xml(data, tag=tag, deep=deep, encoding=xml_encoding, method=method))


def toprettyxml(xml: str | bytes, *, indent: str = '  ', new_line: str = '\n', encoding: Optional[str] = None, standalone: Optional[bool] = None, parser: Optional[XMLParser] = None) -> str | bytes:
    """格式化 xml 字符（节）串

    Args:
        xml (str | bytes): xml 字符串或字节串.
        indent (str, optional): 缩进字符. 默认为 `  `.
        new_line (str, optional): 换行符. 默认为 `\n`.
        encoding (str, optional): 编码格式. 默认为 `None`.
        standalone (Optional[bool], optional):
        parser (XMLParser, optional): xml 解析器, 当为 `None` 时, 使用标准解析器. 默认为 `None`.

        str | bytes: 格式化后的 xml 字符（节）串
    """
    return parseString(xml, parser=parser).toprettyxml(indent, new_line, encoding, standalone)


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
        result[element.tag][f'{ATTR_PREFIX}{k}'] = auto_type(v)

    # 设置子节点
    for child in element:
        tail += child.tail or ''

        if child.tag in result[element.tag]:
            if isinstance(result[element.tag][child.tag], list):
                result[element.tag][child.tag].append(element_to_dict(child)[child.tag])
            else:
                result[element.tag][child.tag] = [
                    result[element.tag][child.tag],
                    element_to_dict(child)[child.tag],
                ]
        else:
            result[element.tag].update(element_to_dict(child))

    # 设置文本
    if not result[element.tag]:
        result[element.tag] = auto_type((element.text or '').strip() or None)
    else:
        if text.lstrip() and tail.rstrip():
            result[element.tag][CONTENT_KEY] = text.lstrip() + tail.rstrip()
        elif text.strip():
            result[element.tag][CONTENT_KEY] = text.strip()
        elif tail.strip():
            result[element.tag][CONTENT_KEY] = tail.strip()
    return result


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


def xml_to_dict(xml: str, *, parser: Optional[XMLParser] = None) -> dict:
    """将 xml 字符串转换为字典

    Args:
        xml (str): xml 字符串
        parser (XMLParser, optional): xml 解析器, 当为 `None` 时, 使用标准解析器. 默认为 `None`.

    Returns:
        dict: 解析后的字典
    """
    return element_to_dict(
        xml_to_element(
            xml,
            parser=parser,
        ),
    )


def element_to_xml(element: Element, *, encoding: str = 'unicode', method: str = 'xml', xml_declaration: bool = False, short_empty_elements: bool = True, default_namespace: Optional[str] = None) -> str | bytes:
    """将 xml.etree.ElementTree.Element 对象转换为 xml 字符串

    如果 encoding 为 `unicode`, 则返回字符串, 否则返回字节串

    Args:
        element (Element): xml.etree.ElementTree.Element 对象
        encoding (str, optional): 编码格式. 默认为 `unicode`.
        method (str, optional): 输出方法, 可选 `xml` | `html` | `text` | `c14n`. 默认为 `xml`.
        xml_declaration (bool, optional): 是否输出 xml 声明. 默认为 `False`.
        short_empty_elements (bool, optional): 是否压缩空元素. 默认为 `True`.
        default_namespace (Optional[str], optional): 默认命名空间. 默认为 `None`.

    Returns:
        str | bytes: xml 字符（节）串
    """
    return tostring(element, encoding, method, xml_declaration=xml_declaration, default_namespace=default_namespace, short_empty_elements=short_empty_elements)


def dict_to_element(data: dict, *, tag: Optional[str] = None, deep: int = -1) -> Element:
    """将字典转换为 xml.etree.ElementTree.Element 对象

    Args:
        data (dict): 字典数据
        tag (Optional[str], optional): 根节点标签. 默认为 `root`.
        deep (int, optional): 递归深度, 当 deep 为 `-1` 时, 则不限制递归深度. 默认为 `-1`.

    Returns:
        Element: xml.etree.ElementTree.Element 对象
    """
    element = Element(tag)

    if deep == 0:
        element.text = str(data)
        return element

    if isinstance(data, dict):
        for k, v in data.items():
            if k.startswith(ATTR_PREFIX):
                element.attrib[k[len(ATTR_PREFIX):]] = str(v)
            elif k == CONTENT_KEY:
                element.text = str(v)
            elif isinstance(v, list):
                for item in v:
                    child = dict_to_element(item, tag=k, deep=deep - 1)
                    element.append(child)
            else:
                child = dict_to_element(v, tag=k, deep=deep - 1)
                element.append(child)
    elif isinstance(data, list):
        for item in data:
            child = dict_to_element(item, tag=tag, deep=deep - 1)
            element.append(child)
    elif data is not None:
        element.text = str(data)

    return element


def dict_to_xml(data: dict, *, tag: Optional[str] = None, deep: int = -1, encoding: str = 'unicode', method: str = 'xml', xml_declaration: bool = False, short_empty_elements: bool = True, default_namespace: Optional[str] = None) -> str | bytes:
    """将字典转换为 xml 字符串

    如果 encoding 为 `unicode`, 则返回字符串, 否则返回字节串

    Args:
        data (dict): 字典数据
        tag (Optional[str], optional): 根节点标签. 默认为 `root`.
        deep (int, optional): 递归深度, 当 deep 为 `-1` 时, 则不限制递归深度. 默认为 `-1`.
        encoding (str, optional): 编码格式. 默认为 `unicode`.
        method (str, optional): 输出方法, 可选 `xml` | `html` | `text` | `c14n`. 默认为 `xml`.
        xml_declaration (bool, optional): 是否输出 xml 声明. 默认为 `False`.
        short_empty_elements (bool, optional): 是否压缩空元素. 默认为 `True`.
        default_namespace (Optional[str], optional): 默认命名空间. 默认为 `None`.

    Returns:
        str | bytes: xml 字符（节）串
    """
    return element_to_xml(
        dict_to_element(
            data,
            tag=tag,
            deep=deep,
        ),
        encoding=encoding,
        method=method,
        xml_declaration=xml_declaration,
        short_empty_elements=short_empty_elements,
        default_namespace=default_namespace,
    )
