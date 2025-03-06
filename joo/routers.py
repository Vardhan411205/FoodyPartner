class DatabaseRouter:
    """
    A router to control database operations between default and items databases.
    """
    def db_for_read(self, model, **hints):
        """
        Route read operations to appropriate database
        """
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions', 'admin']:
            return 'default'
        if model._meta.model_name in ['venuepartner', 'restaurantpartner', 'fooditem', 'diningtable', 'deliverypartner', 'otpverification', 'resetpassword']:
            return 'default'
        if model._meta.model_name == 'order':
            return 'items'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Route write operations to appropriate database
        """
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions', 'admin']:
            return 'default'
        if model._meta.model_name in ['venuepartner', 'restaurantpartner', 'fooditem', 'diningtable', 'deliverypartner', 'otpverification', 'resetpassword']:
            return 'default'
        if model._meta.model_name == 'order':
            return 'items'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations between objects in the same database
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Control which migrations go to which database
        """
        if app_label in ['auth', 'contenttypes', 'sessions', 'admin']:
            return db == 'default'
        if model_name in ['venuepartner', 'restaurantpartner', 'fooditem', 'diningtable', 'deliverypartner', 'otpverification', 'resetpassword']:
            return db == 'default'
        if model_name == 'order':
            return db == 'items'
        return db == 'default' 