import torch
import cv2
import os
from pathlib import Path
from integrated_pipeline import IntegratedMolePipeline

class FullBodyMoleAnalysisPipeline:
    def __init__(self, yolo_model_path, segmentation_model_path):
        """
        Initializes the FullBodyMoleAnalysisPipeline.

        Args:
            yolo_model_path (str): Path to the YOLOv5 model weights file.
            segmentation_model_path (str): Path to the segmentation model weights file.
        """
        # Load YOLOv5 model from PyTorch Hub
        self.yolo_model = torch.hub.load('ultralytics/yolov5', 'custom', path=yolo_model_path)
        
        # Initialize the integrated pipeline for segmentation and analysis
        self.integrated_pipeline = IntegratedMolePipeline(segmentation_model_path)

    def detect_moles(self, image_path):
        """
        Detects moles in a full-body image using the YOLOv5 model.

        Args:
            image_path (str): Path to the full-body image.

        Returns:
            list: A list of bounding boxes for detected moles.
        """
        results = self.yolo_model(image_path)
        return results.xyxyn[0].cpu().numpy()

    def crop_moles(self, image_path, detections, output_dir):
        """
        Crops detected moles from the original image and saves them.

        Args:
            image_path (str): Path to the original full-body image.
            detections (list): A list of bounding box detections.
            output_dir (str): Directory to save the cropped mole images.

        Returns:
            list: A list of dictionaries, each containing mole_id and cropped_image_path.
        """
        img = cv2.imread(image_path)
        h, w, _ = img.shape
        cropped_moles = []

        for i, det in enumerate(detections):
            x1, y1, x2, y2, conf, cls = det
            
            # Convert normalized coordinates to absolute coordinates
            abs_x1 = int(x1 * w)
            abs_y1 = int(y1 * h)
            abs_x2 = int(x2 * w)
            abs_y2 = int(y2 * h)

            # Crop the mole region
            cropped_img = img[abs_y1:abs_y2, abs_x1:abs_x2]
            
            # Save the cropped image
            mole_id = f"mole_{i+1}"
            original_filename = Path(image_path).stem
            cropped_filename = f"{original_filename}_{mole_id}.png"
            cropped_image_path = os.path.join(output_dir, cropped_filename)
            cv2.imwrite(cropped_image_path, cropped_img)
            
            cropped_moles.append({
                'mole_id': mole_id,
                'bbox': [x1, y1, x2, y2],
                'cropped_image_path': cropped_image_path
            })
            
        return cropped_moles

    def process_full_body_image(self, image_path, output_dir):
        """
        Processes a full-body image to detect, crop, and analyze all moles.

        Args:
            image_path (str): Path to the full-body image.
            output_dir (str): Directory to save cropped images and analysis results.

        Returns:
            list: A list of dictionaries, where each dictionary contains the results for a single mole.
        """
        # Step 1: Detect moles in the full-body image
        detections = self.detect_moles(image_path)
        
        if len(detections) == 0:
            return []

        # Step 2: Crop the detected moles and save them
        cropped_moles = self.crop_moles(image_path, detections, output_dir)
        
        # Step 3: Run segmentation and ABCD analysis on each cropped mole
        analysis_results = []
        for mole_info in cropped_moles:
            try:
                # Process each cropped mole image
                abcd_results = self.integrated_pipeline.process_image(
                    mole_info['cropped_image_path'],
                    save_intermediate=False # No need to save intermediate results for each mole here
                )
                
                mole_info['analysis'] = abcd_results
                analysis_results.append(mole_info)
            except Exception as e:
                # Handle cases where analysis might fail for a specific mole
                print(f"Could not analyze mole {mole_info['mole_id']}: {e}")
                mole_info['analysis'] = {'error': str(e)}
                analysis_results.append(mole_info)

        return analysis_results

# Example usage:
if __name__ == '__main__':
    # This is an example of how to use the pipeline. 
    # You would need to provide your own model paths and a test image.
    
    # Define paths
    pathlib.PosixPath = pathlib.WindowsPath
    yolo_model = 'weights/best_1280_default_hyper.pt' # Replace with your YOLO model path
    seg_model = 'weights/segment_mob_unet_.bin' # Replace with your segmentation model path
    test_image = 'test_images/full_body_test.jpg' # Replace with your test image path
    output_directory = 'full_body_output_test'

    # Create output directory if it doesn't exist
    Path(output_directory).mkdir(exist_ok=True)
    
    # Initialize and run the pipeline
    if os.path.exists(yolo_model) and os.path.exists(seg_model) and os.path.exists(test_image):
        pathlib.PosixPath = pathlib.WindowsPath
        full_body_pipeline = FullBodyMoleAnalysisPipeline(yolo_model_path=yolo_model, segmentation_model_path=seg_model)
        results = full_body_pipeline.process_full_body_image(test_image, output_dir=output_directory)
        
        # Print the results
        for result in results:
            print(f"--- Mole ID: {result['mole_id']} ---")
            print(f"Bounding Box: {result['bbox']}")
            print(f"Cropped Image: {result['cropped_image_path']}")
            if 'error' in result['analysis']:
                print(f"Analysis Error: {result['analysis']['error']}")
            else:
                print(f"ABCD Metrics: {result['analysis']}")
            print("\n")
    else:
        print("Please ensure model weights and test image paths are correct.")
