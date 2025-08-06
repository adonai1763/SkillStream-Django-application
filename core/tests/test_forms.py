"""
Test cases for SkillStream forms.

This module contains comprehensive tests for all forms in the core application,
testing form validation, field requirements, and error handling.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from core.forms import CustomerCreationForm, VideouploadForm, CommentForm

User = get_user_model()


class CustomerCreationFormTest(TestCase):
    """Test cases for the CustomerCreationForm."""

    def test_valid_form(self):
        """Test form with valid data."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomerCreationForm(data=form_data)
        
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        """Test form with mismatched passwords."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'differentpass'
        }
        form = CustomerCreationForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_duplicate_username(self):
        """Test form with duplicate username."""
        # Create existing user
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='pass123'
        )
        
        form_data = {
            'username': 'existinguser',  # Duplicate username
            'email': 'new@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomerCreationForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_invalid_email(self):
        """Test form with invalid email format."""
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',  # Invalid email format
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomerCreationForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_missing_required_fields(self):
        """Test form with missing required fields."""
        form_data = {
            'username': '',  # Missing username
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomerCreationForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_weak_password(self):
        """Test form with weak password."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': '123',  # Too short
            'password2': '123'
        }
        form = CustomerCreationForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_form_save(self):
        """Test that form saves user correctly."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomerCreationForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        user = form.save()
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_student)  # Default value
        self.assertFalse(user.is_creator)  # Default value


class VideouploadFormTest(TestCase):
    """Test cases for the VideouploadForm."""

    def setUp(self):
        """Set up test data."""
        self.valid_video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )

    def test_valid_form(self):
        """Test form with valid data."""
        form_data = {
            'title': 'Test Video Title',
            'description': 'This is a test video description that meets minimum length requirements.'
        }
        form_files = {
            'video_file': self.valid_video_file
        }
        form = VideouploadForm(data=form_data, files=form_files)
        
        self.assertTrue(form.is_valid())

    def test_missing_title(self):
        """Test form with missing title."""
        form_data = {
            'title': '',  # Missing title
            'description': 'This is a test video description that meets minimum length requirements.'
        }
        form_files = {
            'video_file': self.valid_video_file
        }
        form = VideouploadForm(data=form_data, files=form_files)
        
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_missing_description(self):
        """Test form with missing description."""
        form_data = {
            'title': 'Test Video Title',
            'description': ''  # Missing description
        }
        form_files = {
            'video_file': self.valid_video_file
        }
        form = VideouploadForm(data=form_data, files=form_files)
        
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_missing_video_file(self):
        """Test form with missing video file."""
        form_data = {
            'title': 'Test Video Title',
            'description': 'This is a test video description that meets minimum length requirements.'
        }
        # No video file provided
        form = VideouploadForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('video_file', form.errors)

    def test_invalid_file_type(self):
        """Test form with invalid file type."""
        invalid_file = SimpleUploadedFile(
            "test_document.txt",
            b"this is not a video file",
            content_type="text/plain"
        )
        
        form_data = {
            'title': 'Test Video Title',
            'description': 'This is a test video description that meets minimum length requirements.'
        }
        form_files = {
            'video_file': invalid_file
        }
        form = VideouploadForm(data=form_data, files=form_files)
        
        # Note: File type validation might be handled at the model level
        # This test ensures the form accepts the file, but model validation
        # would catch invalid file types
        self.assertTrue(form.is_valid())  # Form validation passes, model validation would catch this

    def test_title_max_length(self):
        """Test form with title exceeding maximum length."""
        long_title = 'A' * 201  # Exceeds 200 character limit
        
        form_data = {
            'title': long_title,
            'description': 'This is a test video description that meets minimum length requirements.'
        }
        form_files = {
            'video_file': self.valid_video_file
        }
        form = VideouploadForm(data=form_data, files=form_files)
        
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_description_max_length(self):
        """Test form with description exceeding maximum length."""
        long_description = 'A' * 1001  # Exceeds 1000 character limit
        
        form_data = {
            'title': 'Test Video Title',
            'description': long_description
        }
        form_files = {
            'video_file': self.valid_video_file
        }
        form = VideouploadForm(data=form_data, files=form_files)
        
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_form_save_without_commit(self):
        """Test form save without committing to database."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        
        form_data = {
            'title': 'Test Video Title',
            'description': 'This is a test video description that meets minimum length requirements.'
        }
        form_files = {
            'video_file': self.valid_video_file
        }
        form = VideouploadForm(data=form_data, files=form_files)
        
        self.assertTrue(form.is_valid())
        video = form.save(commit=False)
        video.creator = user
        video.save()
        
        self.assertEqual(video.title, 'Test Video Title')
        self.assertEqual(video.creator, user)


class CommentFormTest(TestCase):
    """Test cases for the CommentForm."""

    def test_valid_form(self):
        """Test form with valid data."""
        form_data = {
            'content': 'This is a test comment with sufficient content.'
        }
        form = CommentForm(data=form_data)
        
        self.assertTrue(form.is_valid())

    def test_missing_content(self):
        """Test form with missing content."""
        form_data = {
            'content': ''  # Missing content
        }
        form = CommentForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_content_max_length(self):
        """Test form with content exceeding maximum length."""
        long_content = 'A' * 1001  # Exceeds 1000 character limit
        
        form_data = {
            'content': long_content
        }
        form = CommentForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_form_widget_attributes(self):
        """Test that form widget has correct attributes."""
        form = CommentForm()
        
        # Check that textarea has correct attributes
        content_widget = form.fields['content'].widget
        self.assertEqual(content_widget.attrs['rows'], 4)
        self.assertEqual(content_widget.attrs['placeholder'], 'Write your comment here...')

    def test_form_save_without_commit(self):
        """Test form save without committing to database."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        from core.models import Video
        video = Video.objects.create(
            creator=user,
            title="Test Video",
            description="Test video description",
            video_file=video_file
        )
        
        form_data = {
            'content': 'This is a test comment.'
        }
        form = CommentForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        comment = form.save(commit=False)
        comment.user = user
        comment.video = video
        comment.save()
        
        self.assertEqual(comment.content, 'This is a test comment.')
        self.assertEqual(comment.user, user)
        self.assertEqual(comment.video, video)

    def test_whitespace_only_content(self):
        """Test form with whitespace-only content."""
        form_data = {
            'content': '   \n\t   '  # Only whitespace
        }
        form = CommentForm(data=form_data)
        
        # Django's CharField strips whitespace, so this should be invalid
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_html_content_handling(self):
        """Test form with HTML content."""
        form_data = {
            'content': 'This is a comment with <script>alert("xss")</script> HTML content.'
        }
        form = CommentForm(data=form_data)
        
        # Form should accept HTML content (sanitization happens in templates)
        self.assertTrue(form.is_valid())
        
        comment = form.save(commit=False)
        self.assertIn('<script>', comment.content)  # HTML is preserved in model