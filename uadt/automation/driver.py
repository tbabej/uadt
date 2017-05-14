import cv2
import numpy
import datetime
import random
import time
import os

from appium import webdriver


class ImageRecognitionDriver(webdriver.Remote):
    """
    Extends the Driver with image recognition methods.
    """

    def click_by_image(self, path, required_confidence=0.7):
        """
        Clicks on the coordinates that correspond to the given subimage in the
        current display screen.
        """

        # Generate the screenshot path
        random_suffix = random.randint(10000, 99999)
        datetime_format = '%Y%m%d_%H%M%S_{0}.png'.format(random_suffix)
        screenshot_path = os.path.join(
            '/tmp',
            datetime.datetime.now().strftime(datetime_format)
        )

        # Obtain screenshot
        time.sleep(2)
        success = self.get_screenshot_as_file(screenshot_path)
        if not success:
            raise Exception("Could not obtain screenshot")

        # Attempt to remove the screenshot file
        try:
            os.remove(screenshot_path)
        except OSError:
            pass

        # Load both images
        screen = cv2.imread(screenshot_path)
        selection = cv2.imread(path)

        # Find the match
        result = cv2.matchTemplate(screen, selection, cv2.TM_CCOEFF_NORMED)
        __, max_confidence, __, max_location = cv2.minMaxLoc(result)

        if max_confidence >= required_confidence:
            # Compute the midpoint of the selection
            coordinates = (
                int(max_location[1] + selection.shape[1] / 2.0),
                int(max_location[0] + selection.shape[0] / 2.0),
            )

            # Tap the coordinates
            self.tap([coordinates])
        else:
            raise Exception("Could not find the required subimage with "
                            "sufficient confidence. Obtained confidence: {0}"
                            .format(max_confidence))
