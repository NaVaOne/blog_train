from rest_framework import serializers
from .models import Post,Tag, Comment, Like
from markdown import markdown
from django.utils.text import slugify


# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id','name', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id','name']


class PostSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = serializers.ChoiceField(choices=Post.CATEGORY_CHOICES)
    likes_count = serializers.SerializerMethodField()
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False,
        default=list  # Явно указываем значение по умолчанию
    )

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'tags', 'category','author', 'created_at', 'likes_count']
        read_only_fields = ['author', 'created_at']

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def create(self, validated_data):
        # Достаём теги (по умолчанию пустой список)
        tags_data = validated_data.pop('tags', [])  
        
        # Создаём пост БЕЗ тегов
        post = Post.objects.create(**validated_data)

        # Обрабатываем теги только если они переданы
        if tags_data:
            tag_instances = []
            for tag_name in tags_data:
                tag_name = tag_name.strip()
                if tag_name:  # Игнорируем пустые строки
                    tag, _ = Tag.objects.get_or_create(name=tag_name,)
                    tag_instances.append(tag)
            
            # Добавляем теги к посту
            post.tags.add(*tag_instances)

        return post

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tags'] = [tag.name for tag in instance.tags.all()]
        return data

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    post = serializers.HiddenField(default=None)
    replies = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'parent', 'created_at', 'replies']

    def get_replies(self, obj):
        if obj.get_children():
            return CommentSerializer(obj.get_children(), many=True, context=self.context).data
        return []
    
    def validate(self, data):
        parent = data.get('parent')
        if parent:
            if parent.level >= 2:
                raise serializers.ValidationError(
                    "Максимальная глубина ответов - 3 уровня"
                )
        return data

class LikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Like
        fields = ('user', 'post')