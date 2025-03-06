class DatabaseRouter:
    """
    A router to control database operations between default and items databases.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to default db.
        All other models go to items db.
        """
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions', 'admin']:
            return 'default'
        if model._meta.model_name in ['venuepartner', 'restaurantpartner', 'fooditem', 'diningtable', 'deliverypartner', 'otpverification', 'resetpassword']:  # Partner, auth, and related models go to default
            return 'default'
        if model._meta.model_name == 'order' or model._meta.app_label == 'joo':  # Order model and other joo models go to items
            return 'items'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to default db.
        All other models go to items db.
        """
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions', 'admin']:
            return 'default'
        if model._meta.model_name in ['venuepartner', 'restaurantpartner', 'fooditem', 'diningtable', 'deliverypartner', 'otpverification', 'resetpassword']:  # Partner, auth, and related models go to default
            return 'default'
        if model._meta.model_name == 'order' or model._meta.app_label == 'joo':  # Order model and other joo models go to items
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
        if app_label in ['auth', 'contenttypes', 'sessions', 'admin'] or app_label == 'sessions':
            return db == 'default'
        if model_name in ['venuepartner', 'restaurantpartner', 'fooditem', 'diningtable', 'deliverypartner', 'otpverification', 'resetpassword']:  # Partner, auth, and related migrations go to default
            return db == 'default'
        if model_name == 'order' or app_label == 'joo':  # Order migrations and other joo migrations go to items
            return db == 'items'
        return db == 'default' 