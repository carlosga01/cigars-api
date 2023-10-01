from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import psycopg2
from psycopg2 import Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
api = Api(app)


def connect_to_db():
    try:
        conn = psycopg2.connect(database="cigarsdb",
                                user="cigarsdb_user",
                                password="40kMy0v70HP5Lc1PyipY8MBSJcvNi2t7",
                                host="dpg-ck4dmqt8ggls73eb2grg-a.oregon-postgres.render.com", port="5432")
        return conn
    except Error as e:
        print(f"Error: (e)")
        return None


class SignIn(Resource):
    def post(self):
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'message': 'Both email and password are required'}, 400

        connection = connect_to_db()

        if connection:
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM accounts WHERE LOWER(email) = LOWER(%s)", (email,))
            user = cursor.fetchone()

            if user:
                # User exists, check the password
                hashed_password = user[5]
                if check_password_hash(hashed_password, password):
                    cursor.close()
                    connection.close()
                    return {'message': 'Login successful'}, 200
                else:
                    cursor.close()
                    connection.close()
                    return {'message': 'The email or password entered are incorrect'}, 401
            else:
                # User does not exist, return error
                cursor.close()
                connection.close()
                return {'message': 'The email or password entered are incorrect'}, 401

        else:
            return {'message': 'Failed to connect to the database'}, 500


class SignUp(Resource):
    def post(self):
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'message': 'Both email and password are required'}, 400

        connection = connect_to_db()

        if connection:
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM accounts WHERE LOWER(email) = LOWER(%s)", (email,))
            user = cursor.fetchone()

            if user:
                # User exists, return error
                return {'message': 'Email already exists. Please use a different email.'}, 400
            else:
                # User does not exist, create a new user
                hashed_password = generate_password_hash(password)
                try:
                    cursor.execute(
                        "INSERT INTO accounts (id, email, password, created_at, updated_at) VALUES (gen_random_uuid(), %s, %s, current_timestamp, current_timestamp);",
                        (email, hashed_password))
                    connection.commit()
                    cursor.close()
                    connection.close()
                    return {'message': 'User created successfully'}, 201
                except Error as e:
                    cursor.close()
                    connection.close()
                    return {'message': 'Error signing up'}, 500

        else:
            return {'message': 'Failed to connect to the database'}, 500


class SearchCigars(Resource):
    def get(self):
        search_query = request.args.get('query')

        connection = connect_to_db()

        if connection:
            cursor = connection.cursor()
            query = "SELECT * FROM cigars WHERE name ILIKE %s OR manufacturer ILIKE %s"
            cursor.execute(query, ('%' + search_query + '%', '%' + search_query + '%',), )

            results = cursor.fetchall()

            cursor.close()
            connection.close()

            response = [{
                "id": row[0],
                "name": row[1],
                "manufacturer": row[2],
                "country": row[3]

            } for row in results]

            return response, 200

        else:
            return {'message': 'Failed to connect to the database'}, 500


api.add_resource(SignIn, '/sign-in')
api.add_resource(SignUp, '/sign-up')
api.add_resource(SearchCigars, '/cigars/search')

if __name__ == '__main__':
    app.run(debug=True)
