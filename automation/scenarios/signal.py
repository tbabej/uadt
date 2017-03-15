from plugins import Plugin

from appium import webdriver

class SignalScenario(Plugin):
    """
    A testing scenario for Signal messagenger.
    """

    identifier = 'signal'

    app_package = "org.thoughtcrime.securesms"
    app_activity = "org.thoughtcrime.securesms.ConversationListActivity"

    def run(self):
        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/menu_search')

        with self.capture('click_search_event'):
            s.click()

            s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/search_src_text')

        with self.capture('user_search'):
            s.send_keys("Babej")

            s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/from')

        with self.capture('conversation_open'):
            s.click()

            s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/embedded_text_editor')

        with self.capture('send_regular_message'):
            s.click()
            s.send_keys("This is an automated message. Please keep calm.\n")
            self.driver.find_element_by_id('org.thoughtcrime.securesms:id/send_button').click()
