from django import template
import os
from Alumni_Tracking.models import add_friend, message_model
from django.db.models import Q
register = template.Library()


@register.filter
def get_filename(value):
    return os.path.split(value)[1]


@register.filter
def get_length(value):
    return len(value)


@register.filter
def check_friend(value, args):
    check = add_friend.objects.filter(friends__user__username=value, profile__user__username=args)
    if check.exists():
        return False
    return True


@register.filter
def confirm_friend(value, args):
    try:
        check = add_friend.objects.get(friends__user__username=args, profile__user__username=value)
    except add_friend.DoesNotExist:
        return 'friend_not'
    if check.confirm:
        return 'accepted'
    return 'not_accepted'


@register.filter
def list_messages(value, args):
    all_message = message_model.objects.filter(Q(sender__user__username=value, receive__user__username=args) |
                                               Q(receive__user__username=value, sender__user__username=args))
    if all_message.exists():
        return all_message.order_by('strap')
    return False



