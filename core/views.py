"""
SkillStream Views - Business Logic and Request Handling

This module contains all the view functions that handle user requests,
implement business logic, and return appropriate responses.

Design Philosophy:
- Separation of concerns: Views handle HTTP logic, models handle data logic
- Role-based access control: Different experiences for creators vs learners
- API-first approach: Traditional views + REST endpoints for future scalability
- User experience focus: Intuitive flows and helpful feedback messages

Key Business Logic:
- Automatic creator promotion when user uploads first video
- Channel-based subscriptions (YouTube-like) vs legacy video subscriptions
- View counting and engagement tracking
- Search across multiple fields (title, description, creator)
"""

from django.shortcuts import render, redirect
from .forms import CustomerCreationForm, VideouploadForm, CommentForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Video, subsciption, Comment, CustomerUser, ChannelSubscription
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.db.models import Q
from django.http import JsonResponse





# ========== HOME AND LANDING VIEWS ==========

def home(request):
    """
    Home page with dual functionality based on authentication status
    
    Design Decision: Single view handles both landing page and video feed
    - Unauthenticated users: See landing page with features and sample videos
    - Authenticated users: See full video feed (YouTube-like experience)
    
    Business Logic:
    - Shows 12 most recent videos for better content discovery
    - Template conditionally renders different content based on auth status
    - Provides immediate value to logged-in users (content front and center)
    """
    # Show more videos for a better feed experience (increased from 6 to 12)
    videos = Video.objects.order_by('-uploaded_at')[:12]
    
    # Pass authentication status to template for conditional rendering
    context = {
        'videos': videos,
        'is_authenticated': request.user.is_authenticated
    }
    
    return render(request, 'home.html', context)







# ========== AUTHENTICATION VIEWS ==========

def register(request):
    """
    User registration with custom user model
    
    Design Decision: Simple registration flow with immediate redirect to login
    - Uses custom CustomerCreationForm for extended user model
    - All users start as students (is_student=True by default)
    - Creator status is automatically granted on first video upload
    
    Business Logic:
    - Form validation handled by Django forms
    - Successful registration redirects to login (no auto-login for security)
    - Failed registration re-renders form with error messages
    """
    if request.method == 'POST':
        form = CustomerCreationForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomerCreationForm()

    context = {'form': form}
    
    return render(request, 'registration/register.html', context)


# ========== DASHBOARD VIEWS ==========

@login_required
def creator_dashboard(request):
    """
    Creator Studio - Content management dashboard for creators
    
    Design Decision: Separate dashboard for creators vs learners
    - Only accessible to users with is_creator=True
    - Focuses on content management and analytics
    - Provides creator-specific metrics and tools
    
    Business Logic:
    - Shows only videos created by current user
    - Calculates total views across all creator's videos
    - Counts channel subscribers (not individual video subscribers)
    - Redirects non-creators to learner dashboard for better UX
    
    Key Features:
    - Video management (upload, view, delete)
    - Performance analytics (views, subscribers)
    - Enhanced video previews with hover-to-play
    """
    if request.user.is_creator:
        # Get creator's videos for management and analytics
        videos = Video.objects.filter(creator=request.user)
        
        # Calculate aggregate metrics for creator analytics
        total_views = sum(video.views for video in videos) if videos else 0
        subscriber_count = ChannelSubscription.objects.filter(creator=request.user).count()
        
        return render(request, 'Dashboard.html/creator_dashboard.html', 
                    {'user_type': 'creator',
                    'videos': videos,
                    'total_views': total_views,
                    'subscriber_count': subscriber_count})
    else:
        # Non-creators redirected to appropriate dashboard
        return redirect('learner_dashboard')



@login_required
def learner_dashboard(request):
    """
    Learner Dashboard - Content discovery and subscription management
    
    Design Decision: Personalized dashboard prioritizing subscribed content
    - Shows subscribed creators' videos first (personalized content)
    - Then shows all available videos for discovery
    - Focuses on content consumption rather than creation
    
    Business Logic:
    - Uses channel subscriptions to filter personalized content
    - Efficient query: Gets creator IDs first, then filters videos
    - Separates subscribed vs all videos for better UX organization
    - Redirects creators to their appropriate dashboard
    
    Key Features:
    - "From Your Subscriptions" section with priority placement
    - "Discover More" section with all platform content
    - Same enhanced video previews as other dashboards
    """
    if request.user.is_student:
        # Get user's channel subscriptions for personalized content
        subscribed_creators = ChannelSubscription.objects.filter(subscriber=request.user)
        
        # Efficient query: Get creator IDs first, then filter videos
        subscribed_creator_ids = subscribed_creators.values_list('creator', flat=True)
        subscribed_videos = Video.objects.filter(creator__in=subscribed_creator_ids)
        
        # All videos for discovery section
        all_videos = Video.objects.all()
        
        return render(request, 'Dashboard.html/learner_dashboard.html',
                    {'user_type': 'learner',
                    'subscribed_videos': subscribed_videos,
                    'subscribed_creators': subscribed_creators,
                    'all_videos': all_videos})
    else:
        # Non-students (creators) redirected to creator dashboard
        return redirect('creator_dashboard') 


