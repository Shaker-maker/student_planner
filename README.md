# Student Study Planner

An automated timetable extraction and personalized notification system designed to help students efficiently manage their academic schedules and receive timely reminders about upcoming classes and assignments.

## 🎯 Overview

The Student Study Planner is a Django-based web application that simplifies academic schedule management by:
- **Automatically extracting class schedules** from institutional PDF timetables
- **Personalizing schedules** based on student course, year, and semester information
- **Sending customizable email reminders** for classes and assignments
- **Managing assignments and tasks** with deadline tracking
- **Providing a user-friendly interface** for profile management and schedule viewing

## ✨ Key Features

### 📋 Timetable Management
- Automated PDF timetable extraction with 99% accuracy
- GROUP-based personalization (students see only their relevant classes)
- Support for multiple semesters and years
- Manual entry editing and deletion
- Batch PDF upload and processing

### 🔔 Notification System
- Automated email reminders for upcoming classes
- Customizable reminder times and frequencies
- Daily schedule summaries
- Task/assignment deadline alerts
- Configurable notification preferences per user

### 👤 Account Management
- User registration and authentication
- Profile management with semester selection
- Profile picture support
- GDPR-compliant account deletion
- Account settings customization

### 📝 Task & Assignment Tracking
- Create and manage assignments with deadlines
- Receive email reminders before deadlines
- Track assignment completion status
- Reminder history and logs

### 🛠️ Technical Features
- Background job processing with APScheduler and Celery
- Advanced PDF processing with pdfplumber and spaCy NLP
- Email service with Gmail SMTP integration
- Database migrations for scalability
- Error handling and comprehensive logging
- Timezone support (default: Africa/Nairobi)

## 🏗️ Tech Stack

### Backend
- **Framework:** Django 5.2.7
- **Database:** SQLite (default) / PostgreSQL (configurable)
- **Task Queue:** Celery 5.3.1 + Redis
- **Job Scheduler:** APScheduler
- **Email:** Gmail SMTP
- **PDF Processing:** pdfplumber
- **NLP:** spaCy

### Frontend
- **HTML/CSS/JavaScript**
- **Crispy Forms** (Bootstrap 5 styling)
- **Responsive Design**

### Infrastructure
- Python 3.8+
- Redis (for task queuing)
- Virtual Environment (venv)

## 📋 Prerequisites

