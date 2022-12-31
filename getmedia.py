import os
import hashlib
import requests
from pathlib import Path
from urllib.parse import urlsplit


def file_as_bytes(file):
    """Opens a file as a string of bytes"""
    with file:
        return file.read()


def save_file(url: str, file_path: Path):
    """Downloads an URL to a file"""
    response = requests.get(url, stream=True, timeout=30)
    assert response.status_code == 200, f"Response code was {response.status_code}"
    #TODO: Add code to compare content-type header with file extension
    with open(file_path, 'wb') as image_file:
        for chunk in response.iter_content():
            image_file.write(chunk)
    return file_path


def get_reddit_media(url: str, settings: dict):
    """Downloads media from Reddit"""
    file_name = Path(urlsplit(url).path).name
    file_extension = Path(urlsplit(url).path).suffix.lower()
    # Fix for issue with i.reddituploads.com links not having a file extension in the URL
    if not file_extension:
        file_extension = '.jpg'
        file_name += file_extension
        url += file_extension
    # Download the file
    file_path = Path(settings["media"]["media_folder"]) / file_name
    print(f'[ OK ] Downloading Reddit media at URL {url} to {file_path}, file type identified as {file_extension}')
    return save_file(url, file_path)


def get_imgur_image_media(url: str, settings: dict):
    """Retrieves a single image from an Imgur i.imgur.com link"""
    file_url = url
    file_name = Path(urlsplit(url).path).name
    file_path = save_file(file_url, Path(settings["media"]["media_folder"]) / file_name)  # Saves the image
    print(f'[ OK ] Downloading Imgur media at URL {file_url} to {file_path}')
    return file_path


def get_imgur_endpoint(url: str, object: str, settings: dict):
    """Retrieves the info of any object/ID pair from the API"""
    object_id = Path(urlsplit(url).path).stem  # Get the object ID
    response = requests.get(
        f"https://api.imgur.com/3/{object}/{object_id}",
        headers={'Authorization': f'Client-ID {settings["imgur"]["client_id"]}'},
        timeout=30
    )
    # Make sure we got a 200 response code
    assert response.status_code == 200, f"Response code was {response.status_code} with body {response.text} from url {response.url}"
    return response.json()


def get_imgur_image(url: str, settings: dict):
    """Retrieves any Imgur image"""
    resp = get_imgur_endpoint(url, "image", settings)
    # Call the image downloader on the image link
    return get_imgur_image_media(resp["data"]["link"], settings)


def get_imgur_album(url: str, settings: dict):
    """Retrieves any Imgur album"""
    resp = get_imgur_endpoint(url, "album", settings)
    # Call the image downloader on the first image link of the album
    return get_imgur_image_media(resp["data"]["images"][0]["link"], settings)


def get_imgur_gallery(url: str, settings: dict):
    """Retrieves any Imgur image or album within a gallery"""
    resp = get_imgur_endpoint(url, "gallery", settings)
    if resp["data"]["is_album"]:
        return get_imgur_album(url, settings)
    else:
        return get_imgur_image(url, settings)


def get_imgur_media(url: str, settings: dict):
    """Downloads any Imgur link"""
    assert settings["imgur"]["client_id"] != "", "Imgur client must not be empty"
    assert settings["imgur"]["client_secret"] != "", "Imgur client secret must not be empty"
    if "/a/" in url:  # It's an album
        return get_imgur_album(url, settings)
    elif "/gallery/" in url:  # It's a gallery
        return get_imgur_gallery(url, settings)
    else:  # It's a single image
        return get_imgur_image(url, settings)


def get_gfycat_media(url: str, settings: dict):
    """Downloads any Gfycat link"""
    gfycat_name = Path(urlsplit(url).path).stem
    response = requests.get(
        f"https://api.gfycat.com/v1/gfycats/{gfycat_name}",
        timeout=30
    )
    assert response.status_code == 200, f"Response code was {response.status_code} with body {response.text} from url {url}"
    gfycat_info: dict = response.json()
    gfycat_url: str = gfycat_info['gfyItem']['gifUrl']
    file_path = (Path(settings["media"]["media_folder"])/ gfycat_name).with_suffix('.gif')
    print(f'[ OK ] Downloading Gfycat at URL {gfycat_url} to {file_path}')
    return save_file(gfycat_url, file_path)


def get_giphy_media(url: str, settings: dict):
    # Returns any Giphy URL in a standardized format
    response = requests.get(
        f"https://giphy.com/services/oembed/?url={url}",
        timeout=30
    )
    assert response.status_code == 200, f"Response code was {response.status_code} with body {response.text} from url {url}"
    giphy_info: dict = response.json()
    giphy_url: str = giphy_info[url]
    giphy_id = Path(urlsplit(url).path).parent
    file_path = (Path(settings["media"]["media_folder"]) / giphy_id).with_suffix('.gif')
    print(f'[ OK ] Downloading Giphy at URL {giphy_url} to {file_path}')
    giphy_file = save_file(giphy_url, file_path)
    # Check the hash to make sure it's not a GIF saying "This content is not available"
    # More info: https://github.com/corbindavenport/tootbot/issues/8
    file_hash = hashlib.md5(file_as_bytes(open(giphy_file, 'rb'))).hexdigest()
    assert file_hash != '59a41d58693283c72d9da8ae0561e4e5', f'File from url {giphy_url} could not be found'
    return giphy_file


def get_media(url: str, settings: dict):
    """Retrieves static images and GIFs from popular image hosts"""
    # Make sure media folder exists
    if not Path(settings["media"]["media_folder"]).exists():
        os.makedirs(settings["media"]["media_folder"])
        print('[ OK ] Media folder not found, created a new one')
    # Download and save the linked image
    if 'redd.it' in url or 'reddituploads.com' in url:  # Reddit-hosted images
        return get_reddit_media(url, settings)
    elif 'imgur.com' in url:  # Imgur
        return get_imgur_media(url, settings)
    elif 'gfycat.com' in url:  # Gfycat
        return get_gfycat_media(url, settings)
    elif 'giphy.com' in url:  # Giphy
        return get_giphy_media(url, settings)
    else:
        # Check if URL is an image, based on the MIME type
        image_formats = ('image/png', 'image/jpeg', 'image/gif', 'image/webp')
        img_site = requests.get(url)
        meta = img_site.headers
        if meta["content-type"] in image_formats:
            # URL appears to be an image, so download it
            file_name = Path(urlsplit(url).path).name
            file_path = Path(settings["media"]["media_folder"]) / file_name
            print(f'[ OK ] Downloading file at URL {url} to {file_path}')
            try:
                img = save_file(url, file_path)
                return img
            except Exception as e:
                print('[ERR ] Error while downloading image:', str(e))
                return
        else:
            raise ValueError(f'URL {url} does not point to a valid image file')
