class UserLogin:
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user['id'])

    def get_email(self):
        return str(self.__user['email'])

    def get_nameorg(self):
        return str(self.__user['nameorg'])

    def get_address(self):
        return str(self.__user['address'])

    def get_email_org(self):
        return str(self.__user['emailorg'])

    def get_phone(self):
        return str(self.__user['tel'])

    def get_website(self):
        return str(self.__user['website'])