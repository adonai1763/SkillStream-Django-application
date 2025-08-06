from django.urls import path
from . import views





urlpatterns = [

    # Home page
    path('', views.home, name='home'),

    # Auth/registration
    path('register/', views.register, name='register'),
    
    # Role-based deshboards
    path('learner/dashboard/', views.learner_dashboard, name='learner_dashboard'),
    path('creator/dashboard/', views.creator_dashboard, name='creator_dashboard'),
    
    # User profile
    path('profile/', views.user_profile, name='user_profile'),
    
    # Redirect after login
    path('dashboard-redirect/', views.dashboard_redirect, name='dashboard_redirect'),

    # upload videos
    path('upload/', views.upload_video, name='upload_video'),

    # view_videos
    path('watch_video/<int:video_id>/', views.watch_video, name='watch_video'),

    # search videos
    path('search/', views.search_videos, name='search_videos'),

    # follow user
    path('follow/<int:user_id>/', views.follow_creator, name='follow_creator'),

    # user comment
    path('comment/<int:video_id>/', views.user_comment, name='user_comment'),

    # toggle subscription
    path('subscribe/<int:video_id>/', views.toggle_subscription, name='toggle_subscription'),

    # like video
    path('like/<int:video_id>/', views.like_video, name='like_video'),

    # delete video
    path('delete_video/<int:video_id>/', views.delete_video, name='delete_video'),

    # user login
    path('login/', views.user_login, name='user_login'),

    # user logout
    path('logout/', views.user_logout, name='user_logout'),

    # ========== API ENDPOINTS ==========
    # Simple REST API endpoints that return JSON data
    path('api/videos/', views.api_videos_list, name='api_videos_list'),
    path('api/videos/<int:video_id>/', views.api_video_detail, name='api_video_detail'),
    path('api/user/stats/', views.api_user_stats, name='api_user_stats'),

]