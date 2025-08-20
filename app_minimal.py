from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'message': 'See Music - 音樂可視化器',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': '音樂可視化器運行正常'
    })

@app.route('/test')
def test():
    return jsonify({
        'message': 'Hello from See Music!',
        'status': 'working'
    })

@app.route('/api/status')
def api_status():
    return jsonify({
        'app': 'See Music - 音樂可視化器',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': ['/', '/health', '/test', '/api/status']
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 啟動極簡版音樂可視化器，端口: {port}")
    print(f"🌐 健康檢查: http://localhost:{port}/health")
    
    app.run(host='0.0.0.0', port=port, debug=False)