Before you begin, ensure you have:
- **Python 3.8 or higher**
- **Redis Server** (for background jobs)
- **Gmail account** with [App Passwords enabled](https://myaccount.google.com/apppasswords)
- **Git** (optional, for version control)
- **pip** (Python package manager)

## 🚀 Installation & Setup

### 1. Clone or Download the Project
```bash
cd student_study_planner
```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r CELERY_REQUIREMENTS.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Gmail SMTP Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password  # Get from myaccount.google.com/apppasswords

# Database (Optional)
DATABASE_URL=postgresql://user:password@localhost:5432/study_planner

# Timezone
TIME_ZONE=Africa/Nairobi

# Allowed Hosts (Production)
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser (Admin Account)
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin account.

### 7. Collect Static Files (for production)
```bash
python manage.py collectstatic --noinput
```

## 🎮 Running the Application

### Development Mode

#### Terminal 1: Start Redis Server
```bash
redis-server
```
Make sure Redis is running on the default port 6379.

#### Terminal 2: Start Django Development Server
```bash
source venv/bin/activate
python manage.py runserver
```
Access the application at `http://localhost:8000`

#### Terminal 3: Start Celery Worker
```bash
source venv/bin/activate
celery -A study_planner worker -l info
```

#### Terminal 4: Start Celery Beat (Scheduler)
```bash
source venv/bin/activate
celery -A study_planner beat -l info
```

### Quick Status Check
Run the startup guide to verify configuration:
```bash
python startup_guide.py
```

## 📁 Project Structure

```
student_study_planner/
├── README.md                           # This file
├── manage.py                           # Django management script
├── db.sqlite3                          # SQLite database
├── .env.example                        # Environment variables template
├── requirements.txt                    # Python dependencies
├── CELERY_REQUIREMENTS.txt             # Celery-specific dependencies
│
├── study_planner/                      # Main Django project settings
│   ├── settings.py                     # Django settings
│   ├── urls.py                         # URL routing
│   ├── wsgi.py                         # WSGI configuration
│   ├── asgi.py                         # ASGI configuration
│   ├── email_backend.py                # Custom email backend
│   ├── middleware.py                   # Custom middleware
│   ├── scheduler_instance.py           # APScheduler configuration
│   └── celery.py                       # Celery configuration
│
├── accounts/                           # User authentication & profiles
│   ├── models.py                       # User model with profile extensions
│   ├── views.py                        # Registration, login, profile views
│   ├── forms.py                        # User forms
│   ├── urls.py                         # Account URLs
│   └── migrations/                     # Database migrations
│
├── timetable/                          # Timetable management
│   ├── models.py                       # TimeTableEntry model
│   ├── views.py                        # Timetable views
│   ├── services.py                     # PDF extraction logic
│   ├── schedulers.py                   # APScheduler jobs
│   ├── urls.py                         # Timetable URLs
│   ├── utils/                          # Utility functions
│   ├── management/                     # Django management commands
│   └── migrations/                     # Database migrations
│
├── tasks/                              # Assignment & task management
│   ├── models.py                       # Task and ReminderLog models
│   ├── views.py                        # Task views
│   ├── email_service.py                # Task email notifications
│   ├── schedulers.py                   # Task scheduling logic
│   ├── urls.py                         # Task URLs
│   └── migrations/                     # Database migrations
│
├── notifications/                      # Notification system
│   ├── models.py                       # NotificationLog model
│   ├── views.py                        # Notification views
│   ├── management/                     # Django management commands
│   └── migrations/                     # Database migrations
│
├── templates/                          # HTML templates
│   ├── base.html                       # Base template
│   ├── home_dashboard.html             # Dashboard
│   ├── landing.html                    # Landing page
│   ├── emails/                         # Email templates
│   │   ├── class_reminder.html
│   │   ├── class_reminder.txt
│   │   ├── daily_schedule.html
│   │   ├── daily_schedule.txt
│   │   ├── task_reminder.html
│   │   └── task_reminder.txt
│   ├── timetable/                      # Timetable templates
│   ├── accounts/                       # Account templates
│   └── tasks/                          # Task templates
│
├── static/                             # Static files (CSS, JS, images)
├── media/                              # User-uploaded files
│   ├── profile_pictures/               # User profile pictures
│   └── timetables/                     # Uploaded PDF timetables
│
└── test_*.py                           # Test files
```

## 🔐 Security Configuration

### Email Setup (Gmail)
1. Go to [Google Account Security](https://myaccount.google.com/apppasswords)
2. Select "Mail" and "Linux"
3. Generate a 16-character app password
4. Add to `.env` as `EMAIL_HOST_PASSWORD`

### Production Checklist
- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate a strong `SECRET_KEY`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Set up proper email configuration
- [ ] Configure Redis with authentication
- [ ] Set up proper logging and monitoring

## 📚 Key Models

### User Profile
Extended Django User model with:
- Profile picture
- Semester selection
- Class reminders preference
- Task reminders preference
- Schedule reminders preference

### TimeTableEntry
Stores individual class schedule entries:
- Unit code and name
- Lecturer name
- Day and time
- Venue/Location
- GROUP information for personalization

### Task
Assignment/task management:
- Title and description
- Deadline
- Completion status
- Reminder times

### NotificationLog
Tracks all notifications sent:
- Recipient
- Message type (class, task, schedule)
- Timestamp
- Status (sent, failed)

## 🔄 Workflow

1. **User Registration**: Student creates account and selects their course/year/semester
2. **PDF Upload**: Student uploads institutional timetable PDF
3. **Automatic Extraction**: System extracts schedule based on student's GROUP
4. **Schedule Viewing**: Student views personalized timetable
5. **Notification Setup**: Student configures reminder preferences
6. **Automated Reminders**: System sends email reminders at configured times
7. **Task Management**: Student adds and manages assignments with reminders

## 📧 Email Templates

The system includes customizable email templates:
- **Class Reminder**: Notifies about upcoming classes
- **Daily Schedule**: Sends daily schedule summary
- **Task Reminder**: Alerts about assignment deadlines

## 🧪 Testing

Run test files to verify functionality:
```bash
# Test email configuration
python check_email_config.py

# Test PDF extraction
python test_pdf_extraction_fixes.py

# Test notifications
python test_notifications.py

# Check user data
python check_user.py
```

## 📊 Database Migrations

Run migrations after pulling updates:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 🐛 Troubleshooting

### Redis Connection Error
```bash
# Ensure Redis is running
redis-server

# Check Redis status
redis-cli ping  # Should return PONG
```

### Email Not Sending
- Verify Gmail app password is correct
- Check that 2-factor authentication is enabled on Gmail
- Ensure `EMAIL_HOST_USER` matches the Gmail account with app password
- Check email logs in Django admin

### PDF Extraction Issues
- Verify PDF format is compatible with pdfplumber
- Check that student GROUP code matches PDF table structure
- Review `debug_pdf_extraction.py` for troubleshooting

### Database Errors
```bash
# Reset database (development only)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## 📞 Support & Contribution

For issues, questions, or contributions:
1. Check existing test files for similar issues
2. Review PROJECT_DOCUMENTATION.md for detailed specifications
3. Check logs in media/ and console output
4. Review error messages in Django admin

## 📄 License

This project is submitted as a partial fulfillment of requirements for the Bachelor of Science in Software Engineering at Multimedia University of Kenya.

## 👨‍🎓 Academic Information

**University:** Multimedia University of Kenya  
**Faculty:** Computing & Information Technology  
**Program:** Bachelor of Science in Software Engineering/Computer Science  
**Date:** June 2026

---

**Happy studying! 📚**
