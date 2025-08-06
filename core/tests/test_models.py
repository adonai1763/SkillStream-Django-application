"""
Test cases for SkillStream models.

This module contains comprehensive unit tests for all models in the core application,
testing model creation, validation, methods, and relationships.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta

from core.models import CustomerUser, Video, Comment, ChannelSubscription, subsciption

User = get_user_model()


class CustomerUserModelTest(TestCase):
    """Test cases for the CustomerUser model."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_create_user(self):
        """Test creating a user with valid data."""
        user = CustomerUser.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_student)  # Default value
        self.assertFalse(user.is_creator)  # Default value
        self.assertTrue(user.check_password('testpass123'))
        self.assertIsNotNone(user.created_at)

    def test_create_superuser(self):
        """Test creating a superuser."""
        admin_user = CustomerUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_student)

    def test_user_string_representation(self):
        """Test the string representation of user."""
        user = CustomerUser.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')

    def test_get_full_name_with_names(self):
        """Test get_full_name method when first and last names are provided."""
        user = CustomerUser.objects.create_user(**self.user_data)
        self.assertEqual(user.get_full_name(), 'Test User')

    def test_get_full_name_without_names(self):
        """Test get_full_name method when no first/last names are provided."""
        user_data = self.user_data.copy()
        user_data['first_name'] = ''
        user_data['last_name'] = ''
        user = CustomerUser.objects.create_user(**user_data)
        self.assertEqual(user.get_full_name(), 'testuser')

    def test_unique_username_constraint(self):
        """Test that usernames must be unique."""
        CustomerUser.objects.create_user(**self.user_data)
        
        with self.assertRaises(IntegrityError):
            CustomerUser.objects.create_user(
                username='testuser',  # Same username
                email='different@example.com',
                password='password123'
            )

    def test_user_bio_field(self):
        """Test the bio field functionality."""
        user = CustomerUser.objects.create_user(**self.user_data)
        user.bio = "This is a test bio for the user."
        user.save()
        
        user.refresh_from_db()
        self.assertEqual(user.bio, "This is a test bio for the user.")

    def test_user_followers_relationship(self):
        """Test the followers many-to-many relationship."""
        user1 = CustomerUser.objects.create_user(
            username='user1', email='user1@example.com', password='pass123'
        )
        user2 = CustomerUser.objects.create_user(
            username='user2', email='user2@example.com', password='pass123'
        )
        
        # user2 follows user1
        user1.followers.add(user2)
        
        self.assertIn(user2, user1.followers.all())
        self.assertIn(user1, user2.following.all())

    def test_get_subscriber_count(self):
        """Test the get_subscriber_count method."""
        creator = CustomerUser.objects.create_user(
            username='creator', email='creator@example.com', password='pass123'
        )
        subscriber = CustomerUser.objects.create_user(
            username='subscriber', email='subscriber@example.com', password='pass123'
        )
        
        # Initially no subscribers
        self.assertEqual(creator.get_subscriber_count(), 0)
        
        # Add a subscription
        ChannelSubscription.objects.create(subscriber=subscriber, creator=creator)
        self.assertEqual(creator.get_subscriber_count(), 1)

    def test_get_subscription_count(self):
        """Test the get_subscription_count method."""
        user = CustomerUser.objects.create_user(
            username='user', email='user@example.com', password='pass123'
        )
        creator = CustomerUser.objects.create_user(
            username='creator', email='creator@example.com', password='pass123'
        )
        
        # Initially no subscriptions
        self.assertEqual(user.get_subscription_count(), 0)
        
        # Add a subscription
        ChannelSubscription.objects.create(subscriber=user, creator=creator)
        self.assertEqual(user.get_subscription_count(), 1)


