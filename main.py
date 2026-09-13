# -*- coding: utf-8 -*-
"""
PVZ2脚本工具 - Android APP版本
基于Kivy框架，集成植物大战僵尸2脚本功能
V9 - 全面优化版，稳定+美观
"""

import os
import sys
import time
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex

# 注册中文字体
def get_resource_path():
    """获取资源路径"""
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

try:
    if os.path.exists(FONT_PATH):
        LabelBase.register(name='ChineseFont', fn_regular=FONT_PATH)
    else:
        LabelBase.register(name='ChineseFont', fn_regular='/system/fonts/DroidSansFallback.ttf')
except:
    pass

# 颜色定义 - 大学狗工具风格
COLORS = {
    'bg': '#fdf2f8',           # 浅粉色背景
    'card': '#ffffff',          # 白色卡片
    'btn_bg': '#e9d5ff',       # 淡紫色按钮背景
    'btn_pressed': '#c4b5fd',  # 按下时的紫色
    'accent': '#7c3aed',       # 紫色强调色
    'green': '#16a34a',        # 绿色
    'text': '#1f2937',         # 深色文字
    'text_dim': '#6b7280',     # 灰色文字
    'text_light': '#ffffff',   # 白色文字
    'log_bg': '#fafafa',       # 日志背景
}

# 导入脚本接口
try:
    from script_interface import ScriptInterface
    SCRIPT_AVAILABLE = True
except:
    SCRIPT_AVAILABLE = False


def get_icon_path(icon_name):
    """获取图标路径"""
    if not icon_name:
        return None
    path = os.path.join(RESOURCE_PATH, f'icon_{icon_name}.png')
    if os.path.exists(path):
        return path
    return None


