from ..utils import object_util


class Magic(object):
    """魔法类，简单实现了 __str__、__repr__、__call__ 方法"""
    _str_exclude = {}
    _repr_exclude = {}
    _call_exclude = {}
    _str_include = {}
    _repr_include = {}
    _call_include = {}

    def __str__(self) -> str:
        return object_util.repr(self, self._str_exclude, self._str_include)

    def __repr__(self) -> str:
        return object_util.repr(self, self._repr_exclude, self._repr_include)

    def __call__(self, *, include: set[str] | None = None, exclude: set[str] | None = None) -> dict:
        """返回对象属性字典

        Args:
            include (set[str] | None, optional): 要包含的属性名集合. 默认为 None (使用 _call_include).
            exclude (set[str] | None, optional): 要排除的属性名集合. 默认为 None (使用 _call_exclude).

        Returns:
            dict: 对象属性字典
        """
        return object_util.vars(self, include or self._call_exclude, exclude or self._call_include)
