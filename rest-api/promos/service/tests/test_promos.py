import pytest
from unittest.mock import MagicMock
from datetime import datetime
import uuid
import grpc
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

from proto import promo_pb2
from ..promo_service import PromoService
from ..database import db

Base = declarative_base()

class Promo(Base):
    __tablename__ = 'promos'
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    creator_id = Column(String)
    discount = Column(Float)
    code = Column(String, unique=True)
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
    monkeypatch.setattr('service.promo_service.Promo', Promo)
    monkeypatch.setattr(db, 'get_session', lambda: session)
    yield

@pytest.fixture
def promo_service():
    return PromoService()

@pytest.fixture
def grpc_context():
    return MagicMock()

@pytest.fixture
def sample_promo(session):
    promo = Promo(
        id=str(uuid.uuid4()),
        name="Summer Sale",
        description="20% off all items",
        creator_id="user123",
        discount=20.0,
        code="SUMMER20",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(promo)
    session.commit()
    return promo

def test_create_promo_duplicate_code(promo_service, grpc_context, sample_promo):
    request = promo_pb2.CreatePromoRequest(
        code=sample_promo.code,
        name="Test",
        creator_id="user123",
        discount=10.0
    )
    
    promo_service.CreatePromo(request, grpc_context)
    grpc_context.abort.assert_called_with(
        grpc.StatusCode.ALREADY_EXISTS, "Promo code must be unique"
    )

def test_get_promo_success(promo_service, sample_promo, grpc_context):
    request = promo_pb2.GetPromoRequest(id=sample_promo.id)
    response = promo_service.GetPromo(request, grpc_context)
    
    assert response.id == sample_promo.id
    assert response.name == sample_promo.name

def test_update_promo_success(promo_service, sample_promo, grpc_context):
    request = promo_pb2.UpdatePromoRequest(
        id=sample_promo.id,
        creator_id=sample_promo.creator_id,
        name="Updated Sale",
        discount=25.0
    )
    
    response = promo_service.UpdatePromo(request, grpc_context)
    
    assert response.name == "Updated Sale"
    assert response.discount == 25.0
    assert response.updated_at != sample_promo.updated_at

def test_update_promo_permission_denied(promo_service, sample_promo, grpc_context):
    request = promo_pb2.UpdatePromoRequest(
        id=sample_promo.id,
        creator_id="wrong_user",
        name="Test"
    )
    
    promo_service.UpdatePromo(request, grpc_context)
    grpc_context.abort.assert_called_with(
        grpc.StatusCode.PERMISSION_DENIED, "Access denied"
    )

def test_delete_promo_success(promo_service, sample_promo, grpc_context):
    request = promo_pb2.DeletePromoRequest(
        id=sample_promo.id,
        creator_id=sample_promo.creator_id
    )
    
    response = promo_service.DeletePromo(request, grpc_context)
    assert response.success

def test_list_promos_filter(promo_service, session):
    user1_promo1 = Promo(
        id=str(uuid.uuid4()),
        name="User1 Promo1",
        creator_id="user1",
        code="USER1_1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    user1_promo2 = Promo(
        id=str(uuid.uuid4()),
        name="User1 Promo2",
        creator_id="user1",
        code="USER1_2",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    user2_promo = Promo(
        id=str(uuid.uuid4()),
        name="User2 Promo",
        creator_id="user2",
        code="USER2",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add_all([user1_promo1, user1_promo2, user2_promo])
    session.commit()

    request = promo_pb2.ListPromosRequest(creator_id="user1", page=1, per_page=10)
    response = promo_service.ListPromos(request, None)
    
    assert response.total == 2
    assert all(p.creator_id == "user1" for p in response.promos)

def test_list_promos_pagination(promo_service, session):
    for i in range(15):
        promo = Promo(
            id=str(uuid.uuid4()),
            name=f"Promo {i}",
            creator_id="user3",
            code=f"CODE_{i}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(promo)
    session.commit()

    request = promo_pb2.ListPromosRequest(creator_id="user3", page=2, per_page=5)
    response = promo_service.ListPromos(request, None)
    
    assert len(response.promos) == 5
    assert response.total == 15
