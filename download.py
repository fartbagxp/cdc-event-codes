#!/usr/bin/env python3

import feedparser
import os
import re
import sys
import requests
import zipfile

from markdownTable import markdownTable

TARGET_DIR="data/raw/"
VALUESET_RSS_FEED_URL="https://phinvads.cdc.gov/vads/ValueSetRssFeed.xml?oid=2.16.840.1.114222.4.11.1015"

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

def unzip_and_remove(target_dir, filename):
  filepath = os.path.abspath(os.path.join(target_dir, filename))
  zip_ref = zipfile.ZipFile(filepath)
  zip_ref.extractall(target_dir)
  zip_ref.close()
  os.remove(filepath)

def get_url_filename(url, headers):
  filename = ''
  if "Content-Disposition" in headers.keys():
    filename = re.findall("filename=(.+)", headers["Content-Disposition"])[0]
  else:
    filename = url.split("/")[-1].split("?")[0]
  filename = filename.strip('\"')
  return filename

def download_and_save_rss(url, target_path):
  r = requests.get(url)
  try: 
    if r and r.text and r.headers and r.status_code == 200:
      filename = get_url_filename(url, r.headers)

      filepath = os.path.join(target_path, filename)
      print(f'Saving RSS file to {filepath}.')
      write(filepath, r.text)
      return r.text
  except Exception as err:
    print(f'Exception error caught during RSS fetching: {err}')
    return None

def download_valueset(id, target_path):
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

  res = s.get('https://phinvads.cdc.gov/vads/RetrieveValueSetDirectDownload.action', 
    headers=headers,
    cookies=s.cookies
  )

  # This seems to be the best way to figure out the filename, regardless if it's
  # encoded in utf-8 or just put into the content-disposition header.
  filename = get_url_filename(res.url, res.headers)

  print(f'Downloading "{filename}"')
  filepath = os.path.join(target_path, filename)
  with open(filepath, 'wb') as f:
    f.write(res.content)

def main():
  print('Starting Event Code lookup and collection')
  text = download_and_save_rss(VALUESET_RSS_FEED_URL, TARGET_DIR)
  if text == None:
    print('Fetching RSS failure detected: exiting program.')
    sys.exit(1)
  event_codes = summarize_rss(text)
  # write_markdown(event_codes)

  download_valueset('4FD34BBC-617F-DD11-B38D-00188B398520', TARGET_DIR)
  download_valueset('A02D2588-5E66-DE11-9B52-0015173D1785', TARGET_DIR)
  download_valueset('2FB63964-45BB-E711-ACE2-0017A477041A', TARGET_DIR)
  print('Completed Event Code lookup and collection')

if __name__ == '__main__':
  main()