"""
SkillStream Models

This module contains all database models for the SkillStream application.
Models are organized by functionality and include comprehensive documentation
for business logic and design decisions.

Models:
    - CustomerUser: Extended user model with creator/student roles
    - Video: Core video content model with engagement tracking
    - Comment: Video comment system for community interaction
    - ChannelSubscription: Modern channel-based subscription system
    - subsciption: Legacy video-based subscription (deprecated)
"""

from typing import Optional
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinLengthValidator, FileExtensionValidator
from django.utils.text import slugify
from django.urls import reverse

# ========== USER MODEL ==========
class CustomerUser(AbstractUser):
    """
    Custom User Model extending Django's AbstractUser
    
    Design Decision: Extended AbstractUser instead of creating a separate profile model
    - Keeps user data in one place for better performance
    - Simplifies authentication and permissions
    - Allows for role-based access control
    
    Business Logic:
    - Users can be both creators and students (not mutually exclusive)
    - is_student=True by default (everyone can learn)
    - is_creator becomes True when user uploads first video
    - followers system enables social features and creator discovery
    """
    
    # Role-based fields for different user experiences
    is_creator = models.BooleanField(
        default=False,
        help_text="True when user uploads their first video. Enables Creator Studio access."
    )
    is_student = models.BooleanField(
        default=True,
        help_text="All users are students by default. Can subscribe to creators and comment."
    )
    
    # Profile fields
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="User biography displayed on profile page"
    )
    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        help_text="User profile picture"
    )
    
    # Social features - users can follow creators
    followers = models.ManyToManyField(
        'self', 
        related_name='following', 
        blank=True,
        symmetrical=False,  # Following is not mutual (like Twitter, not Facebook)
        help_text="Users who follow this creator for updates"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        help_text="When the user account was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        help_text="When the user account was last updated"
    )

    def get_full_name(self) -> str:
        """Return the user's full name or username if no first/last name."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    def get_subscriber_count(self) -> int:
        """Get the number of users subscribed to this creator."""
        return ChannelSubscription.objects.filter(creator=self).count()

    def get_subscription_count(self) -> int:
        """Get the number of creators this user is subscribed to."""
        return ChannelSubscription.objects.filter(subscriber=self).count()

    def get_total_video_views(self) -> int:
        """Get total views across all videos created by this user."""
        return sum(video.views for video in self.video_set.all())

    def __str__(self) -> str:
        return self.username
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=['is_creator']),
            models.Index(fields=['created_at']),
            models.Index(fields=['username']),
        ]

# ========== VIDEO MODEL ==========
class Video(models.Model):
    """
    Core Video Model - represents uploaded video content
    
    Design Decisions:
    - ForeignKey to creator (not generic User) for clear ownership
    - FileField for video storage (could be extended to cloud storage)
    - ManyToMany for likes (users can like multiple videos, videos can have multiple likes)
    - Auto-incrementing views counter for engagement tracking
    
    Business Logic:
    - Views increment on each video page visit (see watch_video view)
    - Likes are toggleable (user can like/unlike)
    - Creator automatically becomes is_creator=True on first upload
    - Videos are ordered by upload date (newest first) in most views
    """
    
    # Core video metadata
    creator = models.ForeignKey(
        CustomerUser, 
        on_delete=models.CASCADE,
        help_text="Video owner - automatically set to current user on upload"
    )
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)],
        db_index=True,
        help_text="Video title - searchable field, minimum 3 characters"
    )
    slug = models.SlugField(
        max_length=250,
        blank=True,
        help_text="URL-friendly version of title for SEO"
    )
    description = models.TextField(
        max_length=1000,
        validators=[MinLengthValidator(10)],
        help_text="Video description - searchable field, minimum 10 characters"
    )
    
    # File storage
    video_file = models.FileField(
        upload_to='videos/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogg'])],
        help_text="Video file - supports MP4, WebM, OGG formats"
    )
    thumbnail = models.ImageField(
        upload_to='thumbnails/',
        blank=True,
        null=True,
        help_text="Video thumbnail image - auto-generated if not provided"
    )
    duration = models.DurationField(
        null=True,
        blank=True,
        help_text="Video duration - auto-calculated on upload"
    )
    
    # Engagement metrics
    views = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="View counter - incremented each time video page is visited"
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='liked_videos', 
        blank=True,
        help_text="Users who liked this video - enables like/unlike functionality"
    )
    
    # Timestamps
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Automatically set when video is created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last time video metadata was updated"
    )

    def save(self, *args, **kwargs):
        """Override save to auto-generate slug from title."""
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug uniqueness
            counter = 1
            original_slug = self.slug
            while Video.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the canonical URL for this video."""
        return reverse('watch_video', kwargs={'video_id': self.id})

    def total_likes(self):
        """
        Helper method to get like count
        Used in templates and API responses for performance
        """
        return self.likes.count()

    def __str__(self):
        return f"{self.title} by {self.creator.username}"
    
    class Meta:
        ordering = ['-uploaded_at']  # Newest videos first
        verbose_name = "Video"
        verbose_name_plural = "Videos"
        indexes = [
            models.Index(fields=['creator', '-uploaded_at']),
            models.Index(fields=['views']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['slug']),
        ]


