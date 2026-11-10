from django.apps import AppConfig


class PileTrackerConfig(AppConfig):
    # Match the id type the existing tables were created with.
    default_auto_field = "django.db.models.AutoField"
    name = "pile_tracker"

    def ready(self):
        print("I'm ready")
