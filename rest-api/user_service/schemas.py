from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    login = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    first_name = fields.Str(validate=validate.Length(max=50))
    last_name = fields.Str(validate=validate.Length(max=50))
    phone = fields.Str(validate=validate.Length(max=20))
    date_of_birth = fields.Date()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class UserRegisterSchema(UserSchema):
    password = fields.Str(required=True, validate=validate.Length(min=6))

class UserUpdateSchema(Schema):
    email = fields.Email()
    first_name = fields.Str(validate=validate.Length(max=50))
    last_name = fields.Str(validate=validate.Length(max=50))
    phone = fields.Str(validate=validate.Length(max=20))
    date_of_birth = fields.Date()
