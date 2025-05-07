from django.urls import path, include
from rest_framework_nested import routers
from .views import (
    PostViewSet, 
    CommentViewSet,
    LikeViewSet
)

# Базовый роутер для постов
router = routers.DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')

# Вложенный роутер для комментариев
comments_router = routers.NestedSimpleRouter(
    router, r'posts', lookup='post'
)
comments_router.register(
    r'comments', CommentViewSet, basename='post-comments'
)

# Вложенный роутер для лайков
likes_router = routers.NestedSimpleRouter(
    router, r'posts', lookup='post'
)
likes_router.register(
    r'likes', LikeViewSet, basename='post-likes'
)


urlpatterns = [
    path('', include(router.urls + comments_router.urls + likes_router.urls)),
]