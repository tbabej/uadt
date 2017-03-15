from plugins import Plugin

from appium import webdriver

class TestScenario(Plugin):
    """
    A testing scenario for educational purposes.
    """

    identifier = 'test'

    def run(self):
        desired_caps = {
            'platformName': 'Android',
            'platformVersion': '7.1',
            'deviceName': 'Nexus 5X',
            'appPackage': 'com.android.chrome',
            'appActivity': 'com.google.android.apps.chrome.Main',
            'newCommandTimeout': '50000',
            'autoLaunch' : True
        }

        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        driver.implicitly_wait(60)

        s = driver.find_element_by_id('com.android.chrome:id/search_box_text')

        with self.capture('click_event'):
            s.click()

        s = driver.find_element_by_id('com.android.chrome:id/url_bar')

        with self.capture('website_visit'):
            s.send_keys("fi.muni.cz\n")
