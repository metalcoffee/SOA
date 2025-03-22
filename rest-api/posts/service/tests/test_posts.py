import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, JSON
from datetime import datetime
import uuid
import grpc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from proto import post_pb2
from ..post_service import PostService
from ..database import db

Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'
    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(String)
    creator_id = Column(String)
    is_private = Column(Boolean)
    tags = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

@pytest.fixture(scope='module')
def engine():
    return create_engine('sqlite:///:memory:')

@pytest.fixture(scope='module')
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(autouse=True)
def setup_db(session, monkeypatch):
    monkeypatch.setattr('service.post_service.Post', Post)
    monkeypatch.setattr(db, 'Session', sessionmaker(bind=session.bind))

@pytest.fixture
def post_service():
    return PostService()

@pytest.fixture
def grpc_context():
    return MagicMock()

def test_create_post_success(post_service, grpc_context, session):
    request = post_pb2.CreatePostRequest(
        title="Test Title",
        description="Test Description",
        creator_id="user123",
        is_private=False,
        tags=["tag1", "tag2"]
    )
    
    response = post_service.CreatePost(request, grpc_context)
    
    assert response.title == request.title
    assert response.creator_id == request.creator_id
    assert uuid.UUID(response.id)
    
    post = session.query(Post).first()
    assert post is not None
    assert post.title == request.title
    assert post.description == request.description

def test_get_post_success(post_service, grpc_context, session):
    post_id = str(uuid.uuid4())
    post = Post(
        id=post_id,
        title="Test",
        creator_id="user123",
        is_private=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(post)
    session.commit()
    
    request = post_pb2.GetPostRequest(id=post_id, user_id="user456")
    response = post_service.GetPost(request, grpc_context)
    assert response.id == post_id
    grpc_context.abort.assert_not_called()

def test_get_post_private_permission_denied(post_service, grpc_context, session):
    post_id = str(uuid.uuid4())
    post = Post(
        id=post_id,
        title="Private",
        creator_id="user123",
        is_private=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(post)
    session.commit()
    
    request = post_pb2.GetPostRequest(id=post_id, user_id="user456")
    post_service.GetPost(request, grpc_context)
    
    grpc_context.abort.assert_called_with(
        grpc.StatusCode.PERMISSION_DENIED, "Access denied"
    )

def test_update_post_success(post_service, grpc_context, session):
    post_id = str(uuid.uuid4())
    post = Post(
        id=post_id,
        title="Old Title",
        creator_id="user123",
        is_private=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(post)
    session.commit()
    
    request = post_pb2.UpdatePostRequest(
        id=post_id,
        user_id="user123",
        title="New Title",
        is_private=True,
        tags=["new_tag"]
    )
    response = post_service.UpdatePost(request, grpc_context)
    
    assert response.title == "New Title"
    assert response.is_private is True
    assert response.tags == ["new_tag"]
    
    updated_post = session.query(Post).get(post_id)
    post.updated_at = datetime.now()
    session.commit()
    assert updated_post.title == "New Title"

def test_update_post_permission_denied(post_service, grpc_context, session):
    post_id = str(uuid.uuid4())
    post = Post(
        id=post_id,
        creator_id="user123",
        is_private=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(post)
    session.commit()
    
    request = post_pb2.UpdatePostRequest(id=post_id, user_id="user456")
    post_service.UpdatePost(request, grpc_context)
    
    grpc_context.abort.assert_called_with(
        grpc.StatusCode.PERMISSION_DENIED, "Access denied"
    )

def test_delete_post_success(post_service, grpc_context, session):
    post_id = str(uuid.uuid4())
    post = Post(
        id=post_id,
        creator_id="user123",
        is_private=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(post)
    session.commit()
    
    request = post_pb2.DeletePostRequest(id=post_id, user_id="user123")
    response = post_service.DeletePost(request, grpc_context)
    
    assert response.success is True
    assert session.query(Post).get(post_id) is None

def test_list_posts_public_and_own_private(post_service, session):
    public_post = Post(
        id=str(uuid.uuid4()),
        title="Public",
        creator_id="user1",
        is_private=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    private_post_user1 = Post(
        id=str(uuid.uuid4()),
        title="Private User1",
        creator_id="user1",
        is_private=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    private_post_user2 = Post(
        id=str(uuid.uuid4()),
        title="Private User2",
        creator_id="user2",
        is_private=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    session.add_all([public_post, private_post_user1, private_post_user2])
    session.commit()

    request = post_pb2.ListPostsRequest(user_id="user2", page=1, per_page=10)
    response = post_service.ListPosts(request, None)
    
    assert len(response.posts) == 2
    titles = {post.title for post in response.posts}
    assert "Public" in titles
    assert "Private User2" in titles
    assert "Private User1" not in titles

def test_list_posts_pagination(post_service, session):
    for i in range(15):
        post = Post(
            id=str(uuid.uuid4()),
            title=f"Post {i}",
            creator_id="user123",
            is_private=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(post)
    session.commit()
    
    request = post_pb2.ListPostsRequest(user_id="user123", page=2, per_page=5)
    response = post_service.ListPosts(request, None)
    
    assert len(response.posts) == 5
    assert response.total == 15
