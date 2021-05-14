from .models import Profile, Relation


def profile_pic(request):
    if request.user.is_authenticated:
        profile_obj = Profile.objects.get(user=request.user)
        pic = profile_obj.avatar
        return {
            'picture': pic
        }
    return {}


def invitations_received_count(request):
    if request.user.is_authenticated:
        profile_obj = Profile.objects.get(user=request.user)
        qs = Relation.objects.invitations_received(receiver=profile_obj).count()
        return {'invite_count': qs}

    return {}
