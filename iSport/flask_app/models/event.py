from flask_app.config.mysqlconnection import connectToMySQL
# from flask_app.models import user
from flask import flash
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class Event:
    DB = 'isport_erd'
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.location = data['location']
        self.type = data['type']
        self.date = data['date']
        self.min_num_of_players = data['min_num_of_players']
        self.max_num_of_players = data['max_num_of_players']
        self.time = data['time']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.attendees = []
        self.creator = None

    @classmethod
    def save(cls, data):
        query = """INSERT INTO events(name, location, type, date, min_num_of_players, max_num_of_players, time, created_at, updated_at, user_id)
                VALUES(%(name)s, %(location)s, %(type)s, %(date)s, %(min_num_of_players)s, %(max_num_of_players)s, %(time)s, NOW(), NOW(), %(user_id)s);"""
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result
    
    @classmethod
    def delete_event_id(cls, id):
        query1 = f"DELETE FROM atendees WHERE event_id = {id};"
        print(connectToMySQL(cls.DB).query_db(query1))
        query2 = f"DELETE FROM messages WHERE event_id = {id};"
        connectToMySQL(cls.DB).query_db(query2)
        query3 = f"DELETE FROM events WHERE id = {id};"
        connectToMySQL(cls.DB).query_db(query3)
        return
    
    @classmethod
    def update_event(cls, data, id):
        event_data = {
            "name": data['name'],
            "location": data['location'],
            "type": data['sport'],
            "date": data['date'],
            "min_num_of_players": data['min_num_of_players'],                        
            "max_num_of_players": data['max_num_of_players'],
            "time": data['time'],
            "id": id}
        query = """UPDATE events
                    SET name = %(name)s, location = %(location)s, type = %(type)s, date = %(date)s, min_num_of_players = %(min_num_of_players)s, max_num_of_players = %(max_num_of_players)s, time = %(time)s, updated_at = NOW()
                    WHERE id = %(id)s;
                    """
        return connectToMySQL(cls.DB).query_db(query, event_data)
    
    @classmethod
    def add_attendee(cls, user_id, event_id):
        query = f"INSERT INTO atendees(event_id, user_id) VALUES({event_id}, {user_id});"
        return connectToMySQL(cls.DB).query_db(query)

    @classmethod
    def count_attendees(cls, event_id):
        query = f"""SELECT event_id, COUNT(DISTINCT user_id) AS attendee_count
                    FROM atendees
                    WHERE event_id = {event_id};"""
        return connectToMySQL(cls.DB).query_db(query)

    @classmethod
    def get_all_events(cls):
        query = "SELECT * FROM events;"
        return connectToMySQL(cls.DB).query_db(query)
    
    @classmethod
    def get_an_event(cls, id):
        query = f"SELECT * FROM events WHERE events.id = {id}"
        return connectToMySQL(cls.DB).query_db(query)

    @classmethod
    def edit(cls, data):
        query = """UPDATE events 
                SET name = %(name)s, location = %(location)s, type = %(type)s, date = %(date)s, min_num_of_players = %(min_num_of_players)s, max_num_of_players = %(max_num_of_players)s, time = %(time)s
                WHERE id = %(id)s;""" 
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result
    
    @classmethod
    def search_by_type(cls, type):
        query = f"""SELECT events.id, events.name, events.location, events.date, COUNT(atendees.user_id) AS attendee_count, events.time, events.max_num_of_players
                    FROM events
                    LEFT JOIN atendees ON events.id = atendees.event_id
                    WHERE events.type = '{type}'
                    GROUP BY events.id, events.name, events.location, events.date, events.time, events.max_num_of_players
                    ORDER BY events.date;
                """
        result = connectToMySQL(cls.DB).query_db(query)
        return result

    @classmethod
    def delete_event(cls, id):
        query = f"DELETE FROM events WHERE id = {id};"
        result = connectToMySQL(cls.DB).query_db(query)
        return result

    @classmethod
    def get_all_events_with_attendees(cls):
        query = """SELECT events.id, events.name, events.location, events.date, COUNT(atendees.user_id) AS attendee_count, events.time, events.max_num_of_players
                    FROM events
                    LEFT JOIN atendees ON events.id = atendees.event_id
                    GROUP BY events.id, events.name, events.location, events.date, events.time, events.max_num_of_players
                    ORDER BY events.date;"""
        return connectToMySQL(cls.DB).query_db(query)
    
    @classmethod
    def get_all_events_for_user(cls, id):
        query = f"""SELECT events.type, events.id, events.name, events.location, events.date, events.time, events.max_num_of_players
                FROM events
                INNER JOIN atendees ON events.id = atendees.event_id
                WHERE atendees.user_id = {id}
                ORDER BY events.date;
                """
        return connectToMySQL(cls.DB).query_db(query)

    @classmethod
    def get_events_counts(cls, id):
        query = f"""SELECT events.id, events.name, events.location, events.date, COUNT(atendees.user_id) AS attendee_count
            FROM events
            LEFT JOIN atendees ON events.id = atendees.event_id
            WHERE events.id = {id}
            GROUP BY events.id, events.name, events.location, events.date
            ORDER BY events.date
                """
        return connectToMySQL(cls.DB).query_db(query)[0]

    @classmethod
    def leave_message(cls, user_id, event_id, str):
        data = {
            "user_id" : user_id,
            "event_id" : event_id,
            "message" : str
        }
        query = """INSERT INTO messages (user_id, event_id, message)
                    VALUES (%(user_id)s, %(event_id)s, %(message)s);
                """
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def get_messages_for_event(cls, event_id):
        query = f"""SELECT messages.*, users.first_name AS name
                    FROM messages
                    JOIN users ON messages.user_id = users.id
                    WHERE event_id = {event_id}
                    ORDER BY id;"""
        return connectToMySQL(cls.DB).query_db(query)

    @classmethod
    def get_all_events_with_creator_for_type(cls, type):
        from flask_app.models.user import User
        query = f"""SELECT * FROM events
                JOIN users ON events.user_id = users.id
                WHERE events.type = '{type}'
                ORDER BY events.date;"""
        results = connectToMySQL(cls.DB).query_db(query)
        all_events = []
        for row in results:
            one_event = cls(row)
            one_events_author_info = {
                "id": row['users.id'],
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email": row['email'],
                "password": row['password'],
                "birthdate": row['birthdate'],
                "created_at": row['users.created_at'],
                "updated_at": row['users.updated_at']
            }

            author = User(one_events_author_info)
            one_event.creator = author
            all_events.append(one_event)
        for event in all_events:
            print()
            print(event.creator.first_name)
            print()
        return all_events

    @classmethod
    def get_all_events_with_creator(cls):
        from flask_app.models.user import User
        query = """SELECT * FROM events
                JOIN users ON events.user_id = users.id
                ORDER BY events.date;"""
        results = connectToMySQL(cls.DB).query_db(query)
        all_events = []
        for row in results:
            one_event = cls(row)
            one_events_author_info = {
                "id": row['users.id'],
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email": row['email'],
                "password": row['password'],
                "birthdate": row['birthdate'],
                "created_at": row['users.created_at'],
                "updated_at": row['users.updated_at']
            }

            author = User(one_events_author_info)
            one_event.creator = author
            all_events.append(one_event)
        for event in all_events:
            print('|')
            print(event.creator.first_name)
            print('|')
        return all_events
    
    @classmethod
    def get_attendees_events_with_creator(cls, id):
        from flask_app.models.user import User
        query = f"""SELECT *
                    FROM events
                    JOIN atendees ON events.id = atendees.event_id
                    JOIN users ON atendees.user_id = users.id
                    WHERE atendees.user_id = {id}
                    ORDER BY events.date;"""
        results = connectToMySQL(cls.DB).query_db(query)
        all_events = []
        for row in results:
            one_event = cls(row)
            one_events_author_info = {
                "id": row['user_id'],
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email": row['email'],
                "password": row['password'],
                "birthdate": row['birthdate'],
                "created_at": row['users.created_at'],
                "updated_at": row['users.updated_at']
            }

            author = User(one_events_author_info)
            one_event.creator = author
            all_events.append(one_event)
        for event in all_events:
            print('|')
            print(event.creator.first_name)
            print('|')
        return all_events

    @classmethod
    def get_an_event_with_creator(cls, id):
        from flask_app.models.user import User
        query = f"""SELECT * FROM events
                JOIN users ON events.user_id = users.id
                WHERE events.id = {id};"""
        results = connectToMySQL(cls.DB).query_db(query)
        all_events = []
        for row in results:
            one_event = cls(row)
            one_events_author_info = {
                "id": row['users.id'],
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email": row['email'],
                "password": row['password'],
                "birthdate": row['birthdate'],
                "created_at": row['users.created_at'],
                "updated_at": row['users.updated_at']
            }

            author = User(one_events_author_info)
            one_event.creator = author
            all_events.append(one_event)
        for i in all_events:
            print()
            print(i.creator.first_name)
            print()
        return all_events[0]
    
    @staticmethod
    def validate_event(event):
        is_valid = True
        if len(event['location']) < 2:
            flash("Location must be more than 1 character")
            is_valid = False
        elif not event['location']:
            flash("Location is required")
            is_valid = False
        if len(event['date']) < 2:
            flash("Enter the date of the event")
            is_valid = False
        if int(event['min_num_of_players']) < 2:
            print(f"\nevent.min_num_of_players: {event['min_num_of_players']}\n")
            flash("Must have a minimum of 2 players")
            is_valid = False
        elif not event['min_num_of_players']:
            flash("Must have a minimum of 2 players")
            is_valid = False
        if int(event['max_num_of_players']) < 2:
            flash("Must have at least 2 players for max")
            is_valid = False
        elif not event['max_num_of_players']:
            flash("Must have at least 2 players for max")
            is_valid = False
        if len(event['time']) < 3:
            flash("Please enter the time of the event")
            is_valid = False
        elif not event['time']:
            flash("Please enter the time of the event")
            is_valid = False
        return is_valid