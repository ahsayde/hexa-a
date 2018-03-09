import uuid, time, hashlib, json, types
from mongoengine import fields, Document, EmbeddedDocument, DoesNotExist, ValidationError

default_meta = {'allow_inheritance': True, "db_alias": 'hexa-a-db'}

minimal_repr = {
    'User': ['username', 'profile_photo'],
    'Group': ['uid', 'name'],
    'Assignment': ['uid', 'name'],
    'Testsuite': ['uid', 'name', 'level', 'attempts'],
    'Testcase':['uid', 'stdin', 'expected_stdout', 'added_by', 'added_at', 'suggested_at', 'suggested_by'],
    'Notification':['uid', 'entity_type', 'entity', 'from_user', 'to_user']
}

class BaseModel(Document):
    meta = {
        'allow_inheritance': True,
        'abstract': True
    }

    @classmethod
    def get(cls, **kwargs):
        response = None
        try:
            response =  cls.objects.get(**kwargs)
        except DoesNotExist:
            response = None

        return response


    def check(self):
        try:
            self.validate()
        except ValidationError as e:
            return e.to_dict()

    def extract_object(self, obj):
        try:
            data = obj.to_dict()
        except:
            data = json.loads(obj.to_json())

        return {k: data[k] for k in minimal_repr[obj.__class__.__name__] if data.get(k)}

    def extract_list(self, objList):
        data = []
        for item in objList:
            if isinstance(item, (User, Group, Assignment, Announcement, Testsuite, Testcase, SuggestedTestcase)):
                item_data = self.extract_object(item)
                data.append(item_data)
            elif isinstance(item, list):
                item_data = self.extract_list(item)
                data.append(item_data)
            else:
                data.append(item)

        return data

    def to_dict(self):
        output = {}
        obj = self
        for item in obj:
            if item == '_cls':
                continue
            instance = obj[item]
            if isinstance(instance, list):
                output[item] = self.extract_list(instance)
            elif isinstance(instance, (User, Group, Assignment, Announcement, Testsuite, Testcase, SuggestedTestcase)):
                output[item] = self.extract_object(instance)
            else:
                output[item] = instance
        return output

    @classmethod
    def delete(cls, **kwargs):
        return cls.objects(**kwargs).delete()

class User(BaseModel):
    username = fields.StringField(primary_key=True, required=True, min_length=3, max_length=15, regex='^[a-zA-Z0-9_]*$')
    email = fields.EmailField(unique=True, required=True)
    firstname = fields.StringField(min_length=3, max_length=15)
    lastname = fields.StringField(min_length=3, max_length=15)
    created_at = fields.IntField(required=True)
    updated_at = fields.IntField()
    profile_photo = fields.StringField(default='/avatars/c21f969b5f03d33d43e04f8f136e7682')
    # db collection
    meta = {"collection":"users"}

class Credentials(BaseModel):
    username = fields.StringField(unique=True, required=True, min_length=3, max_length=15, regex='^[a-zA-Z0-9_]*$')
    email = fields.EmailField(unique=True, required=True)
    salt = fields.StringField(required=True)
    secret = fields.StringField(required=True)
    created_at = fields.IntField(required=True)
    updated_at = fields.IntField()
    # db collection
    meta = {"collection":"credentials"}

class ResetToken(BaseModel):
    user = fields.ReferenceField(User, required=True)
    email = fields.EmailField(unique=True, required=True)
    salt = fields.StringField(required=True)
    secret = fields.StringField(required=True)
    created_at = fields.IntField(required=True)
    # db collection
    meta = {"collection":"reset_tokens"}

class Group(BaseModel):
    uid = fields.StringField(required=True, primary_key=True)
    name = fields.StringField(required=True, min_length=3, max_length=50)
    description = fields.StringField(required=True, max_length=100)
    created_by = fields.ReferenceField(User, required=True)
    created_at = fields.IntField(required=True)
    updated_at = fields.IntField()
    updated_by = fields.ReferenceField(User)
    # db collection
    meta = {"collection":"groups"}

class GroupMembership(BaseModel):    
    uid = fields.StringField(required=True, primary_key=True)
    group = fields.ReferenceField(Group, required=True, reverse_delete_rule=2)
    user = fields.ReferenceField(User, required=True, reverse_delete_rule=2)
    role = fields.StringField(required=True, choise=['admin', 'member'])
    joined_at = fields.IntField()
    added_by = fields.ReferenceField(User, required=True)
    # db collection
    meta = {"collection":"group_membership"}

