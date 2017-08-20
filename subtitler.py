
import os
import sys
import glob
import hashlib
import requests
import json
import PTN
import time
import os

tvdb_body = {
    "apikey": os.environ["APIKEY_TV"],
    "userkey": os.environ["USERKEY_TV"],
    "username": os.environ["TV_USERNAME"]
}
header = {
    "Content-Type": "application/json"
}


r = requests.post("https://api.thetvdb.com/login",
                  headers=header, data=json.dumps(tvdb_body))


tvdb_token = r.json()["token"]

header_auth = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(tvdb_token)
}


def get_hash(name):
    readsize = 64 * 1024
    with open(name, 'rb') as f:
        size = os.path.getsize(name)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()


hashes = []
types = ["**/*mp4", "**/*.mkv"]

for single_type in types:
    for file in (glob.glob(single_type)):
        video = {}
        video["hash"] = (get_hash(file))
        video["filename"] = (file)
        hashes.append(video)


headers = {
    'User-Agent': 'SubDB/1.0 (Subtest/0.1; http://github.com/not_yet)',
}

url_search = 'http://api.thesubdb.com/?action=search&hash={}'
url_download = 'http://api.thesubdb.com/?action=download&hash={}&language=en,es'


for video in hashes:
    response = requests.get(url_search.format(video["hash"]), headers=headers)
    if ('en' or 'es') in response.text:
        download = requests.get(url_download.format(
            video["hash"]), headers=headers)
        with open("{}.srt".format(video["filename"][:-4]), "wb") as subtitle:
            subtitle.write(download.content)


for video in hashes:
    metadata = PTN.parse(video["filename"][video["filename"].find("/") + 1:])
    id_req = requests.get(
        "https://api.thetvdb.com/search/series?name={}".format(metadata["title"]), headers=header_auth)
    video["id"] = id_req.json()["data"][0]["id"]
    video["Series"] = id_req.json()["data"][0]["seriesName"]
    ep_req = requests.get("https://api.thetvdb.com/series/{}/episodes/query?airedSeason={}&airedEpisode={}&Accept-Language=en".format(
        video["id"], metadata["season"], metadata["episode"]), headers=header_auth)
    video["Name"] = ep_req.json()["data"][0]["episodeName"]
    video["Season"] = str(ep_req.json()["data"][0]["airedSeason"])
    video["Episode"] = str(ep_req.json()["data"][0]["airedEpisodeNumber"])


cwd = os.getcwd()


for video in hashes:

    name = video["Name"]
    tvshow = video["Series"]
    season = video["Season"]
    episode = video["Episode"]

    subler_command = r"{}/SublerCLI -dest {}/{} -metadata '{}' -optimize -source {}/{}".format(
        cwd, cwd, video["filename"][0:-3] + "m4v", "{Name:" + name + "}{TV Show:" + tvshow + "}{TV Season:" + season + "}{TV Episode #:" + episode + "}{Media Kind:TV Show}", cwd, video["filename"])
    subler_command_srt = r"'{}/SublerCLI' -source '{}/{}' -language English -dest '{}/{}'".format(
        cwd, cwd, video["filename"][0:-3] + "srt", cwd, video["filename"][0:-3] + "m4v")
    os.rename(video["filename"][0:-3] + "m4v", "/Users/ruben/Music/iTunes/iTunes Media/Automatically Add to iTunes.localized/" +
              video["filename"][video["filename"].find("/") + 1:-3] + "m4v")
