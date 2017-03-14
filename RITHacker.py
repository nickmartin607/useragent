#!/usr/bin/env python
import bs4
import os
import re
import threading

from useragent import UserAgent, URL


MAX_THREADS = 7
THREAD_POOL = threading.BoundedSemaphore(value=MAX_THREADS)
    

def get_links(soup):
    links = []
    for link in soup.findAll('a'):
        url = link.get('href')
        if url:
            url = url.encode('ascii', 'ignore').replace(' ', '')
            links.append(url)
    return links
      
def file_downloader(src, dst):
    THREAD_POOL.acquire()
    with open(dst, 'wb') as f:
        ua = UserAgent('GET', src)
        status_code, headers, message = ua.SendRequest()
        f.write(message)
    THREAD_POOL.release()


class Crawler(object):
    def __init__(self, start_url, scope=None, depth=1):
        url = URL(start_url)
        self.scope = scope or str(url).replace('www.', '')
        self.write_lock = threading.Semaphore(1)
        
        self.master_urls = []
        self.master_emails = []
        self.urls = set([start_url])

        while depth >= 0:
            curr_urls = list(self.urls - set(self.master_urls))
            threads = []
            for url in curr_urls:
                t = threading.Thread(target=self.read_url, args=(url,))
                threads.append(t)
            print("Depth: " + str(depth) + "       Threads: " + str(len(threads)))
            self.master_urls += curr_urls
            self.urls = set()
            [t.start() for t in threads]
            [t.join() for t in threads]
            depth -= 1
        self.master_urls = list(set(self.master_urls).union(self.urls))

    def read_url(self, url):
        THREAD_POOL.acquire()
        try:
            ua = UserAgent('GET', url)
            soup = ua.GetSoup()
            sub_urls = get_links(soup)
        except:
            THREAD_POOL.release()
            return
        emails = set(EMAIL_REGEX.findall(str(soup), re.I))
        urls = []
        for sub_url in sub_urls:
            if sub_url.startswith('/'):
                sub_url = self.scope + sub_url
            if '#' in sub_url:
                sub_url = sub_url.split('#')[0]
            elif '?' in sub_url:
                sub_url = sub_url.split('?')[0]
            if sub_url.endswith('.pdf') or sub_url.endswith('.jpg'):
                continue
            if self.scope not in sub_url:
                continue
            if URL_REGEX.match(sub_url):
                urls.append(sub_url)
        self.write_lock.acquire()
        self.urls = self.urls.union(set(urls))
        self.master_emails = list(set(self.master_emails).union(emails))
        self.write_lock.release()
        THREAD_POOL.release()



def WAS_Lab3_A1_1():
    url = 'https://www.rit.edu/programs/computing-security-bs'
    ua = UserAgent('GET', url)
    status_code, headers, message = ua.SendRequest()
    
    course_regex = re.compile(r'[A-Z]{4}\-[0-9]{3}')
    soup = bs4.BeautifulSoup(message, 'html.parser', from_encoding='iso-8859-1')
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) == 3 and course_regex.match(tds[0].text):
            print("{:>15}   {}".format(tds[0].text, tds[1].text))

def WAS_Lab3_A1_2():
    output_dir = 'images'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    url = 'https://www.rit.edu/gccis/computingsecurity/people'
    ua = UserAgent('GET', url)
    status_code, headers, message = ua.SendRequest()

    images = 0
    base_host = ua.url.base_host
    soup = bs4.BeautifulSoup(message, 'html.parser', from_encoding='iso-8859-1')
    for div in soup.findAll('div', class_='staff-picture'):
        images += 1
        path = div.img['src']
        src = base_host + path.replace('//', '/').replace(' ', '%20')
        dst = os.path.join(output_dir, path.split('/')[-1])
        thread = threading.Thread(target=file_downloader, args=(src, dst))
        thread.start()
        thread.join()
    # total_threads = len(threads)
    # [t.start() for t in threads]
    # [t.join() for t in threads]
    print("Downloaded {} images from {}".format(images, base_host))
    

    # for i in images:
    #     path = str(host + i.replace('//', '/').replace(' ', '%20'))
    #     name = str(os.path.join(dst, i.split('/')[-1]))
    #     thread = threading.Thread(target=file_downloader, args=(path, name))
    #     thread.start()
    # print("Downloaded {} images from {}".format(len(images), ua.url.host))

def WAS_Lab3_A2_1_3(host, scope=None, depth=2):
    c = Crawler(start_url=host, scope=scope, depth=depth)
    with open('scraped_urls.txt', 'wb') as f:
        data = sorted(list(c.master_urls))
        print("Total URLs Found:   {}".format(len(data)))
        f.write('\r\n'.join(data))
    with open('scraped_emails.txt', 'wb') as f:
        data = sorted(list(c.master_emails))
        print("Total Emails Found: {}".format(len(data)))
        f.write('\r\n'.join(data))
    
def WAS_Lab3_A3_1(src='companies.csv', dst='master_url_list.txt', depth=2):
    with open(src, 'r') as infile, open(dst, 'wb') as outfile:
        for c in infile.readlines():
            company_name, company_url = c.split(',')
            c = Crawler(start_url=company_url, depth=depth)
            print("Found {} URLs and {} Emails at: {}".format(len(c.master_urls), len(c.master_emails), company_url))
            outfile.write('\r\n'.join(sorted(c.master_urls)))
def WAS_Lab3_A3_2(src='master_url_list.txt', dst='master_paths_list.txt'):
    with open(src, 'r') as infile, open(dst, 'wb') as outfile:
        for url in infile.readlines():
            url = URL(url.strip())
            outfile.write(url.path)
    



if __name__ == '__main__':
    host = 'https://www.rit.edu'

    # print("RIT CSec Courses...")
    # WAS_Lab3_A1_1()
    
    # print("Downloading Images...")
    WAS_Lab3_A1_2()
    
    # print("Looking for URLs/Emails at rit.edu...")
    # WAS_Lab3_A2_1_3('csec.rit.edu',  depth=4)
    # print("")
    # print("Looking through companies.csv for paths...")
    # WAS_Lab3_A3_1(depth=2)
    # print("")
    # print("Building file of paths from all companies...")
    # WAS_Lab3_A3_2()

