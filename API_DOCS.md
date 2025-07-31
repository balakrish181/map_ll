# Mole Analysis API Documentation

This document provides detailed information about the Mole Analysis API endpoints, request/response formats, and usage examples.

## Base URL
```
http://<hostname>:5001
```

## Authentication
Currently, the API does not require authentication for local development. For production deployments, consider adding API key authentication.

## Endpoints

### 1. Single Mole Analysis

Analyze a single mole image and return ABCD scores and processed images.

**Endpoint**: `POST /analyze`

**Headers**:
```
Content-Type: multipart/form-data
```

**Request Body**:
- `file` (required): Image file (JPG, PNG, or JPEG)

**cURL Example**:
```bash
curl -X POST http://localhost:5001/analyze \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/mole.jpg"
```

**Python Example**:
```python
import requests

url = "http://localhost:5001/analyze"
files = {'file': open('path/to/your/mole.jpg', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

**Success Response (200 OK)**:
```json
{
  "metrics": {
    "Asymmetry": 0.12,
    "Border": 0.85,
    "Colour": 5.2,
    "Diameter": 8.5,
    "Raw_Metrics": {
      "asymmetry_score": 0.12,
      "border_irregularity": 0.85,
      "color_variance": 5.2,
      "diameter_mm": 8.5
    }
  },
  "original_image": "/uploads/20230731_1345_mole.jpg",
  "mask_image": "/outputs/20230731_1345_mole_mask.png",
  "overlay_image": "/outputs/20230731_1345_mole_overlay.png"
}
```

---

### 2. Full Body Analysis

Analyze a full-body image to detect and analyze multiple moles.

**Endpoint**: `POST /analyze_full_body`

**Headers**:
```
Content-Type: multipart/form-data
```

**Request Body**:
- `file` (required): Full-body image file (JPG, PNG, or JPEG)

**cURL Example**:
```bash
curl -X POST http://localhost:5001/analyze_full_body \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/full_body.jpg"
```

**Python Example**:
```python
import requests

url = "http://localhost:5001/analyze_full_body"
files = {'file': open('path/to/your/full_body.jpg', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

**Success Response (200 OK)**:
```json
{
  "analysis": [
    {
      "mole_id": 1,
      "position": {"x": 123, "y": 456, "width": 50, "height": 50},
      "scores": {
        "Asymmetry": 0.15,
        "Border": 0.82,
        "Colour": 4.8,
        "Diameter": 7.2
      },
      "image_path": "/full_body_output/20230731_1345_mole_1.png"
    }
  ],
  "overlay_image": "/full_body_output/20230731_1345_overlay.jpg"
}
```

---

### 3. Access Uploaded Files

Retrieve processed images and analysis results.

**Endpoint**: `GET /<type>/<filename>`

**URL Parameters**:
- `type`: Type of file (`uploads`, `outputs`, or `full_body_output`)
- `filename`: Name of the file to retrieve

**Examples**:
```
GET /uploads/20230731_1345_mole.jpg
GET /outputs/20230731_1345_mole_mask.png
GET /full_body_output/20230731_1345_overlay.jpg
```

**cURL Example**:
```bash
curl -O http://localhost:5001/outputs/20230731_1345_mole_mask.png
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "No file uploaded"
}
```

### 400 Bad Request (Invalid File Type)
```json
{
  "error": "Invalid file type"
}
```

### 500 Internal Server Error
```json
{
  "error": "Error message describing the issue"
}
```

## Rate Limiting
By default, the API does not implement rate limiting. For production deployments, consider adding rate limiting to prevent abuse.

## CORS
CORS is enabled for all origins in development. For production, restrict this to trusted domains.

## Deployment Notes

### Local Development
```bash
conda activate mob
python app.py
```

### Production Deployment
1. Use a production WSGI server (e.g., Gunicorn, uWSGI)
2. Set up Nginx/Apache as a reverse proxy
3. Enable HTTPS using Let's Encrypt
4. Set appropriate file permissions for upload directories

### Environment Variables
```bash
FLASK_APP=app.py
FLASK_ENV=production  # or development
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
FULL_BODY_OUTPUT_FOLDER=full_body_output
```

## Testing
You can test the API using tools like:
- cURL
- Postman
- Python requests library
- Web browser (for GET requests)

## Support
For support, please contact [Your Support Email] or open an issue in the repository.
