from flask import Flask, request, jsonify
import os
import cv2
import numpy as np
from pathlib import Path
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'images'

face_db = {}
image_store = {}

def compute_image_hash(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None
        img = cv2.resize(img, (64, 64))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hash_val = cv2.imencode('.jpg', gray)[1].tobytes()
        return hash(hash_val) % (10**9)
    except:
        return None

def find_matching_grab_id(img_hash, tolerance=5000):
    if not face_db:
        return None
    best_match = None
    min_distance = float('inf')
    for grab_id, hashes in face_db.items():
        for stored_hash in hashes:
            distance = abs(img_hash - stored_hash)
            if distance < min_distance:
                min_distance = distance
                best_match = grab_id
    if min_distance < tolerance:
        return best_match
    return None

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/index', methods=['POST'])
def index_images():
    image_dir = Path('images')
    results = []
    if not image_dir.exists():
        return jsonify({'error': 'images folder not found'}), 400
    for img_file in image_dir.glob('*'):
        if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            try:
                img_hash = compute_image_hash(str(img_file))
                if img_hash is None:
                    results.append({'file': img_file.name, 'status': 'failed'})
                    continue
                grab_id = find_matching_grab_id(img_hash, tolerance=3000)
                if grab_id is None:
                    grab_id = f"grab_{str(uuid.uuid4())[:6]}"
                    face_db[grab_id] = []
                face_db[grab_id].append(img_hash)
                image_store[str(img_file)] = grab_id
                results.append({'file': img_file.name, 'grab_id': grab_id, 'status': 'indexed'})
            except Exception as e:
                results.append({'file': img_file.name, 'error': str(e)})
    return jsonify({'indexed': len([r for r in results if r.get('status') == 'indexed']), 'total_users': len(face_db), 'results': results})

@app.route('/api/auth', methods=['POST'])
def selfie_auth():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    temp_path = 'temp_selfie.jpg'
    try:
        file.save(temp_path)
        img_hash = compute_image_hash(temp_path)
        if img_hash is None:
            return jsonify({'error': 'Could not process image'}), 400
        grab_id = find_matching_grab_id(img_hash, tolerance=4000)
        if grab_id is None:
            return jsonify({'error': 'No matching user found', 'grab_id': None}), 404
        return jsonify({'grab_id': grab_id, 'status': 'authenticated', 'images_count': len([img for img, gid in image_store.items() if gid == grab_id])}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/api/images/<grab_id>', methods=['GET'])
def get_user_images(grab_id):
    user_images = [img for img, gid in image_store.items() if gid == grab_id]
    if not user_images:
        return jsonify({'error': 'No images found'}), 404
    return jsonify({'grab_id': grab_id, 'count': len(user_images), 'images': user_images}), 200

@app.route('/api/stats', methods=['GET'])
def stats():
    return jsonify({'total_users': len(face_db), 'total_images': len(image_store), 'users': list(face_db.keys())})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print("Starting Grabpic API on http://localhost:5000")
    app.run(debug=True, port=5000)