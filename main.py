# -*- coding: utf-8 -*-
"""
PVZ2脚本工具 - Android APP版本
基于Kivy框架，集成植物大战僵尸2脚本功能
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
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex

# 设置窗口大小（手机竖屏）
Window.size = (400, 700)

# 注册中文字体
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'zt3.ttf')
if os.path.exists(FONT_PATH):
    LabelBase.register(name='ChineseFont', fn_regular=FONT_PATH)
else:
    try:
        LabelBase.register(name='ChineseFont', fn_regular='/system/fonts/DroidSansFallback.ttf')
    except:
        LabelBase.register(name='ChineseFont', fn_regular=None)

# 资源路径
RESOURCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
ITEM_DICT_PATH = os.path.join(RESOURCE_PATH, 'item_dict.json')

# 颜色定义
COLORS = {
    'bg': '#1a1a2e',
    'bg_light': '#16213e',
    'card': '#0f3460',
    'accent': '#e94560',
    'text': '#ffffff',
    'text_dim': '#a0a0a0',
    'green': '#4caf50',
    'blue': '#2196f3',
    'orange': '#ff9800',
    'purple': '#9c27b0',
    'red': '#f44336',
}

# 导入脚本接口
try:
    from script_interface import ScriptInterface
    SCRIPT_AVAILABLE = True
except:
    SCRIPT_AVAILABLE = False


class ResourceManager:
    """资源管理器"""
    
    def __init__(self):
        self.item_dict = {}
        self.load_item_dict()
    
    def load_item_dict(self):
        try:
            if os.path.exists(ITEM_DICT_PATH):
                with open(ITEM_DICT_PATH, 'r', encoding='utf-8') as f:
                    self.item_dict = json.load(f)
        except Exception as e:
            print(f"物品字典加载失败: {e}")
    
    def get_plant_name(self, plant_id):
        if '植物字典' in self.item_dict:
            return self.item_dict['植物字典'].get(str(plant_id), f'未知植物({plant_id})')
        return str(plant_id)


class ColoredButton(Button):
    """带颜色的按钮"""
    
    def __init__(self, **kwargs):
        bg_color = kwargs.pop('bg_color', COLORS['card'])
        text_color = kwargs.pop('text_color', COLORS['text'])
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = get_color_from_hex(bg_color)
        self.color = get_color_from_hex(text_color)
        self.font_name = 'ChineseFont'
        self.size_hint_y = None
        self.height = 45
        self.bind(on_press=self._on_press)
        self.bind(on_release=self._on_release)
    
    def _on_press(self, instance):
        self.background_color = get_color_from_hex(COLORS['accent'])
    
    def _on_release(self, instance):
        self.background_color = get_color_from_hex(COLORS['card'])


class MenuButton(Button):
    """菜单按钮"""
    
    def __init__(self, **kwargs):
        bg_color = kwargs.pop('bg_color', COLORS['card'])
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = get_color_from_hex(bg_color)
        self.color = get_color_from_hex(COLORS['text'])
        self.font_name = 'ChineseFont'
        self.font_size = '13sp'
        self.size_hint = (None, None)
        self.size = (110, 80)
        self.bind(on_press=self._on_press)
        self.bind(on_release=self._on_release)
    
    def _on_press(self, instance):
        self.background_color = get_color_from_hex(COLORS['accent'])
    
    def _on_release(self, instance):
        self.background_color = get_color_from_hex(COLORS['card'])


class LogOutput(ScrollView):
    """日志输出区域"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = 0.45
        self.log_label = Label(
            text='',
            font_name='ChineseFont',
            font_size='11sp',
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=200,
            text_size=(self.width, None),
            halign='left',
            valign='top',
            markup=True
        )
        self.log_label.bind(texture_size=self._update_height)
        self.add_widget(self.log_label)
    
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
        self.padding = 8
        self.spacing = 8
        
        # 资源管理器
        self.resource_manager = ResourceManager()
        
        # 脚本接口
        self.script_interface = None
        if SCRIPT_AVAILABLE:
            self.script_interface = ScriptInterface(log_callback=self._on_script_log)
        
        # 创建界面
        self._create_header()
        self._create_menu()
        self._create_log_area()
    
    def _create_header(self):
        header = BoxLayout(orientation='horizontal', size_hint_y=0.07, spacing=8)
        
        logo_path = os.path.join(RESOURCE_PATH, 'logo.png')
        if os.path.exists(logo_path):
            logo = Image(source=logo_path, size_hint_x=0.12, allow_stretch=True)
            header.add_widget(logo)
        
        title = Label(
            text='PVZ2脚本工具',
            font_name='ChineseFont',
            font_size='18sp',
            color=get_color_from_hex(COLORS['accent']),
            size_hint_x=0.55,
            halign='left'
        )
        header.add_widget(title)
        
        self.status_label = Label(
            text='未登录',
            font_name='ChineseFont',
            font_size='11sp',
            color=get_color_from_hex(COLORS['text_dim']),
            size_hint_x=0.33,
            halign='right'
        )
        header.add_widget(self.status_label)
        
        self.add_widget(header)
    
    def _create_menu(self):
        menu_scroll = ScrollView(size_hint_y=0.48, do_scroll_x=False)
        
        menu_grid = GridLayout(cols=3, spacing=8, padding=8, size_hint_y=None)
        menu_grid.bind(minimum_height=menu_grid.setter('height'))
        
        # 菜单配置：(名称, 菜单路径, 颜色)
        menu_items = [
            ('登录账号', ['32'], COLORS['blue']),
            ('一键日常', ['30'], COLORS['green']),
            ('批量养号', ['31'], COLORS['blue']),
            ('植物升阶', ['17', '2'], COLORS['green']),
            ('装扮合成', ['17', '3'], COLORS['purple']),
            ('追击刷分', ['5', '1'], COLORS['orange']),
            ('无尽商店', ['6', '5'], COLORS['red']),
            ('无尽刷币', ['6', '2'], COLORS['red']),
            ('转基因', ['17', '1'], COLORS['purple']),
            ('活动领取', ['1'], COLORS['green']),
            ('存档管理', ['18'], COLORS['blue']),
            ('停止脚本', ['__stop__'], COLORS['red']),
        ]
        
        for name, menu_path, color in menu_items:
            btn = MenuButton(
                text=name,
                bg_color=color,
                on_press=lambda x, mp=menu_path: self._on_menu_click(mp)
            )
            menu_grid.add_widget(btn)
        
        menu_scroll.add_widget(menu_grid)
        self.add_widget(menu_scroll)
    
    def _create_log_area(self):
        log_container = BoxLayout(orientation='vertical', size_hint_y=0.45, spacing=5)
        
        # 日志标题栏
        title_bar = BoxLayout(orientation='horizontal', size_hint_y=0.08)
        log_title = Label(
            text='运行日志',
            font_name='ChineseFont',
            font_size='13sp',
            color=get_color_from_hex(COLORS['accent']),
            halign='left'
        )
        title_bar.add_widget(log_title)
        
        clear_btn = ColoredButton(
            text='清空',
            bg_color=COLORS['card'],
            size_hint_x=0.2,
            height=30,
            on_press=lambda x: self.log_output.clear()
        )
        title_bar.add_widget(clear_btn)
        
        log_container.add_widget(title_bar)
        
        # 日志输出
        self.log_output = LogOutput()
        log_container.add_widget(self.log_output)
        
        # 输入区域
        input_container = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=5)
        
        self.input_field = TextInput(
            font_name='ChineseFont',
            font_size='12sp',
            background_color=get_color_from_hex(COLORS['bg_light']),
            foreground_color=get_color_from_hex(COLORS['text']),
            cursor_color=get_color_from_hex(COLORS['accent']),
            multiline=False,
            hint_text='输入命令...'
        )
        input_container.add_widget(self.input_field)
        
        send_btn = ColoredButton(
            text='发送',
            bg_color=COLORS['accent'],
            size_hint_x=0.2,
            on_press=self._on_send
        )
        input_container.add_widget(send_btn)
        
        log_container.add_widget(input_container)
        self.add_widget(log_container)
    
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
