from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Relation


@receiver(post_save, sender=User)
def post_save_create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Relation)
def post_save_add_to_friend(sender, instance, created, **kwargs):
    sender = instance.sender
    receiver = instance.receiver
    if instance.status == 'accepted':
        sender.friends.add(receiver.user)
        receiver.friends.add(sender.user)
        sender.save()
        receiver.save()


@receiver(pre_delete, sender=Relation)
def pre_delete_remove_from_friend(sender, instance, **kwargs):
    sender = instance.sender
    receiver = instance.receiver

    sender.friends.remove(receiver.user)
    receiver.friends.remove(sender.user)
    sender.save()
    receiver.save()
