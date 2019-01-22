import psycopg2
from psycopg2.extras import RealDictCursor
from app.helpers.authetication import get_current_role, get_current_identity


class Database:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                dbname="fred",
                user="postgres",
                host="localhost",
                password="incorrect6363",
                port="5432"
            )
            self.connection.autocommit = True
            self.cursor = self.connection.cursor(
                cursor_factory=RealDictCursor
            )
            self.create_tables()
        except psycopg2.OperationalError as e:
            print(e, "Database Connection failed")

    def create_tables(self):
        tables = (
            """
                CREATE TABLE IF NOT EXISTS user_table4(
                    ID SERIAL PRIMARY KEY NOT NULL,
                    firstname VARCHAR(20) NOT NULL,
                    lastname VARCHAR(20) NOT NULL,
                    othernames VARCHAR(20),
                    email VARCHAR(20) NOT NULL,
                    phoneNumber VARCHAR(20) NOT NULL,
                    username VARCHAR(20) NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    registered DATE NOT NULL,
                    isAdmin BOOLEAN
                );
            """,
            """
                CREATE TABLE IF NOT EXISTS incident_table4(
                    ID SERIAL PRIMARY KEY NOT NULL,
                    createdOn DATE NOT NULL,
                    createdBy INTEGER REFERENCES user_table4(ID),
                    _type VARCHAR(20) NOT NULL,
                    location TEXT NOT NULL,
                    status VARCHAR(20),
                    images TEXT[],
                    videos TEXT[],
                    comment TEXT NOT NULL
                );
            """
        )
        for table in tables:
            self.cursor.execute(table)

    def add_incident(self, **kwargs):
        insert = f"""INSERT INTO incident_table4(
            createdOn, createdBy, _type, location, status,
            images, videos, comment) VALUES (
            '{kwargs.get("createdOn")}',
            {kwargs.get("createdBy")},
            '{kwargs.get("_type")}',
            '{kwargs.get("location")}',
            '{kwargs.get("status")}',
            ARRAY[]::text[]{kwargs.get("images")},
            ARRAY[]::text[]{kwargs.get("videos")},
            '{kwargs.get("comment")}');"""
        self.cursor.execute(insert)

    def add_user(self, **kwargs):
        insert = f"""INSERT INTO user_table4(
            firstname, lastname, othernames, email, phoneNumber, username,
            password, registered, isAdmin) VALUES (
            '{kwargs.get("firstname")}',
            '{kwargs.get("lastname")}',
            '{kwargs.get("othernames")}',
            '{kwargs.get("email")}',
            '{kwargs.get("phoneNumber")}',
            '{kwargs.get("username")}',
            '{kwargs.get("password")}',
            '{kwargs.get("registered")}',
            '{kwargs.get("isAdmin")}');"""
        self.cursor.execute(insert)

    def get_incidents(self, _type):
        query = f"""SELECT * FROM incident_table4 WHERE _type='{_type}'"""

        if not get_current_role():
            query = f"""SELECT * FROM incident_table4 WHERE createdBy={
                get_current_identity()} AND _type='{_type}'"""
        self.cursor.execute(query)
        incidents = self.cursor.fetchall()
        print("Current id", get_current_identity())
        print("Incidents", incidents)
        return incidents

    def get_all_users(self):
        query = "SELECT * FROM user_table4;"
        self.cursor.execute(query)
        users = self.cursor.fetchall()
        return users

    def is_red_flag_editable(self, red_flag_id):
        red_flag_of_id = self.get_red_flag_of_id(red_flag_id)
        if red_flag_of_id[0]["status"] == "draft":
            return red_flag_of_id

    def get_red_flag_of_id(self, red_flag_id):
        query = f"""SELECT * FROM incident_table4 WHERE id={red_flag_id}"""

        if not get_current_role():
            query = f"""SELECT * FROM incident_table4 WHERE id={red_flag_id}
            AND createdBy={get_current_identity()}"""

        self.cursor.execute(query)
        red_flag_of_id = self.cursor.fetchall()
        return red_flag_of_id

    def admin_update_status(self, incident_id, attribute, value):
        query = f"""UPDATE incident_table4 SET {
            attribute}='{value}' WHERE id={incident_id}"""
        self.cursor.execute(query)

    def update_user_incident(self, incident_id, attribute, value):
        query = f"""UPDATE incident_table4 SET {
            attribute}='{value}' WHERE id={incident_id}
            AND createdBy={get_current_identity()}"""
        self.cursor.execute(query)

    def delete_user_incident(self, incident_id):
        query = f"""DELETE FROM incident_table4 WHERE id={incident_id}
        AND createdBy={get_current_identity()}"""
        self.cursor.execute(query)

    def red_flag_exists(self, comment, location):
        query = f"""SELECT * FROM incident_table4 WHERE comment='{comment}'
        AND location='{location}' AND createdBy={get_current_identity()}"""
        self.cursor.execute(query)
        redflag = self.cursor.fetchall()
        return redflag

    def username_or_email_exists(self, username, email):
        query = f"""SELECT * FROM user_table4 WHERE username='{username}'
        OR email='{email}'"""
        self.cursor.execute(query)
        exists = self.cursor.fetchall()
        return exists

    def username_exists(self, username):
        query = f"""SELECT * FROM user_table4 WHERE username='{username}'"""
        self.cursor.execute(query)
        user = self.cursor.fetchall()
        return user

    def drop_tables(self):
        queries = (
            "DROP TABLE incident_table4;",
            "DROP TABLE user_table4;"
        )
        for query in queries:
            self.cursor.execute(query)
        return "Table dropped"
