from flask_restful import abort, Api, marshal_with, reqparse, Resource
from models import MessageModel, message_fields
from controllers import MessageManager
from datetime import datetime
from pytz import utc
import status
import requests

message_manager = MessageManager()

class Message(Resource):
    def abort_if_message_doesnt_exist(self, id):
        if id not in message_manager.messages:
            abort(
                status.HTTP_404_NOT_FOUND,
                message="Message {0} doesn't exist".format(id))
    
    @marshal_with(message_fields)
    def get(self, id):
        self.abort_if_message_doesnt_exist(id)
        return message_manager.get_message(id)

    def delete(self, id):
        self.abort_if_message_doesnt_exist(id)
        message_manager.delete_message(id)
        return '', status.HTTP_204_NO_CONTENT

    @marshal_with(message_fields)
    def patch(self, id):
        self.abort_if_message_doesnt_exist(id)
        message = message_manager.get_message(id)
        parser = reqparse.RequestParser()
        
        parser.add_argument('message', type=str)
        parser.add_argument('duration', type=int)
        parser.add_argument('printed_times', type=int)
        parser.add_argument('printed_once', type=bool)

        args = parser.parse_args()
        if 'message' in args and args['message']:
            message.message = args['message']
        if 'duration' in args and args['duration']:
            message.duration = args['duration']
        if 'printed_times' in args and args['printed_times']:
            message.printed_times = args['printed_times']
        if 'printed_once' in args and args['printed_once']:
            message.printed_once = args['printed_once']
        return message


class Messages(Resource):
    @marshal_with(message_fields)
    def get(self):
        return [v for v in message_manager.messages.values()]
    
    @marshal_with(message_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('message', type=str, required=True, help='Message cannot be blank!')
        parser.add_argument('duration', type=int, required=True, help='Duration cannot be blank!')
        parser.add_argument('message_category', type=str, required=True, help='Message category cannot be blank!')
        args = parser.parse_args()

        message = MessageModel(
            message=args['message'],
            duration=args['duration'],    
            creation_date=datetime.now(utc),
            message_category=args['message_category'])
        
        message_manager.insert_message(message)
        
        return message, status.HTTP_201_CREATED
    
class Users(Resource):
    def get(self):
        
        users = self.request_users()
                
        return self.format_users(users)

    def request_users(self):
        url = 'https://ciclus.zendesk.com/api/v2/users'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic =='
        }
                
        response = requests.request("GET", url, headers=headers)

        data ={}
        try:
            data = response.json()
        except Exception as err:
            print(err)
            print(response.text.encode('utf8'))
                
        return data['users']
    
    def format_users(self, users):
        users_list = []
        for user in users:
            first_separator = user['name'].find(' ')
            
            users_list.append({
                "first_name": user['name'][:first_separator],
                "last_name": user['name'][first_separator+1:],
                "email": user['email'],
                "integration_id": user['id'],
                "created_at": user['created_at']
            })
        
        return users_list
    
