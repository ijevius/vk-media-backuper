import os
import sys
import json
import time
import wget
import platform
import urllib.request

VK_ACCESS_TOKEN = ""
VK_BASE_API_URL = "https://api.vk.com/method/"
VK_API_VERSION = "5.103" #don't change, work was tested only for that.

def VK_getAllUrlsFromAlbum(album_id):
    all_photos = set()
    BUCKET_SIZE = 1000
    '''Count of photos in one step. Max is 1000.
    Don't set in too small -- this cause many API requests, so VK will return an error. 25 is too small. 
    id -- current VK user or group id; rev -- from latest; photo_sizes=0, latest item is biggest size,
    even VK says size['o'] is original; offset M -- skip M items from start'''
    #print(albumResponse['response']['items'])
    getFromAlbumReq = f"{VK_BASE_API_URL}photos.get?owner_id={id}&album_id={album_id}&rev=1&photo_sizes=0&count={BUCKET_SIZE}&offset=0&v={VK_API_VERSION}&access_token={VK_ACCESS_TOKEN}"
    albumResponse = json.loads(urllib.request.urlopen(getFromAlbumReq).read())
    try:
        albumLen = albumResponse["response"]["count"]
        albumPartUrls = [item['sizes'][-1]["url"] for item in albumResponse['response']['items']]
        all_photos.update(albumPartUrls)
    except:
        print(f"Can't parse it:\n{albumResponse}")
    steps = (int(albumLen/BUCKET_SIZE)+1) if albumLen > BUCKET_SIZE else 1
    if steps > 1:
        for i in range(1, steps):
            offset = i*BUCKET_SIZE
            getFromAlbumReq = f"{VK_BASE_API_URL}photos.get?owner_id={id}&album_id={album_id}&rev=1&photo_sizes=0&count={BUCKET_SIZE}&offset={offset}&v={VK_API_VERSION}&access_token={VK_ACCESS_TOKEN}"
            albumResponse = json.loads(urllib.request.urlopen(getFromAlbumReq).read())
            bucket_items = albumResponse["response"]["items"]
            bucket_urls = [item['sizes'][-1]["url"] for item in bucket_items]
            all_photos.update(bucket_urls)
    return all_photos

def createDirIfNotExists(dirName):
    isDir = os.path.isdir(dirName)
    if not isDir:
        try:
            os.mkdir(dirName)
            #print(f"{dirName} at {os.getcwd()} created")
        except:
            print(f"dcreat: Can't create {dirName}")
    else:
        print(f"dcreat: Dir {os.getcwd()}{getDirsSeparator()}{dirName} is already exists")

def getDirsSeparator():
    return '\\' if "Windows" in platform.system() else '//'

def makeNamePrettyForWin(str):
    not_allowed = '/\:*?"|<>'
    for sym in not_allowed:
        if sym in str:
            str = str.replace(sym, "")
    #return str+"(name mod)"
    return str

def wgetDownload(source, dir):
    '''No need to check what is already exists.
    If so, skip it, if exists and 0 size -- fill it'''
    name = source.split('/')[-1]
    if os.path.exists(dir + name):
        if os.path.getsize(dir + name) == 0:
            os.remove(dir + name)
        else:
            print(f"{name} already exists")
            return
    try:
        wget.download(source, out=dir+name)
        print(f"{name} saved")
    except:
        print(f"Can't write and close file from url={source}")

albums_list = dict()
id = int(input("Enter id, for clubs it is -id:\n"))
ITEM_NAME = f"id={id}"
if id > 0:
    getUserNameReq = f"{VK_BASE_API_URL}users.get?user_ids={id}&v=5.103&access_token={VK_ACCESS_TOKEN}"
    un_name = json.loads(urllib.request.urlopen(getUserNameReq).read())["response"][0]['first_name'] + " " + json.loads(urllib.request.urlopen(getUserNameReq).read())["response"][0]['last_name']
    ITEM_NAME = un_name
    is_closed = json.loads(urllib.request.urlopen(getUserNameReq).read())["response"][0]['is_closed']
    can_access_closed = json.loads(urllib.request.urlopen(getUserNameReq).read())["response"][0]['can_access_closed']
    if is_closed and not can_access_closed:
        print("Profile is closed")
        sys.exit()
    print(f"Saving user: {ITEM_NAME}")
elif id < 0:
    getGroupInfoReq = f"{VK_BASE_API_URL}groups.getById?group_id={abs(id)}&fields=can_see_all_posts&v={VK_API_VERSION}&access_token={VK_ACCESS_TOKEN}"
    ITEM_NAME = json.loads(urllib.request.urlopen(getGroupInfoReq).read())["response"][0]['name']
    print(f"Saving club: {ITEM_NAME}")
else:
    print("No-no-no")
    sys.exit(0)

FOLDER_FOR_ITEM = f"{makeNamePrettyForWin(ITEM_NAME)} id={id}"
createDirIfNotExists(FOLDER_FOR_ITEM)
getAllAlbumsReq = f"{VK_BASE_API_URL}photos.getAlbums?owner_id={id}&v={VK_API_VERSION}&need_covers=1&photo_sizes=0&need_system=1&access_token={VK_ACCESS_TOKEN}"
contents = urllib.request.urlopen(getAllAlbumsReq).read()
res = json.loads(contents)
#print(res)
print(f"{res['response']['count']} albums")
try:
    items = res["response"]["items"]
    for album in items:
        albums_list.update({album['id']:f"{os.getcwd()}{getDirsSeparator()}{FOLDER_FOR_ITEM}{getDirsSeparator()}{makeNamePrettyForWin(album['title'])} id={album['id']}{getDirsSeparator()}"})
        print(f"{album['title']} id={album['id']} photos={album['size']}")
        createDirIfNotExists(f"{os.getcwd()}{getDirsSeparator()}{FOLDER_FOR_ITEM}{getDirsSeparator()}{makeNamePrettyForWin(album['title'])} id={album['id']}\\")
except:
    print(f"Can't parse it:\n{res}")

#print(albums_list)
print(albums_list.items())

total = 0
for al in albums_list.items():
    start = int(round(time.time() * 1000))
    for l in VK_getAllUrlsFromAlbum(al[0]):
        wgetDownload(l, al[1])
    end = int(round(time.time() * 1000))
    total += (end-start)/1000
    print(f"for {(end-start)/1000} sec")

print(f"{total} sec passed")
