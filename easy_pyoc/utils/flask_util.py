"""
Flask 工具
"""

from typing import Any, Sequence, TypeVar, Literal, Type, overload

try:
    import flask
except ModuleNotFoundError:
    raise ModuleNotFoundError('使用该模块前，请先安装 flask 库：`pip install flask`')

from . import object_util


T = TypeVar('T')


# 无键重载：返回整个映射。若 flat 为 True，值为单个字符串，否则为字符串列表
@overload
def quick_data(flat: Literal[True] = ...) -> dict[str, str]: ...
@overload
def quick_data(flat: Literal[False]) -> dict[str, list[str]]: ...

# 单键（字符串）重载：根据 `flat` 返回单个值或列表
@overload
def quick_data(*keys: str, flat: Literal[True] = ...) -> str: ...
@overload
def quick_data(*keys: str, flat: Literal[False]) -> list[str]: ...

# 单键（带类型元组）重载：用户提供类型，返回值为该类型
@overload
def quick_data(*keys: tuple[str, Type[T]], flat: Literal[True] = ...) -> T: ...
@overload
def quick_data(*keys: tuple[str, Type[T]], flat: Literal[False]) -> list[T]: ...

# 单键（带类型与默认值的元组）
@overload
def quick_data(*keys: tuple[str, Type[T], Any], flat: Literal[True] = ...) -> T: ...
@overload
def quick_data(*keys: tuple[str, Type[T], Any], flat: Literal[False]) -> list[T]: ...

# 可变键：返回结果元组
@overload
def quick_data(*keys: Sequence[object], flat: Literal[True] = ...) -> tuple[Any]: ...
@overload
def quick_data(*keys: Sequence[object], flat: Literal[False]) -> tuple[list[Any]]: ...

def quick_data(*keys, flat: bool = True) -> tuple[Any] | dict[str, str | list[str]] | Any:
    """从当前请求快速提取值并按请求键返回。

    函数会合并 `request.args`、`request.values`、`request.form`、`request.files` 的内容，
    并在存在 JSON body 时用其字段覆盖同名字段。合并后的数据作为字典供后续检索。

    Args:
        keys (str, Sequence, optional):
            - 不传（或空）: 返回合并后的完整映射；当 `flat=True` 时每个键对应单个字符串，
                当 `flat=False` 时每个键对应字符串列表。
            - 传入 `str`（字段名）: 返回该字段的值；`flat=True` 返回单个字符串，
                `flat=False` 返回字符串列表。
            - 传入 `(key: str, T)`：索引 0 为字段名，索引 1 为类型/转换函数（如 `int`、`float`），
                返回值会通过该函数转换为 `T`（若原值为空则返回 `None`）。
            - 传入 `(key: str, T, default)`：与上同，但当字段不存在或为 None 时使用 `default`。
            - 传入多个 keys：按顺序返回对应值组成的 `tuple`；若只请求一个字段则直接返回该字段的值而非单元素元组。

        flat (bool, optional):
            - 当 `flat=True` 时，来源于 `MultiDict` 的键会被解析为单一字符串值。
            - 当 `flat=False` 时，值将以字符串列表形式返回。


    Returns:
        (Union[tuple, dict, Any]): 根据 `keys` 与 `flat` 的不同，函数返回 `dict`、
            `tuple` 或单个值；参见模块顶部的重载签名以获取更精确的类型提示。

    Examples:

        - `quick_data()` -> 返回整个请求数据字典
        - `quick_data('id', flat=True)` -> 返回 `id` 的单个字符串值
        - `quick_data(('age', int))` -> 返回 `age` 转为 `int` 的结果或 `None`
        - `quick_data(('x', float, 0.0), ('y', float, 0.0))` -> 返回 `(x: float, y: float)` 元组
    """
    request = flask.request

    # 获取请求数据
    data = {
        **request.args.to_dict(flat),
        **request.values.to_dict(flat),
        **request.form.to_dict(flat),
        **request.files.to_dict(flat),
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
            values.append(object_util.get_value_from_dict(data, key))
        elif isinstance(key, list) or isinstance(key, tuple):
            if len(key) == 2:
                value = object_util.get_value_from_dict(data, key[0])
                values.append(key[1](value) if value else None)
            elif len(key) == 3:
                value = object_util.get_value_from_dict(data, key[0], key[2])
                values.append((key[1](value) if value != None else None))
    return values[0] if len(values) == 1 else tuple(values) if values else None
