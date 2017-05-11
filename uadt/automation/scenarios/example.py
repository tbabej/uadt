from appium import webdriver

from uadt.automation.scenario import Scenario


class TestScenario(Scenario):
    """
    A testing scenario for educational purposes.
    """

    identifier = 'test'

    app_package = "com.android.chrome"
    app_activity = "com.google.android.apps.chrome.Main"

    no_reset = False

    def run(self):
        s = self.driver.find_element_by_id('com.android.chrome:id/search_box_text')

        with self.mark('click_event'):
            s.click()

        s = self.driver.find_element_by_id('com.android.chrome:id/url_bar')

        with self.mark('website_visit'):
            s.send_keys("fi.muni.cz\n")
