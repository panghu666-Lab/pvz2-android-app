# -*- coding: utf-8 -*-
"""
PVZ2脚本工具 - Android APP版本
基于Kivy框架，集成植物大战僵尸2脚本功能
游戏风格UI
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
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.utils import get_color_from_hex

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
ICON_PATH = os.path.join(RESOURCE_PATH, 'icons')
ITEM_DICT_PATH = os.path.join(RESOURCE_PATH, 'item_dict.json')

# 颜色定义 - 游戏风格浅色主题
COLORS = {
    'bg': '#f5f0fa',
    'bg_light': '#ebe0f5',
    'card': '#ffffff',
    'accent': '#7c3aed',
    'accent_light': '#a78bfa',
    'text': '#1f2937',
    'text_dim': '#6b7280',
    'text_light': '#ffffff',
    'green': '#10b981',
    'blue': '#3b82f6',
    'orange': '#f59e0b',
    'purple': '#8b5cf6',
    'red': '#ef4444',
    'pink': '#ec4899',
    'cyan': '#06b6d4',
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


class IconButton(ButtonBehavior, BoxLayout):
    """圆形图标按钮"""
    
    def __init__(self, text='', icon_source=None, bg_color=COLORS['purple'], **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (90, 110)
        self.spacing = 4
        self.padding = [5, 5, 5, 5]
        
        self._bg_color = bg_color
        self._original_color = bg_color
        
        # 圆形图标背景
        self.icon_container = BoxLayout(
            size_hint=(None, None),
            size=(70, 70),
            pos_hint={'center_x': 0.5}
        )
        with self.icon_container.canvas.before:
            Color(*get_color_from_hex(bg_color))
            self.ellipse = Ellipse(pos=self.icon_container.pos, size=self.icon_container.size)
        self.icon_container.bind(pos=self._update_ellipse, size=self._update_ellipse)
        
        # 图标图片
        if icon_source and os.path.exists(icon_source):
            self.icon = Image(source=icon_source, size_hint=(None, None), size=(50, 50), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        else:
            self.icon = Label(text='🌱', font_size='30sp', pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.icon_container.add_widget(self.icon)
        
        self.add_widget(self.icon_container)
        
        # 文字标签
        self.label = Label(
            text=text,
            font_name='ChineseFont',
            font_size='11sp',
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=20,
            halign='center'
        )
        self.add_widget(self.label)
        
        self.bind(on_press=self._on_press)
        self.bind(on_release=self._on_release)
    
    def _update_ellipse(self, instance, value):
        self.ellipse.pos = instance.pos
        self.ellipse.size = instance.size
    
    def _on_press(self, instance):
        self.icon_container.canvas.before.clear()
        with self.icon_container.canvas.before:
            Color(*get_color_from_hex(COLORS['accent']))
            self.ellipse = Ellipse(pos=self.icon_container.pos, size=self.icon_container.size)
    
    def _on_release(self, instance):
        self.icon_container.canvas.before.clear()
        with self.icon_container.canvas.before:
            Color(*get_color_from_hex(self._original_color))
            self.ellipse = Ellipse(pos=self.icon_container.pos, size=self.icon_container.size)


class ColoredButton(Button):
    """带颜色的按钮"""
    
    def __init__(self, **kwargs):
        bg_color = kwargs.pop('bg_color', COLORS['accent'])
        text_color = kwargs.pop('text_color', COLORS['text_light'])
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = get_color_from_hex(bg_color)
        self.color = get_color_from_hex(text_color)
        self.font_name = 'ChineseFont'
        self.font_size = '14sp'
        self.size_hint_y = None
        self.height = 40
        self.bind(on_press=self._on_press)
        self.bind(on_release=self._on_release)
    
    def _on_press(self, instance):
        self.background_color = get_color_from_hex(COLORS['accent_light'])
    
    def _on_release(self, instance):
        self.background_color = get_color_from_hex(COLORS['accent'])


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
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=80, spacing=5)
        
        # 标题行
        title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        
        logo_path = os.path.join(RESOURCE_PATH, 'logo.png')
        if os.path.exists(logo_path):
            logo = Image(source=logo_path, size_hint_x=None, width=35, allow_stretch=True)
            title_row.add_widget(logo)
        
        title = Label(
            text='PVZ2 工具',
            font_name='ChineseFont',
            font_size='22sp',
            color=get_color_from_hex(COLORS['accent']),
            size_hint_x=0.6,
            halign='left',
            bold=True
        )
        title_row.add_widget(title)
        
        self.status_label = Label(
            text='在线加载中...',
            font_name='ChineseFont',
            font_size='12sp',
            color=get_color_from_hex(COLORS['text_dim']),
            size_hint_x=0.35,
            halign='right'
        )
        title_row.add_widget(self.status_label)
        
        header.add_widget(title_row)
        
        # 用户名行
        user_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=5)
        user_icon = Label(text='🍀', font_size='18sp', size_hint_x=None, width=30)
        user_row.add_widget(user_icon)
        
        user_label = Label(
            text='幸运儿',
            font_name='ChineseFont',
            font_size='16sp',
            color=get_color_from_hex(COLORS['blue']),
            halign='left'
        )
        user_row.add_widget(user_label)
        
        header.add_widget(user_row)
        
        self.add_widget(header)
    
    def _get_icon_path(self, icon_name):
        """获取图标路径"""
        path = os.path.join(ICON_PATH, f'{icon_name}.png')
        if os.path.exists(path):
            return path
        return None
    
    def _create_menu(self):
        menu_scroll = ScrollView(size_hint_y=None, height=320, do_scroll_x=False)
        
        menu_grid = GridLayout(
            cols=3,
            spacing=15,
            padding=10,
            size_hint_y=None
        )
        menu_grid.bind(minimum_height=menu_grid.setter('height'))
        
        # 菜单配置：(名称, 菜单路径, 颜色, 图标)
        menu_items = [
            ('登录账号', ['32'], COLORS['blue'], '钻石'),
            ('一键日常', ['30'], COLORS['green'], '金币'),
            ('批量养号', ['31'], COLORS['cyan'], None),
            ('植物升阶', ['17', '2'], COLORS['green'], '进阶书'),
            ('装扮合成', ['17', '3'], COLORS['pink'], '装扮券'),
            ('追击刷分', ['5', '1'], COLORS['orange'], '追击币'),
            ('无尽商店', ['6', '5'], COLORS['red'], '无尽币'),
            ('无尽刷币', ['6', '2'], COLORS['orange'], '金币'),
            ('转基因', ['17', '1'], COLORS['purple'], '基因原质'),
            ('活动领取', ['1'], COLORS['green'], '秘宝券'),
            ('存档管理', ['18'], COLORS['blue'], None),
            ('停止脚本', ['__stop__'], COLORS['red'], None),
        ]
        
        for name, menu_path, color, icon_name in menu_items:
            icon_path = self._get_icon_path(icon_name) if icon_name else None
            btn = IconButton(
                text=name,
                icon_source=icon_path,
                bg_color=color,
                on_press=lambda x, mp=menu_path: self._on_menu_click(mp)
            )
            menu_grid.add_widget(btn)
        
        menu_scroll.add_widget(menu_grid)
        self.add_widget(menu_scroll)
    
    def _create_log_area(self):
        log_container = BoxLayout(orientation='vertical', size_hint_y=1, spacing=8)
        
        # 日志标题栏
        title_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=35)
        log_title = Label(
            text='运行日志',
            font_name='ChineseFont',
            font_size='14sp',
            color=get_color_from_hex(COLORS['accent']),
            halign='left'
        )
        title_bar.add_widget(log_title)
        
        clear_btn = ColoredButton(
            text='清空',
            bg_color=COLORS['bg_light'],
            text_color=COLORS['text'],
            size_hint_x=None,
            width=60,
            height=30,
            on_press=lambda x: self.log_output.clear()
        )
        title_bar.add_widget(clear_btn)
        
        log_container.add_widget(title_bar)
        
        # 日志输出 - 白色卡片背景
        log_card = BoxLayout(
            size_hint_y=1,
            padding=10
        )
        with log_card.canvas.before:
            Color(*get_color_from_hex(COLORS['card']))
            self.log_rect = Rectangle(pos=log_card.pos, size=log_card.size)
        log_card.bind(pos=self._update_log_rect, size=self._update_log_rect)
        
        self.log_output = LogOutput()
        log_card.add_widget(self.log_output)
        log_container.add_widget(log_card)
        
        # 输入区域
        input_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=8)
        
        self.input_field = TextInput(
            font_name='ChineseFont',
            font_size='13sp',
            background_color=get_color_from_hex(COLORS['card']),
            foreground_color=get_color_from_hex(COLORS['text']),
            cursor_color=get_color_from_hex(COLORS['accent']),
            multiline=False,
            hint_text='输入命令...'
        )
        input_container.add_widget(self.input_field)
        
        send_btn = ColoredButton(
            text='发送',
            bg_color=COLORS['accent'],
            size_hint_x=None,
            width=70,
            height=40,
            on_press=self._on_send
        )
        input_container.add_widget(send_btn)
        
        log_container.add_widget(input_container)
        self.add_widget(log_container)
    
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
