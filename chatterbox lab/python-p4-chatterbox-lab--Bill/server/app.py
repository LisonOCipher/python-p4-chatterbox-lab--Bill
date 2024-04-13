from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)


@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at).all()
        message_serial = [message.to_dict() for message in messages]
        response = make_response(jsonify(message_serial), 200)
        return response
    
    elif request.method == 'POST':
        data = request.get_json()
        new_message = Message(
            body=data['body'],
            username=data['username'],
        )
        db.session.add(new_message)
        db.session.commit()
        message_dict = new_message.to_dict()
        response = make_response(jsonify(message_dict), 201)
        response.headers['Content-Type'] = 'application/json'  
        return response

# In app.py

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get(id)
    if message is None:
        return jsonify({"error": "Message not found"}), 404

    if request.method == 'PATCH':
        data = request.get_json()
        for key, value in data.items():
            setattr(message, key, value)
        db.session.commit()
        response = make_response(jsonify(message.to_dict()), 200)
        return response
    
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return jsonify({'deleted': True}), 200


if __name__ == '__main__':
    app.run(port=5555)