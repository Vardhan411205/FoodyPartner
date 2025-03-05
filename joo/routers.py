class DatabaseRouter:
    """
    A router to control database operations between default and items databases.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to default db.
        All other models go to items db.
        """
        if model._meta.app_label == 'joo':
            return 'items'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to default db.
        All other models go to items db.
        """
        if model._meta.app_label == 'joo':
            return 'items'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations between objects in the same database.
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'default' database.
        """
        if app_label == 'joo':
            return db == 'items'
        return db == 'default' 