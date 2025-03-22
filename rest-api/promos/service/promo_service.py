from concurrent import futures
import grpc
from datetime import datetime
from proto import promo_pb2
from proto import promo_pb2_grpc
from service.database import db, Promo
from sqlalchemy.exc import IntegrityError

class PromoService(promo_pb2_grpc.PromoServiceServicer):
    def CreatePromo(self, request, context):
        session = db.get_session()
        try:
            new_promo = Promo(
                name=request.name,
                description=request.description,
                creator_id=request.creator_id,
                discount=request.discount,
                code=request.code
            )
            
            session.add(new_promo)
            session.commit()
            
            return self._promo_to_response(new_promo)
            
        except IntegrityError:
            session.rollback()
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "Promo code must be unique")
        except Exception as e:
            session.rollback()
            context.abort(grpc.StatusCode.INTERNAL, str(e))
        finally:
            session.close()

    def GetPromo(self, request, context):
        session = db.get_session()
        try:
            promo = session.query(Promo).get(request.id)
            if not promo:
                context.abort(grpc.StatusCode.NOT_FOUND, "Promo not found")
                
            return self._promo_to_response(promo)
        finally:
            session.close()

    def UpdatePromo(self, request, context):
        session = db.get_session()
        try:
            promo = session.query(Promo).get(request.id)
            if not promo:
                context.abort(grpc.StatusCode.NOT_FOUND, "Promo not found")
                
            if promo.creator_id != request.creator_id:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Access denied")

            if request.HasField('name'):
                promo.name = request.name
            if request.HasField('description'):
                promo.description = request.description
            if request.HasField('discount'):
                promo.discount = request.discount
            if request.HasField('code'):
                promo.code = request.code
                
            promo.updated_at = datetime.utcnow()
            session.commit()
            
            return self._promo_to_response(promo)
        except IntegrityError:
            session.rollback()
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "Promo code must be unique")
        except Exception as e:
            session.rollback()
            context.abort(grpc.StatusCode.INTERNAL, str(e))
        finally:
            session.close()

    def DeletePromo(self, request, context):
        session = db.get_session()
        try:
            promo = session.query(Promo).get(request.id)
            if not promo:
                context.abort(grpc.StatusCode.NOT_FOUND, "Promo not found")
                
            if promo.creator_id != request.creator_id:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Access denied")
            
            session.delete(promo)
            session.commit()
            return promo_pb2.DeleteResponse(success=True)
        finally:
            session.close()

    def ListPromos(self, request, context):
        session = db.get_session()
        try:
            query = session.query(Promo)

            query = query.filter(Promo.creator_id == request.creator_id)

            per_page = request.per_page if request.per_page > 0 else 10
            page = request.page if request.page > 0 else 1
            offset = (page - 1) * per_page

            total = query.count()

            promos = query.order_by(Promo.created_at.desc()) \
                         .offset(offset) \
                         .limit(per_page) \
                         .all()
            
            return promo_pb2.ListPromosResponse(
                promos=[self._promo_to_response(promo) for promo in promos],
                total=total
            )
        finally:
            session.close()

    def _promo_to_response(self, promo):
        return promo_pb2.PromoResponse(
            id=promo.id,
            name=promo.name,
            description=promo.description,
            creator_id=promo.creator_id,
            discount=promo.discount,
            code=promo.code,
            created_at=promo.created_at.isoformat(),
            updated_at=promo.updated_at.isoformat()
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    promo_pb2_grpc.add_PromoServiceServicer_to_server(PromoService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Promo Service started on port 50052")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
