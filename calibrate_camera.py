import brickpi3
import time
import cv2
import numpy as np
from picamera2 import Picamera2

white = (255, 255, 255)
font = cv2.FONT_HERSHEY_SIMPLEX


# Homography for camera: CHANGE THESE NUMBERS: enter your own correspondences
# to calibrate the ground plane homography for your robot
(x1, y1, u1, v1) = (20, -10, 75, 434)
(x2, y2, u2, v2) = (20, 6, 487, 440)
(x3, y3, u3, v3) = (54, -16, 162, 170)
(x4, y4, u4, v4) = (50, 18, 533, 187)

# Form and solve linear system
A = np.array(
    [
        [x1, y1, 1, 0, 0, 0, -u1 * x1, -u1 * y1],
        [0, 0, 0, x1, y1, 1, -v1 * x1, -v1 * y1],
        [x2, y2, 1, 0, 0, 0, -u2 * x2, -u2 * y2],
        [0, 0, 0, x2, y2, 1, -v2 * x2, -v2 * y2],
        [x3, y3, 1, 0, 0, 0, -u3 * x3, -u3 * y3],
        [0, 0, 0, x3, y3, 1, -v3 * x3, -v3 * y3],
        [x4, y4, 1, 0, 0, 0, -u4 * x4, -u4 * y4],
        [0, 0, 0, x4, y4, 1, -v4 * x4, -v4 * y4],
    ]
)

b = np.array([u1, v1, u2, v2, u3, v3, u4, v4])
R, residuals, RANK, sing = np.linalg.lstsq(A, b, rcond=None)

# Build homography matrix
H = np.array([[R[0], R[1], R[2]], [R[3], R[4], R[5]], [R[6], R[7], 1]])

print("Homography")
print(H)

# Inverse homography
HInv = np.linalg.inv(H)


# Functions to transform via the forward and inverse homography
def HtransformXYtoUV(H, xin, yin):
    xvec = np.array([xin, yin, 1])
    uvec = H.dot(xvec)
    uout = uvec[0] / uvec[2]
    vout = uvec[1] / uvec[2]
    return (uout, vout)


def HtransformUVtoXY(HInv, uin, vin):
    uvec = np.array([uin, vin, 1])
    xvec = HInv.dot(uvec)
    xout = xvec[0] / xvec[2]
    yout = xvec[1] / xvec[2]
    return (xout, yout)


def drawGridOnImage(im):
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Draw a grid
    # Draw a 10cm grid from x in 0 to 80, y in -30 to 30
    # First draw lines for constant x
    for x in range(0, 90, 10):
        (xa, ya, xb, yb, xc, yc) = (x, -30, x, 30, x, 0)
        (ua, va) = HtransformXYtoUV(H, xa, ya)
        (ub, vb) = HtransformXYtoUV(H, xb, yb)
        (uc, vc) = HtransformXYtoUV(H, xc, yc)
        im = cv2.line(im, (int(ua), int(va)), (int(ub), int(vb)), white, 1)
        number = str(x)
        im = cv2.putText(
            im, number, (int(uc), int(vc)), font, 0.5, white, 1, cv2.LINE_AA
        )
    # And now lines for constant y
    for y in range(-30, 40, 10):
        (xa, ya, xb, yb) = (0, y, 80, y)
        (ua, va) = HtransformXYtoUV(H, xa, ya)
        (ub, vb) = HtransformXYtoUV(H, xb, yb)
        im = cv2.line(im, (int(ua), int(va)), (int(ub), int(vb)), white, 1)
    return im


if __name__ == "__main__":
    BP = brickpi3.BrickPi3()

    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(preview_config)

    picam2.start()

    starttime = time.time()
    for i in range(1000):
        img = picam2.capture_array()
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Convert image to HSV color space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Define range for red color in HSV
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)

        lower_red = np.array([170, 120, 70])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red, upper_red)

        # Combine masks
        mask = mask1 + mask2

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw circles around detected red objects
        for contour in contours:
            approx = cv2.approxPolyDP(
                contour, 0.02 * cv2.arcLength(contour, True), True
            )
            area = cv2.contourArea(contour)
            if len(approx) > 8 and area > 30:
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)
                img = cv2.circle(img, center, radius, (0, 255, 0), 2)

        # Draw grid on image
        img = drawGridOnImage(img)

        # Display image on interface
        cv2.imwrite("demo.jpg", img)
        print("drawImg:" + "/home/pi/prac-files/demo.jpg")
        print("Captured image", i, "at time", time.time() - starttime)

    picam2.stop()
