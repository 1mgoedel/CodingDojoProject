from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import event
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class User:
    DB = 'isport_erd'
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.birthdate = data['birthdate']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.events = []

    @classmethod
    def get_all_user_info(cls, id):
        query = f"SELECT * FROM users WHERE id = {id}"
        return connectToMySQL(cls.DB).query_db(query)
    
    @classmethod
    def get_user_info_and_event_count(cls, id):
        query = f"""SELECT users.*, COUNT(atendees.event_id) AS event_count
                FROM users
                LEFT JOIN atendees ON users.id = atendees.user_id
                WHERE users.id = {id};
                """
        return connectToMySQL(cls.DB).query_db(query)

    @classmethod
    def get_name_from_id(cls, id):
        query = f"SELECT first_name FROM users WHERE id = {id}"
        return connectToMySQL(cls.DB).query_db(query)[0]['first_name']

    @classmethod
    def get_last_name_from_id(cls, id):
        query = f"SELECT last_name FROM users WHERE id = {id}"
        return connectToMySQL(cls.DB).query_db(query)[0]['last_name']
    
    @classmethod
    def get_id_from_email(cls, user_email):
        email = {'email': user_email}
        query = "SELECT id FROM users WHERE email = %(email)s;"
        result = connectToMySQL(cls.DB).query_db(query, email)
        return result[0]['id']

    @classmethod
    def save(cls, data):
        query = """INSERT INTO users(first_name, last_name, email, password, birthdate, created_at, updated_at)
                VALUES(%(first_name)s, %(last_name)s, %(email)s, %(password)s, %(birthdate)s, NOW(), NOW());"""
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result
    
    @classmethod
    def get_user_first_name(cls, id):                                   # Might not use
        user_id = {'id': id}
        query = "SELECT first_name FROM users WHERE id = %(id)s;"
        result = connectToMySQL(cls.DB).query_db(query, user_id)
        return result

    @classmethod
    def check_email(cls, email):
        email = {'email': email}
        query = 'SELECT * FROM users WHERE email = %(email)s'
        result = connectToMySQL(cls.DB).query_db(query, email)
        return result
    
    @classmethod
    def get_password_hash(cls, email):                                  # Might not use
        email = {'email': email}
        query = "SELECT password FROM users WHERE email = %(email)s;"
        result = connectToMySQL(cls.DB).query_db(query, email)
        return result[0]['password']

    @staticmethod
    def validate_reg(user):
        is_valid = True
        if not EMAIL_REGEX.match(user['email']):
            flash("Invalad email address!")
            is_valid = False
        if len(user['first_name']) < 2:
            flash("First name must be at least 2 characters")
            is_valid = False
        if len(user['last_name']) < 2:
            flash("Last name must be at least 2 characters")
            is_valid = False
        if len(user['password']) < 8:
            flash("Password must be at least 8 characters")
            is_valid = False
        if user['password'] != user['confirm_password']:
            flash("Password must match")
            is_valid = False
        if not user['birthdate']:
            flash("Enter your birthdate")
            is_valid = False
        if User.check_email(user['email']):
            flash("User already has an account with this email")
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_log(user):
        is_valid = True
        if not EMAIL_REGEX.match(user['email']):
            flash("Invalad email address!")
            is_valid = False
        if not User.check_email(user['email']):
            flash(f"No user with email {user['email']} found")
            is_valid = False
        return is_valid