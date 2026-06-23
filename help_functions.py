import cv2
from PIL import Image as PILImage
from anomalib.utils.post_processing import superimpose_anomaly_map
import numpy as np

def makeOutlineImage(path, pred_mask, image):
    # 1. Prepare your data
    # Ensure pred_mask is uint8 (OpenCV needs this for contour detection)
    mask_uint8 = (pred_mask > 0.5).astype(np.uint8) 

    # Load or use your original image (ensure it's a numpy array)
    # If it's a PIL image, use: original_img = np.array(image)
    original_img_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # 2. Find the contours (the outline)
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 3. Draw the contours on the original image
    # Parameters: (image, contours, contour_index (-1 for all), color (BGR), thickness)
    thickness = 1
    red_color = (0, 0, 255) # Red in BGR
    cv2.drawContours(original_img_bgr, contours, -1, red_color, thickness)

    # 4. Convert back to RGB for displaying or saving
    final_image = cv2.cvtColor(original_img_bgr, cv2.COLOR_BGR2RGB)
    
    PILImage.fromarray(final_image).save(path)

def makeHeatMap(path, anomaly_map, image):
    heat_map = superimpose_anomaly_map(anomaly_map=anomaly_map, image=image, normalize=True)
    PILImage.fromarray(heat_map).save(path)