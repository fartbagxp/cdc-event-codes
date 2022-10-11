#!/usr/bin/env python3

import feedparser
import os
import re
import sys
import requests
import zipfile

from markdownTable import markdownTable
from urllib.parse import urlparse
from urllib.parse import parse_qs

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
      parsed_url = urlparse(item['link'])
      captured_value = parse_qs(parsed_url.query)['id'][0]
      code = {
        'updated': item.updated,
        'version': item.title,
        'link': item.link,
        'guid': captured_value
      }
      event_codes.append(code)
  return event_codes

def write_markdown(event_codes):
  print(markdownTable(event_codes).getMarkdown())

def unzip_and_remove(target_dir, filename):
  filepath = os.path.join(target_dir, filename)
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

  print(f'cookiejar = {s.cookies}')
  http_session_cookie = ''
  for cookie in s.cookies:
    if cookie.name == 'JSESSIONID':
      http_session_cookie = cookie.value
  print(f'cookie value is {http_session_cookie}')

  raw_data=f'callCount=1\npage=/vads/ViewValueSet.action?id={id}\nhttpSessionId={http_session_cookie}\nscriptSessionId={http_session_cookie}\nc0-scriptName=searchResultsManager\nc0-methodName=setDownloadFormat\nc0-id=0\nc0-param0=string:Text\nbatchId=0\n'

  s.post('https://phinvads.cdc.gov/vads/dwr/call/plaincall/searchResultsManager.setDownloadFormat.dwr',
    headers=headers,
    cookies=s.cookies,
    data=raw_data
  )

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
  return filename

def main():
  print('Starting Event Code lookup and collection')
  text = download_and_save_rss(VALUESET_RSS_FEED_URL, TARGET_DIR)
  if text == None:
    print('Fetching RSS failure detected: exiting program.')
    sys.exit(1)
  event_codes = summarize_rss(text)
  # write_markdown(event_codes)

  for code in event_codes:
    filename = download_valueset(code['guid'], TARGET_DIR)
    unzip_and_remove(TARGET_DIR, filename)
    
  print('Completed Event Code lookup and collection')

if __name__ == '__main__':
  main()