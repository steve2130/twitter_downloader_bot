from exif import Image

def adding_exif_to_image(image: obj, tweet_url: str, tweet_author: str) -> obj:
    tweet_image = Image(image_file)
    tweet_image.artist = "@" + tweet_author
    tweet_image.copyright = tweet_url

    return tweet_image