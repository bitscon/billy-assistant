from flask import request, jsonify
from app.services import handle_ask, perform_search, summarize_query
from app.profile import load_profile, save_profile, update_profile_role, update_profile_tone, add_favorite, get_favorites, get_role, get_tone
import time

logs = []
start_time = time.time()

def register_routes(app):
    @app.route('/')
    def index():
        profile = load_profile()
        return f"Good day, {profile.get('name', 'friend')}. How may I assist you?"

    @app.route('/ask', methods=['POST'])
    def ask():
        question = request.json.get('question', '')
        profile = load_profile()
        response = handle_ask(question, profile)
        logs.append({'type': 'ask', 'question': question, 'response': response, 'timestamp': time.time()})
        return jsonify(response)

    @app.route('/search', methods=['POST'])
    def search():
        query = request.json.get('query', '')
        results = perform_search(query)
        logs.append({'type': 'search', 'query': query, 'provider': 'duckduckgo', 'result_count': len(results), 'timestamp': time.time()})
        return jsonify({'provider': 'duckduckgo', 'results': results})

    @app.route('/summarize', methods=['POST'])
    def summarize():
        query = request.json.get('query', '')
        summary = summarize_query(query)
        return jsonify(summary)

    @app.route('/admin/logs')
    def get_logs():
        return jsonify(logs)

    @app.route('/admin/status')
    def status():
        return jsonify({
            'status': 'running',
            'uptime_sec': round(time.time() - start_time, 2),
            'default_search': 'duckduckgo',
            'ollama_url': 'http://ollama:11434/api/generate',
            'profile': load_profile()
        })

    @app.route('/profile', methods=['GET'])
    def get_profile():
        return jsonify(load_profile())

    @app.route('/profile/role', methods=['GET', 'POST'])
    def role():
        if request.method == 'POST':
            return jsonify(update_profile_role(request.json.get('role', '')))
        return jsonify(get_role())

    @app.route('/profile/tone', methods=['GET', 'POST'])
    def tone():
        if request.method == 'POST':
            return jsonify(update_profile_tone(request.json.get('tone', '')))
        return jsonify(get_tone())

    @app.route('/profile/favorite', methods=['POST'])
    def favorite():
        return jsonify(add_favorite(request.json))

    @app.route('/profile/favorites')
    def favorites():
        return jsonify(get_favorites())