# ========== LEGACY SUBSCRIPTION MODEL ==========
class subsciption(models.Model):
    """
    Legacy Video-Based Subscription Model
    
    Design Decision: Kept for backward compatibility and data integrity
    - Originally users subscribed to individual videos (like course enrollment)
    - Now superseded by ChannelSubscription for YouTube-like experience
    - Maintained to preserve existing data relationships
    
    Note: This model represents the old approach where users "enrolled" in specific videos
    The new ChannelSubscription model is preferred for new subscriptions
    """
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        help_text="User who enrolled in this specific video"
    )
    video = models.ForeignKey(
        Video, 
        on_delete=models.CASCADE,
        help_text="Specific video the user enrolled in"
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When user enrolled in this video"
    )
    completed = models.BooleanField(
        default=False,
        help_text="Whether user completed watching this video (future feature)"
    )

    def __str__(self):
        return f"{self.learner.username} enrolled in {self.video.title}"
    
    class Meta:
        verbose_name = "Video Subscription (Legacy)"
        verbose_name_plural = "Video Subscriptions (Legacy)"

# ========== CHANNEL SUBSCRIPTION MODEL ==========
class ChannelSubscription(models.Model):
    """
    Modern Channel-Based Subscription Model (YouTube-like)
    
    Design Decision: Users subscribe to creators (channels), not individual videos
    - Follows YouTube's subscription model for familiar UX
    - Enables creator-focused content discovery
    - Supports notification systems for new uploads
    - More scalable than video-by-video subscriptions
    
    Business Logic:
    - One subscription gives access to all creator's content
    - Prevents duplicate subscriptions with unique_together constraint
    - Enables subscription-based content filtering in feeds
    - Powers "From Your Subscriptions" sections in dashboards
    """
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='subscriptions',
        help_text="User who is subscribing to the creator"
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='subscribers',
        help_text="Creator being subscribed to"
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the subscription was created"
    )

    class Meta:
        unique_together = ('subscriber', 'creator')  # Prevent duplicate subscriptions
        ordering = ['-subscribed_at']  # Newest subscriptions first
        verbose_name = "Channel Subscription"
        verbose_name_plural = "Channel Subscriptions"

    def __str__(self):
        return f"{self.subscriber.username} subscribed to {self.creator.username}"

# ========== COMMENT MODEL ==========
class Comment(models.Model):
    """
    Video Comment System
    
    Design Decisions:
    - Comments belong to specific videos (not creators or channels)
    - Users can comment on any video they can access
    - Comments are ordered by creation time (newest first)
    - Content length limited to prevent spam and maintain readability
    
    Business Logic:
    - Comments enable community engagement and discussion
    - Used for user activity tracking (comments_count in profiles)
    - Could be extended with reply system (parent comment field)
    - Supports moderation through Django admin
    """
    video = models.ForeignKey(
        Video, 
        on_delete=models.CASCADE,
        help_text="Video this comment belongs to"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        help_text="User who wrote this comment"
    )
    content = models.TextField(
        max_length=1000,
        help_text="Comment text content - limited to prevent spam"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When comment was posted"
    )

    def __str__(self):
        return f"Comment by {self.user.username} on {self.video.title}"
    
    class Meta:
        ordering = ['-created_at']  # Newest comments first
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
