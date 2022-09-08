import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebProcess:
    def __init__(self):
        self.domain = 'http://spoc.wzu.edu.cn'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'Referer': '',
            'Host': 'spoc.wzu.edu.cn'
        }
        self.session = requests.session()
        self.drive = webdriver.Chrome()
        self.wait = WebDriverWait(self.drive, timeout=3, poll_frequency=1)
        self.courseOpenId = None
        self.cookies = {}

    def __del__(self):
        self.drive.quit()

    def getCookies(self):
        # if os.path.exists('cookies1.json') and os.path.getsize('cookies.json') != 0:
        #     with open(file='cookies.json', mode='r') as f:
        #         self.drive.get(url='http://spoc.wzu.edu.cn/')
        #         WebDriverWait(self.drive, timeout=3, poll_frequency=1).until(EC.title_contains("SPOC"))
        #         dictCookies = json.load(f)
        #         for cookie in dictCookies:
        #             self.drive.add_cookie(cookie)
        #         time.sleep(2)
        #         self.drive.get(url='http://spoc.wzu.edu.cn/portal/myCourseIndex/1.mooc?checkEmail=false')
        #         print(self.drive.get_cookies())
        # else:
        #     with open(file='cookies.json', mode='w') as f:
        #         self.drive.get(url='http://spoc.wzu.edu.cn/oauth/toMoocAuth.mooc')
        #         WebDriverWait(self.drive, timeout=30, poll_frequency=1).until(EC.title_contains("SPOC"))
        #         dictCookies = self.drive.get_cookies()
        #         json.dump(dictCookies, f)
        self.drive.get(url='http://spoc.wzu.edu.cn/oauth/toMoocAuth.mooc')
        WebDriverWait(self.drive, timeout=9999, poll_frequency=1).until(EC.title_contains("SPOC"))
        dictCookies = self.drive.get_cookies()
        cookiejar = requests.cookies.RequestsCookieJar()
        for cookie in dictCookies:
            cookiejar.set(cookie['name'], cookie['value'])
            self.cookies[cookie['name']] = cookie['value']
        self.session.cookies = cookiejar
        print(self.cookies)

    def selectCourses(self):
        self.drive.find_element(By.CLASS_NAME, "introjs-skipbutton").click()
        self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'view-title')))
        soup = BeautifulSoup(self.drive.page_source, 'lxml')
        courses = [{'title': h3.text.replace('\n', '').replace(' ', ''), 'href': self.domain + a.attrs['href']}
                   for h3, a in zip(soup.find_all('h3', class_='view-title'), soup.find_all('a', class_='view-shadow'))]
        hrefs = []
        for i, course in zip(range(1, len(courses) + 1), courses):
            print(i, '、课程名称:', course['title'])
            hrefs.append(course['href'])
        select = int(input())
        self.courseOpenId = re.search('index/(?P<courseOpenId>.*?).mooc', hrefs[select-1]).group('courseOpenId')
        self.headers['Referer'] = self.domain + '/examTest/stuExamList/' + self.courseOpenId + '.mooc'
        print(self.headers['Referer'])

    def gotoExamTest(self):
        self.drive.get(self.headers['Referer'])
        time.sleep(1)
        soup = BeautifulSoup(self.drive.page_source, 'lxml')
        exams = [h3.text.replace('\n', '').replace(' ', '') for h3 in soup.find_all('td', class_='td1')]
        for i, exam in zip(range(1, len(exams) + 1), exams):
            print(i, '、课程名称:', exam)
        select = int(input())
        self.drive.find_elements(By.CLASS_NAME, 'link-action')[select-1].click()
        time.sleep(1)
        if self.drive.find_elements(By.CLASS_NAME, 'doObjExam'):
            self.drive.find_element(By.CLASS_NAME, 'doObjExam').click()
        else:
            self.drive.find_elements(By.CLASS_NAME, 'enter_exam')[-1].click()
        time.sleep(1)
