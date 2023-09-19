from flask import Flask
from flask_restful import Resource, Api
import psycopg2

app = Flask(__name__)
api = Api(app)

conn = psycopg2.connect(database="cigarsdb",
                            user="cigarsdb_user",
                            password="40kMy0v70HP5Lc1PyipY8MBSJcvNi2t7",
                            host="dpg-ck4dmqt8ggls73eb2grg-a.oregon-postgres.render.com", port="5432")

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)