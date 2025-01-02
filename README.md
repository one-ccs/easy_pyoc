# easy_pyoc

自定义 Python 包，封装一些功能。

注：带 `*` 的需要额外安装依赖，并使用完整路径导入。

## 安装

```python
pip install easy_pyoc
```

## 工具

### 1、classes

- `Config` 配置类，读取配置文件，并让其可以像访问对象属性一样访问配置属性，支持多种格式，如 json、yaml、toml
- `Logger` 单例 Logger 类
- `Magic` 魔法类，简单实现了 __str__、__repr__、__call__ 方法

### 2、socket

对 socket 进行了封装，支持 TCP/UDP/MULTICAST 协议，支持服务端和客户端模式，支持多播。

- `ServerSocket` TCP/UDP/MULTICAST 服务端
- `ClientSocket` TCP/UDP/MULTICAST 客户端

### 3、util

封装了一些工具函数。

- `CRCUtil` CRC 校验工具，提供 CRC16 校验功能
- `DatetimeUtil` 日期相关工具
- *`FlaskUtil` Flask 相关工具
- `FuncUtil` 函数相关工具, 提供函数调用日志装饰器、异常捕获装饰器、执行钩子装饰器等
- `JSONUtil` json 相关工具
- `KNXUtil` KNXnet/IP 相关工具
- `NetworkUtil` 提供网络唤醒、网络信息获取等功能
- `ObjectUtil` 对象相关工具，提供字典与对象相互转换等函数
- `PathUtil` 路径相关工具
- `StringUtil` 字符串相关工具，提供进制转换、字符串命名格式化等功能
- `ThreadUtil` 线程相关工具，提供任务执行/取消等功能
- `TOMLUtil` TOML 相关工具，仅提供 TOML 格式解析功能
- `XMLUtil` xml 相关工具，提供 xml 文件读写功能
- `YAMLUtil` yaml 相关工具，提供 yaml 文件读写功能

### 4、OcGui

实现自定义标题栏的窗口，包含放大、缩小、关闭的基本功能，实现窗口移动，拖动改变大小。

支持加载本地图片或网络资源为背景图片。

配合 OcGuiIconRc 默认的 QSS 效果，可以实现较为不错的主窗口。

#### class OTitleBar(QWidget)

* 自定义标题栏，不可单独使用.

#### class OWindow(QMainWindow)

* 自定义窗口，内置 自定义标题栏及 qss;

1. 实现了自定义标题栏的主窗口，包含以下功能：

   + 窗口最大化、最小化、关闭;
   + 窗口移动;
   + 拖动改变窗口大小;
2. 基于 requests.get 实现了从互联网及本地加载背景图片.
