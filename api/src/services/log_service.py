from models.core_models import Log
from db import db
from flask import current_app as app
from datetime import datetime, timedelta

class LogService:
    """
    Service for logging user actions to database.
    """

    @classmethod
    def log_action(cls, user_id: int, action: str):
        """
        Log a user action to the database.

        Args:
            user_id: int - ID of the user performing the action
            action: str - Description of the action performed
        """
        try:
            log_entry = Log(user_id=user_id, action=action)
            db.session.add(log_entry)
            db.session.commit()

            # Also log to console for debugging
            app.logger.info(f"User {user_id} action logged: {action}")
        except Exception as e:
            # If database logging fails, at least log to console
            app.logger.error(f"Failed to log action for user {user_id}: {action} - Error: {e}")

    @classmethod
    def get_user_logs(cls, user_id: int, limit: int = 50):
        """
        Get recent logs for a specific user.

        Args:
            user_id: int - User ID to get logs for
            limit: int - Maximum number of logs to return
        Returns:
            list of Log objects
        """
        return (db.session.query(Log)
                .filter(Log.user_id == user_id)
                .order_by(Log.created_at.desc())
                .limit(limit)
                .all())

    @classmethod
    def get_recent_logs(cls, page: int = 1, per_page: int = 50):
        """
        Get recent logs from all users with pagination.

        Args:
            page: int - Page number (starting from 1)
            per_page: int - Number of logs per page (default 50)
        Returns:
            dict: {
                'logs': list of (Log, username) tuples,
                'total': int - Total number of logs,
                'pages': int - Total number of pages,
                'current_page': int - Current page number
            }
        """
        from models.core_models import User

        # Calculate offset
        offset = (page - 1) * per_page

        # Get total count
        total = db.session.query(Log).count()

        # Calculate total pages
        pages = (total + per_page - 1) // per_page

        # Get paginated results
        logs = (db.session.query(Log, User.username)
                .join(User, Log.user_id == User.id)
                .order_by(Log.created_at.desc())
                .offset(offset)
                .limit(per_page)
                .all())

        return {
            'logs': logs,
            'total': total,
            'pages': pages,
            'current_page': page
        }

    @classmethod
    def get_access_stats(cls):
        """
        Get access statistics for today, this week, this month, and this year.

        Returns:
            dict: {
                'today': int,
                'week': int,
                'month': int,
                'year': int
            }
        """
        return {
            'today': cls._get_today_logs_count(),
            'week': cls._get_week_logs_count(),
            'month': cls._get_month_logs_count(),
            'year': cls._get_year_logs_count()
        }
        
    @classmethod
    def _get_today_logs_count(cls):
        """
        Get the number of logs from today.

        Returns:
            int: Number of logs created today
        """
        today = datetime.now().date()
        return db.session.query(Log).filter(
            db.func.date(Log.created_at) == today
        ).count()

    @classmethod
    def _get_week_logs_count(cls):
        """
        Get the number of logs from this week (Monday to Sunday).

        Returns:
            int: Number of logs created this week
        """
        today = datetime.now().date()
        # Find the Monday of this week
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)

        return db.session.query(Log).filter(
            db.func.date(Log.created_at) >= monday,
            db.func.date(Log.created_at) <= sunday
        ).count()

    @classmethod
    def _get_month_logs_count(cls):
        """
        Get the number of logs from this month.

        Returns:
            int: Number of logs created this month
        """
        now = datetime.now()
        year = now.year
        month = now.month

        return db.session.query(Log).filter(
            db.extract('year', Log.created_at) == year,
            db.extract('month', Log.created_at) == month
        ).count()

    @classmethod
    def _get_year_logs_count(cls):
        """
        Get the number of logs from this year.

        Returns:
            int: Number of logs created this year
        """
        year = datetime.now().year

        return db.session.query(Log).filter(
            db.extract('year', Log.created_at) == year
        ).count()

