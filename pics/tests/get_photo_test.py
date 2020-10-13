import boto3
from io import BytesIO
from PIL import Image


def media(media_id):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket='pmf-instant-telegram', Key=media_id)

    print(_crop_image(response))


def _crop_image(s3_response):
    image = Image.open(s3_response['Body'])
    w, h = image.size
    new_size = 614
    x1, y1, x2, y2 = 0, 0, w, h

    if w > new_size:
        x1 = (w - new_size) // 2
        x2 = x1 + new_size

    if h > new_size:
        y1 = (h - new_size) // 2
        y2 = y1 + new_size

    image = image.crop((x1, y1, x2, y2))
    image_bytes = BytesIO()
    image.save(image_bytes, format='JPEG')

    image.show()

    b = image_bytes.getvalue()

    return image_bytes


if __name__ == '__main__':
    media('17880279670626165')
