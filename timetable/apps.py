from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class TimetableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'timetable'
    
    def ready(self):
        """Register class reminder scheduler with APScheduler"""
        try:
            from .schedulers import register_class_schedulers
            from study_planner.scheduler_instance import get_scheduler
            
            # Wait for scheduler to be available (created by tasks app)
            scheduler = get_scheduler()
            if scheduler is not None:
                register_class_schedulers(scheduler)
                logger.info("✅ Class reminder jobs registered")
            else:
                logger.warning("Scheduler not yet available - will retry later")
        except Exception as e:
            logger.error(f"❌ Error registering class reminder scheduler: {str(e)}")
