from http import HTTPStatus
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from blog.models import Post, Comment, Like

User = get_user_model()

class RoutesTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser',email='testuser@localhost.ru' ,password='testpass')
        cls.other_user = User.objects.create_user(username='otheruser',email='otheruser@localhost.ru' ,password='testpass')
        cls.post = Post.objects.create(title='Test Post', content='Test Content', author=cls.user, category = 'OTHER')
        cls.comment = Comment.objects.create(post=cls.post, author=cls.user, content='Test Comment')
        cls.like = Like.objects.create(post=cls.post, user=cls.user)

    def setUp(self):
        self.client = APIClient()

    def login_as_user(self, user):
        refresh = RefreshToken.for_user(user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_get_post_list_unauthenticated(self):
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_post_detail_unauthenticated(self):
        response = self.client.get(reverse('post-detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_unauthenticated(self):
        response = self.client.post(reverse('post-list'), {'title': 'New Post', 'content': 'New Content', 'category': 'OTHER'}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_create_post_authenticated(self):
        self.login_as_user(self.user)
        response = self.client.post(reverse('post-list'), {'title': 'New Post', 'content': 'New Content', 'category': 'OTHER'}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_update_post_author(self):
        self.login_as_user(self.user)
        url = reverse('post-detail', args = [self.post.pk])
        response = self.client.put(url, {'title': 'Updated Post', 'content': 'Updated Content', 'category': 'OTHER'}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_update_post_notauthor(self):
        self.login_as_user(self.other_user)
        url = reverse('post-detail', args = [self.post.pk])
        response = self.client.put(url, {'title': 'Updated Post', 'content': 'Updated Content', 'category': 'OTHER'}, format='json') 
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_post_notauthor(self):
        self.login_as_user(self.other_user)
        url = reverse('post-detail', args = [self.post.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_post_author(self):
        self.login_as_user(self.user)
        url = reverse('post-detail', args = [self.post.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_get_comment_list_unauthenticated(self):
        url = reverse('post-comments-list', args=[self.post.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_comment_detail_unauthenticated(self):
        url = reverse('post-comments-detail', args=[self.post.pk, self.comment.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_comment_unauthenticated(self):
        url = reverse('post-comments-list', args=[self.post.pk])
        response = self.client.post(url, {'content': 'New Comment'}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_create_comment_authenticated(self):
        url = reverse('post-comments-list', args=[self.post.pk])
        self.login_as_user(self.user)
        response = self.client.post(url, {'content': 'New Comment'}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_delete_comment_notauthor(self):
        self.login_as_user(self.other_user)
        url = reverse('post-comments-detail', args = [self.post.pk, self.comment.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_comment_author(self):
        self.login_as_user(self.user)
        url = reverse('post-comments-detail', args = [self.post.pk, self.comment.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
