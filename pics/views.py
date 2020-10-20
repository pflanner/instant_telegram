import boto3

from django.contrib.auth import authenticate, login
from django.db.models.fields import Field
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse
from django.utils import timezone

from io import BytesIO
import logging
from operator import attrgetter
from random import randint

from PIL import Image

from instant_telegram import settings
from .forms import SignUpForm
from .models import User, UserFollow, Photo, Like

logger = logging.getLogger(__name__)


def index(request):
    return feed(request)


def users(request):
    if not request.user.is_authenticated:
        users = reverse('users')
        login = reverse('login')
        return redirect(login + '?next=' + users)

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
        user_follows = reverse('user_follows', kwargs={'user_id': user_id})
        login = reverse('login')
        return redirect(login + '?next=' + user_follows)

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
    if not request.user.is_authenticated:
        photos = reverse('photos', kwargs={'user_id': user_id})
        login = reverse('login')
        return redirect(login + '?next=' + photos)

    photos = Photo.objects.filter(user_id=user_id).order_by('-created_datetime')
    media = [
        {
            'url': reverse('media', kwargs={'media_id': photo.locator}),
            'media_type': photo.media_type,
            'caption': photo.caption
        }
        for photo in photos
    ]

    user = User.objects.get(user_id=user_id)

    context = {
        'media': media,
        'username': user.username,
        'user_id': user_id,
        'is_following': _is_following(request.user.user_id, user_id),
    }

    return render(request, 'pics/photos.html', context)


def media(request, media_id):
    if not request.user.is_authenticated:
        return redirect('login')

    photo = Photo.objects.get(locator=media_id)
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=settings.S3_BUCKET, Key=media_id)

    if photo.media_type == Photo.MediaType.VIDEO:
        return HttpResponse(response['Body'].read(), content_type='video/mp4')
    else:
        return HttpResponse(_crop_image(response), content_type='image/jpeg')


def feed(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login') + '?next=' + reverse('feed'))

    # simple feed algorithm
    # get the top 25 most recent pictures from everyone this user follows
    # and pick the most recent 25 out of all of them
    follows = UserFollow.objects.filter(follower_id=request.user.user_id)
    all_photos = []

    for follow in follows:
        all_photos.extend(Photo.objects.filter(user_id=follow.followee_id).order_by('-created_datetime')[:25])

    all_photos.sort(key=attrgetter('created_datetime'), reverse=True)
    media = [
        {
            'username': photo.user.username,
            'url': reverse('media', kwargs={'media_id': photo.locator}),
            'media_type': photo.media_type,
            'caption': photo.caption
        }
        for photo in all_photos
    ]
    context = {
        'media': media,
        'username': request.user.username,
    }

    return render(request, 'pics/feed.html', context)


def post(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    if not hasattr(request, 'FILES') or not request.FILES:
        return HttpResponseBadRequest()

    # only taking the first image for now
    media = next(iter(request.FILES.values()))

    caption = request.POST.get('caption', None)
    logger.debug('caption={}'.format(caption))

    new_image_locator = _new_image_locator()
    logger.debug('new_image_locator={}'.format(new_image_locator))

    s3 = boto3.client('s3')
    s3.put_object(Bucket=settings.S3_BUCKET, Key=new_image_locator, Body=media)

    Photo.objects.create(
        user_id=request.user.user_id,
        caption=caption,
        locator=new_image_locator,
        media_type=Photo.MediaType.IMAGE,
        created_datetime=timezone.now(),
    )

    return HttpResponse()


def follow(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    if request.user.user_id == user_id:
        return HttpResponseBadRequest()

    if _is_following(request.user.user_id, user_id):
        return HttpResponse()

    try:
        user_follow = UserFollow.objects.get(follower_id=request.user.user_id, followee_id=user_id)
        user_follow.follow_datetime = timezone.now()
        user_follow.save()
    except UserFollow.DoesNotExist:
        UserFollow.objects.create(
            follower_id=request.user.user_id,
            followee_id=user_id,
            follow_datetime=timezone.now()
        )

    return HttpResponse()


def unfollow(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    if request.user.user_id == user_id:
        return HttpResponseBadRequest()

    if not _is_following(request.user.user_id, user_id):
        return HttpResponse()

    user_follow = UserFollow.objects.get(follower_id=request.user.user_id, followee_id=user_id)
    user_follow.unfollow_datetime = timezone.now()
    user_follow.save()

    return HttpResponse()


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.modified_datetime = timezone.now()
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('feed')
    else:
        form = SignUpForm()
    return render(request, 'pics/signup.html', {'form': form})


def like(request, photo_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    Like.objects.create(user_id=request.user.user_id, photo_id=photo_id, like_datetime=timezone.now())

    return HttpResponse()


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


def _new_image_locator():
    locator_length = 17
    num_attempts = 1000000

    for _ in range(num_attempts):
        locator = []

        for _ in range(locator_length):
            locator.append(str(randint(0, 9)))

        locator_str = ''.join(locator)

        if not Photo.objects.filter(locator=locator_str).exists():
            return locator_str

    raise RuntimeError('could generate a new image locator within {} iterations'.format(num_attempts))


def _is_following(follower_id, followee_id):
    user_follows = UserFollow.objects.filter(follower_id=follower_id, followee_id=followee_id)

    if user_follows.exists():
        user_follow = user_follows[0]

        if not user_follow.unfollow_datetime or user_follow.unfollow_datetime < user_follow.follow_datetime:
            return True

    return False
