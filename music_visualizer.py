import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import librosa
import numpy as np
import threading
import time
import os
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

class MusicVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("音乐可视化器 - See Music")
        self.root.geometry("1200x800")
        self.root.configure(bg='black')
        
        # 音频相关变量
        self.audio_file = None
        self.y = None
        self.sr = None
        self.is_playing = False
        self.current_position = 0
        
        # 初始化pygame mixer
        pygame.mixer.init()
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主标题
        title_label = tk.Label(
            self.root, 
            text="See Music", 
            font=("Arial", 36, "bold"),
            fg="white",
            bg="black"
        )
        title_label.pack(pady=20)
        
        # 控制按钮框架
        control_frame = tk.Frame(self.root, bg="black")
        control_frame.pack(pady=20)
        
        # 上传按钮
        self.upload_btn = tk.Button(
            control_frame,
            text="上传音乐文件",
            command=self.upload_music,
            font=("Arial", 14),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            padx=20,
            pady=10
        )
        self.upload_btn.pack(side=tk.LEFT, padx=10)
        
        # 播放/暂停按钮
        self.play_btn = tk.Button(
            control_frame,
            text="播放",
            command=self.toggle_play,
            font=("Arial", 14),
            bg="#2196F3",
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.play_btn.pack(side=tk.LEFT, padx=10)
        
        # 停止按钮
        self.stop_btn = tk.Button(
            control_frame,
            text="停止",
            command=self.stop_music,
            font=("Arial", 14),
            bg="#f44336",
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.10, padx=10)
        
        # 文件信息标签
        self.file_label = tk.Label(
            self.root,
            text="未选择文件",
            font=("Arial", 12),
            fg="white",
            bg="black"
        )
        self.file_label.pack(pady=10)
        
        # 可视化画布
        self.canvas_frame = tk.Frame(self.root, bg="black")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建matplotlib图形
        self.fig, self.ax = plt.subplots(figsize=(12, 6), facecolor='black')
        self.ax.set_facecolor('black')
        self.ax.set_xlim(0, 88)  # 88个钢琴键
        self.ax.set_ylim(0, 100)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 绘制钢琴键盘
        self.draw_piano_keyboard()
        
        # 音符列表
        self.notes = []
        
        # 动画
        self.ani = None
        
    def draw_piano_keyboard(self):
        """绘制钢琴键盘"""
        # 白键
        white_keys = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24, 26, 28, 29, 31, 33, 35, 36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88]
        
        for key in white_keys:
            if key <= 88:
                x = key
                rect = plt.Rectangle((x-0.4, 0), 0.8, 20, facecolor='white', edgecolor='black', linewidth=1)
                self.ax.add_patch(rect)
        
        # 黑键
        black_keys = [1, 3, 6, 8, 10, 13, 15, 18, 20, 22, 25, 27, 30, 32, 34, 37, 39, 42, 44, 46, 49, 51, 54, 56, 58, 61, 63, 66, 68, 70, 73, 75, 78, 80, 82, 85, 87]
        
        for key in black_keys:
            if key <= 88:
                x = key
                rect = plt.Rectangle((x-0.25, 12), 0.5, 8, facecolor='black', edgecolor='white', linewidth=1)
                self.ax.add_patch(rect)
        
        self.canvas.draw()
        
    def upload_music(self):
        """上传音乐文件"""
        file_path = filedialog.askopenfilename(
            title="选择音乐文件",
            filetypes=[
                ("音频文件", "*.mp3 *.wav *.flac *.m4a"),
                ("MP3文件", "*.mp3"),
                ("WAV文件", "*.wav"),
                ("FLAC文件", "*.flac"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.audio_file = file_path
                self.file_label.config(text=f"已选择: {os.path.basename(file_path)}")
                
                # 分析音频
                self.analyze_audio()
                
                # 启用播放按钮
                self.play_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.NORMAL)
                
            except Exception as e:
                messagebox.showerror("错误", f"无法加载音频文件: {str(e)}")
                
    def analyze_audio(self):
        """分析音频文件"""
        try:
            # 加载音频
            self.y, self.sr = librosa.load(self.audio_file, sr=None)
            
            # 获取音频长度
            duration = librosa.get_duration(y=self.y, sr=self.sr)
            
            # 提取节拍
            tempo, beats = librosa.beat.beat_track(y=self.y, sr=self.sr)
            
            # 提取频谱
            D = librosa.stft(self.y)
            frequencies = librosa.fft_frequencies(sr=self.sr)
            
            # 存储分析结果
            self.audio_data = {
                'duration': duration,
                'tempo': tempo,
                'beats': beats,
                'frequencies': frequencies,
                'spectrogram': np.abs(D)
            }
            
            messagebox.showinfo("成功", f"音频分析完成！\n时长: {duration:.2f}秒\n节拍: {tempo:.1f} BPM")
            
        except Exception as e:
            messagebox.showerror("错误", f"音频分析失败: {str(e)}")
            
    def toggle_play(self):
        """播放/暂停音乐"""
        if not self.is_playing:
            self.play_music()
        else:
            self.pause_music()
            
    def play_music(self):
        """播放音乐"""
        try:
            pygame.mixer.music.load(self.audio_file)
            pygame.mixer.music.play()
            self.is_playing = True
            self.play_btn.config(text="暂停")
            
            # 开始可视化动画
            self.start_visualization()
            
        except Exception as e:
            messagebox.showerror("错误", f"播放失败: {str(e)}")
            
    def pause_music(self):
        """暂停音乐"""
        pygame.mixer.music.pause()
        self.is_playing = False
        self.play_btn.config(text="播放")
        
        # 停止动画
        if self.ani:
            self.ani.event_source.stop()
            
    def stop_music(self):
        """停止音乐"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_btn.config(text="播放")
        
        # 停止动画
        if self.ani:
            self.ani.event_source.stop()
            
        # 清除音符
        self.notes.clear()
        self.ax.clear()
        self.draw_piano_keyboard()
        self.canvas.draw()
        
    def start_visualization(self):
        """开始可视化动画"""
        if self.ani:
            self.ani.event_source.stop()
            
        self.ani = animation.FuncAnimation(
            self.fig, 
            self.update_visualization, 
            interval=50,  # 20 FPS
            blit=False
        )
        
    def update_visualization(self, frame):
        """更新可视化效果"""
        if not self.is_playing:
            return
            
        # 获取当前播放位置
        current_time = pygame.mixer.music.get_pos() / 1000.0
        
        # 根据时间生成音符
        if frame % 10 == 0:  # 每10帧生成一个音符
            self.generate_note(current_time)
            
        # 更新音符位置
        self.update_notes()
        
        # 重绘画布
        self.canvas.draw()
        
    def generate_note(self, current_time):
        """生成音符"""
        # 随机选择音符位置（对应钢琴键）
        key_position = np.random.randint(0, 88)
        
        # 随机选择颜色
        colors = ['purple', 'green', 'yellow', 'cyan', 'magenta']
        color = np.random.choice(colors)
        
        # 创建音符
        note = {
            'x': key_position,
            'y': 100,  # 从顶部开始
            'color': color,
            'size': np.random.uniform(0.3, 0.8),
            'speed': np.random.uniform(1, 3)
        }
        
        self.notes.append(note)
        
    def update_notes(self):
        """更新音符位置"""
        # 清除之前的音符
        for artist in self.ax.texts + self.ax.patches:
            if hasattr(artist, '_note'):
                artist.remove()
                
        # 更新音符位置
        notes_to_remove = []
        for note in self.notes:
            note['y'] -= note['speed']
            
            # 绘制音符
            circle = plt.Circle((note['x'], note['y']), note['size'], 
                              color=note['color'], alpha=0.8)
            circle._note = True
            self.ax.add_patch(circle)
            
            # 如果音符到达键盘，标记为删除
            if note['y'] <= 20:
                notes_to_remove.append(note)
                
        # 删除到达键盘的音符
        for note in notes_to_remove:
            self.notes.remove(note)
            
        # 限制音符数量
        if len(self.notes) > 50:
            self.notes = self.notes[-50:]

def main():
    root = tk.Tk()
    app = MusicVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
