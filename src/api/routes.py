"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from datetime import datetime
import base64
import requests

from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import Gender, db, User, Payment, Subscription, Review, Match, Like
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import  JWTManager, create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)

bcrypt = Bcrypt()
# Verify identity of the user
@api.route('/<int:dni>', methods=['GET'])
def verify(dni):
  try:
    url = f'https://api.datos.org.pe/reniec/dni/{dni}'
    response = requests.get(url, verify=False)
    data = response.json()
    return jsonify(data), 200
  except Exception as e:
      return jsonify({"error": str(e)}), 500

# Gender CRUD
@api.route('/genders', methods=['POST'])
def create_gender():
    data = request.json
    new_gender = Gender(name=data['name'])
    db.session.add(new_gender)
    db.session.commit()
    return jsonify({'message': 'Gender created successfully'}), 201

@api.route('/genders', methods=['GET'])
def get_genders():
    genders = Gender.query.all()
    return jsonify([{'id': gender.id, 'name': gender.name} for gender in genders])

@api.route('/genders/<int:gender_id>', methods=['GET'])
def get_gender(gender_id):
    gender = Gender.query.get_or_404(gender_id)
    return jsonify({'id': gender.id, 'name': gender.name})

@api.route('/genders/<int:gender_id>', methods=['PUT'])
def update_gender(gender_id):
    gender = Gender.query.get_or_404(gender_id)
    data = request.json
    gender.name = data.get('name', gender.name)
    db.session.commit()
    return jsonify({'message': 'Gender updated successfully'})

@api.route('/genders/<int:gender_id>', methods=['DELETE'])
def delete_gender(gender_id):
    gender = Gender.query.get_or_404(gender_id)
    db.session.delete(gender)
    db.session.commit()
    return jsonify({'message': 'Gender deleted successfully'})

# Payment CRUD
@api.route('/payments', methods=['POST'])
def create_payment():
    data = request.json
    new_payment = Payment(
        user_id=data['user_id'],
        payment_id=data['payment_id'],
        amount=data['amount'],
        currency=data.get('currency'),
        payment_date=datetime.fromisoformat(data['payment_date']),
        payment_status=data.get('payment_status', 'pending'),
        payment_method=data['payment_method']
    )
    db.session.add(new_payment)
    db.session.commit()
    return jsonify({'message': 'Payment created successfully'}), 201

@api.route('/payments', methods=['GET'])
def get_payments():
    payments = Payment.query.all()
    return jsonify([payment.serialize() for payment in payments])

@api.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    return jsonify(payment.serialize())

