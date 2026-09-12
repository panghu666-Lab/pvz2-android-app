# -*- coding: utf-8 -*-
"""
PVZ2脚本接口模块
通过子进程方式调用PVZ2脚本，捕获输出
"""

import os
import sys
import subprocess
import threading
import queue
import time

# 脚本路径
SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pvz2_script.py')


class ScriptInterface:
    """脚本接口类"""
    
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.process = None
        self.output_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.is_running = False
        self.output_thread = None
        self.input_thread = None
    
    def log(self, text, color=None):
        """记录日志"""
        if self.log_callback:
            self.log_callback(text, color)
        else:
            print(text)
    
    def start(self):
        """启动脚本进程"""
        if self.is_running:
            self.log("脚本已在运行中")
            return
        
        try:
            # 启动脚本进程，重定向输入输出
            self.process = subprocess.Popen(
                [sys.executable, SCRIPT_PATH],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )
            
            self.is_running = True
            
            # 启动输出读取线程
            self.output_thread = threading.Thread(target=self._read_output, daemon=True)
            self.output_thread.start()
            
            self.log("脚本进程已启动", "#4caf50")
            
        except Exception as e:
            self.log(f"启动脚本失败: {e}", "#f44336")
    
    def _read_output(self):
        """读取脚本输出"""
        try:
            while self.is_running and self.process:
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    if line:
                        self.output_queue.put(line)
                        self.log(line)
                else:
                    # 进程结束
                    break
        except Exception as e:
            self.log(f"读取输出出错: {e}", "#f44336")
        
        self.is_running = False
        self.log("脚本进程已结束", "#ff9800")
    
    def send_input(self, text):
        """向脚本发送输入"""
        if not self.is_running or not self.process:
            self.log("脚本未运行", "#f44336")
            return False
        
        try:
            self.process.stdin.write(text + '\n')
            self.process.stdin.flush()
            self.log(f"> {text}", "#2196f3")
            return True
        except Exception as e:
            self.log(f"发送输入失败: {e}", "#f44336")
            return False
    
    def stop(self):
        """停止脚本进程"""
        if self.process and self.is_running:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            
            self.is_running = False
            self.log("脚本进程已停止", "#ff9800")
    
    def wait_for_output(self, timeout=10, keywords=None):
        """等待特定输出"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                line = self.output_queue.get_nowait()
                if keywords:
                    for kw in keywords:
                        if kw in line:
                            return line
                else:
                    return line
            except queue.Empty:
                time.sleep(0.1)
        return None
    
    def run_function(self, menu_path, inputs=None):
        """
        运行脚本功能
        menu_path: 菜单路径，如 ['1', '1'] 表示先选1，再选1
        inputs: 额外的输入列表
        """
        if not self.is_running:
            self.start()
            time.sleep(2)  # 等待脚本启动
        
        # 清空输出队列
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except:
                break
        
        # 发送菜单选择
        for choice in menu_path:
            self.send_input(choice)
            time.sleep(0.5)
        
        # 发送额外输入
        if inputs:
            for inp in inputs:
                self.send_input(inp)
                time.sleep(0.5)


# 快捷函数
def quick_run(log_callback, menu_path, inputs=None):
    """快速运行脚本功能"""
    interface = ScriptInterface(log_callback)
    interface.start()
    time.sleep(2)
    interface.run_function(menu_path, inputs)
    return interface


if __name__ == '__main__':
    # 测试
    def test_log(text, color=None):
        print(text)
    
    interface = ScriptInterface(test_log)
    interface.start()
    time.sleep(3)
    interface.send_input('32')  # 登录账号
    time.sleep(5)
    interface.stop()
