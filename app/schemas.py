from marshmallow import Schema, fields, post_load, EXCLUDE, pre_load


class GroupsSchema(Schema):
    id = fields.Int(data_key='groupOid')
    label = fields.String(data_key='number')

    # faculty = fields.String()

    @post_load()
    def post_load(self, data, **kwargs):
        data['label'] = data['label'].strip()
        return data

    class Meta:
        unknown = EXCLUDE


class GroupsListSchema(Schema):
    pairs = fields.List(fields.Nested(GroupsSchema()))

    @pre_load()
    def pre_load(self, data, **kwargs):
        return {'pairs': data}

    @post_load()
    def post_load(self, data, **kwargs):
        return [i for i in data['pairs'] if i['label'][0] != '*']


class LecturersSchema(Schema):
    id = fields.Int(data_key='lecturerOid')
    label = fields.String(data_key='fio')

    # faculty = fields.String(data_key='chair')

    @post_load()
    def post_load(self, data, **kwargs):
        data['label'] = data['label'].strip()
        return data

    class Meta:
        unknown = EXCLUDE


class LecturersListSchema(Schema):
    lecturers = fields.List(fields.Nested(LecturersSchema()))

    @pre_load()
    def pre_load(self, data, **kwargs):
        return {'lecturers': data}

    @post_load()
    def post_load(self, data, **kwargs):
        return [i for i in data['lecturers'] if i['label'][0] != '!']
