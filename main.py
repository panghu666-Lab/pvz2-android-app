# -*- coding: utf-8 -*-
"""
PVZ2脚本工具 - Android APP版本
基于Kivy框架，集成植物大战僵尸2脚本功能
大学狗工具风格UI V3
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
from kivy.uix.floatlayout import FloatLayout
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
    # 尝试多种可能的路径
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources'),
        '/data/data/org.pvz2.pvz2tool/files/app/resources',
        os.path.join(os.getcwd(), 'resources'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            debug_print(f"找到资源路径: {path}")
            return path
    
    debug_print(f"未找到资源路径，使用默认: {possible_paths[0]}")
    return possible_paths[0]

RESOURCE_PATH = get_resource_path()
FONT_PATH = os.path.join(RESOURCE_PATH, 'zt3.ttf')
ITEM_DICT_PATH = os.path.join(RESOURCE_PATH, 'item_dict.json')

debug_print(f"RESOURCE_PATH: {RESOURCE_PATH}")
debug_print(f"FONT_PATH: {FONT_PATH}, exists: {os.path.exists(FONT_PATH)}")

# 列出resources目录下的图标文件
try:
    all_files = os.listdir(RESOURCE_PATH)
    icon_files = [f for f in all_files if f.startswith('icon_') and f.endswith('.png')]
    debug_print(f"resources目录图标文件: {icon_files}")
    debug_print(f"resources目录所有文件: {all_files}")
except Exception as e:
    debug_print(f"列出resources目录失败: {e}")

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
    'bg_light': '#fce7f3',
    'card': '#ffffff',
    'icon_bg': '#e9d5ff',
    'icon_bg_pressed': '#c4b5fd',
    'accent': '#7c3aed',
    'accent_light': '#a78bfa',
    'green': '#16a34a',
    'green_dark': '#15803d',
    'text': '#1f2937',
    'text_dim': '#6b7280',
    'text_light': '#ffffff',
    'border': '#d8b4fe',
    'blue': '#2563eb',
    'orange': '#ea580c',
    'red': '#dc2626',
    'pink': '#db2777',
    'cyan': '#0891b2',
}

# 导入脚本接口
try:
    from script_interface import ScriptInterface
    SCRIPT_AVAILABLE = True
except Exception as e:
    debug_print(f"导入脚本接口失败: {e}")
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
            debug_print(f"物品字典加载失败: {e}")
    
    def get_plant_name(self, plant_id):
        if '植物字典' in self.item_dict:
            return self.item_dict['植物字典'].get(str(plant_id), f'未知植物({plant_id})')
        return str(plant_id)


class IconButton(ButtonBehavior, BoxLayout):
    """圆形图标按钮 - 大学狗工具风格"""
    
    def __init__(self, text='', icon_source=None, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (1, None)
        self.height = 110
        self.spacing = 3
        self.padding = [5, 5, 5, 5]
        
        self._bg_color = bg_color if bg_color else COLORS['icon_bg']
        self._original_color = self._bg_color
        
        # 圆形图标背景 - 使用FloatLayout支持pos_hint居中
        self.icon_container = FloatLayout(
            size_hint=(None, None),
            size=(70, 70),
            pos_hint={'center_x': 0.5}
        )
        with self.icon_container.canvas.before:
            Color(*get_color_from_hex(self._bg_color))
            self.ellipse = Ellipse(pos=self.icon_container.pos, size=self.icon_container.size)
        self.icon_container.bind(pos=self._update_ellipse, size=self._update_ellipse)
        
        # 图标图片
        icon_loaded = False
        if icon_source and os.path.exists(icon_source):
            try:
                self.icon = Image(
                    source=icon_source,
                    size_hint=(None, None),
                    size=(50, 50),
                    pos_hint={'center_x': 0.5, 'center_y': 0.5},
                    allow_stretch=True
                )
                icon_loaded = True
                debug_print(f"图标加载成功: {icon_source}")
            except Exception as e:
                debug_print(f"图标加载失败: {icon_source}, 错误: {e}")
        
        if not icon_loaded:
            # 如果没有图标，显示emoji
            emoji_map = {
                '登录账号': '👤', '一键日常': '📋', '批量养号': '👥',
                '植物升阶': '🌱', '装扮合成': '👗', '追击刷分': '🏆',
                '无尽商店': '🏪', '无尽刷币': '💰', '转基因': '🧬',
                '活动领取': '🎁', '存档管理': '💾', '停止脚本': '⏹️'
            }
            self.icon = Label(
                text=emoji_map.get(text, '📱'),
                font_size='32sp',
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
        self.icon_container.add_widget(self.icon)
        
        self.add_widget(self.icon_container)
        
        # 文字标签
        self.label = Label(
            text=text,
            font_name='ChineseFont',
            font_size='11sp',
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=18,
            halign='center',
            text_size=(95, None)
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
            Color(*get_color_from_hex(COLORS['icon_bg_pressed']))
            self.ellipse = Ellipse(pos=self.icon_container.pos, size=self.icon_container.size)
    
    def _on_release(self, instance):
        self.icon_container.canvas.before.clear()
        with self.icon_container.canvas.before:
            Color(*get_color_from_hex(self._original_color))
            self.ellipse = Ellipse(pos=self.icon_container.pos, size=self.icon_container.size)


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
    """主界面 - 大学狗工具风格"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 12
        self.spacing = 8
        
        # 资源管理器
        self.resource_manager = ResourceManager()
        
        # 脚本接口
        self.script_interface = None
        if SCRIPT_AVAILABLE:
            self.script_interface = ScriptInterface(log_callback=self._on_script_log)
        
        # 创建界面
        self._create_header()
        self._create_main_content()
        
        # 输出调试日志
        for log in debug_logs:
            self.log_output.append_log(log, '#888888')
    
    def _create_header(self):
        """创建顶部标题区域"""
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=80, spacing=5)
        
        # 标题行
        title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=35)
        
        title = Label(
            text='PVZ2 工具',
            font_name='ChineseFont',
            font_size='22sp',
            color=get_color_from_hex(COLORS['text']),
            size_hint_x=0.5,
            halign='left',
            bold=True
        )
        title_row.add_widget(title)
        
        self.status_label = Label(
            text='在线加载中...',
            font_name='ChineseFont',
            font_size='13sp',
            color=get_color_from_hex(COLORS['text_dim']),
            size_hint_x=0.5,
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
        """获取图标路径（使用英文文件名避免编码问题）"""
        if not icon_name:
            return None
        # 尝试多种路径（图标放在resources根目录，避免被清理步骤删除）
        paths = [
            os.path.join(RESOURCE_PATH, f'icon_{icon_name}.png'),
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        debug_print(f"未找到图标: {icon_name}, 尝试的路径: {paths}")
        return None
    
    def _create_main_content(self):
        """创建主内容区域 - 左右分栏"""
        main_content = BoxLayout(orientation='horizontal', size_hint_y=1, spacing=10)
        
        # 左侧：日志区域
        left_panel = BoxLayout(orientation='vertical', size_hint_x=0.42, spacing=8)
        
        # 日志标题
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
            size=(45, 25),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_light']),
            color=get_color_from_hex(COLORS['text']),
            on_press=lambda x: self.log_output.clear()
        )
        log_title_row.add_widget(clear_btn)
        left_panel.add_widget(log_title_row)
        
        # 日志输出卡片
        log_card = BoxLayout(size_hint_y=1, padding=8)
        with log_card.canvas.before:
            Color(*get_color_from_hex(COLORS['card']))
            self.log_rect = RoundedRectangle(pos=log_card.pos, size=log_card.size, radius=[8])
        log_card.bind(pos=self._update_log_rect, size=self._update_log_rect)
        
        self.log_output = LogOutput()
        log_card.add_widget(self.log_output)
        left_panel.add_widget(log_card)
        
        # 输入区域
        input_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=6)
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
        left_panel.add_widget(input_row)
        
        main_content.add_widget(left_panel)
        
        # 右侧：功能图标区域
        right_panel = BoxLayout(orientation='vertical', size_hint_x=0.58, spacing=8)
        
        # 功能图标滚动区域
        icon_scroll = ScrollView(size_hint_y=1, do_scroll_x=False)
        icon_grid = GridLayout(
            cols=3,
            spacing=8,
            padding=[5, 5, 5, 5],
            size_hint_y=None
        )
        icon_grid.bind(minimum_height=icon_grid.setter('height'))
        
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
        
        for name, menu_path, icon_name in menu_items:
            icon_path = self._get_icon_path(icon_name)
            btn = IconButton(
                text=name,
                icon_source=icon_path,
                on_press=lambda x, mp=menu_path: self._on_menu_click(mp)
            )
            icon_grid.add_widget(btn)
        
        icon_scroll.add_widget(icon_grid)
        right_panel.add_widget(icon_scroll)
        
        main_content.add_widget(right_panel)
        
        self.add_widget(main_content)
    
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
