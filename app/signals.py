# from .models import User, OTPCode
# from django.db.models.signals import post_save
# from django.dispatch import receiver


# @receiver(post_save, sender=User)
# def post_save_gen_code(sender, instance, created, *args, **kwargs):
#     if created:
#         OTPCode.objects.create(user=instance)
