from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
import librosa
import numpy as np
import json
from werkzeug.utils import secure_filename
import io
import base64
import matplotlib
matplotlib.use('Agg')  # 使用非交互式後端
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.animation as animation

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# 配置上傳文件夾
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 允許的文件類型
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'm4a', 'ogg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '沒有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '沒有選擇文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # 分析音頻
            audio_data = analyze_audio(filepath)
            
            # 生成可視化
            visualization_data = generate_visualization(audio_data)
            
            # 清理臨時文件
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'audio_data': audio_data,
                'visualization': visualization_data
            })
            
        except Exception as e:
            # 清理臨時文件
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'音頻分析失敗: {str(e)}'}), 500
    
    return jsonify({'error': '不支持的文件類型'}), 400

def analyze_audio(filepath):
    """分析音頻文件"""
    # 加載音頻
    y, sr = librosa.load(filepath, sr=None)
    
    # 獲取音頻長度
    duration = librosa.get_duration(y=y, sr=sr)
    
    # 提取節拍
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    
    # 提取調性
    key = librosa.feature.key_mode(y=y, sr=sr)
    
    # 提取起始點
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    
    # 提取色度圖
    chromagram = librosa.feature.chroma_cqt(y=y, sr=sr)
    
    # 提取MFCC特徵
    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    
    return {
        'duration': float(duration),
        'tempo': float(tempo),
        'beats': beats.tolist(),
        'key': key.tolist(),
        'onset_frames': onset_frames.tolist(),
        'chromagram': chromagram.tolist(),
        'mfcc': mfcc.tolist(),
        'sample_rate': int(sr),
        'samples': len(y)
    }

def generate_visualization(audio_data):
    """生成可視化數據"""
    # 創建鋼琴鍵盤數據
    piano_keys = create_piano_keys()
    
    # 創建音符數據
    notes = create_notes(audio_data)
    
    return {
        'piano_keys': piano_keys,
        'notes': notes,
        'spectrum_data': audio_data['chromagram'],
        'tempo': audio_data['tempo'],
        'duration': audio_data['duration']
    }

def create_piano_keys():
    """創建鋼琴鍵盤數據"""
    white_keys = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24, 26, 28, 29, 31, 33, 35, 36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88]
    black_keys = [1, 3, 6, 8, 10, 13, 15, 18, 20, 22, 25, 27, 30, 32, 34, 37, 39, 42, 44, 46, 49, 51, 54, 56, 58, 61, 63, 66, 68, 70, 73, 75, 78, 80, 82, 85, 87]
    
    return {
        'white_keys': white_keys,
        'black_keys': black_keys
    }

def create_notes(audio_data):
    """創建音符數據"""
    notes = []
    
    # 根據節拍生成音符
    if 'beats' in audio_data and audio_data['beats']:
        beat_times = librosa.frames_to_time(audio_data['beats'], sr=audio_data['sample_rate'])
        
        for i, beat_time in enumerate(beat_times):
            if i < 50:  # 限制音符數量
                # 根據色度圖選擇音符
                if 'chromagram' in audio_data and audio_data['chromagram']:
                    frame_idx = int(beat_time * audio_data['sample_rate'] / 512)
                    if frame_idx < len(audio_data['chromagram'][0]):
                        chroma = [row[frame_idx] for row in audio_data['chromagram']]
                        note_idx = np.argmax(chroma)
                        key_position = note_idx * 7
                        
                        notes.append({
                            'x': int(key_position),
                            'y': 100,
                            'color': get_note_color(note_idx, beat_time),
                            'size': 1.0,
                            'speed': 2.5,
                            'type': 'beat',
                            'time': float(beat_time)
                        })
    
    return notes

def get_note_color(note_idx, time):
    """獲取音符顏色"""
    import colorsys
    
    # 彩虹色彩方案
    hue = (note_idx / 12.0 + time * 0.1) % 1.0
    rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
    return [int(c * 255) for c in rgb]

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': '音樂可視化器運行正常'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
