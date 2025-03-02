from flask import Flask, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from models import db, User
from schemas import UserSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/users'
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
user_schema = UserSchema()

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(login=data['login']).first():
        return {'message': 'Login already exists'}, 400
    if User.query.filter_by(email=data['email']).first():
        return {'message': 'Email already exists'}, 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        login=data['login'],
        password=hashed_password,
        email=data['email'],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(new_user)
    db.session.commit()
    return user_schema.dump(new_user), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(login=data['login']).first()
    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return {'message': 'Invalid credentials'}, 401
    
    access_token = create_access_token(identity=str(user.id))
    return {'access_token': access_token}, 200

@app.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user = get_jwt_identity()
    
    if int(current_user) != int(user_id):
        return {'message': 'Unauthorized', "current_user": current_user, "user": user_id}, 403
    
    user = User.query.get(int(user_id))
    return user_schema.dump(user), 200

@app.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user = get_jwt_identity()
    
    if int(current_user) != int(user_id):
        return {'message': 'Unauthorized', "current_user": current_user, "user": user_id}, 403
    
    user = User.query.get(int(user_id))
    data = request.json

    # Update allowed fields
    for field in ['first_name', 'last_name', 'email', 'phone', 'date_of_birth']:
        if field in data:
            setattr(user, field, data[field])
    user.updated_at = datetime.utcnow()
    db.session.commit()
    return user_schema.dump(user), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)