class LogOutput(ScrollView):
    """日志输出区域"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = 1
        self.log_label = Label(
            text='',
            font_name='ChineseFont',
            font_size='11sp',
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
        self.log_label.text_size = (value - 10, None)
    
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
    """主界面 - V9全面优化版"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [15, 10, 15, 10]
        self.spacing = 8
        
        self.script_interface = None
        if SCRIPT_AVAILABLE:
            self.script_interface = ScriptInterface(log_callback=self._on_script_log)
        
        # 创建界面
        self._create_header()
        self._create_button_area()
        self._create_log_area()
        self._create_input_area()
    
    def _create_header(self):
        """创建顶部标题区域"""
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=75, spacing=3)
        
        # 标题行
        title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=32)
        title = Label(
            text='PVZ2 工具',
            font_name='ChineseFont',
            font_size='24sp',
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
        user_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=28, spacing=6)
        user_icon = Label(text='🍀', font_size='18sp', size_hint_x=None, width=28)
        user_row.add_widget(user_icon)
        user_label = Label(
            text='幸运儿',
            font_name='ChineseFont',
            font_size='17sp',
            color=get_color_from_hex(COLORS['green']),
            halign='left'
        )
        user_row.add_widget(user_label)
        header.add_widget(user_row)
        
        self.add_widget(header)
    
    def _create_button_area(self):
        """创建功能按钮区域 - 优化版"""
        # 标题
        title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        title = Label(
            text='✨ 功能菜单',
            font_name='ChineseFont',
            font_size='15sp',
            color=get_color_from_hex(COLORS['accent']),
            halign='left',
            bold=True
        )
        title_row.add_widget(title)
        self.add_widget(title_row)
        
        # 按钮网格 - 调整高度确保所有按钮都能显示
        btn_scroll = ScrollView(size_hint_y=None, height=320, do_scroll_x=False)
        btn_grid = GridLayout(
            cols=3,
            spacing=10,
            padding=[5, 5, 5, 5],
            size_hint_y=None
        )
        btn_grid.bind(minimum_height=btn_grid.setter('height'))
        
        # 菜单配置：(名称, 菜单路径, 图标名称)
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
        
        # emoji备用图标
        emoji_map = {
            '登录账号': '👤', '一键日常': '📋', '批量养号': '👥',
            '植物升阶': '🌱', '装扮合成': '👗', '追击刷分': '🏆',
            '无尽商店': '🏪', '无尽刷币': '💰', '转基因': '🧬',
            '活动领取': '🎁', '存档管理': '💾', '停止脚本': '⏹️'
        }
        
        for name, menu_path, icon_name in menu_items:
            icon_path = get_icon_path(icon_name)
            
            # 创建按钮
            btn = Button(
                text=name,
                font_name='ChineseFont',
                font_size='12sp',
                color=get_color_from_hex(COLORS['text']),
                size_hint=(1, None),
                height=90,
                background_normal='',
                background_color=get_color_from_hex(COLORS['btn_bg']),
                on_press=lambda x, mp=menu_path: self._on_menu_click(mp)
            )
            
            # 如果有图标，用background_normal显示图标（图标在上，文字在下的效果用换行实现）
            if icon_path:
                try:
                    # 用一个带图标的布局：图标作为背景，文字在底部
                    btn.background_normal = icon_path
                    btn.background_down = icon_path
                    # 文字放在底部，用padding实现
                    btn.text_size = (None, None)
                    btn.valign = 'bottom'
                    btn.padding = [0, 0, 0, 5]
                    btn.color = get_color_from_hex(COLORS['text'])
                    btn.font_size = '11sp'
                except:
                    # 如果图标设置失败，用emoji
                    btn.text = f'{emoji_map.get(name, "📱")}\n{name}'
            else:
                # 没有图标，用emoji
                btn.text = f'{emoji_map.get(name, "📱")}\n{name}'
                btn.font_size = '12sp'
            
            btn_grid.add_widget(btn)
        
        btn_scroll.add_widget(btn_grid)
        self.add_widget(btn_scroll)
    
    def _create_log_area(self):
        """创建日志输出区域 - 优化版"""
        # 标题行
        log_title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=28)
        log_title = Label(
            text='📋 运行日志',
            font_name='ChineseFont',
            font_size='14sp',
            color=get_color_from_hex(COLORS['accent']),
            halign='left',
            bold=True
        )
        log_title_row.add_widget(log_title)
        
        clear_btn = Button(
            text='清空',
            font_name='ChineseFont',
            font_size='12sp',
            size_hint=(None, None),
            size=(50, 25),
            background_normal='',
            background_color=get_color_from_hex('#fce7f3'),
            color=get_color_from_hex(COLORS['text']),
            on_press=lambda x: self.log_output.clear()
        )
        log_title_row.add_widget(clear_btn)
        self.add_widget(log_title_row)
        
        # 日志卡片背景
        log_card = BoxLayout(size_hint_y=1, padding=8)
        with log_card.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*get_color_from_hex(COLORS['card']))
            self.log_rect = RoundedRectangle(pos=log_card.pos, size=log_card.size, radius=[8])
        log_card.bind(pos=self._update_log_rect, size=self._update_log_rect)
        
        self.log_output = LogOutput()
        log_card.add_widget(self.log_output)
        self.add_widget(log_card)
    
    def _create_input_area(self):
        """创建输入区域 - 优化版"""
        input_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=8)
        self.input_field = TextInput(
            font_name='ChineseFont',
            font_size='13sp',
            background_color=get_color_from_hex(COLORS['card']),
            foreground_color=get_color_from_hex(COLORS['text']),
            cursor_color=get_color_from_hex(COLORS['accent']),
            multiline=False,
            hint_text='输入命令...',
            padding=[10, 10, 10, 10]
        )
        input_row.add_widget(self.input_field)
        
        send_btn = Button(
            text='发送',
            font_name='ChineseFont',
            font_size='14sp',
            size_hint=(None, None),
            size=(65, 40),
            background_normal='',
            background_color=get_color_from_hex(COLORS['accent']),
            color=get_color_from_hex(COLORS['text_light']),
            on_press=self._on_send
        )
        input_row.add_widget(send_btn)
        self.add_widget(input_row)
    
    def _update_log_rect(self, instance, value):
        """更新日志卡片背景位置"""
        if hasattr(self, 'log_rect'):
            self.log_rect.pos = instance.pos
            self.log_rect.size = instance.size
    
    def _on_menu_click(self, menu_path):
        """菜单点击事件"""
        if menu_path == ['__stop__']:
            self._stop_script()
            return
        
        self.log_output.append_log(f'执行功能: {menu_path}', COLORS['accent'])
        
        threading.Thread(target=self._run_script_function, args=(menu_path,), daemon=True).start()
    
    def _run_script_function(self, menu_path):
        """运行脚本功能"""
        try:
            if not self.script_interface:
                self.log_output.append_log('脚本接口不可用', COLORS['red'])
                return
            
            if not self.script_interface.is_running:
                self.log_output.append_log('启动脚本进程...', COLORS['blue'])
                self.script_interface.start()
                time.sleep(3)
            
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
