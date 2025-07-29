from flask import Flask, request, jsonify, render_template
from journal import save_entry, get_all_entries, init_db, get_emotion_stats
from emotion_analysis import analyze_emotion, get_combined_analysis, get_wellness_recommendation
import json

app = Flask(__name__)

# Initialize database and table
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/journal', methods=['POST'])
def add_entry():
    data = request.get_json()
    entry = data.get('entry', '')
    voice_data = data.get('voice_data', None)

    if not entry:
        return jsonify({'error': 'Entry text is required'}), 400

    # Enhanced emotion analysis
    if voice_data:
        analysis = get_combined_analysis(entry, voice_data)
    else:
        analysis = get_combined_analysis(entry)
    
    # Save entry with detailed analysis
    save_entry(entry, analysis['text_analysis']['dominant_emotion'], 
               json.dumps(analysis), analysis['text_analysis']['sentiment'])
    
    return jsonify({
        'message': 'Entry saved successfully',
        'analysis': analysis,
        'recommendation': analysis['recommendation']
    }), 201

@app.route('/api/journal', methods=['GET'])
def fetch_entries():
    entries = get_all_entries()
    return jsonify(entries), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get emotion statistics and trends"""
    stats = get_emotion_stats()
    return jsonify(stats), 200

@app.route('/api/wellness-check', methods=['POST'])
def wellness_check():
    """Quick wellness check endpoint"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    analysis = analyze_emotion(text)
    recommendation = get_wellness_recommendation(analysis, None)
    
    return jsonify({
        'emotion': analysis['dominant_emotion'],
        'sentiment': analysis['sentiment'],
        'confidence': analysis['confidence'],
        'recommendation': recommendation,
        'intensity': analysis['intensity']
    }), 200

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'VoiceLens API',
        'version': '1.0.0'
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


