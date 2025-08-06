# SkillStream - Django Video Learning Platform

A modern video learning platform built with Django that enables creators to upload educational content and learners to discover and engage with videos.

## 🚀 Features

- **User Authentication**: Secure registration and login system
- **Role-Based Access**: Separate experiences for creators and learners
- **Video Upload**: Easy video upload with automatic creator promotion
- **Content Discovery**: Search and browse videos by title, description, or creator
- **Social Features**: Like videos, comment, and subscribe to creators
- **Responsive Design**: Mobile-friendly interface with Bootstrap
- **Dashboard Analytics**: Creator statistics and performance metrics

## 🛠️ Tech Stack

- **Backend**: Django 5.2, Python 3.9+
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **File Storage**: Local filesystem (development), cloud storage ready
- **Authentication**: Django's built-in authentication system

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git

## 🔧 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/adonai1763/SkillStream-Django-application.git
   cd SkillStream-Django-application
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv skillstream_env
   source skillstream_env/bin/activate  # On Windows: skillstream_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000`
   - Admin panel: `http://127.0.0.1:8000/admin`

## 📁 Project Structure

```
SkillStream/
├── config/                 # Project configuration
│   ├── settings/          # Environment-specific settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── core/                  # Main application
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── forms.py          # Django forms
│   ├── urls.py           # App URL patterns
│   └── templates/        # HTML templates
├── media/                 # User uploaded files
├── static/               # Static files (CSS, JS, images)
├── requirements/         # Environment-specific requirements
└── manage.py            # Django management script
```

## 🎯 Usage

### For Learners
1. **Register** for a new account or **login**
2. **Browse videos** on the home page
3. **Search** for specific content or creators
4. **Watch videos** and engage with comments
5. **Subscribe** to your favorite creators
6. **Like videos** to show appreciation

### For Creators
1. **Upload your first video** to become a creator
2. **Access Creator Dashboard** to manage your content
3. **View analytics** including views and subscriber count
4. **Delete videos** you no longer want to share
5. **Build your audience** through quality content

## 🔗 API Endpoints

The application includes REST API endpoints:

- `GET /api/videos/` - List all videos
- `GET /api/videos/{id}/` - Get video details
- `GET /api/user/stats/` - Get user statistics (authenticated)

## 🚀 Deployment

The application is configured for deployment on:
- **Heroku** (with PostgreSQL)
- **Render** (with PostgreSQL)
- **DigitalOcean** (App Platform)

Environment variables needed for production:
- `SECRET_KEY`
- `DEBUG=False`
- `DATABASE_URL`
- `ALLOWED_HOSTS`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Adonai Teklit**
- GitHub: [@adonai1763](https://github.com/adonai1763)
- Email: adonaiteklit24@gmail.com

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the responsive CSS framework
- All contributors and users of this platform

---

⭐ **Star this repository if you found it helpful!**