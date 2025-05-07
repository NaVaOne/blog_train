from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Notification
from blog.models import Post

User = get_user_model()

@shared_task
def send_like_notification(post_id,user_id):
    try:
        post = Post.objects.get(id=post_id)
        liker = User.objects.get(id=user_id)
        recipient = post.author
        if liker != recipient:
            Notification.objects.create(
                user=recipient,
                message=f'{liker.username} liked your post "{post.title}"',
            )
    except Post.DoesNotExist:
        pass