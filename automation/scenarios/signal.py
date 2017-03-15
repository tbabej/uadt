import time

from appium import webdriver

from plugins import Plugin

ONLINE_USER = "Kram"
OFFLINE_USER = "Babej"

class SignalScenario(Plugin):
    """
    A testing scenario for Signal messagenger.
    """

    identifier = 'signal'

    app_package = "org.thoughtcrime.securesms"
    app_activity = "org.thoughtcrime.securesms.ConversationListActivity"

    def run(self):
        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/menu_search')

        with self.mark('click_search_event'):
            s.click()

        # User search
        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/search_src_text')
        with self.mark('user_search'):
            s.send_keys(OFFLINE_USER)

        # Open conversation
        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/from')
        with self.mark('conversation_open'):
            s.click()

        # Send regular message
        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/embedded_text_editor')
        with self.mark('send_regular_message'):
            s.click()
            s.send_keys("This is an automated message. Please keep calm.\n")
            self.driver.find_element_by_id('org.thoughtcrime.securesms:id/send_button').click()

        # Send picture
        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/attach_button')
        with self.mark('send_image_no_caption'):
            s.click()
            self.driver.find_element_by_id('org.thoughtcrime.securesms:id/thumbnail').click()
            self.driver.find_element_by_id('org.thoughtcrime.securesms:id/send_button').click()
            time.sleep(3)  # Extra sleep for transfer
