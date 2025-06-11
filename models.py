from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, full_name, user_type, profile_image=None):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.user_type = user_type  # 'participant' or 'organizer'
        self.profile_image = profile_image