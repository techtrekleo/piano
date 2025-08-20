from flask import Flask, jsonify, render_template
import os

app = Flask(__name__)

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
        'endpoints': ['/', '/health', '/test', '/api/status']
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """文件上傳端點（簡化版本）"""
    try:
        # 簡化處理 - 只返回基本信息
        return jsonify({
            'success': True,
            'message': '文件上傳成功！音頻分析功能正在開發中...',
            'status': 'uploaded'
        })
    except Exception as e:
        return jsonify({'error': f'處理失敗: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 啟動音樂可視化器，端口: {port}")
    print(f"🌐 健康檢查: http://localhost:{port}/health")
    print(f"📱 主頁面: http://localhost:{port}/")
    
    app.run(host='0.0.0.0', port=port, debug=False)
