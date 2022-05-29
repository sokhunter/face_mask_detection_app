import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from incidents.models import Incident
from django.db.models import Q

class NotificationsConsumer(WebsocketConsumer):
    def connect(self):
        user_id = self.scope['user'].pk
        self.room_group_name = 'noti' + str(user_id)
        #incidents_unchecked = Incident.objects.filter(Q(security_user=user_id) & Q(is_reviewed=False))
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        #self.send(text_data=json.dumps({
        #    'type': 'connection_established',
        #    'message': incidents_unchecked
        #}))

    #def receive(self, text_data):
    #   text_data_json = json.loads(text_data)
    #   message = text_data_json['message']

    #   print('Message: ', message)

    def notification(self, event):
        self.send(text_data=json.dumps({
            'type': 'incident_received',
            'message': event['incident_context']
        }))

    def notification_read(self, event):
        self.send(text_data=json.dumps({
            'type': 'notification_read',
            'message': 'read'
        }))

    #def disconnect(self, close_code):
    #   pass

