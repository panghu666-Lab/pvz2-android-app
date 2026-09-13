# -*- coding: utf-8 -*-
"""
PVZ2脚本工具 - Android APP版本
基于Kivy框架，集成植物大战僵尸2脚本功能
大学狗工具风格UI V7 - 完全重写
"""

import os
import sys
import json
import time
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex

# 全局调试日志
debug_logs = []

def debug_print(msg):
    """调试打印"""
    debug_logs.append(msg)
    print(f"[DEBUG] {msg}")

# 注册中文字体
def get_resource_path():
    """获取资源路径，兼容Android和PC"""
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources'),
        '/data/data/org.pvz2.pvz2tool/files/app/resources',
        os.path.join(os.getcwd(), 'resources'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return possible_paths[0]

RESOURCE_PATH = get_resource_path()
FONT_PATH = os.path.join(RESOURCE_PATH, 'zt3.ttf')

if os.path.exists(FONT_PATH):
    LabelBase.register(name='ChineseFont', fn_regular=FONT_PATH)
else:
    try:
        LabelBase.register(name='ChineseFont', fn_regular='/system/fonts/DroidSansFallback.ttf')
    except:
        LabelBase.register(name='ChineseFont', fn_regular=None)

# 颜色定义 - 大学狗工具风格
COLORS = {
    'bg': '#fdf2f8',
    'card': '#ffffff',
    'icon_bg': '#e9d5ff',
    'icon_bg_pressed': '#c4b5fd',
    'accent': '#7c3aed',
    'green': '#16a34a',
    'text': '#1f2937',
    'text_dim': '#6b7280',
    'text_light': '#ffffff',
}

# 导入脚本接口
try:
    from script_interface import ScriptInterface
    SCRIPT_AVAILABLE = True
except Exception as e:
    debug_print(f"导入脚本接口失败: {e}")
    SCRIPT_AVAILABLE = False


class IconButton(Button):
    """圆形图标按钮 - 大学狗工具风格
    使用Button的background_normal显示图标，更可靠
    """
    
    def __init__(self, text='', icon_source=None, **kwargs):
        super().__init__(**kwargs)
        
        self.text = text
        self.font_name = 'ChineseFont'
        self.font_size = '11sp'
        self.color = get_color_from_hex(COLORS['text'])
        self.size_hint = (1, None)
        self.height = 110
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)  # 透明背景
        
        # 图标是否加载成功
        self._icon_loaded = False
        
        # 尝试加载图标
        if icon_source and os.path.exists(icon_source):
            try:
                # 用background_down和background_normal来显示图标
                self.background_normal = icon_source
                self.background_down = icon_source
                self._icon_loaded = True
                debug_print(f"图标加载成功(background): {icon_source}")
            except Exception as e:
                debug_print(f"图标加载失败: {icon_source}, 错误: {e}")
        
        # 如果没有图标，用emoji
        if not self._icon_loaded:
            emoji_map = {
                '登录账号': '👤', '一键日常': '📋', '批量养号': '👥',
                '植物升阶': '🌱', '装扮合成': '👗', '追击刷分': '🏆',
                '无尽商店': '🏪', '无尽刷币': '💰', '转基因': '🧬',
                '活动领取': '🎁', '存档管理': '💾', '停止脚本': '⏹️'
            }
            self.text = f"{emoji_map.get(text, '📱')}\n{text}"
        else:
            # 有图标时，文字在图标下方
            self.text = f"\n\n\n\n\n{text}"
        
        # 绘制圆形背景
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['icon_bg']))
            # 圆形背景，居中，大小70x70
            self.circle = Ellipse(
                pos=(self.center_x - 35, self.top - 80),
                size=(70, 70)
            )
        
        self.bind(pos=self._update_circle, size=self._update_circle)
        self.bind(on_press=self._on_press)
        self.bind(on_release=self._on_release)
    
    def _update_circle(self, instance, value):
        """更新圆形背景位置"""
        if hasattr(self, 'circle'):
            self.circle.pos = (self.center_x - 35, self.top - 80)
            self.circle.size = (70, 70)
    
    def _on_press(self, instance):
        """按下时改变颜色"""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['icon_bg_pressed']))
            self.circle = Ellipse(
                pos=(self.center_x - 35, self.top - 80),
                size=(70, 70)
            )
    
    def _on_release(self, instance):
        """释放时恢复颜色"""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['icon_bg']))
            self.circle = Ellipse(
                pos=(self.center_x - 35, self.top - 80),
                size=(70, 70)
            )