class VideoModelTest(TestCase):
    """Test cases for the Video model."""

    def setUp(self):
        """Set up test data."""
        self.user = CustomerUser.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='pass123'
        )
        
        # Create a simple test video file
        self.video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )

    def test_create_video(self):
        """Test creating a video with valid data."""
        video = Video.objects.create(
            creator=self.user,
            title="Test Video",
            description="This is a test video description.",
            video_file=self.video_file
        )
        
        self.assertEqual(video.title, "Test Video")
        self.assertEqual(video.creator, self.user)
        self.assertEqual(video.views, 0)  # Default value
        self.assertIsNotNone(video.uploaded_at)
        self.assertIsNotNone(video.updated_at)

    def test_video_string_representation(self):
        """Test the string representation of video."""
        video = Video.objects.create(
            creator=self.user,
            title="Test Video",
            description="Test description",
            video_file=self.video_file
        )
        expected_str = f"Test Video by {self.user.username}"
        self.assertEqual(str(video), expected_str)

    def test_video_slug_generation(self):
        """Test automatic slug generation from title."""
        video = Video.objects.create(
            creator=self.user,
            title="Test Video Title",
            description="Test description",
            video_file=self.video_file
        )
        self.assertEqual(video.slug, "test-video-title")

    def test_video_slug_uniqueness(self):
        """Test that slugs are made unique when titles are similar."""
        # Create first video
        video1 = Video.objects.create(
            creator=self.user,
            title="Test Video",
            description="First video",
            video_file=self.video_file
        )
        
        # Create second video with same title
        video_file2 = SimpleUploadedFile(
            "test_video2.mp4",
            b"fake video content 2",
            content_type="video/mp4"
        )
        video2 = Video.objects.create(
            creator=self.user,
            title="Test Video",
            description="Second video",
            video_file=video_file2
        )
        
        self.assertEqual(video1.slug, "test-video")
        self.assertEqual(video2.slug, "test-video-1")

    def test_total_likes_method(self):
        """Test the total_likes method."""
        video = Video.objects.create(
            creator=self.user,
            title="Test Video",
            description="Test description",
            video_file=self.video_file
        )
        
        # Initially no likes
        self.assertEqual(video.total_likes(), 0)
        
        # Add a like
        liker = CustomerUser.objects.create_user(
            username='liker', email='liker@example.com', password='pass123'
        )
        video.likes.add(liker)
        self.assertEqual(video.total_likes(), 1)

    def test_get_absolute_url(self):
        """Test the get_absolute_url method."""
        video = Video.objects.create(
            creator=self.user,
            title="Test Video",
            description="Test description",
            video_file=self.video_file
        )
        expected_url = f'/watch_video/{video.id}/'
        self.assertEqual(video.get_absolute_url(), expected_url)

    def test_video_title_validation(self):
        """Test video title validation (minimum length)."""
        with self.assertRaises(ValidationError):
            video = Video(
                creator=self.user,
                title="AB",  # Too short (minimum 3 characters)
                description="Valid description here",
                video_file=self.video_file
            )
            video.full_clean()

    def test_video_description_validation(self):
        """Test video description validation (minimum length)."""
        with self.assertRaises(ValidationError):
            video = Video(
                creator=self.user,
                title="Valid Title",
                description="Short",  # Too short (minimum 10 characters)
                video_file=self.video_file
            )
            video.full_clean()

    def test_video_ordering(self):
        """Test that videos are ordered by upload date (newest first)."""
        # Create first video
        video1 = Video.objects.create(
            creator=self.user,
            title="First Video",
            description="First video description",
            video_file=self.video_file
        )
        
        # Create second video
        video_file2 = SimpleUploadedFile(
            "test_video2.mp4",
            b"fake video content 2",
            content_type="video/mp4"
        )
        video2 = Video.objects.create(
            creator=self.user,
            title="Second Video",
            description="Second video description",
            video_file=video_file2
        )
        
        videos = list(Video.objects.all())
        self.assertEqual(videos[0], video2)  # Newest first
        self.assertEqual(videos[1], video1)


