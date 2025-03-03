class UserRouter:
    """Router to control database operations"""
    
    def db_for_read(self, model, **hints):
        """Send reads to appropriate database"""
        if model._meta.app_label == 'joo':
            # List of models that should use default database
            default_models = [
                'otpverification',
                'deliverypartner',
                'restaurantpartner',
                'venuepartner',
                'fooditem',           # Added for food items
                'diningtable',        # Added for dining tables
                'resetpassword'       # Added for password reset
            ]
            if model._meta.model_name in default_models:
                return 'default'
            return 'user'
        return None

    def db_for_write(self, model, **hints):
        """Send writes to appropriate database"""
        if model._meta.app_label == 'joo':
            # List of models that should use default database
            default_models = [
                'otpverification',
                'deliverypartner',
                'restaurantpartner',
                'venuepartner',
                'fooditem',           # Added for food items
                'diningtable',        # Added for dining tables
                'resetpassword'       # Added for password reset
            ]
            if model._meta.model_name in default_models:
                return 'default'
            return 'user'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow all relations"""
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Control migrations"""
        if app_label == 'joo':
            # List of models that should use default database
            default_models = [
                'otpverification',
                'deliverypartner',
                'restaurantpartner',
                'venuepartner',
                'fooditem',           # Added for food items
                'diningtable',        # Added for dining tables
                'resetpassword'       # Added for password reset
            ]
            if model_name in default_models:
                return db == 'default'
            return db == 'user'
        return None 