#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Union
from flask import Request

from .object_util import ObjectUtil


class RequestUtils(object):

    @staticmethod
    def quick_data(request: Request, *keys) -> Union[tuple, dict, any]:
        """将 flask.Request 中的 args, values, form, files, json 解构为元组

        例 <json>::
            quick_data(request, 'id', 'coords.longitude', 'coords.latitude')
        例 <form>::
            quick_data(request, ('id', int), ('coords[longitude]', float), ('coords[latitude]',float))

        :param keys: None 直接返回整个数据 (dict 类型)
        :param keys: str 返回取到的值
        :param keys: (key: str, type: T) 索引 0 为字段名, 索引 1 为字段类型
        :param keys: (key: str, type: T, default: any) 索引 0 为字段名, 索引 1 为字段类型, 索引 2 为默认值
        :return -> (tuple | dict | any) 返回元组或字典, 当结果列表长度为 1 时直接返回
        """
        # 获取请求数据
        data = {
            **request.args.to_dict(),
            **request.values.to_dict(),
            **request.form.to_dict(),
            **request.files.to_dict(),
        }
        json_data = request.get_json(force=True, silent=True)
        if json_data:
            data.update(json_data)

        if not keys:
            return data
        # 解析为元组
        values = []
        for key in keys:
            if isinstance(key, str):
                values.append(ObjectUtil.get_value_from_dict(data, key))
            elif isinstance(key, list) or isinstance(key, tuple):
                if len(key) == 2:
                    value = ObjectUtil.get_value_from_dict(data, key[0])
                    values.append(key[1](value) if value else None)
                elif len(key) == 3:
                    value = ObjectUtil.get_value_from_dict(data, key[0], key[2])
                    values.append((key[1](value) if value != None else None))
        return values[0] if len(values) == 1 else tuple(values) if values else None
