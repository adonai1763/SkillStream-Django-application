"""
Test cases for SkillStream views.

This module contains comprehensive functional tests for all views in the core application,
testing authentication, permissions, form handling, and response content.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
import json

from core.models import Video, Comment, ChannelSubscription

User = get_user_model()


class HomeViewTest(TestCase):
    """Test cases for the home view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_home_view_unauthenticated(self):
        """Test home view for unauthenticated users shows landing page."""
        response = self.client.get(reverse('home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SkillStream')
        self.assertContains(response, 'Get Started')
        self.assertContains(response, 'Login')

    def test_home_view_authenticated(self):
        """Test home view for authenticated users shows video feed."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Home Feed')
        self.assertNotContains(response, 'Get Started')

    def test_home_view_with_videos(self):
        """Test home view displays videos when available."""
        # Create a creator and video
        creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='pass123'
        )
        
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        video = Video.objects.create(
            creator=creator,
            title="Test Video",
            description="Test video description",
            video_file=video_file
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Video')
        self.assertContains(response, creator.username)


class AuthenticationViewsTest(TestCase):
    """Test cases for authentication views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

    def test_register_view_get(self):
        """Test GET request to register view."""
        response = self.client.get(reverse('register'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_register_view_post_valid(self):
        """Test POST request to register view with valid data."""
        response = self.client.post(reverse('register'), self.user_data)
        
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_view_post_invalid(self):
        """Test POST request to register view with invalid data."""
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'differentpassword'
        
        response = self.client.post(reverse('register'), invalid_data)
        
        self.assertEqual(response.status_code, 200)  # Stay on form page
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_login_view_valid_credentials(self):
        """Test login with valid credentials."""
        # Create user first
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        response = self.client.post(reverse('user_login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_login_view_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(reverse('user_login'), {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('incorrect' in str(message) for message in messages))

    def test_logout_view(self):
        """Test logout functionality."""
        # Create and login user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('user_logout'))
        
        self.assertEqual(response.status_code, 302)  # Redirect after logout


class DashboardViewsTest(TestCase):
    """Test cases for dashboard views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass123',
            is_student=True,
            is_creator=False
        )
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='pass123',
            is_creator=True
        )

    def test_dashboard_redirect_student(self):
        """Test dashboard redirect for student users."""
        self.client.login(username='student', password='pass123')
        response = self.client.get(reverse('dashboard_redirect'))
        
        self.assertRedirects(response, reverse('learner_dashboard'))

    def test_dashboard_redirect_creator(self):
        """Test dashboard redirect for creator users."""
        self.client.login(username='creator', password='pass123')
        response = self.client.get(reverse('dashboard_redirect'))
        
        self.assertRedirects(response, reverse('creator_dashboard'))

    def test_learner_dashboard_access(self):
        """Test learner dashboard access and content."""
        self.client.login(username='student', password='pass123')
        response = self.client.get(reverse('learner_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'learner')

    def test_creator_dashboard_access(self):
        """Test creator dashboard access and content."""
        self.client.login(username='creator', password='pass123')
        response = self.client.get(reverse('creator_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'creator')

    def test_creator_dashboard_with_videos(self):
        """Test creator dashboard displays creator's videos."""
        # Create a video for the creator
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        video = Video.objects.create(
            creator=self.creator,
            title="Creator's Video",
            description="Test video description",
            video_file=video_file
        )
        
        self.client.login(username='creator', password='pass123')
        response = self.client.get(reverse('creator_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Creator's Video")

    def test_user_profile_view(self):
        """Test user profile view."""
        self.client.login(username='student', password='pass123')
        response = self.client.get(reverse('user_profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.student.username)


class VideoManagementViewsTest(TestCase):
    """Test cases for video management views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )

    def test_upload_video_view_get(self):
        """Test GET request to upload video view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('upload_video'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_upload_video_view_post_valid(self):
        """Test POST request to upload video with valid data."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('upload_video'), {
            'title': 'Test Video Upload',
            'description': 'This is a test video description for upload.',
            'video_file': self.video_file
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after upload
        self.assertTrue(Video.objects.filter(title='Test Video Upload').exists())
        
        # Check that user became creator
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_creator)

    def test_upload_video_view_unauthenticated(self):
        """Test upload video view requires authentication."""
        response = self.client.get(reverse('upload_video'))
        
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_watch_video_view(self):
        """Test watch video view."""
        # Create a video
        video = Video.objects.create(
            creator=self.user,
            title="Test Video",
            description="Test video description",
            video_file=self.video_file
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('watch_video', kwargs={'video_id': video.id}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Video')
        
        # Check that view count was incremented
        video.refresh_from_db()
        self.assertEqual(video.views, 1)

    def test_delete_video_by_creator(self):
        """Test video deletion by the creator."""
        video = Video.objects.create(
            creator=self.user,
            title="Test Video",
            description="Test video description",
            video_file=self.video_file
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('delete_video', kwargs={'video_id': video.id}))
        
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(Video.objects.filter(id=video.id).exists())

    def test_delete_video_by_non_creator(self):
        """Test video deletion attempt by non-creator."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        
        video = Video.objects.create(
            creator=other_user,
            title="Other's Video",
            description="Test video description",
            video_file=self.video_file
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('delete_video', kwargs={'video_id': video.id}))
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(Video.objects.filter(id=video.id).exists())  # Video still exists


class SearchViewsTest(TestCase):
    """Test cases for search functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test videos
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        self.video1 = Video.objects.create(
            creator=self.user,
            title="Python Tutorial",
            description="Learn Python programming basics",
            video_file=video_file
        )
        
        video_file2 = SimpleUploadedFile(
            "test_video2.mp4",
            b"fake video content 2",
            content_type="video/mp4"
        )
        
        self.video2 = Video.objects.create(
            creator=self.user,
            title="Django Web Development",
            description="Build web applications with Django",
            video_file=video_file2
        )

    def test_search_videos_by_title(self):
        """Test searching videos by title."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('search_videos'), {'q': 'Python'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Tutorial')
        self.assertNotContains(response, 'Django Web Development')

    def test_search_videos_by_description(self):
        """Test searching videos by description."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('search_videos'), {'q': 'Django'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Web Development')
        self.assertNotContains(response, 'Python Tutorial')

    def test_search_videos_by_creator(self):
        """Test searching videos by creator username."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('search_videos'), {'q': 'testuser'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Tutorial')
        self.assertContains(response, 'Django Web Development')

    def test_search_empty_query(self):
        """Test search with empty query."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('search_videos'), {'q': ''})
        
        self.assertEqual(response.status_code, 200)
        # Should return no results for empty query


class SocialInteractionViewsTest(TestCase):
    """Test cases for social interaction views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='pass123'
        )
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='pass123'
        )
        
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        self.video = Video.objects.create(
            creator=self.creator,
            title="Test Video",
            description="Test video description",
            video_file=video_file
        )

    def test_like_video(self):
        """Test liking a video."""
        self.client.login(username='user', password='pass123')
        response = self.client.get(reverse('like_video', kwargs={'video_id': self.video.id}))
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(self.video.likes.filter(id=self.user.id).exists())

    def test_unlike_video(self):
        """Test unliking a video."""
        # First like the video
        self.video.likes.add(self.user)
        
        self.client.login(username='user', password='pass123')
        response = self.client.get(reverse('like_video', kwargs={'video_id': self.video.id}))
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertFalse(self.video.likes.filter(id=self.user.id).exists())

    def test_subscribe_to_channel(self):
        """Test subscribing to a creator's channel."""
        self.client.login(username='user', password='pass123')
        response = self.client.get(reverse('toggle_subscription', kwargs={'video_id': self.video.id}))
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(ChannelSubscription.objects.filter(
            subscriber=self.user, creator=self.creator
        ).exists())

    def test_unsubscribe_from_channel(self):
        """Test unsubscribing from a creator's channel."""
        # First subscribe
        ChannelSubscription.objects.create(subscriber=self.user, creator=self.creator)
        
        self.client.login(username='user', password='pass123')
        response = self.client.get(reverse('toggle_subscription', kwargs={'video_id': self.video.id}))
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertFalse(ChannelSubscription.objects.filter(
            subscriber=self.user, creator=self.creator
        ).exists())

    def test_self_subscription_prevention(self):
        """Test that users cannot subscribe to themselves."""
        self.client.login(username='creator', password='pass123')
        response = self.client.get(reverse('toggle_subscription', kwargs={'video_id': self.video.id}))
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertFalse(ChannelSubscription.objects.filter(
            subscriber=self.creator, creator=self.creator
        ).exists())

    def test_add_comment(self):
        """Test adding a comment to a video."""
        self.client.login(username='user', password='pass123')
        response = self.client.post(reverse('user_comment', kwargs={'video_id': self.video.id}), {
            'content': 'This is a test comment.'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(Comment.objects.filter(
            video=self.video, user=self.user, content='This is a test comment.'
        ).exists())


class APIViewsTest(TestCase):
    """Test cases for API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        self.video = Video.objects.create(
            creator=self.user,
            title="API Test Video",
            description="Test video for API",
            video_file=video_file
        )

    def test_api_videos_list(self):
        """Test API endpoint for listing videos."""
        response = self.client.get(reverse('api_videos_list'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['videos'][0]['title'], 'API Test Video')

    def test_api_video_detail(self):
        """Test API endpoint for video details."""
        response = self.client.get(reverse('api_video_detail', kwargs={'video_id': self.video.id}))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['video']['title'], 'API Test Video')
        self.assertEqual(data['video']['creator']['username'], 'testuser')

    def test_api_video_detail_not_found(self):
        """Test API endpoint for non-existent video."""
        response = self.client.get(reverse('api_video_detail', kwargs={'video_id': 99999}))
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        
        self.assertFalse(data['success'])
        self.assertIn('error', data)

    def test_api_user_stats_authenticated(self):
        """Test API endpoint for user statistics (authenticated)."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('api_user_stats'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['user_stats']['username'], 'testuser')
        self.assertEqual(data['user_stats']['uploaded_videos_count'], 1)

    def test_api_user_stats_unauthenticated(self):
        """Test API endpoint for user statistics (unauthenticated)."""
        response = self.client.get(reverse('api_user_stats'))
        
        self.assertEqual(response.status_code, 302)  # Redirect to login