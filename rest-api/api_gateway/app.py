from flask import Flask, jsonify, request, g
from functools import wraps
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    get_jwt_identity,
)
import grpc
from google.protobuf.json_format import MessageToDict
from proto import post_pb2
from proto import post_pb2_grpc
from proto import promo_pb2
from proto import promo_pb2_grpc
import requests

app = Flask(__name__)
JWT_SECRET = 'super-secret'
app.config["JWT_SECRET_KEY"] = JWT_SECRET
USER_SERVICE_URL = "http://user-service:5001"
POST_SERVICE = "post-service:50051"
PROMO_SERVICE = "promo-service:50052"
jwt = JWTManager(app)


post_channel = grpc.insecure_channel(POST_SERVICE)
post_stub = post_pb2_grpc.PostServiceStub(post_channel)

promo_channel = grpc.insecure_channel(PROMO_SERVICE)
promo_stub = promo_pb2_grpc.PromoServiceStub(promo_channel)

def handle_grpc_error(e):
    status_code = grpc.StatusCode.INTERNAL
    if isinstance(e, grpc.RpcError):
        status_code = e.code()
    
    error_map = {
        grpc.StatusCode.INVALID_ARGUMENT: (400, "Bad Request"),
        grpc.StatusCode.NOT_FOUND: (404, "Not Found"),
        grpc.StatusCode.PERMISSION_DENIED: (403, "Forbidden"),
        grpc.StatusCode.UNAUTHENTICATED: (401, "Unauthorized"),
        grpc.StatusCode.ALREADY_EXISTS: (409, "Conflict"),
    }
    
    http_code, message = error_map.get(status_code, (500, "Internal Server Error"))
    return jsonify({"error": message, "details": str(e)}), http_code

@app.route('/register', methods=['POST'])
def register():
    response = requests.post(f"{USER_SERVICE_URL}/register", json=request.json)
    return jsonify(response.json()), response.status_code

@app.route('/login', methods=['POST'])
def login():
    response = requests.post(f"{USER_SERVICE_URL}/login", json=request.json)
    return jsonify(response.json()), response.status_code

@app.route('/users/<user_id>', methods=['GET', 'PUT'])
def user_profile(user_id):
    if request.method == 'GET':
        response = requests.get(
            f"{USER_SERVICE_URL}/users/{user_id}",
            headers=request.headers
        )
    elif request.method == 'PUT':
        response = requests.put(
            f"{USER_SERVICE_URL}/users/{user_id}",
            json=request.json,
            headers=request.headers
        )
    return jsonify(response.json()), response.status_code

@app.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    try:
        current_user = get_jwt_identity()
        data = request.json
        
        grpc_request = post_pb2.CreatePostRequest(
            title=data["title"],
            description=data.get("description", ""),
            creator_id=current_user,
            is_private=data.get("is_private", False),
            tags=data.get("tags", []),
        )
        
        response = post_stub.CreatePost(grpc_request)
        return jsonify(MessageToDict(response)), 201
    
    except Exception as e:
        return handle_grpc_error(e)

@app.route('/posts/<string:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    try:
        current_user = get_jwt_identity()
        grpc_request = post_pb2.GetPostRequest(
            id=post_id,
            user_id=current_user
        )
        response = post_stub.GetPost(grpc_request)
        return jsonify(MessageToDict(response))
    
    except Exception as e:
        return handle_grpc_error(e)

@app.route('/posts/<string:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    try:
        current_user = get_jwt_identity()
        data = request.json
        
        grpc_request = post_pb2.UpdatePostRequest(
            id=post_id,
            user_id=current_user,
            title=data.get("title"),
            description=data.get("description"),
            is_private=data.get("is_private"),
            tags=data.get("tags"),
        )
        
        response = post_stub.UpdatePost(grpc_request)
        return jsonify(MessageToDict(response))
    
    except Exception as e:
        return handle_grpc_error(e)

@app.route('/promos', methods=['POST'])
@jwt_required()
def create_promo():
    try:
        current_user = get_jwt_identity()
        data = request.json
        
        grpc_request = promo_pb2.CreatePromoRequest(
            name=data["name"],
            description=data.get("description", ""),
            creator_id=current_user,
            discount=data["discount"],
            code=data["code"],
        )
        
        response = promo_stub.CreatePromo(grpc_request)
        return jsonify(MessageToDict(response)), 201
    
    except Exception as e:
        return handle_grpc_error(e)

@app.route('/promos/<string:promo_id>', methods=['GET'])
@jwt_required()
def get_promo(promo_id):
    try:
        current_user = get_jwt_identity()
        grpc_request = promo_pb2.GetPromoRequest(id=promo_id)
        response = promo_stub.GetPromo(grpc_request)
        
        # Проверка прав доступа
        if response.creator_id != current_user:
            return jsonify({"error": "Forbidden"}), 403
            
        return jsonify(MessageToDict(response))
    
    except Exception as e:
        return handle_grpc_error(e)

@app.route('/posts/<string:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    try:
        current_user = get_jwt_identity()
        grpc_request = post_pb2.DeletePostRequest(
            id=post_id,
            user_id=current_user
        )
        response = post_stub.DeletePost(grpc_request)
        return jsonify({'success': response.success}), 200
    except Exception as e:
        return handle_grpc_error(e)

@app.route('/posts', methods=['GET'])
@jwt_required()
def list_posts():
    try:
        current_user = get_jwt_identity()
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        
        grpc_request = post_pb2.ListPostsRequest(
            user_id=current_user,
            page=page,
            per_page=per_page
        )
        response = post_stub.ListPosts(grpc_request)
        return jsonify({
            'posts': [MessageToDict(post) for post in response.posts],
            'total': response.total
        })
    except Exception as e:
        return handle_grpc_error(e)

@app.route('/promos/<string:promo_id>', methods=['PUT'])
@jwt_required()
def update_promo(promo_id):
    try:
        current_user = get_jwt_identity()
        data = request.json
        
        grpc_request = promo_pb2.UpdatePromoRequest(
            id=promo_id,
            creator_id=current_user,
            name=data.get('name'),
            description=data.get('description'),
            discount=data.get('discount'),
            code=data.get('code')
        )
        response = promo_stub.UpdatePromo(grpc_request)
        return jsonify(MessageToDict(response))
    except Exception as e:
        return handle_grpc_error(e)

@app.route('/promos/<string:promo_id>', methods=['DELETE'])
@jwt_required()
def delete_promo(promo_id):
    try:
        current_user = get_jwt_identity()
        grpc_request = promo_pb2.DeletePromoRequest(
            id=promo_id,
            creator_id=current_user
        )
        response = promo_stub.DeletePromo(grpc_request)
        return jsonify({'success': response.success}), 200
    except Exception as e:
        return handle_grpc_error(e)

@app.route('/promos', methods=['GET'])
@jwt_required()
def list_promos():
    try:
        current_user = get_jwt_identity()
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        
        grpc_request = promo_pb2.ListPromosRequest(
            creator_id=current_user,
            page=page,
            per_page=per_page
        )
        response = promo_stub.ListPromos(grpc_request)
        return jsonify({
            'promos': [MessageToDict(promo) for promo in response.promos],
            'total': response.total
        })
    except Exception as e:
        return handle_grpc_error(e)

@jwt.unauthorized_loader
def unauthorized_callback(callback):
    return jsonify({"error": "Missing or invalid token"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(callback):
    return jsonify({"error": "Invalid token"}), 401

@jwt.expired_token_loader
def expired_token_callback(callback):
    return jsonify({"error": "Token has expired"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
