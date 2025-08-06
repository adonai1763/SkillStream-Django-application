"""
Django Admin Configuration for SkillStream

This module provides comprehensive admin interface configurations for all models,
demonstrating advanced Django admin features and best practices.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import CustomerUser, Video, Comment, ChannelSubscription, subsciption


@admin.register(CustomerUser)
class CustomerUserAdmin(UserAdmin):
    """Enhanced admin interface for CustomerUser model."""
    
    list_display = (
        'username', 'email', 'first_name', 'last_name', 
        'is_creator', 'is_student', 'is_staff', 'date_joined',
        'subscriber_count', 'video_count'
    )
    list_filter = (
        'is_creator', 'is_student', 'is_staff', 'is_superuser',
        'is_active', 'date_joined', 'created_at'
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('SkillStream Profile', {
            'fields': ('is_creator', 'is_student', 'bio', 'profile_image', 'followers')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'date_joined')
    
    def subscriber_count(self, obj):
        """Display subscriber count for creators."""
        if obj.is_creator:
            count = obj.get_subscriber_count()
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                count
            )
        return '-'
    subscriber_count.short_description = 'Subscribers'
    
    def video_count(self, obj):
        """Display video count for creators."""
        if obj.is_creator:
            count = obj.video_set.count()
            if count > 0:
                url = reverse('admin:core_video_changelist') + f'?creator__id__exact={obj.id}'
                return format_html(
                    '<a href="{}" style="color: blue;">{} videos</a>',
                    url, count
                )
            return '0 videos'
        return '-'
    video_count.short_description = 'Videos'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Video model."""
    
    list_display = (
        'title', 'creator', 'views', 'likes_count', 'comments_count',
        'uploaded_at', 'video_thumbnail', 'is_popular'
    )
    list_filter = (
        'uploaded_at', 'creator__is_creator', 'views'
    )
    search_fields = ('title', 'description', 'creator__username')
    ordering = ('-uploaded_at',)
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Video Information', {
            'fields': ('title', 'slug', 'description', 'creator')
        }),
        ('Media Files', {
            'fields': ('video_file', 'thumbnail', 'duration')
        }),
        ('Engagement', {
            'fields': ('views', 'likes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('uploaded_at', 'updated_at', 'slug')
    filter_horizontal = ('likes',)
    
    def likes_count(self, obj):
        """Display like count with styling."""
        count = obj.total_likes()
        if count > 10:
            return format_html(
                '<span style="color: red; font-weight: bold;">❤️ {}</span>',
                count
            )
        elif count > 0:
            return format_html('❤️ {}', count)
        return '0'
    likes_count.short_description = 'Likes'
    
    def comments_count(self, obj):
        """Display comment count with link."""
        count = obj.comment_set.count()
        if count > 0:
            url = reverse('admin:core_comment_changelist') + f'?video__id__exact={obj.id}'
            return format_html(
                '<a href="{}" style="color: blue;">💬 {}</a>',
                url, count
            )
        return '0'
    comments_count.short_description = 'Comments'
    
    def video_thumbnail(self, obj):
        """Display video thumbnail if available."""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="50" height="30" style="border-radius: 4px;" />',
                obj.thumbnail.url
            )
        return '📹'
    video_thumbnail.short_description = 'Thumbnail'
    
    def is_popular(self, obj):
        """Mark popular videos."""
        if obj.views > 100:
            return '🔥 Popular'
        elif obj.views > 50:
            return '📈 Trending'
        return '🆕 New'
    is_popular.short_description = 'Status'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Comment model."""
    
    list_display = (
        'user', 'video_title', 'content_preview', 'created_at', 'is_recent'
    )
    list_filter = ('created_at', 'video__creator')
    search_fields = ('content', 'user__username', 'video__title')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Comment Details', {
            'fields': ('user', 'video', 'content')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def video_title(self, obj):
        """Display video title with link."""
        url = reverse('admin:core_video_change', args=[obj.video.id])
        return format_html(
            '<a href="{}" style="color: blue;">{}</a>',
            url, obj.video.title[:30] + '...' if len(obj.video.title) > 30 else obj.video.title
        )
    video_title.short_description = 'Video'
    
    def content_preview(self, obj):
        """Display content preview."""
        preview = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return format_html('<span title="{}">{}</span>', obj.content, preview)
    content_preview.short_description = 'Content'
    
    def is_recent(self, obj):
        """Mark recent comments."""
        from django.utils import timezone
        from datetime import timedelta
        
        if obj.created_at > timezone.now() - timedelta(hours=24):
            return '🆕 New'
        elif obj.created_at > timezone.now() - timedelta(days=7):
            return '📅 This week'
        return '📆 Older'
    is_recent.short_description = 'Age'


@admin.register(ChannelSubscription)
class ChannelSubscriptionAdmin(admin.ModelAdmin):
    """Enhanced admin interface for ChannelSubscription model."""
    
    list_display = (
        'subscriber', 'creator', 'subscribed_at', 'creator_video_count', 'is_active_subscription'
    )
    list_filter = ('subscribed_at', 'creator__is_creator')
    search_fields = ('subscriber__username', 'creator__username')
    ordering = ('-subscribed_at',)
    date_hierarchy = 'subscribed_at'
    
    fieldsets = (
        ('Subscription Details', {
            'fields': ('subscriber', 'creator', 'subscribed_at')
        }),
    )
    
    readonly_fields = ('subscribed_at',)
    
    def creator_video_count(self, obj):
        """Display creator's video count."""
        count = obj.creator.video_set.count()
        return format_html(
            '<span style="color: green;">{} videos</span>',
            count
        )
    creator_video_count.short_description = 'Creator Videos'
    
    def is_active_subscription(self, obj):
        """Check if subscription is active."""
        if obj.creator.video_set.exists():
            return '✅ Active'
        return '⚠️ Inactive Creator'
    is_active_subscription.short_description = 'Status'


@admin.register(subsciption)
class LegacySubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for legacy subscription model."""
    
    list_display = (
        'learner', 'video_title', 'enrolled_at', 'completed', 'completion_status'
    )
    list_filter = ('enrolled_at', 'completed')
    search_fields = ('learner__username', 'video__title')
    ordering = ('-enrolled_at',)
    
    fieldsets = (
        ('Legacy Subscription', {
            'fields': ('learner', 'video', 'enrolled_at', 'completed'),
            'description': 'This is a legacy subscription model. New subscriptions use ChannelSubscription.'
        }),
    )
    
    readonly_fields = ('enrolled_at',)
    
    def video_title(self, obj):
        """Display video title."""
        return obj.video.title[:40] + '...' if len(obj.video.title) > 40 else obj.video.title
    video_title.short_description = 'Video'
    
    def completion_status(self, obj):
        """Display completion status with styling."""
        if obj.completed:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ Completed</span>'
            )
        return format_html(
            '<span style="color: orange;">⏳ In Progress</span>'
        )
    completion_status.short_description = 'Status'


# Customize admin site headers
admin.site.site_header = "SkillStream Administration"
admin.site.site_title = "SkillStream Admin"
admin.site.index_title = "Welcome to SkillStream Administration"
