from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class User(User):
    pass

class Applicant(User):
    pass

class Application(models.Model):
    pass
    applicant = models.ForeignKey(Applicant)