@login_required
def dashboard_redirect(request):
    if request.user.is_creator:
        return redirect('creator_dashboard')
    elif request.user.is_student:
        return redirect('learner_dashboard')
    else:
        return redirect('home')




@login_required
def user_profile(request):
    user = request.user
    subscribe_to_creator = ChannelSubscription.objects.filter(subscriber=user)
    user_comments_count = Comment.objects.filter(user=user).count()

    context = {'user': user,
               'subscribe_to_creator': subscribe_to_creator,
               'user_comments_count': user_comments_count,
               }
    
    return render(request, 'Dashboard.html/user_profile.html', context)





# ========== VIDEO MANAGEMENT VIEWS ==========

@login_required
def upload_video(request):
    """
    Video upload with automatic creator promotion
    
    Design Decision: Automatic creator status promotion on first upload
    - Any user can upload videos (democratized content creation)
    - First upload automatically grants creator privileges
    - Redirects to creator dashboard after successful upload
    
    Business Logic:
    - Form handles file upload and validation
    - Creator field automatically set to current user (security)
    - User promotion: is_creator becomes True on first upload
    - Success message provides user feedback
    - Redirect to creator dashboard shows new video immediately
    
    Security Considerations:
    - commit=False prevents saving before setting creator
    - Only authenticated users can upload
    - File validation handled by form/model
    """
    if request.method == 'POST':
        form = VideouploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Don't save yet - need to set creator first
            video = form.save(commit=False)
            video.creator = request.user  # Security: Always set to current user
            video.save()

            # Automatic creator promotion on first upload
            if not request.user.is_creator:
                request.user.is_creator = True
                request.user.save()
            
            messages.success(request, "Your video was uploaded successfully!")
            return redirect('creator_dashboard')  # Show new video immediately
    else:
        form = VideouploadForm()

    context = {'form': form}
    return render(request, 'Dashboard.html/upload_video.html', context)

@login_required
def watch_video(request, video_id):
    """
    Video player page with engagement tracking and social features
    
    Design Decision: Central hub for video consumption and interaction
    - Combines video playback with comments, likes, and subscription features
    - Tracks engagement metrics (view count) automatically
    - Shows subscription status for easy channel following
    
    Business Logic:
    - View count incremented on every page load (simple analytics)
    - Subscription check uses new ChannelSubscription model
    - Comments ordered by newest first for active discussion
    - All interaction forms pre-loaded for seamless UX
    
    Key Features:
    - Automatic view counting for creator analytics
    - Channel subscription status and toggle button
    - Comment system with real-time form
    - Like/unlike functionality
    - Creator information display
    """
    video = get_object_or_404(Video, id=video_id)

    # Engagement tracking: Increment view count on each visit
    # Note: In production, this could be optimized with session tracking
    # to prevent multiple counts from same user
    video.views += 1
    video.save()

    # Check subscription status using modern channel-based system
    is_subscribed = ChannelSubscription.objects.filter(
        subscriber=request.user, 
        creator=video.creator
    ).exists()

    # Load comments for discussion (newest first for active conversation)
    comments = video.comment_set.all().order_by('-created_at')
    form = CommentForm()  # Pre-load form for immediate commenting

    context = {
        'video': video,
        'comments': comments,
        'form': form,
        'is_subscribed': is_subscribed
    }

    return render(request, 'videos/watch_video.html', context)


# ========== SEARCH AND DISCOVERY VIEWS ==========

@login_required
def search_videos(request):
    """
    Advanced search functionality across multiple fields
    
    Design Decision: Comprehensive search across title, description, and creator
    - Uses Django Q objects for complex OR queries
    - Case-insensitive search with icontains for better UX
    - Results ordered by upload date (newest first)
    
    Business Logic:
    - Empty query returns empty results (prevents showing all videos)
    - Searches across three key fields for maximum discoverability
    - Provides results count for user feedback
    - Uses same video card template as other views for consistency
    
    Search Fields:
    - Video title: Primary search target
    - Video description: Catches topic-based searches
    - Creator username: Enables creator-specific searches
    """
    q = request.GET.get('q') or ''
    
    # Multi-field search using Q objects for complex queries
    videos = Video.objects.filter(
        Q(title__icontains=q) |           # Search in video titles
        Q(description__icontains=q) |     # Search in descriptions
        Q(creator__username__icontains=q) # Search by creator name
    ).order_by('-uploaded_at')            # Newest results first

    context = {
        'videos': videos,
        'search_query': q,
        'results_count': videos.count()
    }
    
    return render(request, 'search_results.html', context)

@login_required
def follow_creator(request, creator_id):
    creator = get_object_or_404(CustomerUser, id=creator_id)

    if creator == request.user:
        messages.warning(request, "You cannot follow yourself.")
        return redirect('creator_profile', creator_id=creator_id)

    # Check if the user is already following the creator
    already_following = creator.followers.filter(id=request.user.id).exists()

    if already_following:
        messages.info(request, "You are already following this creator.")
    else:
        # Follow the creator
        creator.followers.add(request.user)
        messages.success(request, "You are now following this creator.")

    return redirect('creator_profile', creator_id=creator_id)


