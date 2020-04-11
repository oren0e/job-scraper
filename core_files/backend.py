import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

import re
import string

from typing import List, Tuple, Dict, Optional

import tqdm

import pandas as pd

from core_files import stopwrds_initializer
from nltk.corpus import stopwords

pd.set_option('expand_frame_repr', False)  # To view all the variables in the console


class Notifier:
    def __init__(self, query: str, terms: Optional[str],
                 email: Optional[str] = None, num_recent_jobs: Optional[int] = 15,
                 sort_by: Optional[str] = 'date', all_terms: bool = False) -> None:
        self._query = query
        self._terms = terms     # search terms separated by ','
        self._email = email
        self._num_recent_jobs = num_recent_jobs
        self._urls: List = []
        self._sort_by = sort_by
        self._all_terms = all_terms

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}('
                f'{self._query!r}, {self._terms!r}, {self._email!r}, {self._num_recent_jobs!r},'
                f'{self._sort_by!r}, {self._all_terms!r})'
                )

    @staticmethod
    def _remove_non_ascii(text: str) -> str:
        """ Removes non ASCII characters from 'text' """

        output = ''.join(i for i in text if ord(i) < 128)
        return re.sub(r'(/)|(")|(-)', '', output).strip()

    @staticmethod
    def _get_main_soup(url: str) -> BeautifulSoup:
        """ Gets a BeautifulSoup object from the main search page """

        main_page = requests.get(url)
        return BeautifulSoup(main_page.content, "html5lib")

    @staticmethod
    def _get_job_soup(url: str) -> BeautifulSoup:
        """
        Gets BeautifulSoup object for each job link
        by using Selenium Chrome emulator
        """

        # Use without opening the browser
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        browser = webdriver.Chrome(options=options)
        browser.get(url)
        page = browser.page_source
        soup = BeautifulSoup(page, "html5lib")
        browser.quit()

        return soup

    def _get_num_jobs(self, main_soup: BeautifulSoup) -> int:
        """ Gets the total number of results from the search """

        count_pages = main_soup.find(id="searchCountPages")
        x = self._remove_non_ascii(list(count_pages)[0].strip())
        res = int(re.sub(',', '', x.split()[1]))

        return res - (res % 10)

    @staticmethod
    def _get_jobs_links(soup: BeautifulSoup) -> List[str]:
        """ Extract links from the main search page """

        urls = []
        for link in soup.find_all(name='div', class_='title'):
            var_url = link.find('a')['href']
            url = 'https://il.indeed.com' + var_url
            urls.append(url)

        return urls

    def _get_job_details(self, url: str) -> Tuple[str, str, str]:
        """ Extract the details from each job link """

        soup = self._get_job_soup(url)
        title = self._remove_non_ascii(soup.find(name='h3').get_text())  # job title
        company = soup.find(name='div', class_='icl-u-xs-mr--xs').get_text()
        text = self._remove_non_ascii(soup.find(name='div', class_='jobsearch-jobDescriptionText').get_text().strip())

        return title, company, text

    def _build_urls(self) -> None:
        """ Gets the links for num_jobs of jobs """

        if self._sort_by == 'relevance':
            base_url = f'https://il.indeed.com/jobs?q={self._query}&l=israel&start='
        else:
            base_url = f'https://il.indeed.com/jobs?q={self._query}&l=israel&sort=date&start='

        if self._num_recent_jobs is not None:
            num_jobs = ((self._num_recent_jobs // 15) * 10)     # whole numbers of 15
        else:
            num_jobs = self._get_num_jobs(self._get_main_soup(base_url+'0'))

        # get the links
        for i in tqdm.tqdm(range(0, num_jobs, 10), desc='Getting links:', ascii=True):
            soup = self._get_job_soup(base_url+f'{str(i)}')
            self._urls.extend(self._get_jobs_links(soup))

    def _get_dataframe(self) -> pd.DataFrame:
        """ Builds the Pandas DataFrame from the urls list """

        self._build_urls()
        jobs_dict: Dict[int, Dict[str, str]] = {}

        for i, url in enumerate(tqdm.tqdm(self._urls, desc='Getting content', ascii=True)):
            try:
                jobs_dict[i] = {}
                jobs_dict[i]['title'], jobs_dict[i]['company'], jobs_dict[i]['text'] = self._get_job_details(url)
            except:
                continue

        df = pd.DataFrame.from_dict(jobs_dict, orient='index')
        df['link'] = self._urls

        return df

    @staticmethod
    def _text_process(text: str) -> str:
        """ Removes punctuation and stopwords from job description and requirements """

        no_newline = re.sub(r'\n', ' ', text)
        no_punc = ''.join([word for word in no_newline if word not in string.punctuation]).lower()

        return ' '.join([word for word in no_punc.split(' ') if word not in stopwords.words('english')])  # no stopwords

    def _search_terms(self, terms: str, text: str) -> bool:
        """
        Returns boolean answer if the searched terms are found in the text or not.
        If 'all_terms' = True, the function will return True only if all the terms were
        found.
        """

        # Separates search terms by commas
        terms_lst = terms.split(',')
        terms_lst = [item.strip() for item in terms_lst]
        found_set = set(re.findall(r'\b' + '|'.join(terms_lst) + r'\b', text))

        if self._all_terms:
            res_lst = []
            for item in terms_lst:
                if item in found_set:
                    res_lst.append(True)
                else:
                    res_lst.append(False)
            return all(res_lst)
        else:
            return found_set != set()

    def build_jobs_table(self) -> pd.DataFrame:
        """ Builds the table of jobs according to search terms criteria """

        df = self._get_dataframe()
        df['text'] = df['text'].apply(self._text_process)

        df['contains_terms'] = df['text'].apply(lambda x: self._search_terms(terms=self._terms, text=x))
        filtered_df = df.loc[df['contains_terms'] == True].reset_index(drop=True)
        filtered_df.drop('contains_terms', axis=1, inplace=True)

        hide_index = [''] * len(filtered_df)
        filtered_df.index = hide_index

        return filtered_df