from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, FilePath
import torch
import cv2
import numpy as np
import os
import pathlib
from fastapi.responses import JSONResponse
from match_dir.src.utils.plotting import make_matching_figure
from match_dir.src.loftr import LoFTR, default_cfg
import matplotlib.pyplot as plt

import logging

# Fix WindowsPath issue
pathlib.PosixPath = pathlib.WindowsPath

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path=r'best_1280_default_hyper.pt')

# Load LoFTR model
matcher = LoFTR(config=default_cfg)
matcher.load_state_dict(torch.load("weights/outdoor_ds.ckpt")['state_dict'])
matcher = matcher.eval().cuda()

# Static output folder
STATIC_DIR = "static/output"
os.makedirs(STATIC_DIR, exist_ok=True)

# FastAPI app initialization
app = FastAPI()

class MatchRequest(BaseModel):
    image_path1: FilePath  # previous scan
    image_path2: FilePath  # new scan
    radius: int = 20  # matching radius for YOLOv5 centers

@app.post("/match_moles")
async def match_moles(input: MatchRequest):
    try:
        # Step 1: Load images
        img0_raw = cv2.imread(str(input.image_path1), cv2.IMREAD_GRAYSCALE)
        img1_raw = cv2.imread(str(input.image_path2), cv2.IMREAD_GRAYSCALE)
        
        if img0_raw is None or img1_raw is None:
            raise HTTPException(status_code=400, detail="Error reading images.")

        # Resize images for LoFTR
        img0_resized = cv2.resize(img0_raw, (640, 480))
        img1_resized = cv2.resize(img1_raw, (640, 480))

        img0_tensor = torch.from_numpy(img0_resized)[None][None].cuda() / 255.
        img1_tensor = torch.from_numpy(img1_resized)[None][None].cuda() / 255.
        batch = {'image0': img0_tensor, 'image1': img1_tensor}
        
        # Step 2: Run LoFTR to get keypoints
        with torch.no_grad():
            matcher(batch)
            mkpts0 = batch['mkpts0_f'].cpu().numpy()  # Keypoints from img0
            mkpts1 = batch['mkpts1_f'].cpu().numpy()  # Keypoints from img1

        img0_height, img0_width = img0_resized.shape
        img1_height, img1_width = img1_resized.shape

        normalized_mkpts0 = mkpts0 / [img0_width, img0_height]
        normalized_mkpts1 = mkpts1 / [img1_width, img1_height]  


        # Step 3: Run YOLOv5 to detect bounding boxes in img0
        results = model(str(input.image_path1))  # YOLO detection
        query_points = []
        bboxes = []
        for bbox in results.xyxyn[0].tolist():
            x1, y1, x2, y2 = bbox[:4]
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            query_points.append([cx, cy])
            bboxes.append([x1, y1, x2, y2])
        
        query_points = np.array(query_points)  # NumPy array for faster processing
        print(query_points)
        # Step 4: Find closest LoFTR matches for YOLO centers
        distances = np.linalg.norm(normalized_mkpts0 - query_points[:, None], axis=2)
        closest_idx = np.argmin(distances, axis=1)

        # Step 5: Expand matched points into bounding boxes based on YOLO width/height
        matched_points = normalized_mkpts1[closest_idx]

        # expanded_bboxes = []
        # for i, match in enumerate(matched_points):
        #     x1, y1, x2, y2 = bboxes[i]
        #     width = x2 - x1
        #     height = y2 - y1
        #     expanded_bboxes.append([match[0] - width // 2, match[1] - height // 2, match[0] + width // 2, match[1] + height // 2])

        # Step 6: Generate a matching figure (annotated with bounding boxes)
        color = np.random.rand(matched_points.shape[0], 3)  # Random colors for each match
        text = [f'Matches: {len(matched_points)}']

        img0_height, img0_width = img0_raw.shape
        img1_height, img1_width = img1_raw.shape

        re_scale_query = query_points * [img0_width, img0_height]
        re_scale_matched = matched_points * [img1_width, img1_height]
        
        # Visualize the matches using the `make_matching_figure` function
        fig = make_matching_figure(img0_raw, img1_raw, re_scale_query, re_scale_matched, color, re_scale_query, re_scale_matched, text)

        # Step 7: Save and return the result
        annotated_filename = "matched_image.jpg"
        annotated_path = os.path.join(STATIC_DIR, annotated_filename)
        plt.savefig(annotated_path)
        plt.close()

        return JSONResponse(content={
            "message": "Matching complete",
            "image_path": f"/static/output/{annotated_filename}",
            "matches_count": len(matched_points),
            "bboxes": bboxes,
            "query_points": query_points.tolist(),
            "matched_points": matched_points.tolist(),
            #"expanded_bboxes": expanded_bboxes
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

