import os
from flask import Flask,request, abort, jsonify
from models import setup_db, Category, Item
from flask_cors import CORS

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
    def create_item():
        body = request.get_json()

        new_item = body.get("item", None)
        new_brand = body.get("brand", None)
        new_category = body.get("category", None)
        new_comment = body.get("comment", None)

        if new_item == None or new_brand == None or new_category == None or new_comment == None:
            abort(422)

        try:
            item = Item(item=new_item, brand=new_brand,
                                category=new_category, comment=new_comment)
            item.insert()

            current_items = paginate_items(request)

            return jsonify(
                {
                    "success": True,
                    "created": item.id,
                    "items": current_items,
                    "total_items": len(Item.query.all()),
                }
            )
        except:
            abort(422)
        
    
    @app.route('/items/<int:item_id>', methods=["PATCH"])
    def modify_item():
        body = request.get_json()

        current_item = Item.query.filter(Item.id == id).one_or_none()
        if current_item is None:
            abort(422)

        try:
            current_item.update().values({
                "item": body.get("item", current_item.item), 
                "brand": body.get("item", current_item.item), 
                "category": body.get("category", current_item.brand),
                "comment": body.get("comment", current_item.comment) })
        except:
            abort(422)

            
    @app.route('/items/<int:item_id>', methods=["DELETE"])
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

    return app

app = create_app()

if __name__ == '__main__':
    app.run()
