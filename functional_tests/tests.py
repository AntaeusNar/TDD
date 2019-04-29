"""Functional Tests === Acceptance Test === End-to-End test
These are our 'black box tests'
each section should follow an human readable 'user story'
"""

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import re

MAX_WAIT = 10


class NewVisitorTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def helper_restart_browser(self):
        self.tearDown()
        self.setUp()

    def helper_wait_for_row_in_table(self, row_text, table_id='id_list_table'):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id(table_id)
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (WebDriverException, NoSuchElementException) as e:
                if time.time() - start_time > MAX_WAIT:
                    self.fail(e)
                time.sleep(0.5)
            except AssertionError as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def test_layout_and_styling(self):
        # Edith goes to the home page
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # she notices the input box is nicely centered
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x']+inputbox.size['width']/2,
            512,
            delta=10
        )

        # She starts a new list and sees the input is nicely centered there to
        inputbox.send_keys('testing')
        inputbox.send_keys(Keys.ENTER)
        self.helper_wait_for_row_in_table('1: testing')
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )

    def test_can_start_a_list_for_one_user(self):
        # Edith has heard about a cool new online to-do app. She goes
        # to check out its homepage
        self.browser.get(self.live_server_url)

        # She notices the page title and header mention to-do lists
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        # She is invited to enter a to-do item straight away
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        # She types "Buy peacock feathers" into a text box (Edith's hobby
        # is tying fly-fishing lures)
        inputbox.send_keys('Buy peacock feathers')

        # When she hits enter, the page updates, and now the page lists
        # "1: Buy peacock feathers" as an item in a to-do list
        inputbox.send_keys(Keys.ENTER)
        self.helper_wait_for_row_in_table('1: Buy peacock feathers', 'id_list_table')

        # There is still a text box inviting her to add another item. She
        # enters "Use peacock feathers to make a fly" (Edith is very methodical)
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Use peacock feathers to make a fly')
        inputbox.send_keys(Keys.ENTER)

        # The page updates again, and now shows both items on her list
        self.helper_wait_for_row_in_table('1: Buy peacock feathers', 'id_list_table')
        self.helper_wait_for_row_in_table('2: Use peacock feathers to make a fly', 'id_list_table')

        # Satisfied, she leaves her computer to go check her worms

    def test_multiple_users_can_start_lists_at_different_urls(self):
        # Edith wonders whether the site will remember her list.
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)
        self.helper_wait_for_row_in_table('1: Buy peacock feathers')

        # She rushes back to the computer to see if there is a unique URL!
        # Then she sees that the site has generated a unique URL for her.
        pattern = '(/lists/.+)'
        ending_url = re.search(pattern, self.browser.current_url)
        edith_list_url = ending_url.group(1)
        self.assertRegex(edith_list_url, '/lists/.+')

        # Now a new user, Francis, comes along to the site.

        # We use a new browser session to make sure the no information of Edith's is
        # coming through from cookies etc
        self.browser.quit()
        self.browser = webdriver.Firefox()

        # Francis visits the home page. There is no sign of Edith's list
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertNotIn('make a fly', page_text)

        # Francis starts a new list by entering a new item.
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Buy milk')
        inputbox.send_keys(Keys.ENTER)
        self.helper_wait_for_row_in_table('1: Buy milk')

        # Francis gets his own url
        pattern = '(/lists/.+)'
        ending_url = re.search(pattern, self.browser.current_url)
        francis_list_url = ending_url.group(1)
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        # Again, there is no trace of Edith's list
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertIn('Buy milk', page_text)

        self.fail('Finish the functional test!')
