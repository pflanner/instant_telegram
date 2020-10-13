import os
import json
import requests


def download(instagram_response_filename, dest_dir):
    """
    Parse a response from the Instagram Basic Display API and download all photos and videos from it
    :param instagram_response_filename: json response from 'https://graph.instagram.com/me/media?fields=id,caption...
    :param dest_dir: the directory in which to restore the downloaded files
    """
    with open(instagram_response_filename) as f:
        response_json = json.load(f)
        num_media = len(response_json['data'])
        count = 1

        for meta in response_json['data']:
            media_url = meta['media_url']
            media_id = meta['id']
            media = requests.get(media_url)
            media_type = meta['media_type']
            dest_filename = media_id

            if media_type == 'VIDEO':
                dest_filename += '.mp4'
            else:
                dest_filename += '.jpg'

            dest_full_path = os.path.join(dest_dir, dest_filename)

            with open(os.path.join(dest_full_path), mode='wb') as write_file:
                write_file.write(media.content)
                print('wrote {} of {}'.format(count, num_media))
                count += 1
