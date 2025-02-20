#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from easy_pyoc import XMLUtil


X1 = '''
<item />
<item />
<item />
'''
D1 = {
    "item": [
        "",
        "",
        "",
    ]
}

X2 = '''
<root />
'''
D2 = {
    "root": None
}

X21 = '''
<root id="1" />
'''
D21 = {
    "root": {
        "@id": 1
    }
}

X22 = '''
<root></root>
'''
D22 = {
    "root": None
}

X23 = '''
<root>
</root>
'''
D23 = {
    "root": None
}

X3 = '''
<root>
    <item />
</root>
'''
D3 = {
    "root": {
        "item": None
    }
}

X31 = '''
<root>
    <item />
    <item />
    <item />
</root>
'''
D31 = {
    "root": {
        "item": [
            None,
            None,
            None
        ]
    }
}

X32 = '''
<root>
    <item />
    <item>
    </item>
    <item id="12" />
    <item>123</item>
</root>
'''
D32 = {
    "root": {
        "item": [
            None,
            None,
            {
                "@id": 12,
            },
            123
        ]
    }
}

X5 = '''
<root>
    <item id="1">
        <name>item1</name>
        <value>100.1</value>
        <readonly>true</readonly>
    </item>
    <item id="2">
        <name>item2</name>
        <value>200.2</value>
        <readonly>false</readonly>
    </item>
</root>
'''
D5 = {
    "root": {
        "item": [
            {
                "@id": 1,
                "name": "item1",
                "value": 100.1,
                "readonly": True
            },
            {
                "@id": 2,
                "name": "item2",
                "value": 200.2,
                "readonly": False
            }
        ]
    }
}

X6 = '''
<items>
    <item id="1">
        _id_1_text
        <name>item1</name>
        <value>100</value>
        <subs>
            <sub id="11">
                _id_11_text
                <name>sub11</name>
                <value>110</value>
            </sub>
            <sub id="12">
                <name>sub12</name>
                <value>120</value>
                id_12_text
            </sub>
        </subs>
        id_1_text
    </item>
    <item id="2">

        _id_2_text
        <name>item2</name>
        <value>200</value>
        <subs>
            <sub id="21">
                21
                <name>sub21</name>
                <value>210</value>
                211
            </sub>
            <sub id="22">
                22
                <name>sub22</name>
                222
                <value>220</value>
                223
            </sub>
        </subs>
        id_2_text

    </item>
</items>
'''
D6 = {
    "items": {
        "item": [
            {
                "@id": 1,
                "name": "item1",
                "value": 100,
                "subs": {
                    "sub": [
                        {
                            "@id": 11,
                            "name": "sub11",
                            "value": 110,
                            "#text": "_id_11_text"
                        },
                        {
                            "@id": 12,
                            "name": "sub12",
                            "value": 120,
                            "#text": "id_12_text"
                        }
                    ]
                },
                "#text": "_id_1_text\n        \n        \n        \n        id_1_text"
            },
            {
                "@id": 2,
                "name": "item2",
                "value": 200,
                "subs": {
                    "sub": [
                        {
                            "@id": 21,
                            "name": "sub21",
                            "value": 210,
                            "#text": "21\n                \n                \n                211"
                        },
                        {
                            "@id": 22,
                            "name": "sub22",
                            "value": 220,
                            "#text": "22\n                \n                222\n                \n                223"
                        }
                    ]
                },
                "#text": "_id_2_text\n        \n        \n        \n        id_2_text"
            }
        ]
    }
}


def test_xml_to_dict():
    with pytest.raises(ValueError, match='格式有误'):
        XMLUtil.xml_to_dict(X1)
    assert XMLUtil.xml_to_dict(X2) == D2
    assert XMLUtil.xml_to_dict(X21) == D21
    assert XMLUtil.xml_to_dict(X22) == D22
    assert XMLUtil.xml_to_dict(X23) == D23
    assert XMLUtil.xml_to_dict(X3) == D3
    assert XMLUtil.xml_to_dict(X31) == D31
    assert XMLUtil.xml_to_dict(X32) == D32
    assert XMLUtil.xml_to_dict(X5) == D5
    assert XMLUtil.xml_to_dict(X6) == D6


def test_dict_to_xml():
    with pytest.raises(ValueError, match='格式有误'):
        XMLUtil.dict_to_xml(D1)
    assert XMLUtil.dict_to_xml(D2) == X2
    assert XMLUtil.dict_to_xml(D21) == X21
    assert XMLUtil.dict_to_xml(D22) == X22
    assert XMLUtil.dict_to_xml(D23) == X23
    assert XMLUtil.dict_to_xml(D3) == X3
    assert XMLUtil.dict_to_xml(D31) == X31
    assert XMLUtil.dict_to_xml(D32) == X32
    assert XMLUtil.dict_to_xml(D5) == X5
    assert XMLUtil.dict_to_xml(D6) == X6


if __name__ == '__main__':
    pytest.main(['-s', __file__])
