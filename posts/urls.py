from django.urls import path

from .views import comment_and_post_create_list_view, like_unlike, PostDeleteView, PostUpdateView

app_name = 'posts'

urlpatterns = [
    path('', comment_and_post_create_list_view, name='comment'),
    path('like_unlike', like_unlike, name='like'),
    path('<pk>/delete/', PostDeleteView.as_view(), name='delete'),
    path('<pk>/update/', PostUpdateView.as_view(), name='update'),
]
