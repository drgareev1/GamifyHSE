import mechanize
from bs4 import BeautifulSoup
import time
import re
import json

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from fbs_runtime.application_context.PySide2 import ApplicationContext


class Scraper:

    def __init__(self, display_head, debug_mode, app_context):
        self.app_context = app_context
        options = Options()
        options.add_argument("--window-size=1600,1000")
        options.add_argument("--log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        if (display_head is not True):
            options.add_argument("--headless")

        self.driver = webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())
        self.debug_mode = debug_mode
        
        

    def auth(self, username, password):

        if self.debug_mode == True:
            return 0
        else:

            br = mechanize.Browser()
            br.cookiejar.clear()

            self.driver.get("https://smartedu.hse.ru/login?target=/calendar")
            lnks = self.driver.find_elements_by_tag_name("a")

            authlink = ''

            for lnk in lnks:
                if lnk.get_attribute("href").startswith('https://auth.hse.ru'):
                    authlink = lnk.get_attribute("href")

            br.open(authlink)

            auth_cookies = []

            br.select_form(nr=0)
            br.form['UserName'] = username
            br.form['Password'] = password
            br.submit()

            cookies = br._ua_handlers['_cookies'].cookiejar

            auth_cookies = []
            for c in cookies:
                newDict = {}
                newDict['name'] = c.name
                newDict['value'] = c.value
                newDict['domain'] = c.domain
                newDict['path'] = c.path
                auth_cookies.append(newDict)

            self.driver.get("https://auth.hse.ru/")
            for c in auth_cookies:
                self.driver.add_cookie(c)

            if len(auth_cookies) != 0:
                self.driver.get(authlink)
                return 0
            else:
                return 401

    def classes(self):

        classes_list = []

        if self.debug_mode == True:
            with open(self.app_context.get_resource('debug.hse')) as f:
                data = json.load(f)
                classes_list = data["classes"]
                f.close()

        else:
        
            current_classes = []
            finished_classes = []
            archived_classes = []
        
            self.driver.get("https://smartedu.hse.ru/grades")
            time.sleep(6)

            html = self.driver.find_element_by_tag_name('html').get_attribute('innerHTML')

            soup = BeautifulSoup(html, 'html.parser')

            links_fetched = soup.findAll('a', attrs={'href': re.compile("/grades/")})
            del links_fetched[0::2]

            for lk in links_fetched:
                new_class = {}
                class_link = str(re.search("href=\".*<div", str(lk)).group())[6:-6]
                class_name = str(re.search("\">[^<].*<\/d", str(lk)).group())[2:-3]
                new_class["id"] = class_link.split('/')[-1]
                new_class["name"] = class_name
                current_classes.append(new_class)
                
            finished_button = self.driver.find_element_by_xpath("//*[@id=\"wrapper-offset\"]/div/div[3]/div[1]/div[2]/div[1]/button[4]")
            finished_button.click()
            
            html = self.driver.find_element_by_tag_name('html').get_attribute('innerHTML')

            soup = BeautifulSoup(html, 'html.parser')

            links_fetched = soup.findAll('a', attrs={'href': re.compile("/grades/")})
            del links_fetched[0::2]

            for lk in links_fetched:
                new_class = {}
                class_link = str(re.search("href=\".*<div", str(lk)).group())[6:-6]
                class_name = str(re.search("\">[^<].*<\/d", str(lk)).group())[2:-3]
                new_class["id"] = class_link.split('/')[-1]
                new_class["name"] = class_name
                finished_classes.append(new_class)
                
            archived_button = self.driver.find_element_by_xpath("//*[@id=\"wrapper-offset\"]/div/div[3]/div[1]/div[2]/div[1]/button[5]")
            archived_button.click()
                
            html = self.driver.find_element_by_tag_name('html').get_attribute('innerHTML')

            soup = BeautifulSoup(html, 'html.parser')

            links_fetched = soup.findAll('a', attrs={'href': re.compile("/grades/")})
            del links_fetched[0::2]

            for lk in links_fetched:
                new_class = {}
                class_link = str(re.search("href=\".*<div", str(lk)).group())[6:-6]
                class_name = str(re.search("\">[^<].*<\/d", str(lk)).group())[2:-3]
                new_class["id"] = class_link.split('/')[-1]
                new_class["name"] = class_name
                archived_classes.append(new_class)

        return {"Активные": current_classes, "Завершенные": finished_classes, "Архивные": archived_classes}

    def announcements(self):

        anns = []

        if self.debug_mode == True:
            with open(self.app_context.get_resource('debug.hse')) as f:
                data = json.load(f)
                anns = data["announcements"]
                f.close()

        else:
            self.driver.get("https://smartedu.hse.ru/announcements")
            time.sleep(6)

            html = self.driver.find_element_by_tag_name('html').get_attribute('innerHTML').encode("utf-8")
            soup = BeautifulSoup(html, 'html.parser')

            announcements = soup.find_all("div", {"class": "Announcement_Discussion__2o26h"})
            for ann in announcements:

                new_ann = {}

                subject = ann.find_all("div", {"class": "Announcement_Discussion__subject__VRZaJ"})[0].get_text()
                ann_class = ann.find_all("div", {"class": "Announcement_Discussion__courseTitle__2SASS"})[0].get_text()
                ann_time_passed = ann.find_all("div", {"class": "Author_Author__timePassed__F46PJ"})[0].get_text()
                ann_content = ann.find_all("div", {"class": "MoodleContent_MoodleContent__3fa54"})[0].get_text().replace(u"\u2192", ' - ')
                ann_author = ann.find_all("div", {"class": "Author_Author__fullName__279QA"})[0].get_text().replace(u"\u2192", ' - ')

                new_ann["subject"] = subject
                new_ann["class"] = ann_class
                new_ann["time_passed"] = ann_time_passed
                new_ann["content"] = ann_content
                new_ann["author"] = ann_author

                anns.append(new_ann)


        print(anns)
        return anns

    def deadlines(self):

        self.driver.get("https://smartedu.hse.ru/calendar")
        time.sleep(2)
        self.driver.get("https://smartedu.hse.ru/calendar")
        time.sleep(3)

        button = self.driver.find_element_by_xpath("//*[@id=\"wrapper-offset\"]/div/div[3]/div[1]/div[2]/div/button[3]")
        button.click()

        html = self.driver.find_element_by_tag_name('html').get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')

        tasks = []

        days = soup.find_all("div", {"class": "CalendarPage_DateContainer__1drAe"})
        for day in days:

            day_value = day.find_all("div", {"class": "CalendarPage_DateValue__3UUNY"})[0].get_text()
            month_value = day.find_all("div", {"class": "CalendarPage_DateAddition__1hj6p"})[0].get_text()

            events = day.find_all("div", {"class": "CalendarPage_EventsList__3zgt2"})[0]
            no_events = day.find_all("div", {"class": "CalendarPage_NoEvents__Bjq6n"})
            if len(no_events) != 0:
                pass
            else:
                events_list = events.find_all("div", {"class": "CalendarPage_EventsListItem__3DXY5 CalendarPage_EventsListItem_course__k33Eo"})
                for event in events_list:

                    new_task = {}

                    event_info = event.find_all("div", {"class": "CalendarPage_EventsListItemContent__3hrCH"})[0]

                    event_title = str(re.search("_3hrCH\">.*<div", str(event_info)).group())[8:-4]

                    new_task["date"] = day_value + " " + month_value
                    new_task["title"] = event_title

                    tasks.append(new_task)

        return tasks

    def class_tasks(self, class_id):

        tasks = {}

        if self.debug_mode == True:
            with open(self.app_context.get_resource('debug.hse')) as f:
                data = json.load(f)
                classes_list = data["classes"]
                for cl in classes_list:
                    if cl["id"] == int(class_id):
                        tasks = cl["tasks"]
                f.close()

        else:
            self.driver.get("https://smartedu.hse.ru/grades/0/" + str(class_id))
            time.sleep(3)

            html = self.driver.find_element_by_tag_name('html').get_attribute('innerHTML').encode("utf-8")
            soup = BeautifulSoup(html, 'html.parser')

            data = []
            table = soup.find('table', attrs={'class': 'CourseGradesOverviewPage_GradesTable__1EBgv'})
            table_body = table.find('tbody')

            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols])

            footer = table.find('tfoot')
            final_grades = footer.find_all('td')

            final_grade = final_grades[1].getText()

            tasks["list"] = []
            tasks["final"] = final_grade

            for item in data:
                new_task = {}
                new_task["name"] = item[0]
                new_task["weight"] = item[1]
                new_task["grade"] = item[2]
                tasks["list"].append(new_task)

        return tasks
