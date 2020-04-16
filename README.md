# vk-media-backuper

## Requries
wget, urllib.request. Use: `pip install`.

## Notes
Sure your disk has enouth space.
Be careful! Frequent writes to disk may may damage it. 
Speed depends on your machine and network connection.
Read my comments -- incorrect params due initialization may cause some problems.
I don't have tested it on *nix.


## Authenicaton 
First you need get access_token for you. Create your own standalone app at https://vk.com/editapp?act=create. Then read https://vk.com/dev/implicit_flow_user. Or you can use my app, go to https://oauth.vk.com/authorize?client_id=7413734&display=page&scope=friends,photos,groups,offline&response_type=code&v=5.103. 