class Testcase(EmbeddedDocument):
    uid = fields.StringField(unique=True, required=True)
    stdin = fields.StringField(required=True)
    expected_stdout = fields.StringField(required=True)
    added_by = fields.StringField(required=True)
    added_at = fields.IntField(required=True)
    suggested_by = fields.StringField(default=None)
    suggested_at = fields.IntField(default=None)
    
class Testsuite(BaseModel):
    uid = fields.StringField(required=True, primary_key=True)
    name = fields.StringField(required=True, min_length=3, max_length=50)
    level = fields.StringField(required=True, choice=['basic', 'extended', 'advanced'])
    public = fields.BooleanField(default=False)
    attempts = fields.IntField(default=0)
    group = fields.ReferenceField(Group, required=True, reverse_delete_rule=2)
    testcases = fields.EmbeddedDocumentListField(Testcase, default=[])
    created_at = fields.IntField(required=True)
    created_by = fields.ReferenceField(User, required=True)
    updated_at = fields.IntField()
    updated_by = fields.ReferenceField(User)
    attachment = fields.ListField(fields.StringField())
    # db collection
    meta = {"collection":"testsuite"}

class SuggestedTestcase(BaseModel):
    uid = fields.StringField(required=True, primary_key=True)
    user = fields.ReferenceField(User, required=True, reverse_delete_rule=2)
    group = fields.ReferenceField(Group, required=True, reverse_delete_rule=2)
    testsuite = fields.ReferenceField(Testsuite, required=True, reverse_delete_rule=2)
    suggested_at = fields.IntField()
    stdin = fields.StringField(required=True)
    expected_stdout = fields.StringField(required=True)
    # db collection
    meta = {"collection":"suggested_testcase"}
    
class Assignment(BaseModel):
    uid = fields.StringField(required=True, primary_key=True)
    name = fields.StringField(required=True, min_length=3, max_length=100)
    description = fields.StringField(required=True)
    group = fields.ReferenceField(Group, required=True, reverse_delete_rule=2)
    published = fields.BooleanField(default=False)
    published_at = fields.IntField()
    published_by = fields.ReferenceField(User)
    created_at = fields.IntField(required=True)
    created_by = fields.ReferenceField(User, required=True)
    updated_at = fields.IntField()
    updated_by = fields.ReferenceField(User)
    deadline = fields.IntField()
    testsuites = fields.ListField(fields.ReferenceField(Testsuite), reverse_delete_rule=4)
    settings = fields.DictField(default={})
    # db collection
    meta = {"collection":"assignemnts"}

class Announcement(BaseModel):
    uid = fields.StringField(required=True, primary_key=True)
    content = fields.StringField(required=True, min_length=1, max_length=10000)
    group = fields.ReferenceField(Group, required=True, reverse_delete_rule=2)
    created_at = fields.IntField(required=True)
    created_by = fields.ReferenceField(User, required=True)
    updated_at = fields.IntField()
    # db collection
    meta = {"collection":"announcements"}

class Session(BaseModel):
    key = fields.StringField(required=True, primary_key=True)    
    user_id = fields.StringField(required=True)
    jwt = fields.StringField(required=True)
    created_at = fields.IntField(required=True)
    expires_at = fields.IntField(required=True)
    # db collection
    meta = {"collection":"session"}
    
class Submission(BaseModel):
    uid = fields.StringField(required=True, primary_key=True)
    group = fields.ReferenceField(Group, required=True, reverse_delete_rule=2)
    assignment = fields.ReferenceField(Assignment, required=True, reverse_delete_rule=2)
    testsuite = fields.ReferenceField(Testsuite, required=True, reverse_delete_rule=2)
    username = fields.StringField(required=True)
    submitted_at = fields.IntField(required=True)
    language = fields.StringField(required=True)
    result = fields.DictField(required=True)
    status = fields.StringField(required=True)
    # db collection
    meta = {"collection":"submissions"}

class GroupJoinRequest(BaseModel):
    uid = fields.StringField(required=True, primary_key=True)
    group = fields.ReferenceField(Group, required=True, reverse_delete_rule=2)
    user = fields.ReferenceField(User, required=True, reverse_delete_rule=2)
    created_at = fields.IntField(required=True)
    # db collection
    meta = {"collection":"join_requests"}
