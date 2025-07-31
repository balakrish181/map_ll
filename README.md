# Mole Analysis Application

A Flask-based web application for analyzing skin lesions using deep learning models. The application provides ABCD (Asymmetry, Border, Color, Diameter) scoring for mole assessment and full-body mole detection.

## Features

- **Single Mole Analysis**: Upload and analyze individual mole images
- **Full Body Analysis**: Process full-body images to detect and analyze multiple moles
- **ABCD Scoring**: Comprehensive analysis of Asymmetry, Border, Color, and Diameter
- **Interactive Web Interface**: User-friendly interface for uploading and viewing results
- **RESTful API**: Programmatic access to analysis functionality

## System Architecture

### Main Components

1. **Flask Web Server** (`app.py`)
   - Handles HTTP requests and responses
   - Manages file uploads and serving analysis results
   - Provides REST API endpoints

2. **Integrated Pipeline** (`integrated_pipeline.py`)
   - Combines segmentation and ABCD analysis
   - Processes individual mole images
   - Handles result formatting and saving

3. **Full Body Pipeline** (`full_body_pipeline.py`)
   - Processes full-body images
   - Uses YOLOv5 for mole detection
   - Applies segmentation and analysis to detected moles

4. **Mole Analysis** (`metrics/merged_improved_metrics.py`)
   - Implements ABCD scoring algorithms
   - Handles image processing and feature extraction

## API Endpoints

### Single Mole Analysis
- `POST /analyze`
  - Accepts: Image file upload
  - Returns: Analysis results including ABCD scores and processed images

### Full Body Analysis
- `POST /analyze_full_body`
  - Accepts: Full-body image upload
  - Returns: Analysis of all detected moles with locations and scores

### File Access
- `GET /uploads/<filename>`: Access uploaded original images
- `GET /outputs/<filename>`: Access processed mole analysis results
- `GET /full_body_output/<filename>`: Access full-body analysis results

## Workflow

### Single Mole Analysis Flow
1. User uploads an image of a mole
2. Server saves the image to the uploads directory
3. `IntegratedMolePipeline` processes the image:
   - Applies segmentation using MobileUNETR model
   - Extracts ABCD features
   - Calculates risk scores
4. Results are saved and returned to the user

### Full Body Analysis Flow
1. User uploads a full-body image
2. Server saves the image
3. `FullBodyMoleAnalysisPipeline` processes the image:
   - Uses YOLOv5 to detect moles
   - For each detected mole:
     - Extracts the region of interest
     - Applies segmentation
     - Performs ABCD analysis
4. Results are compiled and returned

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Mole-mapping-app
   ```

2. Create and activate a conda environment:
   ```bash
   conda create -n mob python=3.10
   conda activate mob
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download model weights (place in `weights/` directory):
   - `segment_mob_unet_.bin` - Segmentation model
   - `best_1280_default_hyper.pt` - YOLOv5 detection model

## Running the Application

1. Start the Flask development server:
   ```bash
   conda activate mob
   python app.py
   ```

2. Access the web interface at `http://localhost:5001`

## Configuration

The application can be configured by modifying the following in `app.py`:
- `UPLOAD_FOLDER`: Directory for uploaded images
- `OUTPUT_FOLDER`: Directory for processed mole images
- `FULL_BODY_OUTPUT_FOLDER`: Directory for full-body analysis results
- Model paths in the pipeline initializations

## Dependencies

- Python 3.10+
- Flask
- PyTorch
- OpenCV
- NumPy
- MONAI
- YOLOv5
- Other dependencies listed in `requirements.txt`

## License

[Specify License]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

[Your Contact Information]
