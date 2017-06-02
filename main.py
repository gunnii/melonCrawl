# 2017.06.01
# by Gunhwi
import re
import json
import requests
import time
import os.path
from bs4 import BeautifulSoup

songInfo = dict()
year = 1984
mon = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']


def getSonginfo(age, year, mon):
    singers = []
    titles = []
    songids = []
    url = "http://www.melon.com/chart/search/list.htm"
    params = {
        'chartType': 'MO',
        'age': age,
        'year': year,
        'mon': mon,
        'classCd': 'DP0100',
        'moved': 'Y'
    }
    html = requests.get(url, params=params).text
    soup = BeautifulSoup(html, 'html.parser')

    # get singer
    for tag in soup.findAll('span', {'class':'checkEllipsis'}):
        singer = tag.text
        singers.append(singer)

    # get title
    for tag in soup.findAll('div', {'class':'ellipsis rank01'}):
        title = tag.find('strong').text
        titles.append(title)

    # get song id from lyrics button
    for tag in soup.select('a[href*=goSongDetail]'):
        js = tag['href']
        matched = re.search(r"'(\d+)'\);", js)
        if matched:
            song_id = matched.group(1)
            songids.append(song_id)

    for i in range(0, len(songids)):
        if songids[i] not in songInfo:
            songInfo[songids[i]] = singers[i] + " - " + titles[i]


def outSonginfo(info):
    with open("melon_songinfo.txt", 'w+', encoding='utf-8') as outfile:
        outfile.write(json.dumps(info, indent=4))
    print("Completed melon_songinfo.txt")


def selectAge(x):
    if x < 1990:
        return 1980
    elif x < 2000:
        return 1990
    elif x < 2010:
        return 2000
    elif x < 2020:
        return 2010


def getLyrics(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    if soup.findAll('div', {'class': 'lyric'}):
        for x in soup.findAll('div', {'class': 'lyric'}):
            lyric = x.getText(separator=u' ').strip() + '\n'
        return lyric
    elif soup.findAll('div', {'class': 'lyric_none'}):
        lyric = 0
        return lyric
    return 0


def lyricsCrawl(ids):
    result = {}
    i = 0

    for song_id in ids.keys():
        url = "http://www.melon.com/song/detail.htm?songId=" + str(song_id)
        lyric = getLyrics(url)
        if lyric != 0:
            result[song_id] = lyric
        i += 1
        time.sleep(2)
        if i % 10 == 0:
            time.sleep(5)
            print(str(i) + "개 완료 stop, sleep 5 seconds")
    return result


def outLyrics(lyric):
    with open("melon_lyrics.txt", 'w+', encoding='utf-8') as outfile:
        outfile.write(json.dumps(lyric, indent=4))
    print("Completed melon_lyrics.txt")


def checkSongs():
    # Load JSON File
    with open("melon_tester.txt", 'r+') as f:
        jload = json.load(f)
    print("총 곡수 :" + str(len(jload)))
    return jload  # dict 형태


def checklyric(i):
    # Load JSON File
    with open("melon_lyrics/melon_lyrics_" + str(i) + ".txt", 'r+') as f:
        jload = json.load(f)
    print("총 가사 개수 : " + str(len(jload)))
    return jload


def tester(ids, lyric):
    result = dict()
    for x in lyric.keys():
        if x in ids:
            result[x] = ids[x]
    return result

# songID | singer - title |  melon_songinfo.txt
# songID | lyrics |  melon_lyrics.txt

if __name__=='__main__':
    if not os.path.isfile('melon_songinfo.txt'):
        count = 2
        while True:
            if year == 2017 and count == 5:
                break
            ages = selectAge(year)
            getSonginfo(ages, year, mon[count])
            print(str(year) + "년 " + str(mon[count]) + "월 TOP 100 완료")
            count += 1
            if count > 11:
                count = 0
                year += 1

        outSonginfo(songInfo)  # write json file

    # Crawl Lyrics by song id
    if not os.path.isfile('melon_lyrics.txt'):
        songids = checkSongs()
        lyrics = lyricsCrawl(songids)
        outLyrics(lyrics)

