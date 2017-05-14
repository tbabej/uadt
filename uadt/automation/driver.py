import cv2
import numpy
import datetime
import random
import os

from appium import webdriver


class ImageRecognitionDriver(webdriver.Remote):
    """
    Extends the Driver with image recognition methods.
    """

    def click_by_image(self, path):
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
        success = self.get_screenshot_as_file(screenshot_path)
        if not success:
            raise Exception("Could not obtain screenshot")

        # Load both images
        screen = cv2.imread(screenshot_path)
        selection = cv2.imread(path)

        # Find the match
        result = cv2.matchTemplate(screen, selection, cv2.TM_CCOEFF_NORMED)
        best_coordinates = numpy.unravel_index(result.argmax(), result.shape)

        # Compute the midpoint of the selection
        coordinates = (
            int(best_coordinates[1] + selection.shape[1] / 2.0),
            int(best_coordinates[0] + selection.shape[0] / 2.0),
        )

        # Tap the coordinates
        self.tap([coordinates])
