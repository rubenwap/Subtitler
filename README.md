# Subtitler

Script made for personal use, so you might have to tweak some attributes to get it working for your case. 

What it does:

- Scans for mkv and mp4 files in a specified directory (you are supposed to schedule the script in your OS scheduler)

- Connects to the SubDB and downloads the subtitle for the new videos. 

- Connects to the TvDB and grabs info for that video

- Uses SublerCLI to create an Apple friendly version of the video

## Requirements:

- THETVDB API Credentials (get them at https://www.thetvdb.com/)
- Register your app at The SUB DB (http://thesubdb.com/)
- Install SublerCLI in your PATH (https://bitbucket.org/galad87/sublercli/downloads/)