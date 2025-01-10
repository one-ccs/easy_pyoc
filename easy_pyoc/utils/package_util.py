#!/usr/bin/env python
# -*- coding: utf-8 -*-
from importlib import metadata


class PackageUtil:
    """包工具类"""

    @staticmethod
    def get_version(package_name: str) -> str:
        """获取包的版本字符串

        Args:
            package_name (str): 包名

        Returns:
            _type_: 版本字符串
        """
        return metadata.version(package_name)


if __name__ == '__main__':
    print(PackageUtil.get_version('easy_pyoc'))
