from flask import Flask, render_template, request, jsonify
import os
import json

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

@app.route('/health')
def health():
    """健康檢查端點"""
    try:
        return jsonify({
            'status': 'healthy', 
            'message': '音樂可視化器運行正常',
            'timestamp': '2025-01-20T20:30:00Z'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/test')
def test():
    """測試端點"""
    return jsonify({
        'message': 'Hello from See Music!',
        'status': 'working'
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """文件上傳端點（簡化版本）"""
    if 'file' not in request.files:
        return jsonify({'error': '沒有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '沒有選擇文件'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # 簡化處理 - 只返回基本信息
            filename = file.filename
            file_size = len(file.read())
            file.seek(0)  # 重置文件指針
            
            # 保存文件
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 返回基本信息
            result = {
                'success': True,
                'filename': filename,
                'size': file_size,
                'message': '文件上傳成功！音頻分析功能正在開發中...'
            }
            
            # 清理臨時文件
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': f'處理失敗: {str(e)}'}), 500
    
    return jsonify({'error': '不支持的文件類型'}), 400

@app.route('/api/status')
def api_status():
    """API狀態端點"""
    return jsonify({
        'app': 'See Music - 音樂可視化器',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': [
            '/',
            '/health',
            '/test',
            '/upload',
            '/api/status'
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 啟動音樂可視化器，端口: {port}")
    print(f"🌐 健康檢查端點: http://localhost:{port}/health")
    print(f"📊 狀態端點: http://localhost:{port}/api/status")
    
    app.run(host='0.0.0.0', port=port, debug=False)
