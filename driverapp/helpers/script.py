import os
import time
import json
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
from driverapp import db, MEDIA_FOLDER
from lxml import etree
import re
import traceback
from driverapp.models import Scan, Events, ScanEvents


class NessusDriverScript:

    def __init__(self, scan):
        self.scan = scan
        self.path_to_chromedriver = '/home/mani/work/Elliott/nessus-driver/chromedriver'
        self.prefs = {"download.default_directory": MEDIA_FOLDER}
        self.options = Options()
        self.options.add_argument("window-size=1420,1080")
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_experimental_option("prefs", self.prefs)
        self.display = Display(visible=0, size=(1420, 1080))

    def get_status(self):
        before = os.listdir(MEDIA_FOLDER)

        display = self.display
        display.start()
        driver = webdriver.Chrome(
            executable_path=self.path_to_chromedriver,
            chrome_options=self.options)

        # Target website name
        driver.get(self.scan.nessus_url)

        try:
            username_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div/form/div[1]/input"))
            )
            password_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div/form/div[2]/input"))
            )
            username_input.clear()
            username_input.send_keys(self.scan.nessus_username)

            password_input.clear()
            password_input.send_keys(self.scan.nessus_password)

            login_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div/form/button"))
            )

            login_button.click()

            time.sleep(15)
        except Exception as e:
            error = "unable to login in nessus server either wrong url ({}) "\
                "or wrong xpath supplied".format(self.scan.nessus_url)
            scanEvent = ScanEvents.query.filter_by(
                scan_id=self.scan.id).first()
            if scanEvent:
                scanEvent.scan_event_history = error
            else:
                scanEvent = ScanEvents(scan_id=self.scan.id, 
                    event_id=int(self.scan.event_id), 
                    scan_event_history=error
                    )
                db.session.add(scanEvent)
            self.scan.scan_message = 'Scan is Running'
            self.scan.status = 'Running'
            db.session.commit()
            driver.close()
            driver.quit()
            display.stop()
            return False

        try:
            table = driver.\
                find_element_by_xpath('//*[@id="DataTables_Table_0"]/tbody')
            td_regex = '// tr/td' + "[contains(text(), '" + self.scan.scan_name + "')]"
            td = table.find_element_by_xpath(td_regex)

            td.click()
        except Exception as e:
            error = 'unable to find the Running scan, wrong xpth '\
                'supplied(//*[@id="DataTables_Table_0"]/tbody)'
            scanEvent = ScanEvents.query.filter_by(scan_id=self.scan.id).first()
            if scanEvent:
                scanEvent.scan_event_history = error
            else:
                scanEvent = ScanEvents(scan_id=self.scan.id, 
                    event_id=int(self.scan.event_id), 
                    scan_event_history=error
                    )
                db.session.add(scanEvent)
            self.scan.scan_message = 'Scan is Running'
            self.scan.status = 'Running'
            db.session.commit()
            driver.close()
            driver.quit()
            display.stop()
            return False

        try:
            status = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="content"]/section/div[1]/div[2]/span[4]'))
            )
        except Exception as e:
            error = 'unable to find the scan Status, wrong xpath '\
                'supplied(//*[@id="content"]/section/div[1]/div[2]/span[4])'
            scanEvent = ScanEvents.query.filter_by(scan_id=self.scan.id).first()
            if scanEvent:
                scanEvent.scan_event_history = error
            else:
                scanEvent = ScanEvents(scan_id=self.scan.id, 
                    event_id=int(self.scan.event_id), 
                    scan_event_history=error
                    )
                db.session.add(scanEvent)
            self.scan.scan_message = 'Scan is Running'
            self.scan.status = 'Running'
            db.session.commit()
            driver.close()
            driver.quit()
            display.stop()
            return False

        if status.text == "Completed":
            self.scan.scan_message = 'Scan is Completed'
            try:
                export = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="export"]'))
                )
                export.click()
            except Exception as e:
                error = 'unable to export nessus, wrong xpth supplied(//*[@id="export"])'
                scanEvent = ScanEvents.query.filter_by(scan_id=self.scan.id).first()
                if scanEvent:
                    scanEvent.scan_event_history = error
                else:
                    scanEvent = ScanEvents(scan_id=self.scan.id, 
                            event_id=int(self.scan.event_id), 
                            scan_event_history=error
                        )
                    db.session.add(scanEvent)
                self.scan.scan_message = 'Scan is Running'
                self.scan.status = 'Running'
                db.session.commit()
                driver.close()
                driver.quit()
                display.stop()
                return False

            try:
                nessus = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="export"]/ul/li[1]'))
                )
                nessus.click()
                time.sleep(20)
            except Exception as e:
                error = 'unable to download nessus file, wrong xpath '\
                    'supplied(//*[@id="export"]/ul/li[1])'
                scanEvent = ScanEvents.query.filter_by(scan_id=self.scan.id).first()
                if scanEvent:
                    scanEvent.scan_event_history = error
                else:
                    scanEvent = ScanEvents(scan_id=self.scan.id, 
                        event_id=int(self.scan.event_id), 
                        scan_event_history=error
                        )
                    db.session.add(scanEvent)
                self.scan.scan_message = 'Scan is Running'
                self.scan.status = 'Running'
                db.session.commit()
                driver.close()
                driver.quit()
                display.stop()
                return False

            after = os.listdir(MEDIA_FOLDER)

            change = set(after) - set(before)

            if len(change) == 1:
                file_name = change.pop()
                self.scan.result = MEDIA_FOLDER + '/' + str(file_name)
                self.scan.status = status.text
                self.scan.scan_message = 'Scan is Completed'
                scanEvent = ScanEvents.query.filter_by(scan_id=self.scan.id).first()
                success_msg = 'Scan Completed Successfully'
                if scanEvent:
                    scanEvent.scan_event_history = success_msg
                else:
                    scanEvent = ScanEvents(scan_id=self.scan.id, 
                        event_id=int(self.scan.event_id), 
                        scan_event_history=success_msg
                        )
                    db.session.add(scanEvent)

                db.session.commit()

            time.sleep(10)
            driver.close()
            driver.quit()
            display.stop()
            return True
        else:
            self.scan.status = status.text
            self.scan.scan_message = 'Scan is Running'
            db.session.commit()
            time.sleep(10)
            driver.close()
            driver.quit()
            display.stop()
            return False

    def add_data(self):

        display = self.display
        display.start()

        driver = webdriver.Chrome(executable_path=self.path_to_chromedriver,
                                chrome_options=self.options)

        # Target website name
        if self.scan.nessus_url:
            url = self.scan.nessus_url
            driver.get(url)
        else:
            error = "Nessus Url not found"
            scanEvent = ScanEvents.query.filter_by(scan_id=self.scan.id).first()
            if scanEvent:
                scanEvent.scan_event_history = error
            else:
                scanEvent = ScanEvents(scan_id=self.scan.id, 
                            event_id=int(self.scan.event_id), 
                            scan_event_history=error
                            )
                db.session.add(scanEvent)
            self.scan.scan_message = 'Add Scan Failed'
            self.scan.status = 'Failed'
            db.session.commit()
            driver.close()
            driver.quit()
            display.stop()
            return False

        try:
            username_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div/form/div[1]/input"))
            )
            password_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div/form/div[2]/input"))
            )

            username_input.clear()
            username_input.send_keys(self.scan.nessus_username)

            password_input.clear()
            password_input.send_keys(self.scan.nessus_password)

            login_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div/form/button"))
            )

            login_button.click()

            time.sleep(10)

        except Exception as e:
            error = "unable to login in nessus server either wrong url ({}) or "\
                "wrong xpath supplied".format(self.scan.nessus_url)
            scanEvent = ScanEvents.query.filter_by(scan_id=self.scan.id).first()
            if scanEvent:
                scanEvent.scan_event_history = error
            else:
                scanEvent = ScanEvents(scan_id=self.scan.id, 
                            event_id=int(self.scan.event_id), 
                            scan_event_history=error
                            )
                db.session.add(scanEvent)
            self.scan.scan_message = 'Add Scan Failed'
            self.scan.status = 'Failed'
            db.session.commit()
            driver.close()
            driver.quit()
            display.stop()
            return False

        try:
            driver.find_element_by_xpath('//*[@id="titlebar"]/a[1]').click()
        except Exception as e:
            error = 'unable to find "New Scan" button to add scan wrong xpath supplied'
            scanEvent = ScanEvents.query.filter_by(scan_id=self.scan.id).first()
            if scanEvent:
                scanEvent.scan_event_history = error
            else:
                scanEvent = ScanEvents(scan_id=self.scan.id, 
                            event_id=int(self.scan.event_id), 
                            scan_event_history=error
                            )
                db.session.add(scanEvent)
            self.scan.scan_message = 'Add Scan Failed'
            self.scan.status = 'Failed'
            db.session.commit()
            driver.close()
            driver.quit()
            display.stop()
            return False

        try:
            user_defined = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="tabs"]/a[2]'))
            )
            user_defined.click()
        except Exception as e:
            error = 'unable to find "User Defined" scan section '\
                'wrong xpath supplied(//*[@id="tabs"]/a[2])'
            scanEvent = ScanEvents.query.filter_by(scan_id=scan.id).first()
            if scanEvent:
                scanEvent.scan_event_history = error
            else:
                scanEvent = ScanEvents(scan_id=scan.id, 
                            event_id=int(self.scan.event_id), 
                            scan_event_history=error
                            )
                db.session.add(scanEvent)
            self.scan.scan_message = 'Add Scan Failed'
            self.scan.status = 'Failed'
            db.session.commit()
            driver.close()
            driver.quit()
            display.stop()
            return False

        try:
            policy = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="content"]/section/div[1]/a[20]'))

            )
            policy.click()
        except Exception as e:
            error = 'unable to find User Defined policy wrong '\
                'xpath supplied(//*[@id="content"]/section/div[1]/a[20])'
            scanEvent = ScanEvents.query.filter_by(scan_id=self.scan.id).first()
            if scanEvent:
                scanEvent.scan_event_history = error
            else:
                scanEvent = ScanEvents(scan_id=self.scan.id, 
                            event_id=int(self.scan.event_id), 
                            scan_event_history=error
                            )
                db.session.add(scanEvent)
            self.scan.scan_message = 'Add Scan Failed'
            self.scan.status = 'Failed'
            db.session.commit()
            driver.close()
            driver.quit()
            display.stop()
            return False

        try:
            name_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="editor-tab-view"]/div/div[1]/'
                               'section/div[1]/div[1]/div[1]/div[1]/div/input'))
            )
            name_input.clear()
            name_input.send_keys(self.scan.scan_name)
        except Exception as e:
            error = 'unable to add scan name, wrong xpath supplied '\
                '(//*[@id="editor-tab-view"]/div/div[1]/section/div[1]/div[1]/div[1]/div[1]/div/input)'
            scanEvent = ScanEvents.query.filter_by(scan_id=self.scan.id).first()
            if scanEvent:
                scanEvent.scan_event_history = error
            else:
                scanEvent = ScanEvents(scan_id=self.scan.id, 
                            event_id=int(self.scan.event_id), 
                            scan_event_history=error
                            )
                db.session.add(scanEvent)
            self.scan.scan_message = 'Add Scan Failed'
            self.scan.status = 'Failed'
            db.session.commit()
            driver.close()
            driver.quit()
            display.stop()
            return False

        try:
            target_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="editor-tab-view"]/div/div[1]/section/'
                               'div[1]/div[1]/div[1]/div[6]/div/textarea'))
            )
            target_input.clear()
            target_input.send_keys(self.scan.targets)
        except Exception as e:
            error = 'unable to add targets, wrong xpath supplied '\
                '(//*[@id="editor-tab-view"]/div/div[1]/section/div[1]/div[1]/div[1]/div[1]/div/input)'
            scanEvent = ScanEvents.query.filter_by(scan_id=self.scan.id).first()
            if scanEvent:
                scanEvent.scan_event_history = error
            else:
                scanEvent = ScanEvents(scan_id=self.scan.id, 
                            event_id=int(self.scan.event_id), 
                            scan_event_history=error
                            )
                db.session.add(scanEvent)
            self.scan.scan_message = 'Scan is Failed'
            self.scan.status = 'Failed'
            db.session.commit()
            driver.close()
            driver.quit()
            display.stop()
            return False

        try:
            save_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="content"]/section/form/div[2]/i'))
            )
            save_dropdown.click()
        except Exception as e:
            error = 'unable to save scan, wrong xpath supplied (//*[@id="content"]/section/form/div[2]/i)'
            scanEvent = ScanEvents.query.filter_by(scan_id=self.scan.id).first()
            if scanEvent:
                scanEvent.scan_event_history = error
            else:
                scanEvent = ScanEvents(scan_id=self.scan.id, 
                            event_id=int(self.scan.event_id), 
                            scan_event_history=error
                            )
                db.session.add(scanEvent)
            self.scan.scan_message = 'Scan is Failed'
            self.scan.status = 'Failed'
            db.session.commit()
            driver.close()
            driver.quit()
            display.stop()
            return False

        try:
            launch = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="content"]/section/form/div[2]/ul/li'))
            )
            launch.click()
        except Exception as e:
            error = 'unable to launch scan, wrong xpath supplied (//*[@id="content"]/section/form/div[2]/ul/li)'
            scanEvent = ScanEvents.query.filter_by(scan_id=self.scan.id).first()
            if scanEvent:
                scanEvent.scan_event_history = error
            else:
                scanEvent = ScanEvents(scan_id=self.scan.id, 
                            event_id=int(self.scan.event_id), 
                            scan_event_history=error
                            )
                db.session.add(scanEvent)
            self.scan.scan_message = 'Scan is Failed'
            self.scan.status = 'Failed'
            db.session.commit()
            driver.close()
            driver.quit()
            display.stop()
            return False

        self.scan.status = 'Running'
        self.scan.scan_message = 'Scan is Running'
        db.session.commit()

        time.sleep(10)

        driver.close()
        driver.quit()
        display.stop()
        return True
