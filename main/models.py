from django.db import models

# Create your models here.
class FearGreed(models.Model):
    date = models.DateField(auto_now_add=True)
    index = models.IntegerField(default=0)
    name= models.CharField(max_length=50)
    def __str__(self):
        return self.index

class Crypto(models.Model):
    name = models.CharField(max_length=50)
    abv = models.CharField(max_length=50)
    img_url = models.URLField(max_length=200,default=None)
    labels = models.CharField(max_length=200,default=None, null=True)
    def __str__(self):
        return self.name

class UsuarioCrypto(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    crypto = models.ForeignKey('Crypto', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " - " + self.crypto.name

class Ico(models.Model): 
    name = models.CharField(max_length=50)
    icon_url = models.URLField(max_length=200,default=None)
    date = models.CharField(max_length=200)
    desc = models.TextField()
    url_vid = models.URLField(max_length=200,default=None, null=True)
    def __str__(self):
        return self.name
