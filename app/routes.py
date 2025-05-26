from flask import Blueprint, request, jsonify
from app.models import Note, User
from app.database import SessionLocal
from sqlalchemy import select, or_
import jwt
import datetime
from flask import current_app
from app.auth_utils import jwt_required
from flask import g
from datetime import datetime, timedelta

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/notes', methods=['GET'])
@jwt_required
def get_user_notes():
    search      = request.args.get('search')
    tags_param  = request.args.get('tags')
    page        = int(request.args.get('page', 1))
    limit       = int(request.args.get('limit', 10))
    offset      = (page - 1) * limit

    with SessionLocal() as db:
        stmt = select(Note).where(
            Note.user_id == g.current_user.id,
            Note.is_deleted == False
        )

        if search:
            stmt = stmt.where(or_(
                Note.title.ilike(f"%{search}%"),
                Note.content.ilike(f"%{search}%")
            ))

        if tags_param:
            tags = [tag.strip() for tag in tags_param.split(",") if tag.strip()]
            tag_filters = []
            for tag in tags:
                tag_filters.append(Note.tags.ilike(f"{tag}"))
                tag_filters.append(Note.tags.ilike(f"{tag},%"))
                tag_filters.append(Note.tags.ilike(f"%,{tag}"))
                tag_filters.append(Note.tags.ilike(f"%,{tag},%"))
            stmt = stmt.where(or_(*tag_filters))

        stmt = stmt.order_by(Note.created_at.desc()).offset(offset).limit(limit)

        notes = db.execute(stmt).scalars().all()
        return jsonify([n.to_dict() for n in notes]), 200

    search      = request.args.get('search')
    tags_param  = request.args.get('tags')
    page        = int(request.args.get('page',1))
    limit       = int(request.args.get('limit',10))
    offset      = (page - 1) * limit

    with SessionLocal() as db:
        
        stmt = select(Note).where(
            Note.user_id == g.current_user.id, Note.is_deleted == False
        ).order_by(Note.created_at.desc())

        if search:
            stmt = stmt.where(or_(
                Note.title.ilike(f"%{search}%"),
                Note.content.ilike(f"%{search}%")
            ))

        if tags_param:
            tags        = [tag.strip() for tag in tags_param.split(",") if tag.strip() ]
            tag_filters = []
            for tag in tags:
                tag_filters.append(Note.tags.ilike(f"{tag}"))
                tag_filters.append(Note.tags.ilike(f"{tag},%"))
                tag_filters.append(Note.tags.ilike(f"%,{tag}"))
                tag_filters.append(Note.tags.ilike(f"%,{tag},%"))
            stmt = stmt.where(or_(*tag_filters))

        stmt = stmt.order_by(Note.created_at.desc()).offset(offset).limit(limit)

        #scalars extracts just ORM objects not raw sql
        notes = db.execute(stmt).scalars().all()
        return jsonify([n.to_dict() for n in notes]), 200


@api.route('/notes', methods=['POST'])
@jwt_required
def add_note():
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify(error="Missing required fields"), 400
    
    with SessionLocal() as db:
        
        note = Note(
            title   =data['title'], 
            content =data['content'],
            tags = data['tags'],
            user_id = g.current_user.id
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return jsonify(note.to_dict()), 201


@api.route('/notes/<int:note_id>', methods=['PUT'])
@jwt_required
def update_note(note_id):
    data = request.get_json()
    with SessionLocal() as db: 
        #prepare the query
        stmt = select(Note).where(Note.user_id == g.current_user.id, Note.id == note_id)
        note = db.execute(stmt).scalars().first()
        if not note:
            return jsonify({'error':'Note not found'}), 404
        note.title = data['title']
        note.content = data['content']
        db.commit()
        return jsonify(note.to_dict()), 200

@api.route('/notes/<int:note_id>', methods=['DELETE'])
@jwt_required
def delete_notes(note_id):
    with SessionLocal() as db:
        stmt = select(Note).where(
             Note.user_id == g.current_user.id,
            Note.id == note_id)
        note = db.execute(stmt).scalars().first()
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        note.is_deleted = True
        db.commit()
        return jsonify({'message': 'Note deleted'}), 200
    
@api.route('/notes/<int:note_id>/restore', methods=['PUT'])
@jwt_required
def recovery_deleted_notes(note_id):
    with SessionLocal() as db:
        stmt = select(Note).where( Note.user_id == g.current_user.id, Note.id == note_id)
        note = db.execute(stmt).scalars().first()
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        if not note.is_deleted:
            return jsonify({'message': 'Note is already active'}), 200
        
        note.is_deleted = False
        db.commit()
        
        return jsonify({'message': 'Note restored'}), 200
    
@api.route('/notes/deleted', methods=['GET'])
@jwt_required
def get_deleted_notes():
    with SessionLocal() as db:
        stmt = select(Note).where( Note.user_id == g.current_user.id, Note.is_deleted == True)
        #scalars extracts just ORM objects not raw sql
        notes = db.execute(stmt).scalars().all()
        return jsonify([n.to_dict() for n in notes]), 200


#create users
@api.route('/register', methods=['POST'])
def create_user():
    data = request.get_json()
    print("Request JSON:", request.get_json())

    if not data or 'user_name' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required"}), 400

    with SessionLocal() as db:
        #check if the username exist
        stmt = select(User).where(User.user_name == data['user_name'])
        exising_user = db.execute(stmt).scalars().first()

        if exising_user:
            return jsonify({'error': 'Username already exist'}), 409
        
        user = User(user_name=data['user_name'])
        user.set_password(data['password'])
        db.add(user)
        db.commit()
        db.refresh(user)

        token = jwt.encode({"user_id": user.id, "exp": ...}, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")
        return jsonify({
            "id": user.id,
            "user_name": user.user_name,
            "token": token
        }), 201

    

#USER LOGIN
@api.route('/auth/login', methods=['POST'])
def user_login():
    data = request.get_json()
    with SessionLocal() as db:
        stmt = select(User).where(User.user_name == data['user_name'])
        user = db.execute(stmt).scalars().first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid username or password'}), 403
        
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=15)
        }, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

        refresh_token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

        return jsonify({
            'message': 'Login successful',
            'access_token': token,
            'refresh_token': refresh_token
        }), 200
    

@api.route('auth/refresh', methods=['POST'])
def refresh_token():
    data = request.get_json()
    token = data.get('refresh_token')

    if not token:
        return jsonify({'error': 'Refresh token is required'}), 401
    
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Refresh token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    
    new_access_token = jwt.encode({
        'user_id': payload['user_id'],
        'exp': datetime.utcnow() + timedelta(minutes=15)
    }, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

    return jsonify({'access_token': new_access_token}), 200


@api.route('/user/info', methods=['GET'])
@jwt_required
def user_information():
    user = g.current_user
    return jsonify({
        "id": user.id,
        "user_name": user.user_name,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat()
    }), 200