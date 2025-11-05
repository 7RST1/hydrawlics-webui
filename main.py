import os
import uuid
import threading
import csv
import cv2
import numpy as np
import pandas as pd
from CannyEdge import Canny_detector
from polygonOutline import draw_polygon_outlines
from datetime import datetime
from time import sleep
from io import BytesIO

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
ALLOWED_EXTENSIONS = {'png', 'jpg'}

# Sort polygons by area (smallest to largest)
def sort_polygons_by_area(contours, sort_by='area'):
    if sort_by == 'area':
        return sorted(contours, key=cv2.contourArea)
    elif sort_by == 'perimeter':
        return sorted(contours, key=cv2.arcLength)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def apply_edge_detection(input_path, output_path, job_id):
    """TODO: Apply edge detection to image in background thread"""
    try:
        # do some arbitrary waiting to simulate processing
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 10

        img = cv2.imread(input_path)
        if img is None:
            raise Exception("Could not read the image file.")
        
        jobs[job_id]['progress'] = 30

        edges = Canny_detector(img)
        contours, _ = cv2.findContours(edges.astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        jobs[job_id]['progress'] = 50

        # Keep all contours by default. Adjust MIN_CONTOUR_AREA if you want to drop tiny fragments.
        MIN_CONTOUR_AREA = 0.0
        contours = [c for c in contours if cv2.contourArea(c) > MIN_CONTOUR_AREA]

        sorted_contours = sort_polygons_by_area(contours, sort_by='area')
        jobs[job_id]['sorted_contours'] = sorted_contours
        jobs[job_id]['contour_count'] = len(sorted_contours)
        
        result = draw_polygon_outlines(img, sorted_contours)
        cv2.imwrite(output_path, result)

        areas = [cv2.contourArea(c) for c in sorted_contours]
        print(f"[{job_id}] Smallest 10 areas: {areas[:10]}")
        print(f"[{job_id}] Largest 10 areas: {areas[-10:]}")

        for c in sorted_contours[:10]:
            print(len(c), c.reshape(-1, 2)[:5])

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

# sanity check route
@app.route('/config', methods=['GET'])
def provide_config():
    return jsonify({
        'allowed_extensions': list(ALLOWED_EXTENSIONS),
    })

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
    
    # sanitize and parse slider value (default 100)
    slider_raw = request.form.get('slider')
    try:
        slider_val = int(slider_raw) if slider_raw is not None else 100
    except ValueError:
        slider_val = 100
    slider_val = max(1, min(100, slider_val))

    # Create job record
    jobs[job_id] = {
        'id': job_id,
        'status': 'queued',
        'progress': 0,
        'created_at': datetime.now().isoformat(),
        'original_filename': filename,
        'input_path': input_path,
        'output_path': output_path,
        'slider': slider_val
    }

    # log saved slider so you can verify server got it
    print(f"[{job_id}] Uploaded with slider={slider_val}")
    
    # Start background processing, use a dummy image output for now
    thread = threading.Thread(target=apply_edge_detection, args=(input_path, output_path, job_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'status': 'queued',
        'message': 'Image uploaded successfully, processing started'
    }), 202

@app.route('/jobs/<job_id>/render', methods=['GET'])
def render_with_slider(job_id):
    """Render cached contours with a slider-controlled amount (after processing)."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404

    job = jobs[job_id]
    if job.get('status') != 'completed':
        return jsonify({'error': 'Job not completed yet'}), 400

    sorted_contours = job.get('sorted_contours')
    if not sorted_contours:
        return jsonify({'error': 'No contours cached for this job'}), 400

    slider = request.args.get('slider', type=int)
    if slider is None:
        slider = job.get('slider', 100)
    # clamp slider
    slider = max(1, min(100, int(slider)))

    total = len(sorted_contours)

    # Interpret slider 1..100 as percentage of total contours.
    # slider=None or slider>=100 => show all
    if slider is None or slider >= 100:
        n = total
    elif slider <= 0:
        n = 1
    else:
        # use rounding to avoid losing contours due to truncation
        n = max(1, int(round(total * (slider / 100.0))))

    print(f"[{job_id}] Rendering with slider={slider}, n={n} of {total} contours.")

    img = cv2.imread(job['input_path'])
    if img is None:
        return jsonify({'error': 'Original image missing'}), 500    

    # sorted_contours is ascending by area. Show the largest N polygons first:
    contours_to_draw = sorted_contours[-n:] if n > 0 else []
    rendered = draw_polygon_outlines(img, contours_to_draw)
    ok, png = cv2.imencode('.png', rendered)
    if not ok:
        return jsonify({'error': 'Failed to encode image'}), 500

    return send_file(
        BytesIO(png.tobytes()),
        mimetype='image/png',
        as_attachment=False,
        download_name=f"render_{job['original_filename']}.png"
    )
 
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
        'created_at': job['created_at'],
        'contour_count': job.get('contour_count', 0),  # <-- added
        'slider': job.get('slider', 100)
    }
    
    if job['status'] == 'completed':
        # point frontend to the render endpoint and include the stored slider
        response['download_url'] = f'/jobs/{job_id}/render?slider={job.get("slider", 100)}'
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
