from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    
    def ready(self):
        """Initialize APScheduler when Django starts"""
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from .schedulers import register_schedulers
            from study_planner.scheduler_instance import set_scheduler, get_scheduler
            
            # Only start scheduler once
            if get_scheduler() is None:
                scheduler = BackgroundScheduler()
                set_scheduler(scheduler)
                register_schedulers(scheduler)
                scheduler.start()
                logger.info("✅ APScheduler started successfully!")
        except Exception as e:
            logger.error(f"❌ Error starting scheduler: {str(e)}")
