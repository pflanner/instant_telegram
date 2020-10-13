import boto3

from io import BytesIO
from django.db.models.fields import Field
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse

import logging

from PIL import Image

from instant_telegram import settings
from .models import User, UserFollow, Photo


logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse('This is the index page.')


def users(request):
    if not request.user.is_authenticated:
        return redirect('login', next='users')

    users = [(u.username, u.user_id) for u in User.objects.all()]
    context = {
        'users': users,
    }
    template = loader.get_template('pics/users.html')

    return HttpResponse(template.render(context, request))


def user_details(request, user_id):
    if not request.user.is_authenticated:
        user_details = reverse('user_details', kwargs={'user_id': user_id})
        login = reverse('login')
        return redirect(login + '?next=' + user_details)

    user = User.objects.get(user_id=user_id)
    user_details = []

    for field in user._meta.get_fields():
        if isinstance(field, Field):
            field_val = getattr(user, field.name)
            user_details.append((field.name, field_val))

    context = {
        'username': user.username,
        'user_details': user_details,
    }
    template = loader.get_template('pics/user_details.html')

    return HttpResponse(template.render(context, request))


def user_follows(request, user_id):
    if not request.user.is_authenticated:
        return redirect('login', next='user_follows', user_id=user_id)

    me = User.objects.get(user_id=user_id)
    my_followers = UserFollow.objects.filter(followee_id=user_id)
    who_i_follow = UserFollow.objects.filter(follower_id=user_id)

    context = {}

    try:
        context['followers'] = [(u.follower.user_id, u.follower.username) for u in my_followers]
    except TypeError:
        context['followers'] = [(my_followers.follower.user_id, my_followers.follower.username)]

    try:
        context['followees'] = [(u.followee.user_id, u.followee.username) for u in who_i_follow]
    except TypeError:
        context['followees'] = [(who_i_follow.followee.user_id, who_i_follow.followee.username)]

    context['user_id'] = user_id
    context['username'] = me.username

    template = loader.get_template('pics/user_follows.html')

    return HttpResponse(template.render(context, request))


def photos(request, user_id):
    url_base = '/pics/media/'
    photos = Photo.objects.filter(user_id=user_id).order_by('-created_datetime')
    media = [
        {
            'url': url_base + photo.locator + '/',
            'media_type': photo.media_type,
            'caption': photo.caption
        }
        for photo in photos
    ]

    context = {
        'media': media,
    }

    return render(request, 'pics/photos.html', context)


def media(request, media_id):
    photo = Photo.objects.get(locator=media_id)
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=settings.S3_BUCKET, Key=media_id)

    if photo.media_type == Photo.MediaType.VIDEO:
        return HttpResponse(response['Body'].read(), content_type='video/mp4')
    else:
        return HttpResponse(_crop_image(response), content_type='image/jpeg')


def _crop_image(s3_response):
    image = Image.open(s3_response['Body'])
    w, h = image.size
    new_size = 614

    # resize so that the smaller dimension equals new_size
    if w < h:
        resize_ratio = new_size / w
    else:
        resize_ratio = new_size / h

    image = image.resize((int(w * resize_ratio), int(h * resize_ratio)))
    w, h = image.size
    x1, y1, x2, y2 = 0, 0, w, h

    # crop the resized image
    if w > new_size:
        x1 = (w - new_size) // 2
        x2 = x1 + new_size

    if h > new_size:
        y1 = (h - new_size) // 2
        y2 = y1 + new_size

    image = image.crop((x1, y1, x2, y2))
    image_bytes = BytesIO()
    image.save(image_bytes, format='JPEG')

    return image_bytes.getvalue()
