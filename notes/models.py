from django.db import models


class UserDetails(models.Model):
    userId = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField()


class Notes(models.Model):
    noteId = models.AutoField(primary_key=True)
    heading = models.TextField()
    content = models.TextField()
    user = models.ForeignKey(UserDetails, to_field='userId', on_delete=models.CASCADE)


class WordSet(models.Model):
    user = models.OneToOneField(UserDetails, to_field='userId', on_delete=models.CASCADE)
    wordSet = models.TextField()



# Create your models here.
