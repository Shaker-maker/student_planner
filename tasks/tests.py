from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Task, ReminderLog

User = get_user_model()


class TaskModelTest(TestCase):
    """Test cases for the Task model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='student@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )
    
    def test_create_task(self):
        """Test creating a task"""
        task = Task.objects.create(
            user=self.user,
            name='Database Assignment',
            unit_name='Database Systems',
            task_type='assignment',
            due_date=timezone.now() + timedelta(days=5),
            status='pending'
        )
        self.assertEqual(task.name, 'Database Assignment')
        self.assertEqual(task.unit_name, 'Database Systems')
        self.assertEqual(task.task_type, 'assignment')
        self.assertEqual(task.status, 'pending')
    
    def test_get_days_left(self):
        """Test days left calculation"""
        now = timezone.now()
        task = Task.objects.create(
            user=self.user,
            name='Test Task',
            unit_name='Test Unit',
            due_date=now + timedelta(days=5),
            status='pending'
        )
        # Account for timing: should be 5 or 4 days depending on execution time
        days_left = task.get_days_left()
        self.assertIn(days_left, [4, 5])
    
    def test_get_reminder_message_multiple_days(self):
        """Test reminder message for tasks with 5+ days"""
        now = timezone.now()
        task = Task.objects.create(
            user=self.user,
            name='Test Assignment',
            unit_name='Test Unit',
            due_date=now + timedelta(days=5),
            status='pending'
        )
        message = task.get_reminder_message()
        self.assertIn('John', message)
        # Should mention 4 or 5 days depending on execution time
        self.assertTrue('4 days' in message or '5 days' in message)
    
    def test_get_reminder_message_tomorrow(self):
        """Test reminder message for tasks due tomorrow"""
        now = timezone.now()
        # Set due date to tomorrow at the same time
        tomorrow = now + timedelta(days=1)
        task = Task.objects.create(
            user=self.user,
            name='Test CAT',
            unit_name='Test Unit',
            task_type='cat',
            due_date=tomorrow,
            status='pending'
        )
        days_left = task.get_days_left()
        message = task.get_reminder_message()
        # Should be either 0 or 1 day depending on current hour
        if days_left == 1:
            self.assertIn('tomorrow', message)
        elif days_left == 0:
            self.assertIn("today's the deadline", message)
    
    def test_is_overdue(self):
        """Test overdue detection"""
        now = timezone.now()
        task = Task.objects.create(
            user=self.user,
            name='Overdue Task',
            unit_name='Test Unit',
            due_date=now - timedelta(days=1),
            status='pending'
        )
        self.assertTrue(task.is_overdue())
    
    def test_is_due_today(self):
        """Test due today detection"""
        now = timezone.now()
        task = Task.objects.create(
            user=self.user,
            name='Today Task',
            unit_name='Test Unit',
            due_date=now.replace(hour=23, minute=59, second=59),
            status='pending'
        )
        self.assertTrue(task.is_due_today())
    
    def test_task_ordering(self):
        """Test that tasks are ordered by due date"""
        now = timezone.now()
        task1 = Task.objects.create(
            user=self.user,
            name='First Task',
            unit_name='Unit 1',
            due_date=now + timedelta(days=3),
            status='pending'
        )
        task2 = Task.objects.create(
            user=self.user,
            name='Second Task',
            unit_name='Unit 2',
            due_date=now + timedelta(days=1),
            status='pending'
        )
        tasks = Task.objects.all()
        self.assertEqual(tasks.first().name, 'Second Task')
        self.assertEqual(tasks.last().name, 'First Task')


class ReminderLogModelTest(TestCase):
    """Test cases for the ReminderLog model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='student@example.com',
            first_name='Jane',
            last_name='Smith',
            password='testpass123'
        )
        self.task = Task.objects.create(
            user=self.user,
            name='Test Task',
            unit_name='Test Unit',
            due_date=timezone.now() + timedelta(days=3),
            status='pending'
        )
    
    def test_create_reminder_log(self):
        """Test creating a reminder log"""
        log = ReminderLog.objects.create(
            task=self.task,
            user=self.user,
            message='Test reminder message',
            notification_method='email',
            sent_date=timezone.now().date()
        )
        self.assertEqual(log.message, 'Test reminder message')
        self.assertEqual(log.notification_method, 'email')
    
    def test_reminder_log_ordering(self):
        """Test that reminder logs are ordered by sent time (newest first)"""
        log1 = ReminderLog.objects.create(
            task=self.task,
            user=self.user,
            message='First reminder',
            notification_method='email',
            sent_date=timezone.now().date()
        )
        log2 = ReminderLog.objects.create(
            task=self.task,
            user=self.user,
            message='Second reminder',
            notification_method='email',
            sent_date=timezone.now().date()
        )
        logs = ReminderLog.objects.all()
        self.assertEqual(logs.first().message, 'Second reminder')
        self.assertEqual(logs.last().message, 'First reminder')


class TaskViewsTest(TestCase):
    """Test cases for Task views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            email='student@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()
    
    def test_task_dashboard_requires_login(self):
        """Test that task dashboard requires login"""
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_task_dashboard_authenticated(self):
        """Test task dashboard for authenticated user"""
        self.client.login(email='student@example.com', password='testpass123')
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)
    
    def test_add_task_GET(self):
        """Test getting add task form"""
        self.client.login(email='student@example.com', password='testpass123')
        response = self.client.get('/tasks/add/')
        self.assertEqual(response.status_code, 200)

