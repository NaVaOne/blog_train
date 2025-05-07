from django.shortcuts import get_object_or_404
from rest_framework import viewsets,mixins ,filters, status
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .permissions import AuthorOrReadOnly
from notifications.tasks import send_like_notification
from rest_framework.decorators import action
# Create your views here.


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AuthorOrReadOnly,]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [AuthorOrReadOnly,]
    def get_queryset(self):
        # Фильтруем комментарии по post_pk из URL
        return Comment.objects.filter(post_id=self.kwargs['post_pk'])

    def perform_create(self, serializer):
        # Автоматически привязываем пост из URL
        post_id = self.kwargs['post_pk']
        serializer.save(
            author=self.request.user,
            post_id=post_id  # post_id берётся из URL
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return Response({'detail': 'You do not have permission to delete this comment.'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(comment)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def update(self, request, *args, **kwargs):
        return Response({'detail': 'Updating comments is not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def partial_update(self, request, *args, **kwargs):
        return Response({'detail': 'Updating comments is not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            

class LikeViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,viewsets.GenericViewSet):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Фильтруем лайки по post_pk из URL
        return Like.objects.filter(post_id=self.kwargs['post_pk'])

    def create(self, request, *args, **kwargs):
        # post_pk берётся из URL автоматически
        post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        
        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post
        )
        
        if not created:
            return Response(
                {'detail': 'Вы уже лайкали этот пост'},
                status=status.HTTP_400_BAD_REQUEST
            )
        send_like_notification(post.id, request.user.id)
        return Response(
            LikeSerializer(like).data,
            status=status.HTTP_201_CREATED
        )
    @action(detail=False, methods=['delete'], url_path='remove')
    def delete_like(self, request, *args, **kwargs):
        like = get_object_or_404(Like, user=request.user, post_id=self.kwargs['post_pk'])
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class LikeViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticatedOrReadOnly]

#     @transaction.atomic
#     def create(self, request, post_pk):
#         # post_pk берётся из URL автоматически
#         post = get_object_or_404(Post, pk=post_pk)
        
#         like, created = Like.objects.get_or_create(
#             user=request.user,
#             post=post
#         )
        
#         if not created:
#             return Response(
#                 {'detail': 'Вы уже лайкали этот пост'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
            
#         return Response(
#             LikeSerializer(like).data,
#             status=status.HTTP_201_CREATED
#         )

#     @action(detail=False)
#     @transaction.atomic
#     def delete_like(self, request, post_pk=None):
#         post = get_object_or_404(Post, pk=post_pk)
#         like = get_object_or_404(Like, user=request.user, post=post)
#         like.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

