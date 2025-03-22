from concurrent import futures
import grpc
from datetime import datetime
import uuid
from service.database import db, Post

from proto import post_pb2
from proto import post_pb2_grpc

class PostService(post_pb2_grpc.PostServiceServicer):
    def CreatePost(self, request, context):
        session = db.Session()
        try:
            post_id = str(uuid.uuid4())
            new_post = Post(
                id=post_id,
                title=request.title,
                description=request.description,
                creator_id=request.creator_id,
                is_private=request.is_private,
                tags=list(request.tags),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(new_post)
            session.commit()
            
            return post_pb2.PostResponse(
                id=post_id,
                title=request.title,
                description=request.description,
                creator_id=request.creator_id,
                created_at=new_post.created_at.isoformat(),
                updated_at=new_post.updated_at.isoformat(),
                is_private=request.is_private,
                tags=request.tags
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))
        finally:
            session.close()

    def GetPost(self, request, context):
        session = db.Session()
        try:
            post = session.query(Post).get(request.id)
            if not post:
                context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
            
            if post.is_private and post.creator_id != request.user_id:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Access denied")
            
            return self._post_to_response(post)
        finally:
            session.close()

    def UpdatePost(self, request, context):
        session = db.Session()
        try:
            post = session.query(Post).get(request.id)
            if not post:
                context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
            
            if post.creator_id != request.user_id:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Access denied")
            
            if request.title:
                post.title = request.title
            if request.description:
                post.description = request.description
            if request.is_private:
                post.is_private = request.is_private
            if request.tags:
                post.tags = list(request.tags)
            
            post.updated_at = datetime.now()
            session.commit()
            
            return self._post_to_response(post)
        finally:
            session.close()

    def DeletePost(self, request, context):
        session = db.Session()
        try:
            post = session.query(Post).get(request.id)
            if not post:
                context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
            
            if post.creator_id != request.user_id:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Access denied")
            
            session.delete(post)
            session.commit()
            return post_pb2.DeleteResponse(success=True)
        finally:
            session.close()

    def ListPosts(self, request, context):
        session = db.Session()
        try:
            query = session.query(Post)

            query = query.filter(
                (Post.is_private == False) | 
                (Post.creator_id == request.user_id)
            )

            per_page = request.per_page if request.per_page > 0 else 10
            page = request.page if request.page > 0 else 1
            offset = (page - 1) * per_page

            total = query.count()

            posts = query.order_by(Post.created_at.desc()) \
                        .limit(per_page) \
                        .all()
            
            return post_pb2.ListPostsResponse(
                posts=[self._post_to_response(post) for post in posts],
                total=total
            )
        finally:
            session.close()

    def _post_to_response(self, post):
        return post_pb2.PostResponse(
            id=post.id,
            title=post.title,
            description=post.description or "",
            creator_id=post.creator_id,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat(),
            is_private=post.is_private,
            tags=post.tags if post.tags else []
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_pb2_grpc.add_PostServiceServicer_to_server(PostService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
