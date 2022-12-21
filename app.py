import os
from flask import Flask,request, abort, jsonify
from models import commit_session, setup_db, Category, Item
from flask_cors import CORS
from sqlalchemy import insert
from auth import AuthError, requires_auth

ITEMS_PER_PAGE = 10


def paginate_items(request):
    page = request.args.get("page", 1, type=int)
    current_index = page - 1
    items = Item.query.order_by(Item.id).limit(
        ITEMS_PER_PAGE).offset(current_index * ITEMS_PER_PAGE).all()
    return [item.format() for item in items]

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET,PUT,POST,DELETE,OPTIONS")
        return response

    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.type).all()

        if len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": {category.id: category.type for category in categories}
            }
        )

    @app.route('/items')
    def get_items():
        current_items = paginate_items(request)
        categories = Category.query.order_by(Category.type).all()

        if len(current_items) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": {category.id: category.type for category in categories},
                "items": current_items,
                "total_items": len(Item.query.all()),
            }
        )
    
    @app.route('/items', methods=["POST"])
    @requires_auth('post:item')
    def create_item():
        body = request.get_json()

        new_title = body.get("title")
        new_brand = body.get("brand")
        new_category = body.get("category")
        new_comment = body.get("comment")

        if new_title is None or new_brand is None or new_category is None or new_comment is None:
            abort(422)

        try:
            item = Item(title=new_title, brand=new_brand, category=new_category, comment=new_comment)
            item.insert()
            
            commit_session()
            current_items = paginate_items(request)

            return jsonify(
                {
                    "success": True,
                    "items": current_items,
                    "total_items": len(Item.query.all()),
                }
            )
        except Exception as ex:
            abort(422)
        
    
    @app.route('/items/<int:item_id>', methods=["PATCH"])
    @requires_auth('patch:item')
    def modify_item(item_id):
        body = request.get_json()

        current_item = Item.query.filter(Item.id == item_id)
        if current_item is None:
            abort(422)

        try:
            new_title = body.get("title")
            new_brand = body.get("brand")
            new_category = body.get("category")
            new_comment = body.get("comment")
            
            if new_title is None or new_brand is None or new_category is None or new_comment is None:
                abort(422)

            ret = current_item.update({
                "title": body.get("title", current_item.one_or_none().format().get('title')),
                "brand": body.get("brand", current_item.one_or_none().format().get('brand')),
                "category": body.get("category", current_item.one_or_none().format().get('category')),
                "comment": body.get("comment", current_item.one_or_none().format().get('comment'))
                }, synchronize_session='fetch')
            
            commit_session()

            return jsonify(
                {
                    "success": True,
                    "updated": item_id,
                    "items": current_item.one_or_none().format(),
                    "total_items": len(Item.query.all()),
                }
            )
        except Exception as ex:
            abort(422)

            
    @app.route('/items/<int:item_id>', methods=["DELETE"])
    @requires_auth('delete:item')
    def delete_item(item_id):
        item = Item.query.filter(
            Item.id == item_id).one_or_none()

        if item is None:
            abort(404)

        try:
            item.delete()
            current_items = paginate_items(request)

            return jsonify(
                {
                    "success": True,
                    "deleted": item_id,
                    "items": current_items,
                    "total_items": len(Item.query.all()),
                }
            )
        except Exception as ex:
            #print('delete item ', ex)
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False,
                     "error": 404,
                    "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False,
                     "error": 422,
                    "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    
    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        return jsonify({
            "success": False,
            "error": ex.status_code,
            'message': ex.error
        }), 401
        
    return app

app = create_app()

if __name__ == '__main__':
    app.run()
