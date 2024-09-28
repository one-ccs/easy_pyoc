# pyoc

自定义 Python 包，封装一些功能


## 1、socket

- `ServerSocket` TCP/UDP/MULTICAST 服务端
- `ClientSocket` TCP/UDP/MULTICAST 客户端

## 2、OcGui

实现自定义标题栏的窗口，包含放大、缩小、关闭的基本功能，实现窗口移动，拖动改变大小。

支持加载本地图片或网络资源为背景图片。

配合 OcGuiIconRc 默认的 QSS 效果，可以实现较为不错的主窗口。

### class OTitleBar(QWidget)

* 自定义标题栏，不可单独使用.

### class OWindow(QMainWindow)

* 自定义窗口，内置 自定义标题栏及 qss;

1. 实现了自定义标题栏的主窗口，包含以下功能：

   + 窗口最大化、最小化、关闭;
   + 窗口移动;
   + 拖动改变窗口大小;
2. 基于 requests.get 实现了从互联网及本地加载背景图片.
