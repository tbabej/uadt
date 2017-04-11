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
        self.perform_user_dependent_events(OFFLINE_USER, False)
        self.perform_user_dependent_events(ONLINE_USER, True)

    def perform_user_dependent_events(self, user, delivered):
        """
        Performs all the logged actions that depend on the target user status
        (whether he's online or offline).
        """

        def delivered_suffix(event_identifier):
            return event_identifier + ('_delivered' if delivered else '_undelivered')

        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/menu_search')
        with self.mark('click_search_event'):
            s.click()

        # User search
        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/search_src_text')
        with self.mark('user_search'):
            s.send_keys(user)

        # Open conversation
        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/from')
        with self.mark('conversation_open'):
            s.click()

        # Send regular message
        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/embedded_text_editor')
        with self.mark(delivered_suffix('send_regular_message')):
            s.click()
            text = self.generator.text() + "\n"
            self.add_metadata('message_length', len(text))
            s.send_keys(text)
            self.driver.find_element_by_id('org.thoughtcrime.securesms:id/send_button').click()

        # Send picture
        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/attach_button')
        with self.mark(delivered_suffix('send_image_no_caption')):
            s.click()
            self.driver.find_element_by_id('org.thoughtcrime.securesms:id/thumbnail').click()
            self.driver.find_element_by_id('org.thoughtcrime.securesms:id/send_button').click()
            time.sleep(3)  # Extra sleep for transfer

        # Send location
        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/attach_button')
        with self.mark(delivered_suffix('send_location')):
            s.click()
            self.driver.find_element_by_id('org.thoughtcrime.securesms:id/location_button').click()
            self.driver.find_element_by_id('com.google.android.gms:id/select_marker_location').click()
            self.driver.find_element_by_id('com.google.android.gms:id/confirm_button').click()
            self.driver.find_element_by_id('org.thoughtcrime.securesms:id/send_button').click()
            time.sleep(3)  # Extra sleep for transfer

        # Send GIF
        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/attach_button')
        with self.mark(delivered_suffix('send_gif')):
            s.click()
            self.driver.find_element_by_id('org.thoughtcrime.securesms:id/giphy_button').click()
            self.driver.find_element_by_id('org.thoughtcrime.securesms:id/thumbnail').click()
            self.driver.find_element_by_id('org.thoughtcrime.securesms:id/send_button').click()
            time.sleep(2)  # Extra sleep for transfer

        # Press the back button (once to retract keyboard, once to go back)
        self.driver.press_keycode(4)
        time.sleep(2)
        self.driver.press_keycode(4)

        s = self.driver.find_element_by_id('org.thoughtcrime.securesms:id/search_close_btn')
        s.click()
