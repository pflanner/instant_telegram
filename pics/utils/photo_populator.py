import boto3
from botocore.exceptions import ClientError
from django.utils import timezone
import json
import logging
import os

from pics.models import Photo


BASE_DIR = '../static/images/'
S3_BUCKET = os.getenv('S3_BUCKET')


def populate(instagram_response_filename):
    with open(instagram_response_filename) as f:
        response_json = json.load(f)
        num_media = len(response_json['data'])
        count = 1

        for meta in response_json['data']:
            media_id = meta['id']
            media_type = meta['media_type']

            timestamp = meta['timestamp']
            timestamp = timestamp[:-2] + ':' + timestamp[-2:]
            d = timezone.datetime.fromisoformat(timestamp)
            filename = media_id
            filename += '.mp4' if media_type == 'VIDEO' else '.jpg'
            file_path = os.path.join(BASE_DIR, filename)

            if upload_to_s3(file_path, S3_BUCKET, media_id):
                p = Photo(locator=media_id, created_datetime=d, user_id=1)
                p.save()
                print('saved photo {} of {}'.format(count, num_media))
            else:
                print('photo {} of {} failed'.format(count, num_media))

            count += 1


def add_caption_and_media_type(instagram_response_filename):
    with open(instagram_response_filename) as f:
        response_json = json.load(f)
        num_media = len(response_json['data'])
        count = 1

        for meta in response_json['data']:
            media_id = meta['id']
            media_type = meta['media_type']

            photo = Photo.objects.get(locator=media_id)
            if 'caption' in meta and meta['caption']:
                photo.caption = meta['caption']

            photo.media_type = media_type
            photo.save()

            print('updated {} of {}'.format(count, num_media))
            count += 1


def compare(response1_path, response2_path):
    response1 = set()
    response2 = set()

    with open(response1_path) as f:
        response_json = json.load(f)

        for meta in response_json['data']:
            response1.add(meta['id'])

    with open(response2_path) as f:
        response_json = json.load(f)

        for meta in response_json['data']:
            response2.add(meta['id'])

    print(response1 == response2)


def upload_to_s3(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        logging.debug(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True
