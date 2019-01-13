from django.db import models
from django.contrib.auth.models import User

from django.db.models import Model, CharField, ManyToManyField

class Genre(Model):
    name = CharField(max_length=255, db_index=True, unique=True, null=False, blank=False)

    def __str__(self):
        return 'Genre(%s)' % self.name

class Tag(Model):
    name = CharField(max_length=255, db_index=True, unique=True, null=False, blank=False)

    def __str__(self):
        return 'Tag(%s)' % self.name

class Movie(Model):
    title = CharField(max_length=255, db_index=True, unique=True, null=False, blank=False)

    genres = ManyToManyField(Genre)
    tags = ManyToManyField(Tag)

    liked_by = ManyToManyField(User)

    def __str__(self):
        return 'Movie(%s)' % self.title

