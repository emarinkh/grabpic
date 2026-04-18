cat > README.md << 'EOF'
# Grabpic - Face Recognition Image Retrieval API

## Build & Run
```bash
pip install flask opencv-python numpy
python app.py
```

## API Endpoints

### POST /api/index
Index all images in `images/` folder
```bash
curl -X POST http://localhost:5000/api/index
```

### POST /api/auth
Authenticate with selfie
```bash
curl -X POST -F "file=@selfie.jpg" http://localhost:5000/api/auth
```

### GET /api/images/<grab_id>
Get all images for user
```bash
curl http://localhost:5000/api/images/grab_d8531a
```

### GET /api/stats
System stats
```bash
curl http://localhost:5000/api/stats
```

## Architecture
- Image hashing for face recognition
- In-memory database with grab_id mapping
- One image → Many grab_ids (multiple faces)
- Selfie authentication
- Full error handling
EOF
