import json

from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from .auth.auth import AuthError, requires_auth
from .database.models import setup_db, Drink

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json 
    {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure --> done
'''


@app.route("/drinks")
def drinks():
    try:
        all_drinks = Drink.query.all()
        all_drinks = [d.short() for d in all_drinks]
        return jsonify(
            {
                "success": True,
                "drinks": all_drinks
            }
        )
    except():
        abort(400)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and
     json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure --> done
'''


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def drinks_detail(payload):
    try:
        all_drinks = Drink.query.all()
        all_drinks = [d.long() for d in all_drinks]

        return jsonify(
            {
                "success": True,
                "drinks": all_drinks
            }
        )
    except():
        abort(400)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 
    and json {"success": True, "drinks": drink}
     where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure --> done
'''


@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def drink_insert(payload):
    try:
        if type(request.json['recipe']) != list:
            recipe = [request.json['recipe']]
        else:
            recipe = request.json['recipe']

        drink = Drink(
            title=json.dumps(request.json['title']),
            recipe=json.dumps(recipe)
        )

        drink.insert()

        return jsonify(
            {
                "success": True,
                "drinks": [drink.long()]
            }
        )
    except():
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 
    and json {"success": True, "drinks": drink} where drink
     an array containing only the updated drink
        or appropriate status code indicating reason for failure --> done
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, id):
    try:
        drink = Drink.query.get(id)

        if not drink:
            abort(404)

        drink.title = json.dumps(request.json['title'])
        drink.insert()

        return jsonify(
            {
                'success': True,
                "drinks": [drink.long()]
            }
        )
    except():
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
     where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.get(id)

        if not drink:
            abort(404)

        drink.delete()

        return jsonify(
            {
                'success': True,
                "delete": id
            }
        )
    except():
        abort(400)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                        "success": False, 
                        "error": 404,
                        "message": "resource not found"
                    }), 404 -

'''
'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(400)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.error['code'],
        "message": error.error['description']
    }), error.status_code
