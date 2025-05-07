from django.contrib import admin
from .models import Post, Like, Comment, Tag
# Register your models here.

admin.site.empty_value_display = 'Не задано'

class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'title','category','created_at', 'updated_at', 'likes_count')
    search_fields = ['title', 'content','category','tags', 'author__username']
    list_filter = ['created_at','category','tags']
    list_display_links = ['title']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['tags']

    def likes_count(self, obj):
        return obj.like_set.count()
    likes_count.short_description = 'Likes'
admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'content', 'created_at', 'short_content', 'reply_count')
    list_filter = ['created_at', 'post__category', 'post__tags']
    search_fields = ['content', 'post__title', 'post__content', 'post__category', 'post__tags', 'author__username']

    def short_content(self, obj):
        return obj.content[:20]
    short_content.short_description = 'Текст комментария'

    def reply_count(self, obj):
        return obj.get_children().count()
    reply_count.short_description = 'Количество ответов'
admin.site.register(Comment, CommentAdmin)

class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post')
    search_fields = ['post__title', 'user__username']
admin.site.register(Like, LikeAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name',]
admin.site.register(Tag, TagAdmin)
