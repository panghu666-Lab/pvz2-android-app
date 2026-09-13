# -*- coding: utf-8 -*-
"""
PVZ2脚本工具 - Android APP版本
基于Kivy框架，集成植物大战僵尸2脚本功能
V8 - 稳定版，确保能正常打开
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

# 颜色定义
COLORS = {
    'bg': '#fdf2f8',
    'card': '#ffffff',
    'btn_bg': '#e9d5ff',
    'btn_pressed': '#c4b5fd',
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
except:
    SCRIPT_AVAILABLE = False


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
    """主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10
        
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
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=80, spacing=5)
        
        # 标题行
        title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=35)
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
            font_size='14sp',
            color=get_color_from_hex(COLORS['text_dim']),
            size_hint_x=0.4,
            halign='right'
        )
        title_row.add_widget(self.status_label)
        header.add_widget(title_row)
        
        # 用户名行
        user_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=8)
        user_icon = Label(text='🍀', font_size='20sp', size_hint_x=None, width=30)
        user_row.add_widget(user_icon)
        user_label = Label(
            text='幸运儿',
            font_name='ChineseFont',
            font_size='18sp',
            color=get_color_from_hex(COLORS['green']),
            halign='left'
        )
        user_row.add_widget(user_label)
        header.add_widget(user_row)
        
        self.add_widget(header)
    
    def _create_button_area(self):
        """创建功能按钮区域"""
        # 标题
        title = Label(
            text='功能菜单',
            font_name='ChineseFont',
            font_size='15sp',
            color=get_color_from_hex(COLORS['accent']),
            size_hint_y=None,
            height=25,
            halign='left'
        )
        self.add_widget(title)
        
        # 按钮网格
        btn_scroll = ScrollView(size_hint_y=None, height=280, do_scroll_x=False)
        btn_grid = GridLayout(
            cols=3,
            spacing=10,
            padding=[5, 5, 5, 5],
            size_hint_y=None
        )
        btn_grid.bind(minimum_height=btn_grid.setter('height'))
        
        # 菜单配置：(名称, 菜单路径, emoji)
        menu_items = [
            ('登录账号', ['32'], '👤'),
            ('一键日常', ['30'], '📋'),
            ('批量养号', ['31'], '👥'),
            ('植物升阶', ['17', '2'], '🌱'),
            ('装扮合成', ['17', '3'], '👗'),
            ('追击刷分', ['5', '1'], '🏆'),
            ('无尽商店', ['6', '5'], '🏪'),
            ('无尽刷币', ['6', '2'], '💰'),
            ('转基因', ['17', '1'], '🧬'),
            ('活动领取', ['1'], '🎁'),
            ('存档管理', ['18'], '💾'),
            ('停止脚本', ['__stop__'], '⏹️'),
        ]
        
        for name, menu_path, emoji in menu_items:
            btn = Button(
                text=f'{emoji}\n{name}',
                font_name='ChineseFont',
                font_size='13sp',
                color=get_color_from_hex(COLORS['text']),
                size_hint=(1, None),
                height=80,
                background_normal='',
                background_color=get_color_from_hex(COLORS['btn_bg']),
                on_press=lambda x, mp=menu_path: self._on_menu_click(mp)
            )
            btn_grid.add_widget(btn)
        
        btn_scroll.add_widget(btn_grid)
        self.add_widget(btn_scroll)
    
    def _create_log_area(self):
        """创建日志输出区域"""
        # 标题行
        log_title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=28)
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
            size=(50, 25),
            background_normal='',
            background_color=get_color_from_hex('#fce7f3'),
            color=get_color_from_hex(COLORS['text']),
            on_press=lambda x: self.log_output.clear()
        )
        log_title_row.add_widget(clear_btn)
        self.add_widget(log_title_row)
        
        # 日志区域
        self.log_output = LogOutput()
        self.add_widget(self.log_output)
    
    def _create_input_area(self):
        """创建输入区域"""
        input_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=8)
        self.input_field = TextInput(
            font_name='ChineseFont',
            font_size='13sp',
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
            font_size='14sp',
            size_hint=(None, None),
            size=(60, 40),
            background_normal='',
            background_color=get_color_from_hex(COLORS['accent']),
            color=get_color_from_hex(COLORS['text_light']),
            on_press=self._on_send
        )
        input_row.add_widget(send_btn)
        self.add_widget(input_row)
    
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
