import os
import re
import sqlite3
from os import path
from moviepy import editor as mp
from pytube import Playlist, YouTube
import yt_args 
import requests
import sys

Playlist_vids = []
ReadyToDownload = []

def main():

    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, r'music')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)

    parser = yt_args.get_args()
    args = parser.parse_args()

    PLAYLIST_URL = args.url
    FOLDER = final_directory


    try:
        print("Checking url...")
        response = requests.get(args.url)
        print("url exists\n")

    except Exception as e:
        print("url does not exists", e)
        sys.exit()

    #connect to database
    conn = sqlite3.connect('music.db')

    #function that get links from Youtube playlist 
    def GetTheLinks(url):
        pl = Playlist(url)
        pl._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")

        #Save links to Playlist_vids list
        for video_url in pl.video_urls:
            Playlist_vids.append(video_url)


    #Save Youtube links in a txt file 
    def BackupLinks():
        global Playlist_vids, ReadyToDownload

        #create cursor
        c = conn.cursor()

        for i in Playlist_vids:
            db_data = c.execute("SELECT LINK FROM MUSIC WHERE LINK = (?);",(i,))
            result = c.fetchone()
            if result:
                pass
            else:
                ReadyToDownload.append(i)

    #Check if music already in database
    def CheckIfExists(list):
        global conn, ReadyToDownload

        #connect to database
        conn = sqlite3.connect('music.db')
        c = conn.cursor()

        for i in range(len(list)):
            #print("link #{}: {}".format(i, list[i]))
            #print("num: ", list[i])
            c.execute("SELECT LINK FROM MUSIC WHERE LINK = (?) ",(list[i],))
            result = c.fetchone()
            if result:
                print("Found {}".format(result))
            else:
                ReadyToDownload.append(list[i])


    #convert Mp4 to Mp3
    def Mp4Converter():
        #folder = "C:/Users/sulta/OneDrive/Desktop/Python/Automation/youtube/usb"
        folder = final_directory
        for file in os.listdir(folder):
            if re.search('mp4', file):
                mp4_path = os.path.join(folder,file)
                mp3_path = os.path.join(folder,os.path.splitext(file)[0]+'.mp3')
                new_file = mp.AudioFileClip(mp4_path)
                new_file.write_audiofile(mp3_path)
                os.remove(mp4_path)



    #connect to database
    conn = sqlite3.connect('music.db')

    #create cursor
    c = conn.cursor()

    #checks if table exists in database file
    c.execute("SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='MUSIC';")
    if c.fetchone()[0]==1:
        TABLE_EXISTS = True
        print("Table Exists")
    else:
        TABLE_EXISTS = False
        print("Table does not exist - creating table...")

    #create db if not exists
    if TABLE_EXISTS == False:
        c.execute("""CREATE TABLE MUSIC(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            TITLE TEXT,
            LINK TEXT );
            """)
        conn.commit
        #conn.close

    else:
        print("File already exists. Ignoring creation!")

    
    

    #Call GetTheLinks() function
    GetTheLinks(PLAYLIST_URL)
    print("\nNumber of Videos in playlist: ", len(Playlist_vids))
    
    #Check if url exists in database and save it in ReadyToDownload list
    #Call CheckIfExists function
    CheckIfExists(Playlist_vids)

    #Download Playlist videos
    for link in ReadyToDownload:
        link = link.strip()
        try:
            yt = YouTube(link)
            #yt.streams.get_audio_only().download(output_path=r"C:/Users/sulta/OneDrive/Desktop/Python/Automation/youtube/usb")
            yt.streams.get_audio_only().download(output_path=final_directory)

            print(yt.title+" - has been downloaded !!!")

        except Exception as e:
            print("An Error has occurred = ", e)
            ReadyToDownload.remove(link)

    for link in ReadyToDownload:
        yt = YouTube(link)
        conn.execute("INSERT INTO MUSIC (title, link) VALUES (?, ?)", (yt.title, link))
        values = conn.execute("SELECT * FROM MUSIC ORDER BY ID DESC;")
        values = values.fetchone()

        print("ID: ", values[0])
        print("Title: ", values[1])
        print("Url: ", values[2], "\n")
        
    # Saves the data and closes the connection
    conn.commit()
    conn.close()


    #Call Mp4Converter() function  
    print("") 
    try: 
        Mp4Converter()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()