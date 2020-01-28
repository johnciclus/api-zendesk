from flask import Flask
from flask_restful import Api
from resources import Message, Messages, Users
import pymongo 

app = Flask(__name__)
api = Api(app)


client = pymongo.MongoClient("mongodb+srv://user:usertest@ciclus-s4xx3.mongodb.net/test?retryWrites=true&w=majority")
test = client.db("zendesk").collection("test")

print(test)

# const client = new MongoClient(uri, { useNewUrlParser: true });
# client.connect(err => {
#   const collection = client.db("test").collection("devices");
#   // perform actions on the collection object
#   client.close();
# });


api.add_resource(Users, '/api/users/')
api.add_resource(Messages, '/api/messages/')
api.add_resource(Message, '/api/messages/<int:id>', endpoint='message_endpoint')

if __name__ == '__main__':
    app.run(debug=True)