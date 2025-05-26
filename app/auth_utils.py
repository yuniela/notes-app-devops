import jwt
from functools import wraps
from flask import request, jsonify, current_app, g
from sqlalchemy import select
from app.models import User
from app.database import SessionLocal

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid Authorization header'}), 401
        
        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms='HS256')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        with SessionLocal() as db:
            stmt = select(User).where(User.id == payload['user_id'])
            user = db.execute(stmt).scalars().first()

            if not user:
                return jsonify({'error': 'User not found'}), 404

            g.current_user = user

        return f(*args, **kwargs)  # ✅ Call route function outside session
    return decorated_function  # ✅ Properly return the decorated function
