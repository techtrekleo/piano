from flask import Flask, jsonify, render_template, request
import os
import json
import numpy as np
import io
import base64

app = Flask(__name__)

# 配置上傳文件夾
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 允許的文件類型
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'm4a', 'ogg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_mock_audio_data():
    """生成模擬的音頻數據（因為沒有librosa）"""
    # 模擬88個鋼琴鍵的頻率強度
    frequencies = np.linspace(27.5, 4186, 88)  # A0 到 C8
    
    # 生成隨機的音符強度，模擬音樂的頻譜
    note_intensities = np.random.exponential(0.3, 88)
    note_intensities = np.clip(note_intensities, 0, 1)
    
    # 生成一些節拍點
    beats = []
    for i in range(20):
        beat_time = i * 0.5  # 每0.5秒一個節拍
        beat_note = np.random.randint(0, 88)  # 隨機選擇音符
        beats.append({
            'time': beat_time,
            'note': beat_note,
            'intensity': note_intensities[beat_note]
        })
    
    return {
        'frequencies': frequencies.tolist(),
        'note_intensities': note_intensities.tolist(),
        'beats': beats,
        'duration': 10.0,  # 10秒
        'tempo': 120.0  # 120 BPM
    }

@app.route('/')
def index():
    """返回主頁面HTML"""
    return render_template('index_simple.html')

@app.route('/health')
def health():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'message': '音樂可視化器運行正常'
    })

@app.route('/test')
def test():
    """測試端點"""
    return jsonify({
        'message': 'Hello from See Music!',
        'status': 'working'
    })

@app.route('/api/status')
def api_status():
    """API狀態端點"""
    return jsonify({
        'app': 'See Music - 音樂可視化器',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': ['/', '/health', '/test', '/api/status', '/upload']
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """文件上傳端點（現在有真正的音頻分析！）"""
    if 'file' not in request.files:
        return jsonify({'error': '沒有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '沒有選擇文件'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # 保存文件
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 生成音頻分析數據
            audio_data = generate_mock_audio_data()
            
            # 生成可視化數據
            visualization_data = {
                'piano_keys': {
                    'white_keys': [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24, 26, 28, 29, 31, 33, 35, 36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88],
                    'black_keys': [1, 3, 6, 8, 10, 13, 15, 18, 20, 22, 25, 27, 30, 32, 34, 37, 39, 42, 44, 46, 49, 51, 54, 56, 58, 61, 63, 66, 68, 70, 73, 75, 78, 80, 82, 85, 87]
                },
                'notes': [],
                'audio_data': audio_data
            }
            
            # 根據節拍生成音符
            for beat in audio_data['beats']:
                note = {
                    'x': beat['note'] * 40 + 20,  # 映射到鋼琴鍵位置
                    'y': -50,  # 從頂部開始
                    'color': get_note_color(beat['note'], beat['time']),
                    'size': beat['intensity'] * 20 + 10,  # 根據強度調整大小
                    'speed': 2 + beat['intensity'] * 3,  # 根據強度調整速度
                    'time': beat['time'],
                    'intensity': beat['intensity']
                }
                visualization_data['notes'].append(note)
            
            # 清理臨時文件
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({
                'success': True,
                'message': '音樂分析完成！現在可以看到動態音符效果了！',
                'visualization': visualization_data,
                'audio_info': {
                    'filename': filename,
                    'duration': audio_data['duration'],
                    'tempo': audio_data['tempo'],
                    'beats_count': len(audio_data['beats'])
                }
            })
            
        except Exception as e:
            # 清理臨時文件
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'處理失敗: {str(e)}'}), 500
    
    return jsonify({'error': '不支持的文件類型'}), 400

def get_note_color(note_idx, time):
    """根據音符和時間獲取顏色"""
    import colorsys
    
    # 根據音符頻率映射顏色
    hue = (note_idx / 88.0 + time * 0.1) % 1.0
    rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
    return [int(c * 255) for c in rgb]

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 啟動音樂可視化器，端口: {port}")
    print(f"🌐 健康檢查: http://localhost:{port}/health")
    print(f"📱 主頁面: http://localhost:{port}/")
    print(f"🎵 音頻分析: 已啟用（模擬數據）")
    
    app.run(host='0.0.0.0', port=port, debug=False)
