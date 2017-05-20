import random
import time

from appium import webdriver

from uadt.automation.scenario import Scenario

ONLINE_USER = "Kram"
OFFLINE_USER = "Babej"


class SignalScenario(Scenario):
    """
    A testing scenario for Signal messagenger.

    Initial: main_screen
    Final: main_screen
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

        self.user = user
        self.delivered = delivered
        self.steps_by_random_walk(length=50)

    def delivered_suffix(self, event_identifier):
        return event_identifier + ('_delivered' if self.delivered else '_undelivered')

    def step_user_search(self):
        """
        Searches for the user in conversation list (main screen).

        Start: main_screen
        End:   filtered_screen
        """

        s = self.find('org.thoughtcrime.securesms:id/menu_search')
        with self.mark('click_search_event'):
            self.click(s)

        s = self.find('org.thoughtcrime.securesms:id/search_src_text')
        with self.mark('user_search'):
            s.send_keys(self.user)

    def step_open_conversation(self):
        """
        Opens the conversation with the first user in the conversation list.
        There should be only one, since this step is preceded by filtering by name.

        Start: filtered_screen
        End:   conversation
        """

        s = self.find('org.thoughtcrime.securesms:id/from')
        with self.mark('conversation_open'):
            self.click(s)

    def step_send_regular_message(self):
        """
        Sends a message in the currently open conversation.

        Start: conversation
        End:   conversation
        Weight: 50
        """

        s = self.find('org.thoughtcrime.securesms:id/embedded_text_editor')
        with self.mark(self.delivered_suffix('send_regular_message')):
            self.click(s)
            text = self.generator.text()
            self.add_metadata('message_length', len(text))
            s.send_keys(text)

            self.click('org.thoughtcrime.securesms:id/send_button')

    def step_send_picture(self):
        """
        Sends a randomly selected picture in the currently open conversation.

        Start: conversation
        End:   conversation
        Weight: 20
        """

        s = self.find('org.thoughtcrime.securesms:id/attach_button')
        with self.mark(self.delivered_suffix('send_image_no_caption')):
            self.click(s)
            self.click(
                "//android.widget.FrameLayout[@index='{0}']"
                "/android.widget.ImageView".format(random.randint(0, 4))
            )

            self.click('org.thoughtcrime.securesms:id/send_button')
            time.sleep(3)  # Extra sleep for transfer

    def step_send_location(self):
        """
        Send current location in the currently open conversation.

        Start: conversation
        End:   conversation
        Weight: 10
        """

        s = self.find('org.thoughtcrime.securesms:id/attach_button')
        with self.mark(self.delivered_suffix('send_location')):
            self.click(s)
            self.click('org.thoughtcrime.securesms:id/location_button')
            self.click('com.google.android.gms:id/select_marker_location')
            self.click('com.google.android.gms:id/confirm_button')

            self.click('org.thoughtcrime.securesms:id/send_button')
            time.sleep(3)  # Extra sleep for transfer

    def step_send_gif(self):
        """
        Send the first offered GIF from GIPHY in the currently open conversation.

        Start: conversation
        End:   conversation
        Weight: 10
        """

        s = self.find('org.thoughtcrime.securesms:id/attach_button')
        with self.mark(self.delivered_suffix('send_gif')):
            self.click(s)
            self.click('org.thoughtcrime.securesms:id/giphy_button')
            self.click('org.thoughtcrime.securesms:id/thumbnail')

            self.click('org.thoughtcrime.securesms:id/send_button')
            time.sleep(2)  # Extra sleep for transfer

    def step_leave_conversation(self):
        """
        Send the first offered GIF from GIPHY in the currently open conversation.

        Start: conversation
        End:   main_screen
        Weight: 0
        """

        # Press the back button (once to retract keyboard, once to go back)
        self.driver.press_keycode(4)
        time.sleep(2)
        self.driver.press_keycode(4)

        self.click('org.thoughtcrime.securesms:id/search_close_btn')
