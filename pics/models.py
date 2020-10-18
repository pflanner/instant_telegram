from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    date_of_birth = models.DateTimeField(null=True, blank=True)
    modified_datetime = models.DateTimeField(null=True, blank=True)
    deleted_at_datetime = models.DateTimeField(null=True, blank=True)
    last_logout_datetime = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.modified_datetime = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return 'id={} username={}'.format(self.user_id, self.username)


class Photo(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = 'IMAGE'
        CAROUSEL_ALBUM = 'CAROUSEL_ALBUM'
        VIDEO = 'VIDEO'

    photo_id = models.AutoField(primary_key=True)
    media_type = models.CharField(max_length=20, choices=MediaType.choices, default=MediaType.IMAGE)
    user = models.ForeignKey(User, models.DO_NOTHING)
    locator = models.CharField(max_length=255)
    caption = models.TextField(max_length=2200, null=True, blank=True)
    photo_lat = models.FloatField(null=True, blank=True)
    photo_long = models.FloatField(null=True, blank=True)
    user_lat = models.FloatField(null=True, blank=True)
    user_long = models.FloatField(null=True, blank=True)
    created_datetime = models.DateTimeField()

    class Meta:
        db_table = 'photos'

    def __str__(self):
        return 'photo_id={} locator={}'.format(self.photo_id, self.locator)


class UserFollow(models.Model):
    user_follow_id = models.AutoField(primary_key=True)
    followee = models.ForeignKey(User, models.DO_NOTHING, related_name='followee')
    follower = models.ForeignKey(User, models.DO_NOTHING, related_name='follower')
    follow_datetime = models.DateTimeField()
    unfollow_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'user_follows'
        unique_together = [['followee_id', 'follower_id']]
        indexes = [
            models.Index(fields=['followee_id']),
            models.Index(fields=['follower_id']),
        ]

    def __str__(self):
        return 'followee_id={} follower_id={}'.format(self.followee, self.follower)
#JF5RK