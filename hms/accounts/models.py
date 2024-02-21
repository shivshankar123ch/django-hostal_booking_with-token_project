from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.core.exceptions import PermissionDenied


# Create your models here.

class Room(models.Model):
    no = models.CharField(max_length=5, default=None, unique=True)
    cover = models.ImageField(upload_to='images/')
    room_choice = [('S', 'Single Room'), ('D', 'Double Room'), ('T', 'Triple Room')]
    room_type = models.CharField(choices=room_choice, max_length=1, default=None)
    vacant = models.BooleanField(default=False)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    present = models.PositiveIntegerField(validators=[MaxValueValidator(4)], default=0, blank=True, null=True)

    def __str__(self):
        return self.no


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.DO_NOTHING, blank=True, null=True, unique=False)
    location = models.CharField(max_length=10)
    age = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])
    dob = models.DateField(
        max_length=10,
        help_text="format : YYYY-MM-DD",
        null=True, blank=True
    )
    gender_choices = [('M', 'Male'), ('F', 'Female')]
    gender = models.CharField(
        choices=gender_choices,
        max_length=1,
        default=None,
        null=True
    )
    course_choices = [('CSE', 'CSE'), ('IT', 'IT'), ('ECE', 'ECE')]
    course = models.CharField(
        choices=course_choices,
        max_length=3,
        default=None,
        null=True
    )
    room_allotted = models.BooleanField(default=False)
    fees_paid = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        self.user.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def __str__(self):
        return self.user.username


class Approval(models.Model):
    old_room = models.ForeignKey(Room, on_delete=models.DO_NOTHING, blank=True, null=True, unique=False,
                                 related_name='old')
    new_room = models.ForeignKey(Room, on_delete=models.DO_NOTHING, blank=True, null=True, unique=False,
                                 related_name='new')
    requester = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, blank=True, null=True, unique=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.requester.user.username


class Fees(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, blank=True, null=True, unique=False)
    date_paid = models.DateField(auto_now=True)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(9000), MaxValueValidator(15000)])
    is_approved = models.BooleanField(default=False)


class NewRegistration(models.Model):
    requester = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, blank=True, null=True, unique=False)
    new_room = models.ForeignKey(Room, on_delete=models.DO_NOTHING, blank=True, null=True, unique=False,
                                 related_name='newroom')


@receiver(pre_delete, sender=User)
def delete_user(sender, instance, **kwargs):
    if instance.is_superuser:
        raise PermissionDenied
