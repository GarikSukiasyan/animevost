import time
import requests
from PIL import Image
import subprocess
import pytesseract
import cv2
import urllib
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from requests_html import HTMLSession
import os
import sys
import cv2
from pathlib import Path
# pip install tqdm
from tqdm import tqdm
# pip install requests
import requests
import configparser

# Живые обои
# https://winzoro.net/wallpapers_all/zhivye-oboi-anime/

class Parser():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini", encoding="utf-8")

        options = webdriver.ChromeOptions()
        # options.add_argument("--start-maximized")
        self.browser = webdriver.Chrome()
        # self.browser.set_window_position(0, 0)
        # self.browser.set_window_size(700, 600)

        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        self.anime_link = "https://анимевост.рф/dw.php?file=MzEzMyU3QzMrJUYxJUU1JUYwJUU4JUZGJTdDMTY3NDU2NTc0Ng=="
        self.anime_wost = "https://анимевост.рф/"

        self.anime_name = "Жизнь в альтернативном мире с нуля" # В поиске не
        self.seria = 3

        self.unick_video = True


    # Ищем аниме на сайте
    def Anime_Search(self):
        # Перейти на главную страницу, указать в поиске название аниме, далее из списка взять нужное

        self.browser.get(self.anime_wost)

        time.sleep(2.0)

        # Указываем название нужного аниме
        inputCode = self.browser.find_element(By.CLASS_NAME, "form_pole_search")
        inputCode.send_keys(self.anime_name)

        time.sleep(2.0)

        # Нажимаем на поиск
        self.browser.find_element(By.CLASS_NAME, 'hand_kursor_smile').click()

        time.sleep(5.0)


        quotes = self.browser.find_element(By.CLASS_NAME, 'text_b')
        text = quotes.text

        if text == "Скачать аниме ":
            # Нажимаем скачать у первого попавшегося
            self.browser.find_element(By.CLASS_NAME, 'text_b').click()

            time.sleep(8.0)

            self.get_link_series()
        else:
            print(quotes.text)
            self.browser.close()


    # Получаем ссылку на серию
    def get_link_series(self):
        list_link = []
        element = self.browser.find_elements(By.CLASS_NAME, 'link_list') # text_save
        for i in element:
            html_link = i.get_attribute('innerHTML')
            soup = BeautifulSoup(html_link, 'html.parser')
            link = soup.find('a').get('href')
            list_link.append(link)

        # print(list_link)

        try:
            self.get_download_link(list_link[self.seria])
        except:
            print(f"У аниме: {self.anime_name} нету серии {self.seria}")
            self.browser.close()


    # Получаем ссылку на скачивание
    def get_download_link(self, link):
        status = False
        next_link = None
        new_link = str("https://анимевост.рф/") + str(link)

        while status != True:
            self.browser.get(new_link)

            time.sleep(2.0)

            image = self.browser.find_elements(By.CLASS_NAME, "form_pole_search")
            for i in image:
                with open('capha.png', 'wb') as file:
                   file.write(i.screenshot_as_png)

            img = cv2.imread('capha.png')
            img = cv2.resize(img, None, fx=9, fy=9)  # Увеличение изображения в 9 раз

            balance = pytesseract.image_to_string(img, config='outputbase digits')

            time.sleep(4.0)

            inputCode = self.browser.find_element(By.CLASS_NAME, "form_cod")
            inputCode.send_keys(balance)

            time.sleep(5.0)

            try:
                quotes = self.browser.find_element(By.CLASS_NAME, 'text_save')
                print(quotes.text)

            except:
                list_link = []
                element = self.browser.find_elements(By.CLASS_NAME, 'text_download')

                for i in element:
                    html_link = i.get_attribute('innerHTML')
                    soup = BeautifulSoup(html_link, 'html.parser')
                    link = soup.find('a').get('href')
                    list_link.append(link)

                try:
                    next_link = list_link[1] # Порой несколько ссылок, а порой одна, переделай

                    status = True
                    break
                except:
                    pass

        self.browser.close()
        self.download_anime(next_link)


    # Скачиваем аниме
    def download_anime(self, link):

        print('Start download')

        urllib.request.urlretrieve(link, 'anime.mp4')

        print('End download')

        self.crop_video()


    # Вырезаем нужную часть
    def crop_video(self):
        print('Start edit video')

        # Short 0
        # # ffmpeg -ss 12:45 -t 1:00 -i fight.mp4 -vcodec copy -acodec copy out5.mp4

        # Short 1
        # ffmpeg -ss 12:34 -t 1:00 -i fight.mp4 -vf crop=ih*(9/16):ih YT.mp4

        # Short 2
        # ffmpeg -ss 12:45 -t 1:00 -i fight.mp4 -i imgg.jpg -filter_complex "overlay=(W-w)/2:(H-h)/2" output.mp4

        # Short 3 Идеал
        # ffmpeg -ss 12:45 -t 1:00 -i fight.mp4 -i imgg.jpg -filter_complex "[0:v]scale=1280:720[v];[1:v][v]overlay=80:1000" -c:a copy output.mp4

        subprocess.call([
            "ffmpeg",
            "-ss",  "00:05:00",
            "-t",  "00:01:00",
            "-i",  "anime.mp4",
            "-i", "bg.jpg",
            "-filter_complex", "[0:v]scale=1280:720[v];[1:v][v]overlay=80:1000",
            "-c:a", "copy",
            "output.mp4"])

        print('End edit video')


    # Загружаем на ютуб
    # https://github.com/linouk23/youtube_uploader_selenium
    # https://github.com/ContentAutomation/YouTubeUploader
    # https://github.com/dquint54/YT-Shorts-AI
    # https://github.com/NickFerd/Highlights
    def upload_to_youtube(self):
        pass



if __name__ == "__main__":
    app = Parser()
    app.upload_to_youtube()


"""
В этой команде (Ww)/2 и (Hh)/2 вычисляют смещение, необходимое для центрирования видео на изображении.  W и H — ширина и высота изображения, а w и h — ширина и высота видео.


ffmpeg -ss 12:45 -t 1:00 -i fight.mp4 -i imgg.jpg -filter_complex "overlay=(2560-720)/2:(1440-1280)/2" output.mp4



ffmpeg -ss 12:45 -t 1:00 -i fight.mp4 -i imgg.jpg -filter_complex "overlay=(1440-1280)/2:(2560-720)/2" output.mp4


Скопируйте и вставьте в терминал такую команду: ffmpeg -i ИМЯ_ФАЙЛА -vf «delogo=x=AAA:y=BBB:w=CCC:h=DDD» -c:a copy output.mp4. Вместо ААА и BBB укажите координаты водяного знака в пикселях по осям x и y, соответственно. А вместо CCC и DDD — ширину и высоту самого штампа. Должно получиться что-то вроде ffmpeg -i in.mp4 -vf «delogo=x=1550:y=830:w=100:h=100» -c:a copy output.mp4.


ffmpeg -ss 12:45 -t 1:00 -i fight.mp4 -i imgg.jpg -filter_complex "[0:v]scale=1280:720[v];[1:v][v]overlay=80:1000" -c:a copy output.mp4
"""