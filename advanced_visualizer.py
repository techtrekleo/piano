import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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
import colorsys

class AdvancedMusicVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("高级音乐可视化器 - See Music")
        self.root.geometry("1400x900")
        self.root.configure(bg='black')
        
        # 音频相关变量
        self.audio_file = None
        self.y = None
        self.sr = None
        self.is_playing = False
        self.current_position = 0
        self.audio_data = None
        
        # 可视化参数
        self.visualization_mode = "falling_notes"  # falling_notes, spectrum, waveform
        self.color_scheme = "rainbow"  # rainbow, frequency_based, mood_based
        
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
        
        # 控制面板
        control_panel = tk.Frame(self.root, bg="black")
        control_panel.pack(fill=tk.X, padx=20, pady=10)
        
        # 左侧控制按钮
        left_controls = tk.Frame(control_panel, bg="black")
        left_controls.pack(side=tk.LEFT)
        
        # 上传按钮
        self.upload_btn = tk.Button(
            left_controls,
            text="上传音乐文件",
            command=self.upload_music,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            padx=15,
            pady=8
        )
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        # 播放/暂停按钮
        self.play_btn = tk.Button(
            left_controls,
            text="播放",
            command=self.toggle_play,
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            relief="flat",
            padx=15,
            pady=8,
            state=tk.DISABLED
        )
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        # 停止按钮
        self.stop_btn = tk.Button(
            left_controls,
            text="停止",
            command=self.stop_music,
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            relief="flat",
            padx=15,
            pady=8,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 右侧设置面板
        right_controls = tk.Frame(control_panel, bg="black")
        right_controls.pack(side=tk.RIGHT)
        
        # 可视化模式选择
        tk.Label(right_controls, text="可视化模式:", fg="white", bg="black").pack(side=tk.LEFT, padx=5)
        self.mode_var = tk.StringVar(value="falling_notes")
        mode_combo = ttk.Combobox(
            right_controls,
            textvariable=self.mode_var,
            values=["falling_notes", "spectrum", "waveform", "piano_roll"],
            state="readonly",
            width=15
        )
        mode_combo.pack(side=tk.LEFT, padx=5)
        mode_combo.bind("<<ComboboxSelected>>", self.change_visualization_mode)
        
        # 颜色方案选择
        tk.Label(right_controls, text="颜色方案:", fg="white", bg="black").pack(side=tk.LEFT, padx=5)
        self.color_var = tk.StringVar(value="rainbow")
        color_combo = ttk.Combobox(
            right_controls,
            textvariable=self.color_var,
            values=["rainbow", "frequency_based", "mood_based"],
            state="readonly",
            width=15
        )
        color_combo.pack(side=tk.LEFT, padx=5)
        color_combo.bind("<<ComboboxSelected>>", self.change_color_scheme)
        
        # 文件信息标签
        self.file_label = tk.Label(
            self.root,
            text="未选择文件",
            font=("Arial", 12),
            fg="white",
            bg="black"
        )
        self.file_label.pack(pady=10)
        
        # 音频信息框架
        self.info_frame = tk.Frame(self.root, bg="black")
        self.info_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # 音频信息标签
        self.duration_label = tk.Label(self.info_frame, text="", fg="white", bg="black")
        self.duration_label.pack(side=tk.LEFT, padx=10)
        
        self.tempo_label = tk.Label(self.info_frame, text="", fg="white", bg="black")
        self.tempo_label.pack(side=tk.LEFT, padx=10)
        
        self.key_label = tk.Label(self.info_frame, text="", fg="white", bg="black")
        self.key_label.pack(side=tk.LEFT, padx=10)
        
        # 可视化画布
        self.canvas_frame = tk.Frame(self.root, bg="black")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建matplotlib图形
        self.fig, self.ax = plt.subplots(figsize=(14, 7), facecolor='black')
        self.ax.set_facecolor('black')
        self.ax.set_xlim(0, 88)
        self.ax.set_ylim(0, 100)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 绘制钢琴键盘
        self.draw_piano_keyboard()
        
        # 音符和效果列表
        self.notes = []
        self.effects = []
        
        # 动画
        self.ani = None
        
        # 音频分析数据
        self.onset_frames = None
        self.chromagram = None
        self.mfcc = None
        
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
            # 显示加载提示
            self.file_label.config(text="正在分析音频...")
            self.root.update()
            
            # 加载音频
            self.y, self.sr = librosa.load(self.audio_file, sr=None)
            
            # 获取音频长度
            duration = librosa.get_duration(y=self.y, sr=self.sr)
            
            # 提取节拍
            tempo, beats = librosa.beat.beat_track(y=self.y, sr=self.sr)
            
            # 提取调性
            key = librosa.feature.key_mode(y=self.y, sr=self.sr)
            
            # 提取起始点
            self.onset_frames = librosa.onset.onset_detect(y=self.y, sr=self.sr)
            
            # 提取色度图
            self.chromagram = librosa.feature.chroma_cqt(y=self.y, sr=self.sr)
            
            # 提取MFCC特征
            self.mfcc = librosa.feature.mfcc(y=self.y, sr=self.sr)
            
            # 存储分析结果
            self.audio_data = {
                'duration': duration,
                'tempo': tempo,
                'beats': beats,
                'key': key,
                'onset_frames': self.onset_frames,
                'chromagram': self.chromagram,
                'mfcc': self.mfcc
            }
            
            # 更新信息显示
            self.duration_label.config(text=f"时长: {duration:.2f}秒")
            self.tempo_label.config(text=f"节拍: {tempo:.1f} BPM")
            self.key_label.config(text=f"调性: {key}")
            
            self.file_label.config(text=f"已选择: {os.path.basename(self.audio_file)}")
            
            messagebox.showinfo("成功", f"音频分析完成！\n时长: {duration:.2f}秒\n节拍: {tempo:.1f} BPM")
            
        except Exception as e:
            messagebox.showerror("错误", f"音频分析失败: {str(e)}")
            self.file_label.config(text="分析失败")
            
    def change_visualization_mode(self, event=None):
        """改变可视化模式"""
        self.visualization_mode = self.mode_var.get()
        self.clear_visualization()
        
    def change_color_scheme(self, event=None):
        """改变颜色方案"""
        self.color_scheme = self.color_var.get()
        
    def clear_visualization(self):
        """清除可视化效果"""
        self.notes.clear()
        self.effects.clear()
        self.ax.clear()
        self.draw_piano_keyboard()
        self.canvas.draw()
        
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
            
        # 清除可视化
        self.clear_visualization()
        
    def start_visualization(self):
        """开始可视化动画"""
        if self.ani:
            self.ani.event_source.stop()
            
        self.ani = animation.FuncAnimation(
            self.fig, 
            self.update_visualization, 
            interval=33,  # 30 FPS
            blit=False
        )
        
    def update_visualization(self, frame):
        """更新可视化效果"""
        if not self.is_playing:
            return
            
        # 获取当前播放位置
        current_time = pygame.mixer.music.get_pos() / 1000.0
        
        # 根据可视化模式更新
        if self.visualization_mode == "falling_notes":
            self.update_falling_notes(current_time, frame)
        elif self.visualization_mode == "spectrum":
            self.update_spectrum_visualization(current_time, frame)
        elif self.visualization_mode == "waveform":
            self.update_waveform_visualization(current_time, frame)
        elif self.visualization_mode == "piano_roll":
            self.update_piano_roll_visualization(current_time, frame)
            
        # 重绘画布
        self.canvas.draw()
        
    def update_falling_notes(self, current_time, frame):
        """更新落下的音符效果"""
        # 根据节拍生成音符
        if self.audio_data and 'beats' in self.audio_data:
            beat_times = librosa.frames_to_time(self.audio_data['beats'], sr=self.sr)
            if len(beat_times) > 0:
                # 找到最近的节拍
                beat_idx = np.argmin(np.abs(beat_times - current_time))
                if abs(beat_times[beat_idx] - current_time) < 0.1:  # 在节拍附近
                    self.generate_beat_note(current_time)
        
        # 随机生成音符
        if frame % 15 == 0:
            self.generate_random_note(current_time)
            
        # 更新音符位置
        self.update_notes()
        
    def generate_beat_note(self, current_time):
        """根据节拍生成音符"""
        # 使用色度图信息生成音符
        if self.chromagram is not None:
            current_frame = int(current_time * self.sr / 512)  # 假设hop_length=512
            if current_frame < self.chromagram.shape[1]:
                chroma = self.chromagram[:, current_frame]
                # 找到最强的音符
                note_idx = np.argmax(chroma)
                key_position = note_idx * 7  # 映射到钢琴键
                
                note = {
                    'x': key_position,
                    'y': 100,
                    'color': self.get_note_color(note_idx, current_time),
                    'size': 1.0,
                    'speed': 2.5,
                    'type': 'beat'
                }
                self.notes.append(note)
                
    def generate_random_note(self, current_time):
        """生成随机音符"""
        key_position = np.random.randint(0, 88)
        
        note = {
            'x': key_position,
            'y': 100,
            'color': self.get_note_color(key_position, current_time),
            'size': np.random.uniform(0.3, 0.8),
            'speed': np.random.uniform(1, 3),
            'type': 'random'
        }
        
        self.notes.append(note)
        
    def get_note_color(self, note_idx, current_time):
        """根据音符和时间获取颜色"""
        if self.color_scheme == "rainbow":
            hue = (note_idx / 88.0 + current_time * 0.1) % 1.0
            return colorsys.hsv_to_rgb(hue, 0.8, 0.9)
        elif self.color_scheme == "frequency_based":
            # 根据频率映射颜色
            freq = librosa.midi_to_freq(note_idx + 21)  # 21是A0的MIDI音高
            hue = (np.log10(freq) - np.log10(27.5)) / (np.log10(4186) - np.log10(27.5))
            hue = np.clip(hue, 0, 1)
            return colorsys.hsv_to_rgb(hue, 0.8, 0.9)
        else:  # mood_based
            # 根据MFCC特征映射颜色
            if self.mfcc is not None:
                current_frame = int(current_time * self.sr / 512)
                if current_frame < self.mfcc.shape[1]:
                    mfcc_val = self.mfcc[0, current_frame]  # 使用第一个MFCC系数
                    hue = (mfcc_val + 20) / 40  # 归一化到0-1
                    hue = np.clip(hue, 0, 1)
                    return colorsys.hsv_to_rgb(hue, 0.8, 0.9)
            
            return colorsys.hsv_to_rgb(0.5, 0.8, 0.9)  # 默认蓝色
            
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
            if note['type'] == 'beat':
                # 节拍音符使用星形
                star = self.draw_star(note['x'], note['y'], note['size'], note['color'])
                star._note = True
                self.ax.add_patch(star)
            else:
                # 普通音符使用圆形
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
        if len(self.notes) > 100:
            self.notes = self.notes[-100:]
            
    def draw_star(self, x, y, size, color):
        """绘制星形"""
        angles = np.linspace(0, 2*np.pi, 10, endpoint=False)
        star_x = x + size * np.cos(angles[::2])
        star_y = y + size * np.sin(angles[::2])
        
        star = plt.Polygon(list(zip(star_x, star_y)), color=color, alpha=0.9)
        return star
        
    def update_spectrum_visualization(self, current_time, frame):
        """更新频谱可视化"""
        if self.audio_data and 'chromagram' in self.audio_data:
            current_frame = int(current_time * self.sr / 512)
            if current_frame < self.chromagram.shape[1]:
                chroma = self.chromagram[:, current_frame]
                
                # 清除之前的频谱条
                for artist in self.ax.patches:
                    if hasattr(artist, '_spectrum'):
                        artist.remove()
                        
                # 绘制频谱条
                for i, intensity in enumerate(chroma):
                    x = i * 7
                    height = intensity * 80
                    bar = plt.Rectangle((x-0.3, 20), 0.6, height, 
                                      color=self.get_note_color(i, current_time),
                                      alpha=0.8)
                    bar._spectrum = True
                    self.ax.add_patch(bar)
                    
    def update_waveform_visualization(self, current_time, frame):
        """更新波形可视化"""
        if self.y is not None:
            # 获取当前时间窗口的波形
            window_size = int(0.1 * self.sr)  # 100ms窗口
            start_sample = int(current_time * self.sr)
            end_sample = min(start_sample + window_size, len(self.y))
            
            if start_sample < len(self.y):
                waveform = self.y[start_sample:end_sample]
                
                # 清除之前的波形
                for artist in self.ax.lines:
                    artist.remove()
                    
                # 绘制波形
                x = np.linspace(0, 88, len(waveform))
                y = 60 + waveform * 20  # 缩放并居中
                line, = self.ax.plot(x, y, color='cyan', linewidth=2, alpha=0.8)
                
    def update_piano_roll_visualization(self, current_time, frame):
        """更新钢琴卷可视化"""
        if self.audio_data and 'chromagram' in self.audio_data:
            current_frame = int(current_time * self.sr / 512)
            if current_frame < self.chromagram.shape[1]:
                chroma = self.chromagram[:, current_frame]
                
                # 清除之前的钢琴卷
                for artist in self.ax.patches:
                    if hasattr(artist, '_piano_roll'):
                        artist.remove()
                        
                # 绘制钢琴卷
                for i, intensity in enumerate(chroma):
                    if intensity > 0.1:  # 只显示强度较高的音符
                        x = i * 7
                        y = 25 + intensity * 70
                        note = plt.Rectangle((x-0.3, y), 0.6, 2, 
                                           color=self.get_note_color(i, current_time),
                                           alpha=intensity)
                        note._piano_roll = True
                        self.ax.add_patch(note)

def main():
    root = tk.Tk()
    app = AdvancedMusicVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
