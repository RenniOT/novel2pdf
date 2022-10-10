import asyncio
import requests
from httpx import Client, AsyncClient
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from tkinter import messagebox
import os


class ScrapeNovel:
    def __init__(self, link):
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_colwidth', None)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        self.link = link
        self.id = self.yoink_manga_id(link)
        self.title = self.yoink_title(link)
        self.cover = ''
        self.big_df_list = []
        asyncio.run(self.scrape_chapters())
        self.df = pd.DataFrame(self.big_df_list, columns=['Chapter', 'Part', 'Title', 'Content']).sort_values(by=['Chapter', 'Part'], ascending=[True, True]).reset_index()

    def get_chapter_urls(self):
        url_list = []
        payload = {
            'action': 'manga_get_reading_nav',
            'manga': self.id,
            'chapter': 'chapter-29-7',
            'volume_id': '0',
            'type': 'content'
        }
        with Client(headers=self.headers, timeout=60.0, follow_redirects=True) as client:
            r = client.post('https://www.box-novel.com/wp-admin/admin-ajax.php', data=payload)
            soup = BeautifulSoup(r.text, 'html.parser')
            links = soup.select_one(
                'select.c-selectpicker.selectpicker_chapter.selectpicker.single-chapter-select').select(
                'option')
            for link in links:
                url_list.append(link.get('data-redirect'))
        return url_list

    async def get_chapters(self, url):
        async with AsyncClient(headers=self.headers, timeout=60.0, follow_redirects=True) as client:
            try:
                r = await client.get(url)
                soup = BeautifulSoup(r.text, 'html.parser')
                title = soup.select_one('h1#chapter-heading').get_text(strip=True)
                text_content = soup.find('div', class_='text-left')
                chapter = await self.yoink_chapter_number(soup)
                part = 0
                if "." in chapter:
                    numbers = chapter.split(".")
                    chapter = float(numbers[0])
                    part = float(numbers[1])
                else:
                    chapter = int(chapter)
                self.big_df_list.append((chapter, part, title, text_content))
            except Exception as e:
                print(url, e)

    async def scrape_chapters(self):
        print(f"Parsing data for {self.title}...")
        messagebox.showinfo(title="Parsing Chapters...", message=f"Loading chapters for {self.title}, this may take "
                                                                 f"several minutes...")
        start_time = datetime.now()
        tasks = asyncio.Queue()
        for x in self.get_chapter_urls():
            tasks.put_nowait(self.get_chapters(x))

        async def worker():
            while not tasks.empty():
                await tasks.get_nowait()

        await asyncio.gather(*[worker() for _ in range(20)])
        end_time = datetime.now()
        duration = end_time - start_time
        print('chapters scraping took', duration)

    def dl_novel_cover(self, destination):
        self.cover = os.path.join(destination, "cover-image.jpg")
        r = requests.get(self.link)
        soup = BeautifulSoup(r.text, 'html.parser')
        image_link = soup.find("meta",  property="og:image").get('content')
        response = requests.get(image_link)
        if response.status_code == 200:
            with open(self.cover, 'wb') as file:
                file.write(response.content)

    @staticmethod
    async def yoink_chapter_number(soup):
        s = soup.find(class_='c-selectpicker selectpicker_chapter chapter-selection chapters_selectbox_holder').get(
            'data-chapter')
        after_chapter_string = s[s.index("-") + 1:len(s)].strip().replace("-", ".", 1).replace("_", ".", 1)
        if after_chapter_string.replace(".", "", 1).isdigit():
            return after_chapter_string
        try:
            return [s for s in after_chapter_string.split() if s.replace(".", "", 1).isdigit()][0]
        except Exception:
            spliced_string = ''.join(''.join([*after_chapter_string.split()[0]]).split('_')[0]).split('-')[0]
            return ''.join([s for s in spliced_string if s.replace(".", "", 1).isdigit()])

    @staticmethod
    def yoink_manga_id(link):
        r = requests.get(link)
        soup = BeautifulSoup(r.content, 'html.parser')
        s = soup.find(class_='wp-manga-action-button')
        return s.get('data-post')

    @staticmethod
    def yoink_title(link):
        r = requests.get(link)
        soup = BeautifulSoup(r.content, 'html.parser')
        return soup.find("meta",  property="og:title").get('content').removesuffix(' - Box Novel')
