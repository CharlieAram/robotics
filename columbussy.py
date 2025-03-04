from probalistic_motion import Robot, motion
from calibrate_camera import HInv, HtransformUVtoXY, cv2, np, Picamera2


class Columbussy(Robot):
    def __init__(
        self, x: float, y: float, theta: float, left_lim: float, right_lim: float
    ):
        super().__init__(x, y, theta)
        self.left_lim = left_lim
        self.right_lim = right_lim
        self.picam2 = Picamera2()
        self.picam2.start()
        import atexit

        atexit.register(self.picam2.stop)

    def get_obstacles(self):
        img = self.picam2.capture_array()

        # Convert to HSV colour space
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Apply colour thresholding: for red this is done in two steps
        # lower mask (0-10)
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([10, 255, 255])
        mask0 = cv2.inRange(hsv, lower_red, upper_red)
        # upper mask (170-180)
        lower_red = np.array([170, 50, 50])
        upper_red = np.array([180, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)
        # join my masks
        mask = mask0 + mask1
        # Calculate connected components: colour thresholded "blob" regions
        output = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32F)
        (numLabels, labels, stats, centroids) = output

        # Find the properties of the detected blobs
        for i in range(1, numLabels):
            area = stats[i, cv2.CC_STAT_AREA]
            (cu, cv) = centroids[i]
            # Print out the properties of blobs above a certain size
            if area > 150:
                yield HtransformUVtoXY(HInv, cu, cv)

    def get_dangerous_obstacles(self):
        for obs in self.get_obstacles():
            x, y = obs
            if self.left_lim < x < self.right_lim:
                yield obs

    def identify_closest_threat(self):
        obs = list(self.get_dangerous_obstacles())
        if not obs:
            return None
        return min(obs, key=lambda x: (x[0] ** 2 + x[1] ** 2) ** 0.5)

    @motion
    def navigate(self):
        avoid = self.identify_closest_threat()
        if avoid:
            print("Avoiding obstacle at", avoid)
            x, y = avoid
            if self.left_lim < x < self.right_lim:
                if x > 0:
                    self.rotate(-1)
                else:
                    self.rotate(1)
        self.move_forward(5)


if __name__ == "__main__":
    robot = Columbussy(0, 0, 0, -7.63, 6.54)
    while True:
        print("nav")
        robot.navigate()
