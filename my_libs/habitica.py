
import json

import requests

API_URI_BASE = 'api/v3'
API_CONTENT_TYPE = 'application/json'


class habitica:
    """
    A minimalist Habitica API class.
    """

    def __init__(self, auth=None, resource=None, aspect=None):
        self.auth = auth
        self.resource = resource
        self.aspect = aspect
        self.headers = auth if auth else {}
        self.headers.update({'content-type': API_CONTENT_TYPE})

    def __getattr__(self, m):
        try:
            return object.__getattr__(self, m)
        except AttributeError:
            if not self.resource:
                return Habitica(auth=self.auth, resource=m)
            else:
                return Habitica(auth=self.auth, resource=self.resource,
                                aspect=m)
    
    def __call__(self, **kwargs):
        method = kwargs.pop('_method', 'get')

        # build up URL... Habitica's api is the *teeniest* bit annoying
        # so either i need to find a cleaner way here, or i should
        # get involved in the API itself and... help it.
        if self.aspect:
            aspect_id = kwargs.pop('_id', None)
            direction = kwargs.pop('_direction', None)
            uri = '%s/%s' % (self.auth['url'],
                             API_URI_BASE)
            if aspect_id is not None:
                uri = '%s/%s/%s' % (uri,
                                    self.aspect,
                                    str(aspect_id))
            elif self.aspect == 'tasks':
                uri = '%s/%s/%s' % (uri,
                                    self.aspect,
                                    self.resource)
            else:
                uri = '%s/%s/%s' % (uri,
                                    self.resource,
                                    self.aspect)
            if direction is not None:
                uri = '%s/score/%s' % (uri, direction)
        else:
            uri = '%s/%s/%s' % (self.auth['url'],
                                API_URI_BASE,
                                self.resource)
        return self.request_call(uri,method,kwargs)
        
            
    def request_call(self,uri, method =None, kwargs=None):
        # actually make the request of the API
        if method in ['put', 'post', 'delete']:
            res = getattr(requests, method)(uri, headers=self.headers,
                                            data=json.dumps(kwargs))
        else:
            res = getattr(requests, method)(uri, headers=self.headers,
                                            params=kwargs)

        # print(res.url)  # debug...
        if res.status_code == requests.codes.ok:
            return res.json()["data"]
        else:
            res.raise_for_status()
            

class habiticaImp(habitica):
    
    def __init__(self):
        rv = {'url': "https://habitica.com",
              'checklists':"false",
              'x-api-user': "1da76d7e-9002-4cdf-9322-81806481ea95",
              'x-api-key': "eb667fc1-8f44-4b44-ada4-c122945ac916"
        }
        super().__init__(rv)

    @property
    def all_my_tag(self):
        self.resource = "tags"
        self.my_tags = self.__call__()
        return self.my_tags
    
    def create_a_tag(self,name):
        return self.__call__(_method="post",name=name)
    
    def delete_a_tag(self,uuid):
        return getattr(self,uuid)(_method="delete")
        super().__init__(rv,"tags",uuid)
        
    @property
    def my_group(self):
        self.resource = "groups"
        self.my_groups = self.__call__(type="party")
        return self.my_groups
    
    def my_active_group_id(self, activeName = "Super Active Daily Quests"):
        _id = list(filter(lambda x: x["name"]==activeName, self.my_group))[0]
        return _id["_id"]
    
    def get_a_group(self,groupId):
        return getattr(self,groupId)()
    
    def accept_quest(self):
        groupId = self.my_active_group_id()
        url = f"https://habitica.com/api/v3/groups/{groupId}/quests/accept"
        self.request_call(method="post",uri=url)
        
    def create_a_todo(self,text):
        self.resource  = "user"
        self.tasks(
        _method = "post",
        type = "todo",
        text=text
        )
        
        