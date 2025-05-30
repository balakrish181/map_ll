import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys 
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))


def compute_asymmetry(binary_image):
    moments = cv2.moments(binary_image)

    if moments["m00"] == 0:
        return 0, None, None, None  # Consistent return type

    cx = int(moments["m10"] / moments["m00"])
    cy = int(moments["m01"] / moments["m00"])

    mu20 = moments["mu20"] / moments["m00"]
    mu02 = moments["mu02"] / moments["m00"]
    mu11 = moments["mu11"] / moments["m00"]

    angle = 0.5 * np.arctan2(2 * mu11, mu20 - mu02)

    rows, cols = binary_image.shape
    M = cv2.getRotationMatrix2D((cx, cy), np.degrees(angle), 1)
    rotated = cv2.warpAffine(binary_image, M, (cols, rows))

    flipped = cv2.flip(rotated, 1)
    diff = cv2.absdiff(rotated, flipped)
    asymmetry_score = np.sum(diff) / np.sum(rotated)

    return asymmetry_score, rotated, flipped, diff



    """
        There is an issue here! Flipping is not happening on the lesion level, but, on the rotated image! ideally, we need to flip along prinicpal axis of the lesion
    """





# Load your binary lesion image (white = lesion, black = background)
binary_img = cv2.imread("test_images/image_mask.png", cv2.IMREAD_GRAYSCALE)
#_, binary_img = cv2.threshold(binary_img, 127, 255, cv2.THRESH_BINARY)

score, rotated, flipped, diff = compute_asymmetry(binary_img)

print(f"Asymmetry Score: {score:.4f}")

# Show results
plt.figure(figsize=(12, 4))
plt.subplot(1, 4, 1)
plt.title("Original")
plt.imshow(binary_img, cmap='gray')

plt.subplot(1, 4, 2)
plt.title("Rotated")
plt.imshow(rotated, cmap='gray')

plt.subplot(1, 4, 3)
plt.title("Flipped")
plt.imshow(flipped, cmap='gray')

plt.subplot(1, 4, 4)
plt.title("Difference")
plt.imshow(diff, cmap='hot')
plt.show()
