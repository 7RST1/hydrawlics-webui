import os
import uuid
import threading
from CannyEdge import Canny_detector
from datetime import datetime
from time import sleep

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# In-memory job storage (use Redis in production)
jobs = {}

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def apply_edge_detection(input_path, output_path, job_id):
    """TODO: Apply edge detection to image in background thread"""
    try:
        # do some arbitrary waiting to simulate processing
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 10
        sleep(1)

        import cv2

        img = cv2.imread(input_path)
        if img is None:
            raise Exception("Could not read the image file.")
        
        jobs[job_id]['progress'] = 30
        sleep(1)

        edges = Canny_detector(img)

        jobs[job_id]['progress'] = 50
        sleep(1)

        cv2.imwrite(output_path, edges) 

        jobs[job_id]['progress'] = 80
        sleep(1)
        jobs[job_id]['progress'] = 100
        
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['result_path'] = output_path
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        
    except Exception as e:
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['error'] = str(e)
        jobs[job_id]['completed_at'] = datetime.now().isoformat()

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/upload', methods=['POST'])
def handle_upload():
    """Upload image and start edge detection processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Generate job ID with a radnom file name
    job_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
    output_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{job_id}_edges_{filename}")
    
    # Save uploaded file
    file.save(input_path)
    
    # Create job record
    jobs[job_id] = {
        'id': job_id,
        'status': 'queued',
        'progress': 0,
        'created_at': datetime.now().isoformat(),
        'original_filename': filename,
        'input_path': input_path,
        'output_path': output_path
    }
    
    # Start background processing, use a dummy image output for now
    thread = threading.Thread(target=apply_edge_detection, args=(input_path, 'exampleout.jpg', job_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'status': 'queued',
        'message': 'Image uploaded successfully, processing started'
    }), 202

@app.route('/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """Get processing status of a job"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    response = {
        'job_id': job_id,
        'status': job['status'],
        'progress': job['progress'],
        'created_at': job['created_at']
    }
    
    if job['status'] == 'completed':
        response['download_url'] = f'/jobs/{job_id}/download'
        response['completed_at'] = job['completed_at']
    elif job['status'] == 'failed':
        response['error'] = job['error']
        response['completed_at'] = job['completed_at']
    
    return jsonify(response)

@app.route('/jobs/<job_id>/download', methods=['GET'])
def download_result(job_id):
    """Download processed image"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed yet'}), 400
    
    if not os.path.exists(job['result_path']):
        return jsonify({'error': 'Processed file not found'}), 404
    
    return send_file(
        job['result_path'],
        as_attachment=True,
        download_name=f"edges_{job['original_filename']}"
    )

@app.route('/jobs', methods=['GET'])
def list_jobs():
    """list all jobs"""
    return jsonify([{
        'job_id': job_id,
        'status': job['status'],
        'progress': job['progress'],
        'created_at': job['created_at'],
        'original_filename': job['original_filename']
    } for job_id, job in jobs.items()])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
