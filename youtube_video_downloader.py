import yt_dlp

url = input("Enter the YouTube video URL: ")

options = {
    "outtmpl": "downloads/%(title)s.%(ext)s", 
    "js_runtimes": {"node": {}},
}

audio = {
    "format": "bestaudio",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
    }]
}


with yt_dlp.YoutubeDL(options) as ydl:
    ydl.download([url])


print("Download completed!")