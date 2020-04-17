import os
import sys
import json
import time
import wget
import datetime
import platform
import urllib.request

VK_ACCESS_TOKEN = ""
VK_BASE_API_URL = "https://api.vk.com/method/"
VK_API_VERSION = "5.103" #don't change, work was tested only for that.
DIRS_SEPARATOR = '\\' if "Windows" in platform.system() else '//'

def VK_getAllUrlsFromAlbum(album_id):
    all_photos = set()
    BUCKET_SIZE = 1000
    '''Count of photos in one step. Max is 1000.
    Don't set in too small -- this cause many API requests, so VK will return an error. 25 is too small. 
    id -- current VK user or group id; rev -- from oldest; photo_sizes=0, latest item is biggest size,
    even VK says size['o'] is original; offset M -- skip M items from start'''
    #print(albumResponse['response']['items'])
    getFromAlbumReq = f"{VK_BASE_API_URL}photos.get?owner_id={id}&album_id={album_id}&rev=0&photo_sizes=0&count={BUCKET_SIZE}&offset=0&v={VK_API_VERSION}&access_token={VK_ACCESS_TOKEN}"
    albumResponse = json.loads(urllib.request.urlopen(getFromAlbumReq).read())
    try:
        albumLen = albumResponse["response"]["count"]
        albumPartUrls = [item['sizes'][-1]["url"] for item in albumResponse['response']['items']]
        all_photos.update(albumPartUrls)
    except:
        print(f"urlscollector: Can't parse it:\n{albumResponse}")
    steps = (int(albumLen/BUCKET_SIZE)+1) if albumLen > BUCKET_SIZE else 1
    if steps > 1:
        for i in range(1, steps):
            offset = i*BUCKET_SIZE
            #wall -- to get all photos from wall (actually for club)
            getFromAlbumReq = f"{VK_BASE_API_URL}photos.get?owner_id={id}&album_id={album_id}&rev=0&photo_sizes=0&count={BUCKET_SIZE}&offset={offset}&v={VK_API_VERSION}&access_token={VK_ACCESS_TOKEN}"
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
        print(f"dcreat: Dir {os.getcwd()}{DIRS_SEPARATOR}{dirName} is already exists")

def makeNamePretty(str):
    not_allowed = '!@#$&~%*()[]{}\'"\:;<>`' #and space?
    if "Windows" in platform.system():
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
FOLDER_FOR_ITEM = ITEM_NAME
if id > 0:
    getUserNameReq = f"{VK_BASE_API_URL}users.get?user_ids={id}&v=5.103&access_token={VK_ACCESS_TOKEN}"
    un_name = json.loads(urllib.request.urlopen(getUserNameReq).read())["response"][0]['first_name'] + " " + json.loads(urllib.request.urlopen(getUserNameReq).read())["response"][0]['last_name']
    ITEM_NAME = un_name
    FOLDER_FOR_ITEM = f"{makeNamePretty(ITEM_NAME)} id={id}"
    createDirIfNotExists(FOLDER_FOR_ITEM)
    #is_closed = json.loads(urllib.request.urlopen(getUserNameReq).read())["response"][0]['is_closed']
    can_access_closed = json.loads(urllib.request.urlopen(getUserNameReq).read())["response"][0]['can_access_closed']
    #if is_closed and not can_access_closed:
    if not can_access_closed:
        print("Profile is closed")
        sys.exit()
    print(f"Saving user: {ITEM_NAME}")
    getFriendsReq = f"{VK_BASE_API_URL}friends.get?user_id={id}&oder=hints&fields=city&name_case=nom&v={VK_API_VERSION}&access_token={VK_ACCESS_TOKEN}"
    # domain,sex,bdate
    friends = json.loads(urllib.request.urlopen(getFriendsReq).read())['response']
    r_list = friends["items"]
    print(r_list)
    now = int(round(time.time() * 1000))
    now = datetime.datetime.fromtimestamp(now / 1000.0)
    now = str(now).replace(":", "-").replace(".", "-")  # TODO makeNamePretty
    friends_file_name = f'friends list on {now}.txt'
    fr_list_buffer = ""
    for fr_item in r_list:
        friend_id = fr_item['id']
        fr_first_name = fr_item['first_name']
        fr_last_name = fr_item['last_name']
        fr_city = ""
        if "city" in fr_item:
            fr_city = fr_item['city']['title']
        friend_pattern = f"vk.com/id{friend_id} - {fr_first_name} {fr_last_name} - {fr_city}\n"
        fr_list_buffer += friend_pattern
    if friends["count"] > 5000:
        next_part = f"{VK_BASE_API_URL}friends.get?user_id={id}&oder=hints&offset=5000&fields=city&name_case=nom&v={VK_API_VERSION}&access_token={VK_ACCESS_TOKEN}"
        part = json.loads(urllib.request.urlopen(next_part).read())['response']['items']
        fr_list_buffer.append(part)
    f = open(f'{os.getcwd()}{DIRS_SEPARATOR}{FOLDER_FOR_ITEM}{DIRS_SEPARATOR}{friends_file_name}', 'a', encoding='utf-8')
    print(fr_list_buffer.strip())
    f.write(fr_list_buffer)
    f.close()
    # print(friends)
elif id < 0:
    getGroupInfoReq = f"{VK_BASE_API_URL}groups.getById?group_id={abs(id)}&fields=can_see_all_posts&v={VK_API_VERSION}&access_token={VK_ACCESS_TOKEN}"
    ITEM_NAME = json.loads(urllib.request.urlopen(getGroupInfoReq).read())["response"][0]['name']
    FOLDER_FOR_ITEM = f"{makeNamePretty(ITEM_NAME)} id={id}"
    print(f"Saving club: {ITEM_NAME}")
else:
    print("No-no-no")
    sys.exit(0)

getAllAlbumsReq = f"{VK_BASE_API_URL}photos.getAlbums?owner_id={id}&v={VK_API_VERSION}&need_covers=1&photo_sizes=0&need_system=1&access_token={VK_ACCESS_TOKEN}"
contents = urllib.request.urlopen(getAllAlbumsReq).read()
res = json.loads(contents)
#print(res)
print(f"{res['response']['count']} albums")
try:
    items = res["response"]["items"]
    #print(items)
    for album in items:
        albums_list.update({album['id']:f"{os.getcwd()}{DIRS_SEPARATOR}{FOLDER_FOR_ITEM}{DIRS_SEPARATOR}{makeNamePretty(album['title'])} id={album['id']}{DIRS_SEPARATOR}"})
        print(f"{album['title']} id={album['id']} photos={album['size']}")
        createDirIfNotExists(f"{os.getcwd()}{DIRS_SEPARATOR}{FOLDER_FOR_ITEM}{DIRS_SEPARATOR}{makeNamePretty(album['title'])} id={album['id']}\\")
except:
    print(f"118: Can't parse it:\n{res}")

#print(albums_list)
print(albums_list.items())

total = 0
for album in albums_list.items():
    start = int(round(time.time() * 1000))
    #skip saved photos: check al[0]==-15
    if album[0] == -15 or album[0] == -9000: continue
    for link in VK_getAllUrlsFromAlbum(album[0]):
        wgetDownload(link, album[1])
    end = int(round(time.time() * 1000))
    total += (end-start)/1000
    print(f"for {(end-start)/1000} sec")

print(f"{total} sec per profile")
