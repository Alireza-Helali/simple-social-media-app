from django.urls import path
from .views import (
    my_profile_view,
    invite_received_views,
    invite_profile_list_view,
    ProfileListView,
    profile_list_view,
    send_invitation,
    delete_from_friend,
    accept_invitation,
    reject_invitation,
    ProfileDetail
)

app_name = 'profiles'

urlpatterns = [
    path('', my_profile_view, name='profile'),
    path('<pk>/<name>', ProfileDetail.as_view(), name='detail'),
    path('my_invites/', invite_received_views, name='invites'),
    path('profile_list/', ProfileListView.as_view(), name='profile_list'),
    path('profile_list2/', profile_list_view, name='profile_list2'),
    path('invite/', invite_profile_list_view, name='invite'),
    path('send_invite/', send_invitation, name='send_invite'),
    path('remove_friend/', delete_from_friend, name='delete'),
    path('accept/', accept_invitation, name='accept'),
    path('reject/', reject_invitation, name='reject'),
]