@login_required
def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    # only the creator can delete their own video
    if request.user == video.creator:
        video.delete()
    else:
        messages.error(request, "You do not have permission to delete this video.")
    
    return redirect('creator_dashboard')






@login_required
def user_comment(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.video = video
            comment.save()
    
    return redirect('watch_video', video_id=video_id)


# ========== SOCIAL INTERACTION VIEWS ==========

@login_required
def toggle_subscription(request, video_id):
    """
    Channel subscription toggle (YouTube-like subscription system)
    
    Design Decision: Channel-based subscriptions instead of video-based
    - Users subscribe to creators (channels), not individual videos
    - One subscription gives access to all creator's content
    - Prevents self-subscription for logical consistency
    
    Business Logic:
    - Gets creator from video (subscription is channel-based)
    - Checks existing subscription to determine toggle action
    - Creates or deletes ChannelSubscription record
    - Provides clear feedback messages to user
    - Redirects back to video page for seamless UX
    
    Key Features:
    - Toggle functionality (subscribe/unsubscribe with same button)
    - Self-subscription prevention with error message
    - Channel-focused (not video-focused) subscription model
    """
    video = get_object_or_404(Video, id=video_id)
    creator = video.creator
    
    # Check if user is already subscribed to this creator's channel
    subscription = ChannelSubscription.objects.filter(subscriber=request.user, creator=creator).first()

    # Prevent self-subscription (logical business rule)
    if request.user == creator:
        messages.error(request, "You cannot subscribe to your own channel.")
        return redirect('watch_video', video_id=video_id)
    
    if subscription:
        # Unsubscribe from channel
        subscription.delete()
        messages.success(request, f"You have unsubscribed from {creator.username}'s channel")
    else:
        # Subscribe to channel
        ChannelSubscription.objects.create(subscriber=request.user, creator=creator)
        messages.success(request, f"You have subscribed to {creator.username}'s channel")
    
    return redirect('watch_video', video_id=video_id)


@login_required
def like_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    
    if request.user in video.likes.all():
        # Unlike the video
        video.likes.remove(request.user)
        messages.success(request, f"You unliked '{video.title}'")
    else:
        # Like the video
        video.likes.add(request.user)
        messages.success(request, f"You liked '{video.title}'")
    
    return redirect('watch_video', video_id=video_id)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard_redirect')
        else:
            messages.error(request, "❌ Username or password is incorrect")
    
    return render(request, 'registration/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')




# ========== SIMPLE REST API ENDPOINTS ==========
# These return JSON data instead of HTML pages

def api_videos_list(request):
    """
    Simple API endpoint that returns all videos as JSON
    Example: GET /api/videos/ 
    """
    videos = Video.objects.all()[:20]  # Limit to 20 for performance
    
    videos_data = []
    for video in videos:
        videos_data.append({
            'id': video.id,
            'title': video.title,
            'description': video.description,
            'creator': video.creator.username,
            'views': video.views,
            'likes': video.total_likes(),
            'uploaded_at': video.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
            'video_url': video.video_file.url if video.video_file else None,
        })
    
    return JsonResponse({
        'success': True,
        'count': len(videos_data),
        'videos': videos_data
    })

def api_video_detail(request, video_id):
    """
    API endpoint that returns details of a specific video
    Example: GET /api/videos/1/
    """
    try:
        video = Video.objects.get(id=video_id)
        
        video_data = {
            'id': video.id,
            'title': video.title,
            'description': video.description,
            'creator': {
                'id': video.creator.id,
                'username': video.creator.username,
                'is_creator': video.creator.is_creator,
            },
            'views': video.views,
            'likes': video.total_likes(),
            'uploaded_at': video.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
            'video_url': video.video_file.url if video.video_file else None,
        }
        
        return JsonResponse({
            'success': True,
            'video': video_data
        })
        
    except Video.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Video not found'
        }, status=404)

@login_required
def api_user_stats(request):
    """
    API endpoint that returns current user's statistics
    Example: GET /api/user/stats/
    """
    user = request.user
    
    # Get user stats
    uploaded_videos = Video.objects.filter(creator=user)
    subscriptions = ChannelSubscription.objects.filter(subscriber=user)
    comments_count = Comment.objects.filter(user=user).count()
    
    user_stats = {
        'username': user.username,
        'is_creator': user.is_creator,
        'uploaded_videos_count': uploaded_videos.count(),
        'total_views': sum(video.views for video in uploaded_videos),
        'subscriptions_count': subscriptions.count(),
        'comments_count': comments_count,
    }
    
    # If user is a creator, add subscriber count
    if user.is_creator:
        user_stats['subscribers_count'] = ChannelSubscription.objects.filter(creator=user).count()
    
    return JsonResponse({
        'success': True,
        'user_stats': user_stats
    })