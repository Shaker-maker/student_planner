"""
Singleton scheduler instance shared across the app.
"""
_scheduler = None


def set_scheduler(scheduler):
    """Store the scheduler instance when created"""
    global _scheduler
    _scheduler = scheduler


def get_scheduler():
    """Retrieve the scheduler instance"""
    return _scheduler