class LogOutput(ScrollView):
    """日志输出区域"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = 1
        self.log_label = Label(
            text='',
            font_name='ChineseFont',
            font_size='10sp',
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            size_hint_x=1,
            height=200,
            halign='left',
            valign='top',
            markup=True
        )
        self.log_label.bind(texture_size=self._update_height)
        self.bind(width=self._update_width)
        self.add_widget(self.log_label)
    
    def _update_width(self, instance, value):
        self.log_label.text_size = (value, None)
    
    def _update_height(self, instance, value):
        instance.height = value[1] + 20
    
    def append_log(self, text, color=None):
        if color:
            self.log_label.text += f'[color={color}]{text}[/color]\n'
        else:
            self.log_label.text += f'{text}\n'
        self.scroll_y = 0
    
    def clear(self):
        self.log_label.text = ''


class MainScreen(BoxLayout):
    """主界面 - 大学狗工具风格 V7"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10
        
        # 资源管理器
        self.script_interface = None
        if SCRIPT_AVAILABLE:
            self.script_interface = ScriptInterface(log_callback=self._on_script_log)
        
        # 创建界面
        self._create_header()
        self._create_icon_area()
        self._create_log_area()
        self._create_input_area()
        
        # 输出调试日志
        for log in debug_logs:
            self.log_output.append_log(log, '#888888')
    
    def _create_header(self):
        """创建顶部标题区域"""
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=75, spacing=5)
        
        # 标题行
        title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=32)
        
        title = Label(
            text='PVZ2 工具',
            font_name='ChineseFont',
            font_size='22sp',
            color=get_color_from_hex(COLORS['text']),
            size_hint_x=0.6,
            halign='left',
            bold=True
        )
        title_row.add_widget(title)
        
        self.status_label = Label(
            text='在线加载中...',
            font_name='ChineseFont',
            font_size='13sp',
            color=get_color_from_hex(COLORS['text_dim']),
            size_hint_x=0.4,
            halign='right'
        )
        title_row.add_widget(self.status_label)
        
        header.add_widget(title_row)
        
        # 用户名行
        user_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=28, spacing=8)
        user_icon = Label(text='🍀', font_size='18sp', size_hint_x=None, width=28)
        user_row.add_widget(user_icon)
        
        user_label = Label(
            text='幸运儿',
            font_name='ChineseFont',
            font_size='16sp',
            color=get_color_from_hex(COLORS['green']),
            halign='left'
        )
        user_row.add_widget(user_label)
        
        header.add_widget(user_row)
        
        self.add_widget(header)
    
    def _get_icon_path(self, icon_name):
        """获取图标路径"""
        if not icon_name:
            return None
        path = os.path.join(RESOURCE_PATH, f'icon_{icon_name}.png')
        if os.path.exists(path):
            return path
        debug_print(f"未找到图标: {icon_name}, 路径: {path}")
        return None
    
    def _create_icon_area(self):
        """创建功能图标区域"""
        # 图标区域标题
        title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        title = Label(
            text='功能菜单',
            font_name='ChineseFont',
            font_size='14sp',
            color=get_color_from_hex(COLORS['accent']),
            halign='left'
        )
        title_row.add_widget(title)
        self.add_widget(title_row)
        
        # 图标网格
        icon_scroll = ScrollView(size_hint_y=None, height=250, do_scroll_x=False)
        icon_grid = GridLayout(
            cols=3,
            spacing=10,
            padding=[5, 5, 5, 5],
            size_hint_y=None
        )
        icon_grid.bind(minimum_height=icon_grid.setter('height'))
        
        # 菜单配置
        menu_items = [
            ('登录账号', ['32'], 'diamond'),
            ('一键日常', ['30'], 'coin'),
            ('批量养号', ['31'], None),
            ('植物升阶', ['17', '2'], 'book'),
            ('装扮合成', ['17', '3'], 'costume'),
            ('追击刷分', ['5', '1'], 'pursuit'),
            ('无尽商店', ['6', '5'], 'endless'),
            ('无尽刷币', ['6', '2'], 'coin'),
            ('转基因', ['17', '1'], 'gene'),
            ('活动领取', ['1'], 'ticket'),
            ('存档管理', ['18'], None),
            ('停止脚本', ['__stop__'], None),
        ]
        
        for name, menu_path, icon_name in menu_items:
            icon_path = self._get_icon_path(icon_name)
            btn = IconButton(
                text=name,
                icon_source=icon_path,
                on_press=lambda x, mp=menu_path: self._on_menu_click(mp)
            )
            icon_grid.add_widget(btn)
        
        icon_scroll.add_widget(icon_grid)
        self.add_widget(icon_scroll)
    
    def _create_log_area(self):
        """创建日志输出区域"""
        # 日志标题
        log_title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        log_title = Label(
            text='运行日志',
            font_name='ChineseFont',
            font_size='14sp',
            color=get_color_from_hex(COLORS['accent']),
            halign='left'
        )
        log_title_row.add_widget(log_title)
        
        clear_btn = Button(
            text='清空',
            font_name='ChineseFont',
            font_size='12sp',
            size_hint=(None, None),
            size=(45, 22),
            background_normal='',
            background_color=get_color_from_hex('#fce7f3'),
            color=get_color_from_hex(COLORS['text']),
            on_press=lambda x: self.log_output.clear()
        )
        log_title_row.add_widget(clear_btn)
        self.add_widget(log_title_row)
        
        # 日志卡片
        log_card = BoxLayout(size_hint_y=1, padding=8)
        with log_card.canvas.before:
            Color(*get_color_from_hex(COLORS['card']))
            self.log_rect = RoundedRectangle(pos=log_card.pos, size=log_card.size, radius=[8])
        log_card.bind(pos=self._update_log_rect, size=self._update_log_rect)
        
        self.log_output = LogOutput()
        log_card.add_widget(self.log_output)
        self.add_widget(log_card)
    
    def _create_input_area(self):
        """创建输入区域"""
        input_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=8)
        self.input_field = TextInput(
            font_name='ChineseFont',
            font_size='12sp',
            background_color=get_color_from_hex(COLORS['card']),
            foreground_color=get_color_from_hex(COLORS['text']),
            cursor_color=get_color_from_hex(COLORS['accent']),
            multiline=False,
            hint_text='输入命令...'
        )
        input_row.add_widget(self.input_field)
        
        send_btn = Button(
            text='发送',
            font_name='ChineseFont',
            font_size='13sp',
            size_hint=(None, None),
            size=(55, 36),
            background_normal='',
            background_color=get_color_from_hex(COLORS['accent']),
            color=get_color_from_hex(COLORS['text_light']),
            on_press=self._on_send
        )
        input_row.add_widget(send_btn)
        self.add_widget(input_row)
    
    def _update_log_rect(self, instance, value):
        self.log_rect.pos = instance.pos
        self.log_rect.size = instance.size
    
    def _on_menu_click(self, menu_path):
        """菜单点击事件"""
        if menu_path == ['__stop__']:
            self._stop_script()
            return
        
        self.log_output.append_log(f'执行功能: {menu_path}', COLORS['accent'])
        
        # 在新线程中执行
        threading.Thread(target=self._run_script_function, args=(menu_path,), daemon=True).start()
    
    def _run_script_function(self, menu_path):
        """运行脚本功能"""
        try:
            if not self.script_interface:
                self.log_output.append_log('脚本接口不可用', COLORS['red'])
                return
            
            # 如果脚本未运行，先启动
            if not self.script_interface.is_running:
                self.log_output.append_log('启动脚本进程...', COLORS['blue'])
                self.script_interface.start()
                time.sleep(3)
            
            # 运行功能
            self.script_interface.run_function(menu_path)
            
        except Exception as e:
            self.log_output.append_log(f'执行出错: {e}', COLORS['red'])
    
    def _stop_script(self):
        """停止脚本"""
        if self.script_interface and self.script_interface.is_running:
            self.script_interface.stop()
            self.log_output.append_log('脚本已停止', COLORS['orange'])
        else:
            self.log_output.append_log('脚本未运行', COLORS['text_dim'])
    
    def _on_script_log(self, text, color=None):
        """脚本日志回调"""
        self.log_output.append_log(text, color)
    
    def _on_send(self, instance):
        """发送按钮"""
        command = self.input_field.text.strip()
        if command:
            self.log_output.append_log(f'> {command}', COLORS['blue'])
            self.input_field.text = ''
            
            # 发送到脚本
            if self.script_interface and self.script_interface.is_running:
                self.script_interface.send_input(command)
            else:
                self.log_output.append_log('脚本未运行，请先点击功能按钮启动', COLORS['text_dim'])


class PVZ2App(App):
    """PVZ2应用主类"""
    
    def build(self):
        Window.clearcolor = get_color_from_hex(COLORS['bg'])
        return MainScreen()
    
    def on_stop(self):
        """应用退出时停止脚本"""
        if hasattr(self, 'root') and self.root and self.root.script_interface:
            self.root.script_interface.stop()


if __name__ == '__main__':
    PVZ2App().run()
