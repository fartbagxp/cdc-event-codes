#!/usr/bin/env python3

import feedparser
import os
import re
import requests
import zipfile

from markdownTable import markdownTable

TARGET_DIR="data/raw/"

def write(path=None, data=None):
  if data is None:
    print(f'No data provided for path: {path}')
    return
  try:
    with open(path, "w") as outfile:
      outfile.write(data)
  except IOError:
    print(f'Failed to write to {path}')

def summarize_rss(text):
  d = feedparser.parse(text)
  print("Parsing RSS feed: ")
  print(f"RSS version: {d.version}")
  print(f"Number of Event code changes: {len(d['items'])}")
  event_codes = []

  if 'items' in d:
    for item in d['items']:
      code = {
        'updated': item.updated,
        'version': item.title,
        'link': item.link
      }
      event_codes.append(code)
  return event_codes

def write_markdown(event_codes):
  print(markdownTable(event_codes).getMarkdown())

def unzip_and_remove(path, filename):
  file_name = os.path.abspath(os.path.abspath(path, file_name))
  zip_ref = zipfile.ZipFile(file_name)
  zip_ref.extractall(path)
  zip_ref.close()
  os.remove(file_name)

def download_rss():
  rss_target="https://phinvads.cdc.gov/vads/ValueSetRssFeed.xml?oid=2.16.840.1.114222.4.11.1015"
  r = requests.get(rss_target)
  return r.text

def download_valueset(id):
  s = requests.Session()
  s.get(f'http://phinvads.cdc.gov/vads/ViewValueSet.action?id={id}')
  headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34', 
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 
    'Accept-Language': 'en-US,en;q=0.5', 
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive' ,
    'Referer': f'https://phinvads.cdc.gov/vads/ViewValueSet.action?id={id}',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'iframe', 
    'Sec-Fetch-Mode': 'navigate', 
    'Sec-Fetch-Site': 'same-origin', 
    'Pragma': 'no-cache', 
    'Cache-Control': 'no-cache'
  }

  s.get('https://phinvads.cdc.gov/vads/AJAXSelectValueSetDirectDownload.action?_=1665378527294',
    headers=headers,
    cookies=s.cookies
  )

  s.get('https://phinvads.cdc.gov/vads/AJAXGenerateValueSetDirectDownload.action?_=1665378527334',
    headers=headers,
    cookies=s.cookies
  )

  req = s.get('https://phinvads.cdc.gov/vads/RetrieveValueSetDirectDownload.action', 
    headers=headers,
    cookies=s.cookies
  )

  # This seems to be the best way to figure out the filename, regardless if it's
  # encoded in utf-8 or just put into the content-disposition header.
  fname = ''
  if "Content-Disposition" in req.headers.keys():
    fname = re.findall("filename=(.+)", req.headers["Content-Disposition"])[0]
  else:
    fname = url.split("/")[-1]
  fname = fname.strip('\"')

  print(f'Downloading "{fname}"')

  with open(f'{TARGET_DIR}{fname}', 'wb') as f:
    f.write(req.content)

def main():
  print('Starting Event Code lookup and collection')
  text = download_rss()
  event_codes = summarize_rss(text)
  write_markdown(event_codes)
  # download_valueset('4FD34BBC-617F-DD11-B38D-00188B398520')
  # download_valueset('A02D2588-5E66-DE11-9B52-0015173D1785')
  # download_valueset('2FB63964-45BB-E711-ACE2-0017A477041A')
  print('Completed Event Code lookup and collection')

if __name__ == '__main__':
  main()