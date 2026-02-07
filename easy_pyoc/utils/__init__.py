"""
工具函数
"""


class NotThisModule(object):

    def __new__(cls, *args, **kwargs):
        raise ImportError(cls.get_msg())

    def __repr__(self):
        raise ImportError(self.get_msg())

    def __getattribute__(self, name):
        raise ImportError(self.get_msg())

    @classmethod
    def get_msg(cls):
        return f'没有成功导入 "{cls.get_name()}", 原因: "{cls.get_reason()}".'

    @classmethod
    def get_name(cls):
        return cls.__not_this_module__['name']

    @classmethod
    def get_reason(cls):
        return cls.__not_this_module__['reason']


def not_this_module(name: str, reason: str):
    return type('NotThisModule', (NotThisModule,), {
        '__not_this_module__': {'name': name, 'reason': reason},
    })
