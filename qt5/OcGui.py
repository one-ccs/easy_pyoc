#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""基于 PyQt5 的 GUI.


classes:
    class OTitleBar(QWidget)
    自定义标题栏，不可单独使用.

    class OWindow(QMainWindow)
    自定义窗口，内置 自定义标题栏及 qss;
    1. 实现了自定义标题栏的主窗口，包含以下功能：
        a. 窗口最大化、最小化、关闭;
        b. 窗口移动;
        c. 拖动改变窗口大小;
    2. 基于 requests.get 实现了从互联网及本地加载背景图片.
"""

from PyQt5.QtCore import Qt, QObject, QEvent, QSize, QRect
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import *
from requests import get
from os.path import exists
import logging

from PyOc import OcGuiRes


__auth__ = 'one-ccs'

logging.basicConfig(format='%(levelname)s: %(message)s')


class OTitleBar(QWidget):
    """自定义标题栏

    实现了最大化与最小化"""

    def __init__(self, parent):
        super().__init__()
        # 设置尺寸策略
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(36)
        # ~ self.setAttribute(Qt.WA_TransparentForMouseEvents)  # 鼠标点击穿透

        self._parent = parent                 # 父（主）窗口
        self._menu_button = None              # 菜单按钮（QWidget）
        self._skin_button = None              # 换肤按钮（QWidget）
        self._title_icon = None               # 图标（QLabel）
        self.title_label = None               # 标题（QLabel）
        self._min_button = None               # 最小化按钮（QWidget）
        self._max_button = None               # 最大化按钮（QWidget）
        self._close_button = None             # 关闭按钮（QWidget）
        self._central_layout = None           # 主布局（水平）

        self._menu_icon = None                # 菜单图标
        self._skin_icon = None                # 换肤图标
        self._min_icon = None                 # 最小化按钮图标
        self._max_icon = None                 # 最大化按钮图标
        self._restore_icon = None             # 最大化按钮恢复图标
        self._close_icon = None               # 关闭按钮图标

        self._series = 'black'                # 图标样式（默认黑色）

        # 初始化标题栏属性
        self.init_titlebar()
        # 设置最窄宽度
        self.setMinimumWidth(self._title_icon.width() * 13)
        # 去除布局及控件间的间隔及边距
        set_all_gap(self._central_layout, left=8)
        self.setMouseTracking(True)
        self._title_icon.setMouseTracking(True)
        self.title_label.setMouseTracking(True)

    def init_titlebar(self):
        """初始化标题栏属性"""
        # 添加标题控件
        self._title_icon = QLabel()
        self.title_label = QLabel()
        self._min_button = QPushButton()
        self._max_button = QPushButton()
        self._close_button = QPushButton()
        self._title_icon.setObjectName('OTitleIcon')
        self.title_label.setObjectName('OTitleLabel')
        self._min_button.setObjectName('OMinButton')
        self._max_button.setObjectName('OMaxButton')
        self._close_button.setObjectName('OCloseButton')

        # 设置 icon
        set_icon(self._title_icon, ':/res/images/one_ccs.ico')
        self._load_icon()

        # 设置 icon 宽度
        self._title_icon.setFixedHeight(24)
        self._title_icon.setFixedWidth(24)

        # 设置标题控件策略
        expanding = QSizePolicy.Expanding
        self.title_label.setSizePolicy(expanding, expanding)

        # 设置窗口主布局，并放入主容器中
        self._central_layout = QHBoxLayout(self)

        # 把控件添加进标题栏布局
        self._central_layout.addWidget(self._title_icon, alignment=Qt.AlignVCenter)
        self._central_layout.addWidget(self.title_label, alignment=Qt.AlignVCenter)
        self._central_layout.addWidget(self._min_button, alignment=Qt.AlignVCenter)
        self._central_layout.addWidget(self._max_button, alignment=Qt.AlignVCenter)
        self._central_layout.addWidget(self._close_button, alignment=Qt.AlignVCenter)

        # 链接信号/槽
        self._min_button.clicked.connect(self.min_button_click)
        self._max_button.clicked.connect(self.max_button_click)
        self._close_button.clicked.connect(self.close_button_click)

    def set_menu_icon(self, icon):
        """设置菜单按钮图标"""
        if not isinstance(icon, QPixmap):
            icon = QPixmap(icon)

        icon = icon.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._menu_icon = QIcon(QPixmap(icon))
        self._menu_button.setPixmap()
        self._menu_button.setIcon(self._menu_icon)

    def set_skin_icon(self, icon):
        """设置最换肤按钮图标"""
        self._skin_icon = QIcon(QPixmap(icon))
        self._skin_button.setIcon(self._skin_icon)

    def set_min_icon(self, icon):
        """设置最小化按钮图标"""
        self._min_icon = QIcon(QPixmap(icon))
        self._min_button.setIcon(self._min_icon)

    def set_max_icon(self, icon):
        """设置最大化按钮图标"""
        self._max_icon = QIcon(QPixmap(icon))
        self._max_button.setIcon(self._max_icon)

    def set_restore_icon(self, icon):
        """设置恢复按钮图标"""
        self._restore_icon = QIcon(QPixmap(icon))

    def set_close_icon(self, icon):
        """设置关闭按钮图标"""
        self._close_icon = QIcon(QPixmap(icon))
        self._close_button.setIcon(self._close_icon)

    def set_icon_series(self, series):
        """设置标题图标系列（黑/白）"""
        if series == 'black' or series == 'white':
            self._series = series
            self._load_icon()

    def add_menu_button(self):
        """添加菜单按钮"""
        self._menu_button = QPushButton()
        self.setObjectName('OMenuButton')
        self._menu_button.installEventFilter(self._parent)
        if self._series == 'black':
            self.set_menu_icon(':/res/images/title_menu.ico')
        elif self._series == 'white':
            self.set_menu_icon(':/res/images/title_menu_w.ico')
        self._central_layout.addWidget(self._menu_button)
        # 重新放置主按钮
        self._central_layout.addWidget(self._min_button)
        self._central_layout.addWidget(self._max_button)
        self._central_layout.addWidget(self._close_button)

        return self._menu_button

    def add_skin_button(self):
        """添加换肤按钮"""
        self._skin_button = QPushButton()
        self._skin_button.setObjectName('OSkinButton')
        self._skin_button.installEventFilter(self._parent)
        if self._series == 'black':
            self.set_skin_icon(':/res/images/title_skin.ico')
        elif self._series == 'white':
            self.set_skin_icon(':/res/images/title_skin_w.ico')
        # 设置图标大小
        # ~ self._skin_button.setIconSize(QSize(22, 22))
        self._central_layout.addWidget(self._skin_button)
        # 重新放置主按钮
        self._central_layout.addWidget(self._min_button)
        self._central_layout.addWidget(self._max_button)
        self._central_layout.addWidget(self._close_button)

        return self._skin_button

    def _load_icon(self):
        """设置图标"""

        res = ':/res/images/'
        if self._series == 'black':
            if self._menu_button:
                self.set_menu_icon(res + 'title_menu.ico')
            if self._skin_button:
                self.set_skin_icon(res + 'title_skin.ico')
            self.set_min_icon(res + 'title_min.ico')
            self.set_max_icon(res + 'title_max.ico')
            self.set_restore_icon(res + 'title_restore.ico')
            self.set_close_icon(res + 'title_close.ico')
        elif self._series == 'white':
            if self._menu_button:
                self.set_menu_icon(res + 'title_menu_w.ico')
            if self._skin_button:
                self.set_skin_icon(res + 'title_skin_w.ico')
            self.set_min_icon(res + 'title_min_w.ico')
            self.set_max_icon(res + 'title_max_w.ico')
            self.set_restore_icon(res + 'title_restore_w.ico')
            self.set_close_icon(res + 'title_close_w.ico')

    def _check_parent(self):
        """判断是否有父窗口"""
        if isinstance(self._parent, QWidget) or (
           isinstance(self._parent, QMainWindow)):
            return True
        else:
            return False

    # 槽函数
    def min_button_click(self):
        """最小化"""
        if self._check_parent():
            self._parent.showMinimized()
        else:
            self.showMinimized()

    def max_button_click(self):
        """最大化（恢复）"""
        if self._check_parent():
            if self._parent.isMaximized():
                self._parent.showNormal()
                self._max_button.setIcon(self._max_icon)
            else:
                self._parent.showMaximized()
                self._max_button.setIcon(self._restore_icon)

    def close_button_click(self):
        """关闭"""
        if self._check_parent():
            self._parent.close()
        else:
            self.close()


class OWindow(QMainWindow):
    """这是自定义的窗口"""

    def __init__(self, title='PyOc'):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)         # 设置为无标题栏
        # ~ self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        # ~ self.setWindowOpacity(0.85)                     # 设置窗口不透明度

        self._super = None                    # 顶级控件（放置背景图片）
        self._central = None                  # 主部件（放置标题栏、工具栏、客户区）
        self._super_layout = None             # 顶级布局（垂直）
        self._central_layout = None           # 中心布局（垂直）

        self.title = title                    # 标题
        self.titlebar = None                  # 标题栏（OTitleBar）
        self.toolbar = None                   # 工具栏（QStackedWidget）
        self.client = None                    # 客户区（QStackedWidget）

        self.MOVE_SENSITIVITY = 3             # 窗口移动反应灵敏度，反比
        self.MARGIN = 9                       # 边缘宽度(拖动改变窗口大小)

        self._bgimg = None                    # 存放背景图片的变量
        self._isPressed = False
        self._press_button = None
        self._last_geometry = None
        self._area = None
        self._move_count = 0

        # 初始化窗口属性
        self.init_window()
        self.setMinimumHeight(self.titlebar.height())
        self.setMinimumWidth(self.titlebar.minimumWidth())
        # 设置布局间隙
        set_all_gap(self._super_layout)
        set_all_gap(self._central_layout)
        # 设置尺寸策略
        self.toolbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # 安装事件过滤器
        self.titlebar._min_button.installEventFilter(self)
        self.titlebar._max_button.installEventFilter(self)
        self.titlebar._close_button.installEventFilter(self)
        # 设置鼠标追踪
        self.setMouseTracking(True)
        self._super.setMouseTracking(True)
        self._central.setMouseTracking(True)
        self.toolbar.setMouseTracking(True)
        self.client.setMouseTracking(True)
        # 加载默认样式表
        self.setStyleSheet('')
        # 显示窗口
        self.show()

    def init_window(self):
        """初始化窗口"""

        # 超·部件（不显示）
        self._super = QWidget()
        self._super.setObjectName('OSuper')
        # 重设窗口主控件
        self.setCentralWidget(self._super)

        # 中心控件(显示部分)
        self._central = QWidget()
        self._central.setObjectName('OCentral')
        self._central_layout = QVBoxLayout(self._central)

        # 标题栏
        self.titlebar = OTitleBar(self)
        # 设置标题
        self.setWindowTitle(self.title)

        # 工具栏
        self.toolbar = QStackedWidget()

        # 客户区，放入客户区布局
        self.client = QStackedWidget()
        self.client.setObjectName('OClient')

        # 中心布局添加部件
        self._central_layout.addWidget(self.titlebar)
        self._central_layout.addWidget(self.toolbar)
        self._central_layout.addWidget(self.client)

        # 超·布局
        self._super_layout = QVBoxLayout(self._super)
        self._super_layout.addWidget(self._central)
        self._super.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.setMinimumHeight(self.titlebar.title_label.height())

    def set_titlebar_height(self, height):
        """设置标题栏高度"""

        self.titlebar.setFixedHeight(height)

    def _adapt_bg(self, image):
        """返回适应窗口大小的背景图片"""
        image = image.scaled(self.width(), self.height(), \
                             Qt.KeepAspectRatioByExpanding, \
                             Qt.SmoothTransformation)
        return image

    def set_bg(self, image):
        """设置本地背景图片

        形参 image 可以是 QPixmap 实例、资源路径或磁盘路径。
        """
        if type(image) == QPixmap:
            self._bgimg = image
        elif type(image) == str:
            image = image.strip()
            if image[:4] == 'http':
                logging.warning("set_bg(self, image: Union[QPixmap, path])" +
                                "\n:  The argument 1 is a URL like, you might want to use" +
                                " set_web_bg(self, url, params=None, **kwargs).")
                self.set_web_bg(image)
                return None
            elif not image:
                logging.warning("set_bg(self, image: Union[QPixmap, path])" +
                                "\n:  The argument 1 is null.")
                return None
            elif not exists(image) and image[:2] != ':/':
                logging.warning("set_bg(self, image: Union[QPixmap, path])" +
                                "\n:  The file '{}' is inexistence.".format(image))
                return None
            image = QPixmap(image)
            self._bgimg = image
        else:
            return None
        adapt_image = self._adapt_bg(self._bgimg)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(adapt_image))
        self.setPalette(palette)

    def set_web_bg(self, url, params=None, **kwargs):
        """使用 requests.get 加载来自网络的背景图片"""

        if url[:4] == 'http':
            try:
                response = get(url, params=None, **kwargs)
            except Exception as e:
                loggin.warning('Error: OcGui.OWindow.set_web_bg, ', e)
                return False
            else:
                img = QPixmap()
                img.loadFromData(response.content)
                self._bgimg = img
                palette = QPalette()
                adapt = self._adapt_bg(img)
                palette.setBrush(QPalette.Window, QBrush(adapt))
                self.setPalette(palette)
                return True

    def add_tools(self, widget):
        """添加工具栏"""

        if not isinstance(widget, QWidget):
            logging.warning('add_tools(self, widget: QWidget): argument 1 ' +
                            'is unexpected type {}'.format(type(widget)))
            return None

        return self.toolbar.addWidget(widget)

    def set_page(self, index, obj='client'):
        """切换页面"""

        if obj == 'client':
            self.client.setCurrentIndex(index)
        elif obj == 'toolbar':
            self.toolbar.setCurrentIndex(index)

    def _change_cursor_icon(self, area):
        """改变鼠标在窗口边缘时的图片"""

        if self.maximumWidth() == self.minimumWidth() and (area == 21 or area == 23):
            return None
        if self.maximumHeight() == self.minimumHeight() and (area == 12 or area == 32):
            return None

        if area == 11 or area == 33:
            self.setCursor(Qt.SizeFDiagCursor)
        elif area == 12 or area == 32:
            self.setCursor(Qt.SizeVerCursor)
        elif area == 13 or area == 31:
            self.setCursor(Qt.SizeBDiagCursor)
        elif area == 21 or area == 23:
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def _compute_area(self, pos):
        """计算鼠标在窗口中的区域

        Args:
            pos: 鼠标相对于窗口的位置
            margin: 以此值为外边框宽度，划为九宫格区域
        """
        margin = self.MARGIN

        # 定位列坐标
        if pos.x() < margin:
            line = 1
        elif pos.x() > self.width() - margin:
            line = 3
        else:
            line = 2
        # 定位行坐标并结合列坐标
        if pos.y() < margin:
            return 10 + line
        elif pos.y() > self.height() - margin:
            return 30 + line
        else:
            return 20 + line

    def _pos_percent(self, pos):
        """返回鼠标相对窗口的纵横百分比"""

        if pos.x() <= 0:
            x = 0
        else:
            x = round(pos.x() / self.width(), 3)

        if pos.y() <= 0:
            y = 0
        else:
            y = round(pos.y() / self.height(), 3)

        return x, y

    def _move(self, event):
        """实现窗口移动"""

        self._move_count += 1

        # 判断移动次数，减少灵敏度
        if self._move_count < self.MOVE_SENSITIVITY:
            return None

        # 最大化时需恢复并移动到鼠标位置
        if self.isMaximized():
            relative = self._pos_percent(event.pos())
            self.titlebar.max_button_click()
            gpos = event.globalPos()
            width = self._last_geometry.width()
            height = self._last_geometry.height()
            x = gpos.x() - round(width * relative[0])
            y = gpos.y() - round(height * relative[1])

            self.setGeometry(x, y, width, height)
        else:
            # 鼠标移动偏移量
            offsetPos = event.globalPos() - self._posLast
            # ~ print(self.pos(), '->', self.pos() + offsetPos)
            self.move(self.pos() + offsetPos)

    def _resize(self, event):
        """实现拖动调整窗口大小的函数

        以新旧坐标差计算偏移量，使用 QRect 实例附带位置坐标；
        核心算法做了三重校验，以确保任意情况下窗口都能以正确的方式调整大小：
            一: 横纵坐标与最值校验，确保在最值范围内调整大小；
            二: 横纵坐标与左右区块校验，确保鼠标在窗口边缘时才调整大小；
            三: 横纵坐标与极值偏移量校验，确保在改变坐标的情况下，窗口不会发生漂移
        """
        # 鼠标在窗口中的区域
        area = self._area
        # 鼠标偏移量
        offsetPos = event.globalPos() - self._posLast
        # 鼠标在窗口中的坐标
        winPos = event.pos()

        # 矩形实例，被赋予窗口的几何属性（x, y, width, height）
        # 利用其改变左上角坐标，但右下角坐标不变的特性，实现窗口移动效果
        rect = QRect(self.geometry())

        x = rect.x()
        y = rect.y()
        width = rect.width()
        height = rect.height()

        minWidth = self.minimumWidth()
        minHeight = self.minimumHeight()
        maxWidth = self.maximumWidth()
        maxHeight = self.maximumHeight()

        # 根据不同区域选择不同操作
        if area == 11:
            # 左上
            pos = rect.topLeft()

            if offsetPos.x() < 0 and width < maxWidth or offsetPos.x() > 0 and width > minWidth:
                if offsetPos.x() < 0 and winPos.x() <= 0 or offsetPos.x() > 0 and winPos.x() >= 0:
                    if (maxWidth - width) >= -offsetPos.x() and (width - minWidth) >= offsetPos.x():
                        pos.setX(pos.x() + offsetPos.x())

            if offsetPos.y() < 0 and height < maxHeight or offsetPos.y() > 0 and height > minHeight:
                if offsetPos.y() < 0 and winPos.y() <= 0 or offsetPos.y() > 0 and winPos.y() >= 0:
                    if (maxHeight - height) >= -offsetPos.y() and (height - minHeight) >= offsetPos.y():
                        pos.setY(pos.y() + offsetPos.y())

            rect.setTopLeft(pos)

        elif area == 13:
            # 右上
            pos = rect.topRight()

            if offsetPos.x() < 0 and width > minWidth or offsetPos.x() > 0 and width < maxWidth:
                if offsetPos.x() < 0 and winPos.x() <= width or offsetPos.x() > 0 and winPos.x() >= width:
                    pos.setX(pos.x() + offsetPos.x())

            if offsetPos.y() < 0 and height < maxHeight or offsetPos.y() > 0 and height > minHeight:
                if offsetPos.y() < 0 and winPos.y() <= 0 or offsetPos.y() > 0 and winPos.y() >= 0:
                    if (maxHeight - height) >= -offsetPos.y() and (height - minHeight) >= offsetPos.y():
                        pos.setY(pos.y() + offsetPos.y())

            rect.setTopRight(pos)

        elif area == 31:
            # 左下
            pos = rect.bottomLeft()

            if offsetPos.x() < 0 and width < maxWidth or offsetPos.x() > 0 and width > minWidth:
                if offsetPos.x() < 0 and winPos.x() <= 0 or offsetPos.x() > 0 and winPos.x() >= 0:
                    if (maxWidth - width) >= -offsetPos.x() and (width - minWidth) >= offsetPos.x():
                        pos.setX(pos.x() + offsetPos.x())

            if offsetPos.y() < 0 and height > minHeight or offsetPos.y() > 0 and height < maxHeight:
                if offsetPos.y() < 0 and winPos.y() <= height or offsetPos.y() > 0 and winPos.y() >= height:
                    pos.setY(pos.y() + offsetPos.y())

            rect.setBottomLeft(pos)

        elif area == 33:
            # 右下
            pos = rect.bottomRight()

            if offsetPos.x() < 0 and width > minWidth or offsetPos.x() > 0 and width < maxWidth:
                if offsetPos.x() < 0 and winPos.x() <= width or offsetPos.x() > 0 and winPos.x() >= width:
                    pos.setX(pos.x() + offsetPos.x())

            if offsetPos.y() < 0 and height > minHeight or offsetPos.y() > 0 and height < maxHeight:
                if offsetPos.y() < 0 and winPos.y() <= height or offsetPos.y() > 0 and winPos.y() >= height:
                    pos.setY(pos.y() + offsetPos.y())

            rect.setBottomRight(pos)

        elif area == 12:
            # 中上
            if offsetPos.y() < 0 and height < maxHeight or offsetPos.y() > 0 and height > minHeight:
                if offsetPos.y() < 0 and winPos.y() <= 0 or offsetPos.y() > 0 and winPos.y() >= 0:
                    if (maxHeight - height) >= -offsetPos.y() and (height - minHeight) >= offsetPos.y():
                        rect.setTop(rect.top() + offsetPos.y())

        elif area == 21:
            # 中左
            if offsetPos.x() < 0 and width < maxWidth or offsetPos.x() > 0 and width > minWidth:
                if offsetPos.x() < 0 and winPos.x() <= 0 or offsetPos.x() > 0 and winPos.x() >= 0:
                    if (maxWidth - width) >= -offsetPos.x() and (width - minWidth) >= offsetPos.x():
                        rect.setLeft(rect.left() + offsetPos.x())

        elif area == 23:
            # 中右
            if offsetPos.x() < 0 and width > minWidth or offsetPos.x() > 0 and width < maxWidth:
                if offsetPos.x() < 0 and winPos.x() <= width or offsetPos.x() > 0 and winPos.x() >= width:
                    rect.setRight(rect.right() + offsetPos.x())

        elif area == 32:
            # 中下
            if offsetPos.y() < 0 and height > minHeight or offsetPos.y() > 0 and height < maxHeight:
                if offsetPos.y() < 0 and winPos.y() <= height or offsetPos.y() > 0 and winPos.y() >= height:
                    rect.setBottom(rect.bottom() + offsetPos.y())

        # 设置窗口几何属性（坐标，宽高）
        self.setGeometry(rect)

    # 重写方法
    def setWindowIcon(self, icon='default', width=16, height=16):
        """设置窗口图标"""

        if icon == 'default':
            icon = set_icon(self.titlebar._title_icon, ':/res/images/one_ccs.ico',
                            width=width, height=height)
        else:
            icon = set_icon(self.titlebar._title_icon, icon, width=width, height=height)

        QWidget.setWindowIcon(self, QIcon(icon))

    def setWindowTitle(self, string):
        """设置窗口标题"""
        self.titlebar.title_label.setText(string)

    def addWidget(self, widget):
        """每添加一个 widget 既一页"""

        if not isinstance(widget, QWidget):
            logging.warning('addWidget(self, widget: QWidget): argument 1 ' +
                            'is unexpected type {}'.format(type(widget)))
            return None

        return self.client.addWidget(widget)

    def addLayout(self, *args):
        """禁止添加布局"""
        logging.warning("You shouldn't useadd Layout(self, *args), " +
                        "you should use addWidget(self, widget).")

    def setStyleSheet(self, qss, default='enabled'):
        """加载样式表"""

        if not isinstance(qss, str):
            logging.warning('setStyleSheet(self, qss: str): argument 1' +
                            'is a unexpected type ' + type(qss))
            return None

        if default != 'disabled':
            qss = OcGuiRes.qss + qss

        if qss[:8] == 'PyOc.qss':
            qss = qss[8:]
            QWidget.setStyleSheet(self, qss)
        elif qss.find('\\') or qss.find('/'):
            try:
                with open(qss, 'r') as f:
                    lines = f.readlines()
                    stylesheet = ''.join(lines)
            except Exception as e:
                logging.warning('Error of function OWindow.setStyleSheet()\n', e)
            else:
                QWidget.setStyleSheet(self, stylesheet)
        else:
            QWidget.setStyleSheet(self, qss)

    # 重写事件
    def eventFilter(self, obj, event):
        """事件过滤器"""

        minb = self.titlebar._min_button
        maxb = self.titlebar._max_button
        clob = self.titlebar._close_button
        skib = self.titlebar._skin_button
        menb = self.titlebar._menu_button

        if obj == minb or obj == maxb or obj == clob or obj == skib or obj == menb:
            self.setCursor(Qt.ArrowCursor)
            if obj == maxb and event.type() == QEvent.MouseButtonPress:
                self._last_geometry = self.geometry()

            # ~ return True  # 说明这个事件已被处理，其他控件别插手

        return QObject.eventFilter(self, obj, event)  # 交由其他控件处理

    def resizeEvent(self, event):
        """重写窗口大小改变事件，实现自适应背景图片"""

        if not self._bgimg:
            return None
        palette = QPalette()
        img = self._adapt_bg(self._bgimg)
        palette.setBrush(QPalette.Window, QBrush(img))
        self.setPalette(palette)

    def mouseDoubleClickEvent(self, event):
        """重写继承的鼠标双击事件"""

        self._last_geometry = self.geometry()
        self.titlebar.max_button_click()

        return QMainWindow.mouseDoubleClickEvent(self, event)

    def mousePressEvent(self, event):
        """重写继承的鼠标按住事件"""

        self._isPressed = True
        self._press_button = event.button()
        self._area = self._compute_area(event.pos())
        self._move_count = 0
        self._posLast = event.globalPos()

        return QMainWindow.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """重写继承的鼠标释放事件"""

        self._isPressed = False
        self._press_button = None
        self._area = None
        self._move_count = 0
        self.setCursor(Qt.ArrowCursor)

        return QMainWindow.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        """重写继承的鼠标移动事件，实现拖动改变窗口大小"""

        area = self._compute_area(event.pos())

        # 调整窗口大小及移动
        if self._isPressed and self._press_button == Qt.LeftButton:
            if self._area == 22:
                self._move(event)
            elif not self.isMaximized():
                self._resize(event)

            # 更新鼠标全局坐标
            self._posLast = event.globalPos()
            return None
        if not self._isPressed and not self.isMaximized():
            # 调整鼠标图标，按下鼠标后锁定状态
            self._change_cursor_icon(area)

        return QMainWindow.mouseMoveEvent(self, event)


def set_icon(obj, icon, width=20, height=20):
    """为 QLabel 或 QPushButton 设置图像"""

    if not isinstance(obj, QLabel) and not isinstance(obj, QPushButton):
        logging.warning('set_icon(obj: Union[QLabel, QPushButton], icon,' +
                        ' width=20, height=20): argument 1 is unexpected' +
                        ' type {}'.format(type(obj)))
        return None

    KAR = Qt.KeepAspectRatio
    STFM = Qt.SmoothTransformation

    if isinstance(obj, QLabel):
        if isinstance(icon, str):
            icon = QPixmap(icon).scaled(width, height, KAR, STFM)

        obj.setPixmap(icon)
    else:
        if isinstance(icon, str):
            icon = QIcon(QPixmap(icon))
        if isinstance(icon, QPixmap):
            icon = QIcon(icon)

        obj.setIcon(icon)
        obj.setIconSize(QSize(width, height))

    return icon


def set_all_gap(layout, left=0, top=0, right=0, bottom=0, spacing=0):
    """设置布局间的所有间距"""

    # 设置布局边距(左,顶,右,底)
    layout.setContentsMargins(left, top, right, bottom)
    # 去除布局及控件间的间隔
    layout.setSpacing(spacing)

