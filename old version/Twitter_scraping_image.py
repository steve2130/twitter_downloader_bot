# Objective: Scrap image(s) from a tweet, download it to local, and adding the credit to the image(s)' metadata 
# Date: 2025/07/23
# Version: 0.1

import os
import httpx
import asyncio
import argparse
import Twitter_Account
from pathlib import Path
from alive_progress import alive_bar

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'




async def main():

    # Get url of the twitter post via console
    # Something like this: 
    #    PS C:\Users\Steve\Documents\GitHub\Redirect\src> python Twitter_scraping_image.py Hello
    #    ['Hello']
    # parser = argparse.ArgumentParser()
    # parser.add_argument("file_path", help="Path to the text file containing the url of Twitter posts", type=str, nargs="+")
    # args = parser.parse_args()


    # Get the actual argc from console input
    Twitter_Post_Link = []
    Twitter_Post_ID = []

    # Text_File_Content = Open_Text_File(args.file_path[0])
    Text_File_Content = Open_Text_File("C:\\Users\\Steve\\Documents\\GitHub\\Redirect\\src\\t.txt")

    # make the subfolder for the images to be saved in
    # https://gist.github.com/krishh-konar/e584d3fa5e8f215618c53d6f13f669e1
    try:
        os.mkdir('twitter_images')
        os.chdir('twitter_images')
    except:
        os.chdir('twitter_images')


    for Link in Text_File_Content:
        Twitter_Post_Link.append(str(Link))
        Twitter_Post_ID.append(int(Link.split("/")[-1]))

    for tweet in Twitter_Post_ID:
        photo_url_list, username_list, Tweet_Link = await Twitter_Scraper(tweet)
        await Download_Images(photo_url_list, username_list, Tweet_Link)


    # Removing ".jpg_original" file (Created after adding metadata)
    # WILL REMOVE ANY FILE WITH ".jpg_original" AS FILE TYPE
    for filename in Path(".").glob("*.jpg_original"):
        filename.unlink()
        
    for filename in Path(".").glob("*.png_original"):
        filename.unlink()


    print(f"{bcolors.OKGREEN}Done!{bcolors.ENDC}")




def Open_Text_File(filename: str) -> list:
    try:
        with open(filename, "r") as file:
            content = [line.rstrip() for line in file]

        filtered_content = list(set(content))    ### Remove duplicate

        print(f"Received {len(content)} links.\n")
        print(f"{len(filtered_content)} unique tweets will be scraped now.")

        return filtered_content

    except FileNotFoundError:
        print(f'{bcolors.FAIL}This file does not exist.{bcolors.ENDC}')

    except:
        print(f"{bcolors.FAIL}Error reading text file.{bcolors.ENDC}")







async def Twitter_Scraper(Tweet_ID: str) -> dict:

    media_url = []
    username_list = []
    Tweet_Link = []


    try:
        r = requests.get(f'https://api.vxtwitter.com/Twitter/status/{Tweet_ID}')
        r.raise_for_status()
        res =  r.json()

    except requests.exceptions.JSONDecodeError: # the api likely returned an HTML page, try looking for an error message
        # <meta content="{message}" property="og:description" />
        if match := re.search(r'<meta content="(.*?)" property="og:description" />', r.text):
            raise APIException(f'API returned error: {html.unescape(match.group(1))}')
        raise


    try:
        tweet_url = str(res["tweetURL"])
        tweet_author = str(res["user_screen_name"])
        tweet_media = res['media_extended']

    except:
        print(f'{bcolors.FAIL}Error when extracting tweet metadata.{bcolors.ENDC}')

    try:
        processed_url_list = []

        for url in tweet_media:
            processed_url = Process_Media_url(url)
            processed_url_list.append(processed_url)

    except:


    try:




def Process_Media_url(url: str):
    file_type = url.split(".")[-1]

    # To get the image that has the largest resolution
    if file_type == "jpg":
        url = url.replace(".jpg", "?format=jpg&name=orig")
    
    elif file_type == "png":
        url = url.replace(".png", "?format=png&name=orig")


    url = str(url)

    return url





async def Download_Images(url_list: list, username_list: list, Tweet_Link: list) -> None:
    headers = {
        'Host': 'pbs.twimg.com',
        'method': 'GET',
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image,webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'macOS',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
        
    NumberOfLinks = len(Tweet_Link)
    with alive_bar(NumberOfLinks) as bar:
        # remove the "?format=jpg&name=orig"
        for url, username, Tweet in zip(url_list, username_list, Tweet_Link):
            # Making the filename for the image
            try:
                if "?format" in url:
                    filename = url.split("?format")[0].split("/")[-1]
                    filename = filename + ".jpg"

                else:
                    filename = str(url.split("/")[-1])

            except:
                print(f"{bcolors.FAIL}Error when making a file name for {filename}{bcolors.ENDC}")


            # download images
            try: 
                client = httpx.AsyncClient(http2=True)
                response = await client.get(url, headers=headers)
            
            except:
                print(f"{bcolors.FAIL}Cannot connect to <{url}>{bcolors.ENDC}")


            # Saving the image
            try:
                with open(filename, "wb") as file:
                    file.write(response.content)
                
                Editing_Metadata(str(username), str(filename), str(Tweet))

                print(f"{filename}✅", end="\r")  ### For progress bar
                bar()
                
            except:
                print(f"{bcolors.FAIL}Error when saving {filename}{bcolors.ENDC}")








def Editing_Metadata(image_file: obj, tweet_author: str, tweet_url: str, Tweet_ID: str):
    try:
        tweet_image = Image(image_file)
        tweet_image.artist = "@" + tweet_author
        tweet_image.copyright = tweet_url

        

    except:
        print(f"{bcolors.FAIL}Error when adding metadata for {Tweet_ID}{bcolors.ENDC}")



if __name__ == "__main__":
    print(f"Downloaded images will be stored in the current path.")
    asyncio.run(main())