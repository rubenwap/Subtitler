
import os
import sys
import glob
import hashlib
import requests
import json
import PTN
import time
import os

# REQUIREMENTS:
# You need to have TVDB API credentials in your environment:
# APIKEY_TV
# USERKEY_TV
# TV_USERNAME

# This function obtains the login token of TVDB based on your credentials


def tvdb_login():
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
    return r.json()["token"]

# This function gets the hash of a filename
# It will be used to search in the DB for the hash instead of the name


def get_hash(name):
    readsize = 64 * 1024
    with open(name, 'rb') as f:
        size = os.path.getsize(name)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()

# Builds a list of hashes in directory
# If you want to adapt it so it searches elsewhere, modify the glob.glob path


def hash_list():
    hashes = []
    types = ["**/*mp4", "**/*.mkv"]

    for single_type in types:
        for file in (glob.glob(single_type)):
            video = {}
            video["hash"] = (get_hash(file))
            video["filename"] = (file)
            hashes.append(video)

    return hashes

# Gets subtitles of passed file hash, just if english or spanish exist. Modify the 'en' or 'es' if you need


def get_subtitles(video):

    headers = {
        'User-Agent': 'SubDB/1.0 (Subtitler/0.1; https://github.com/rubenwap/Subtitler)',
    }
    url_search = 'http://api.thesubdb.com/?action=search&hash={}'
    url_download = 'http://api.thesubdb.com/?action=download&hash={}&language=en,es'

    response = requests.get(url_search.format(
        video["hash"]), headers=headers)
    if ('en' or 'es') in response.text:
        download = requests.get(url_download.format(
            video["hash"]), headers=headers)
        with open("{}.srt".format(video["filename"][:-4]), "wb") as subtitle:
            subtitle.write(download.content)

# Logs into TVDB with the token created in the tvdb_login function and retrieves metadata of the video


def get_metadata(video):

    tvdb_token = tvdb_login()
    header_auth = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(tvdb_token)
    }

    metadata = PTN.parse(
        video["filename"][video["filename"].find("/") + 1:])
    id_req = requests.get(
        "https://api.thetvdb.com/search/series?name={}".format(metadata["title"]), headers=header_auth)
    video["id"] = id_req.json()["data"][0]["id"]
    video["Series"] = id_req.json()["data"][0]["seriesName"]
    ep_req = requests.get("https://api.thetvdb.com/series/{}/episodes/query?airedSeason={}&airedEpisode={}&Accept-Language=en".format(
        video["id"], metadata["season"], metadata["episode"]), headers=header_auth)
    video["Name"] = ep_req.json()["data"][0]["episodeName"]
    video["Season"] = str(ep_req.json()["data"][0]["airedSeason"])
    video["Episode"] = str(ep_req.json()["data"][0]["airedEpisodeNumber"])

# Creates the final m4v file with the metadata tags that I need. You may add or remove items in the subler_command
# Also, notice that the m4v are being added to my automatic iTunes folder. You need to change that path to reuse the script yourself


def save_final_file(video):
    cwd = os.getcwd()

    name = video["Name"]
    tvshow = video["Series"]
    season = video["Season"]
    episode = video["Episode"]

    subler_command = r"{}/SublerCLI -dest {}/{} -metadata '{}' -optimize -source {}/{}".format(
        cwd, cwd, video["filename"][0:-3] + "m4v", "{Name:" + name + "}{TV Show:" + tvshow + "}{TV Season:" + season + "}{TV Episode #:" + episode + "}{Media Kind:TV Show}", cwd, video["filename"])
    subler_command_srt = r"'{}/SublerCLI' -source '{}/{}' -language English -dest '{}/{}'".format(
        cwd, cwd, video["filename"][0:-3] + "srt", cwd, video["filename"][0:-3] + "m4v")
    os.system(subler_command)
    os.system(subler_command_srt)
    os.rename(video["filename"][0:-3] + "m4v", "/Users/ruben/Music/iTunes/iTunes Media/Automatically Add to iTunes.localized/" +
              video["filename"][video["filename"].find("/") + 1:-3] + "m4v")


if __name__ == '__main__':

    for video in hash_list():
        get_subtitles(video)
        get_metadata(video)
        save_final_file(video)
