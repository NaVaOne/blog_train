from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.

User = get_user_model()

class Tag(models.Model):
    name = models.CharField('название',max_length=50, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Tags'
        verbose_name = 'Tag'

    def __str__(self):
        return self.name
    
# class Category(models.Model):
#     name = models.CharField(max_length=50, unique=True)
#     slug = models.SlugField(max_length=50, unique=True, blank=True)

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         super().save(*args, **kwargs)

#     class Meta:
#         ordering = ['name']
#         verbose_name_plural = 'Categories'
#         verbose_name = 'Category'

#     def __str__(self):
#         return self.name
    


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('PROGRAMMING', 'Программирование'),
        ('CARS', 'Машины'),
        ('COOKING', 'Кулинария'),
        ('TRAVEL', 'Путешествия'),
        ('MUSIC', 'Музыка'),
        ('SPORT', 'Спорт'),
        ('MOVIES', 'Кино'),
        ('GAMES', 'Игры'),
        ('PHOTOGRAPHY', 'Фотография'),
        ('ENTERTAINMENT', 'Развлечения'),
        ('HEALTH', 'Здоровье'),
        ('EDUCATION', 'Образование'),
        ('BUSINESS', 'Бизнес'),
        ('ANIMALS', 'Животные'),
        ('OTHER', 'Другое'),
    ]
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE, verbose_name='Автор')
    title = models.CharField(max_length=255, verbose_name='Название')
    content = models.TextField(verbose_name='Текст')
    tags = models.ManyToManyField(Tag, blank=True,verbose_name='Теги')
    category = models.CharField(choices=CATEGORY_CHOICES, default='OTHER', verbose_name='Категория')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['created_at'])]
        verbose_name_plural = 'Posts'
        verbose_name = 'Post'

    def __str__(self):
        return self.title
    

class Comment(MPTTModel):
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE, verbose_name='Автор')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Пост')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Родительский комментарий')
    content = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class MPTTMeta:
        order_insertion_by = ['created_at']

    class Meta:
        verbose_name_plural = 'Comments'
        verbose_name = 'Comment'

    def __str__(self):
        return self.content[:20]
    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Пост')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'], 
                name='unique_like'
                )
        ]
        verbose_name_plural = 'Likes'
        verbose_name = 'Like'

    def __str__(self):
        return f'{self.user} likes {self.post}'