@api.route('/payments/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    data = request.json
    payment.payment_status = data.get('payment_status', payment.payment_status)
    db.session.commit()
    return jsonify({'message': 'Payment updated successfully'})

@api.route('/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    db.session.delete(payment)
    db.session.commit()
    return jsonify({'message': 'Payment deleted successfully'})

# Subscription CRUD
@api.route('/subscriptions', methods=['POST'])
def create_subscription():
    data = request.json
    new_subscription = Subscription(
        name=data['name'],
        price=data['price'],
        duration_in_days=data['duration_in_days'],
        description=data['description']
    )
    db.session.add(new_subscription)
    db.session.commit()
    return jsonify({'message': 'Subscription created successfully'}), 201

@api.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    subscriptions = Subscription.query.all()
    return jsonify([subscription.serialize() for subscription in subscriptions])

@api.route('/subscriptions/<int:subscription_id>', methods=['GET'])
def get_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    return jsonify(subscription.serialize())

@api.route('/subscriptions/<int:subscription_id>', methods=['PUT'])
def update_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    data = request.json
    subscription.name = data.get('name', subscription.name)
    subscription.price = data.get('price', subscription.price)
    subscription.duration_in_days = data.get('duration_in_days', subscription.duration_in_days)
    subscription.description = data.get('description', subscription.description)
    db.session.commit()
    return jsonify({'message': 'Subscription updated successfully'})

@api.route('/subscriptions/<int:subscription_id>', methods=['DELETE'])
def delete_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    db.session.delete(subscription)
    db.session.commit()
    return jsonify({'message': 'Subscription deleted successfully'})

# Calculate the age of a user
def calculate_age(birthdate):
  today = datetime.today()
  birthdate = datetime.strptime(birthdate, '%Y-%m-%d')
  age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
  return age

# User CRUD
@api.route('/register', methods=['POST'])
def register():
  try:
    data = request.json
    birthdate = data.get('age')
    
    if 'image' in data and len(data['image']) > 0:
      base64_str = data['image'][0].split(',')[1]
      image_data = base64.b64decode(base64_str)
    else:
      image_data = None
      
    try:
        age = calculate_age(birthdate)
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400
      
    password = data.get('password')
    
    print("Password:", password)  # Imprime el valor de password
    print("Type of password:", type(password))  # Imprime el tipo de password
    
    if not password:
        return jsonify({"msg": "Password is required"}), 400
    
    # Asegúrate de que password sea una cadena
    if isinstance(password, tuple):
        password = password[0] if password else ''
    
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
      return jsonify({"msg": "Email already in use"}), 400
    
    print("Password after check:", password)  # Imprime el valor de password después de la verificación
    print("Type of password after check:", type(password))  # Imprime el tipo de password después de la verificación
    
    hashed_password = generate_password_hash(password)
    new_user = User(
        name=data.get('name'),
        email=data.get('email'),
        password=hashed_password,
        country=data.get('country'),
        age=str(age),
        gender_id=data.get('gender_id'),
        gender_to_show_id=data.get('gender_to_show_id'),
        subscription_id=data.get('subscription_id'),
        role=data.get('role'),  # Cambiado de data['role'] a data.get('role')
        image = image_data
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201
  except Exception as e:
    return jsonify({"msg": str(e)}), 500
  
@api.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token, user = user.id), 200
    else:
        return jsonify({"msg": "Bad email or password"}), 401

@api.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users])

@api.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.serialize())

@api.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.password = data.get('password', user.password)
    user.country = data.get('country', user.country)
    user.age = data.get('age', user.age)
    user.gender_id = data.get('gender_id', user.gender_id)
    user.gender_to_show_id = data.get('gender_to_show_id', user.gender_to_show_id)
    user.subscription_id = data.get('subscription_id', user.subscription_id)
    user.role = data.get('role', user.role)
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@api.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@api.route('/reviews', methods=['GET'])
def create_review():
  try:
    reviews = Review.query.all()
    results = list(map(lambda review: review.serialize(), reviews))
    return jsonify(results), 201
  except Exception as e:
    return jsonify({"msg": str(e)}), 500
  
# Crear un "Like" y verificar si hay match
@api.route('/likes', methods=['POST'])
def create_like():
    try:
        data = request.json
        user_from_id = data['user_from_id']
        user_to_id = data['user_to_id']

        # Verify that both users exist
        user_from = User.query.get_or_404(user_from_id)
        user_to = User.query.get_or_404(user_to_id)

        # Verificar if exist a previous like
        existing_like = Like.query.filter_by(user_from_id=user_from_id, user_to_id=user_to_id).first()
        if existing_like:
            return jsonify({"msg": "Like already exists"}), 400

        # Create a new like
        new_like = Like(user_from_id=user_from_id, user_to_id=user_to_id)
        db.session.add(new_like)

        # Verificar if user_to_id has liked user_from_id
        mutual_like = Like.query.filter_by(user_from_id=user_to_id, user_to_id=user_from_id).first()

        if mutual_like:
            # If both users have liked each other, create a match
            new_match = Match(user1_id=user_from_id, user2_id=user_to_id)
            db.session.add(new_match)
            msg = "Match created!"
        else:
            msg = "Like registered."
        db.session.commit()
        return jsonify({"msg": msg}), 201
    except Exception as e:
        return jsonify({"msg": str(e)}), 500


# Get matches from a user
@api.route('/user/<int:user_id>/matches', methods=['GET'])
def get_user_matches(user_id):
    try:
        matches = Match.query.filter(
            (Match.user1_id == user_id) | (Match.user2_id == user_id)
        ).all()
        
        # Serializar los resultados
        results = [m.serialize() for m in matches]
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500