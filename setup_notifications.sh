#!/bin/bash

# Study Planner Notifications System - Quick Setup Script
# This script automates the setup of Celery, Redis, and notifications

echo "🚀 Study Planner Notifications System - Setup"
echo "=============================================="
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ Virtual environment not activated"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment detected: $VIRTUAL_ENV"
echo ""

# Step 1: Install dependencies
echo "📦 Installing Celery and Redis dependencies..."
pip install celery redis django-celery-beat django-celery-results
echo "✅ Dependencies installed"
echo ""

# Step 2: Create migrations
echo "🗄️ Creating database migrations..."
python manage.py makemigrations notifications
python manage.py makemigrations accounts
python manage.py makemigrations tasks
echo "✅ Migrations created"
echo ""

# Step 3: Apply migrations
echo "📤 Applying migrations to database..."
python manage.py migrate
echo "✅ Migrations applied"
echo ""

# Step 4: Initialize notification preferences
echo "⚙️ Initializing notification preferences for existing users..."
python manage.py init_notification_prefs
echo "✅ Notification preferences initialized"
echo ""

# Step 5: Verify Redis
echo "🔍 Checking Redis connection..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is running and accessible"
    else
        echo "⚠️  Redis CLI found but not responding"
        echo "   Start Redis with: redis-server"
    fi
else
    echo "⚠️  Redis CLI not found in PATH"
    echo "   Install Redis or use Docker: docker run -d -p 6379:6379 redis"
fi
echo ""

echo "✨ Setup complete!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Start Redis (if not already running):"
echo "   redis-server"
echo "   OR (using Docker):"
echo "   docker run -d -p 6379:6379 redis"
echo ""
echo "2. In terminal 1 - Django dev server:"
echo "   python manage.py runserver"
echo ""
echo "3. In terminal 2 - Celery worker:"
echo "   celery -A study_planner worker -l info"
echo ""
echo "4. In terminal 3 - Celery Beat scheduler:"
echo "   celery -A study_planner beat -l info"
echo ""
echo "5. Test the system:"
echo "   python manage.py shell"
echo "   >>> from tasks.celery_tasks import send_daily_reminders"
echo "   >>> send_daily_reminders()"
echo ""
echo "📚 For more details, see NOTIFICATIONS_SETUP.md"