class CommentModelTest(TestCase):
    """Test cases for the Comment model."""

    def setUp(self):
        """Set up test data."""
        self.user = CustomerUser.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='pass123'
        )
        
        self.creator = CustomerUser.objects.create_user(
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

    def test_create_comment(self):
        """Test creating a comment with valid data."""
        comment = Comment.objects.create(
            video=self.video,
            user=self.user,
            content="This is a test comment."
        )
        
        self.assertEqual(comment.video, self.video)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, "This is a test comment.")
        self.assertIsNotNone(comment.created_at)

    def test_comment_string_representation(self):
        """Test the string representation of comment."""
        comment = Comment.objects.create(
            video=self.video,
            user=self.user,
            content="Test comment"
        )
        expected_str = f"Comment by {self.user.username} on {self.video.title}"
        self.assertEqual(str(comment), expected_str)

    def test_comment_ordering(self):
        """Test that comments are ordered by creation date (newest first)."""
        # Create first comment
        comment1 = Comment.objects.create(
            video=self.video,
            user=self.user,
            content="First comment"
        )
        
        # Create second comment
        comment2 = Comment.objects.create(
            video=self.video,
            user=self.user,
            content="Second comment"
        )
        
        comments = list(Comment.objects.all())
        self.assertEqual(comments[0], comment2)  # Newest first
        self.assertEqual(comments[1], comment1)


class ChannelSubscriptionModelTest(TestCase):
    """Test cases for the ChannelSubscription model."""

    def setUp(self):
        """Set up test data."""
        self.subscriber = CustomerUser.objects.create_user(
            username='subscriber',
            email='subscriber@example.com',
            password='pass123'
        )
        
        self.creator = CustomerUser.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='pass123'
        )

    def test_create_subscription(self):
        """Test creating a channel subscription."""
        subscription = ChannelSubscription.objects.create(
            subscriber=self.subscriber,
            creator=self.creator
        )
        
        self.assertEqual(subscription.subscriber, self.subscriber)
        self.assertEqual(subscription.creator, self.creator)
        self.assertIsNotNone(subscription.subscribed_at)

    def test_subscription_string_representation(self):
        """Test the string representation of subscription."""
        subscription = ChannelSubscription.objects.create(
            subscriber=self.subscriber,
            creator=self.creator
        )
        expected_str = f"{self.subscriber.username} subscribed to {self.creator.username}"
        self.assertEqual(str(subscription), expected_str)

    def test_unique_subscription_constraint(self):
        """Test that a user cannot subscribe to the same creator twice."""
        ChannelSubscription.objects.create(
            subscriber=self.subscriber,
            creator=self.creator
        )
        
        with self.assertRaises(IntegrityError):
            ChannelSubscription.objects.create(
                subscriber=self.subscriber,
                creator=self.creator  # Same subscription
            )

    def test_subscription_ordering(self):
        """Test that subscriptions are ordered by subscription date (newest first)."""
        creator2 = CustomerUser.objects.create_user(
            username='creator2',
            email='creator2@example.com',
            password='pass123'
        )
        
        # Create first subscription
        sub1 = ChannelSubscription.objects.create(
            subscriber=self.subscriber,
            creator=self.creator
        )
        
        # Create second subscription
        sub2 = ChannelSubscription.objects.create(
            subscriber=self.subscriber,
            creator=creator2
        )
        
        subscriptions = list(ChannelSubscription.objects.all())
        self.assertEqual(subscriptions[0], sub2)  # Newest first
        self.assertEqual(subscriptions[1], sub1)


class LegacySubscriptionModelTest(TestCase):
    """Test cases for the legacy subsciption model."""

    def setUp(self):
        """Set up test data."""
        self.learner = CustomerUser.objects.create_user(
            username='learner',
            email='learner@example.com',
            password='pass123'
        )
        
        self.creator = CustomerUser.objects.create_user(
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

    def test_create_legacy_subscription(self):
        """Test creating a legacy video subscription."""
        subscription = subsciption.objects.create(
            learner=self.learner,
            video=self.video
        )
        
        self.assertEqual(subscription.learner, self.learner)
        self.assertEqual(subscription.video, self.video)
        self.assertFalse(subscription.completed)  # Default value
        self.assertIsNotNone(subscription.enrolled_at)

    def test_legacy_subscription_string_representation(self):
        """Test the string representation of legacy subscription."""
        subscription = subsciption.objects.create(
            learner=self.learner,
            video=self.video
        )
        expected_str = f"{self.learner.username} enrolled in {self.video.title}"
        self.assertEqual(str(subscription), expected_str)

    def test_legacy_subscription_completion(self):
        """Test marking a legacy subscription as completed."""
        subscription = subsciption.objects.create(
            learner=self.learner,
            video=self.video
        )
        
        subscription.completed = True
        subscription.save()
        
        subscription.refresh_from_db()
        self.assertTrue(subscription.completed)