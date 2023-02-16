import os
import json
from urllib.parse import quote_plus, urlencode

from flask import Flask,request, abort, make_response, jsonify, render_template, flash, redirect, session, url_for
from models import *
from flask_cors import CORS
from sqlalchemy import insert
from forms import *
from user import auth0_create_user
from auth import AuthError, requires_auth
from authlib.integrations.flask_client import OAuth
from flask_wtf.csrf import CSRFProtect
from config import setup_db, db
from pagination import *



def create_app(test_config=None):
    app = Flask(__name__)
    csrf = CSRFProtect(app)
    csrf.init_app(app)
    app.config.from_object('config')

    oauth = OAuth(app)

    oauth.register(
        "auth0",
        client_id=os.getenv("AUTH0_CLIENT_ID"),
        client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
    )

    setup_db(app)
    #CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET,PUT,POST,DELETE,OPTIONS")
        return response


    @app.route("/login")
    def login():
        return oauth.auth0.authorize_redirect(
            redirect_uri=url_for("callback", _external=True)
        )

    @app.route("/login-results", methods=["GET", "POST"])
    def callback():
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
        session["username"] = "Username:TODO"
        return redirect("/")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(
            "https://" + os.getenv("AUTH0_DOMAIN")
            + "/v2/logout?"
            + urlencode(
                {
                    "returnTo": url_for("index", _external=True),
                    "client_id": os.getenv("AUTH0_CLIENT_ID"),
                },
                quote_via=quote_plus,
            )
        )

    @app.route('/', methods=['GET', 'POST'])
    def index():
        return render_template('pages/home.html',session = session)

    @app.route('/user/create', methods=['GET'])
    def signup():
        form = UserForm()
        return render_template('forms/register.html', form=form)
    
    @app.route('/user/create', methods=['POST'])
    def post_signup():
        error = False

        try:
            form = UserForm(request.form, meta={"csrf": False})
            print('form ', form)
            if form.validate():
                email = request.form['email']
                password = request.form['password']

                res = auth0_create_user(email, password)

                #print(res)
                #print(res.get("auth_user_id"))

                return jsonify(
                    {
                        "success": True,
                        "email": res.get("auth0_email"),
                    }
                )
            else:
                error = True

        except Exception as ex:
            abort(422)

        if error: 
            flash('Failed. User ' + request.form['username'] + ' was not successfully created.')
        
        if not error: flash('User ' + request.form['username'] + ' was successfully created!')

        return render_template('forms/register.html', form=form)
        

    @app.route('/api/v1/categories')
    def api_get_categories():
        categories = Category.query.order_by(Category.type).all()

        if len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": {category.id: category.type for category in categories}
            }
        )
    

    @app.route('/categories/<int:category_id>')
    def get_item_in_category(category_id):
        
        ret = api_get_item_in_category(category_id)

        if (ret.status_code == 404):
            return render_template('errors/404.html')

        cur_items = json.loads(ret.get_data())['items']
        cur_category = json.loads(ret.get_data())['category']
        
        return render_template('pages/items_in_category.html', items=cur_items, category=cur_category)

    @app.route('/api/v1/categories/<int:category_id>')
    def api_get_item_in_category(category_id):
        '''
        get items under the given category
        input:
        {
            category_id:int
        }
        return:
        list of items
        '''
        try:
            items = Item.query.filter(Item.category == category_id).all()
            category_type = Category.query.filter(Category.id == category_id).one_or_none()
        except Exception as ex:
            abort(422)

        if len(items) is None or category_type is None:
            return make_response(jsonify(items), 404)
        
        cur_items = []
        for item in items:
            cur_items.append({'id':item.id, 'title':item.title, 'brand':item.brand})

        return jsonify(
            {
                "success": True,
                "category": category_type.type,
                "items": cur_items
            }
        )

    @app.route('/items')
    def get_items():
        
        ret = api_get_items()
    
        cur_items = json.loads(ret.get_data())['data']
        
        if not cur_items: 
            return render_template('errors/404.html')
        
        return render_template('pages/items.html', all_items=cur_items)


    @app.route('/api/v1/items')
    def api_get_items():
        '''
        get all items in database
        return: "data" :[ {category: "category", items:[{id: "id", title: "t", brand: "b"}, {}]},{}]
        '''
        #items = paginate_items(request)
        
        categories = Category.query.order_by(Category.type).all()
        data = []
        for category_record in categories:
            cur_data={}
            cur_data["category"] = category_record.type
            cur_items=[]
            all_items = Item.query.filter(Item.category==category_record.id).all()
            for item in all_items:
                cur_items.append({'id':item.id, 'title':item.title, 'brand':item.brand})
            cur_data["snacks"] = cur_items
            data.append(cur_data)

        return jsonify(
            {
                "success": True,
                "data": data,
                "total_items": len(Item.query.all()),
            }
        )
    
    @app.route('/snack/<int:item_id>')
    def get_an_item(item_id):
        
        
        ret = api_an_item(item_id)
        
        cur_item = json.loads(ret.get_data())['data']
        print('cur_item', cur_item)
        
        if not cur_item: 
            return render_template('errors/404.html')
        
        return render_template('pages/single_item.html', Snack=cur_item)


    @app.route('/api/v1/snack/<int:item_id>')
    def api_an_item(item_id):
        """
        get a snack's detail data

        input: item_id: int
        """
        cur_item={}
        try:
            
            snack = Item.query.filter(Item.id == item_id).one_or_none()
            
            if not snack: 
                return jsonify(
            {
                "success": False,
                "data": {}
            }
        )

            category = Category.query.filter(
                Category.id == snack.category).one_or_none()
            taste = Taste.query.filter(Taste.item == item_id).all()
            holiday = Holiday.query.filter(Holiday.item == item_id).all()

            combined_taste=''
            combined_holiday=''

            for tst in taste:
                combined_taste += ' ' + tst

            for day in holiday:
                combined_holiday += ' ' + day

            cur_item['title'] = snack.title
            cur_item['brand'] = snack.brand
            cur_item['category'] = category.type
            cur_item['taste'] = combined_taste
            cur_item['holiday'] = combined_holiday

        except Exception as ex:
            print(ex)
            return jsonify(
            {
                "success": False,
                "data": {},
            }
        )
        
        return jsonify(
            {
                "success": True,
                "data": cur_item,
            }
        )



    @app.route('/items', methods=["POST"])
    @requires_auth('post:item')
    def create_item():
        '''
        create a new item
        input:
        {
            title: "",
            brand:""
            category: int
        }
        '''
        body = request.get_json()
        
        new_title = body.get("title")
        new_brand = body.get("brand")
        new_category = body.get("category")
        
        if new_title is None or new_brand is None or new_category is None:
            abort(422)

        try:
            item = Item(title=new_title, brand=new_brand, category=new_category)
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
        
    @app.route('/item/search', methods=["POST"])
    #def search_item():
        # TODO


    @app.route('/items/<int:item_id>', methods=["PATCH"])
    @requires_auth('patch:item')
    def modify_item(item_id):
        '''
        update item basic information
        input:
        {
            title: "",
            brand: ""
            category: int
        }

        '''
        body = request.get_json()
        current_item = Item.query.filter(Item.id == item_id)
        
        if current_item is None:
            abort(404)

        try:
            current_item.update({
                "title": body.get("title", current_item.one_or_none().format().get('title')),
                "brand": body.get("brand", current_item.one_or_none().format().get('brand')),
                "category": body.get("category", current_item.one_or_none().format().get('category'))
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
        '''
        delete item from database table

        '''
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
            
            abort(422)


    @app.route('/user/comments', methods=["POST"])
    @requires_auth('temp_post:comments')
    def add_temp_comment():
        '''
        add comments to temporary table
        input:
        {
            comment: "",
            item: int,
            rating: float,
            userid: int
        }
        '''
        body = request.get_json()
        
        try:
            new_comment = body.get("comment")
            new_item = body.get("item")
            new_rating = body.get("rating")
            new_userid = body.get("userid")

            comment = Temp_comment(comment=new_comment, item=new_item, rating = new_rating, userid = new_userid)
            comment.insert()
            
            current_comments = paginate_temp_comments(request)
            
            cnt_total_items = len(Temp_comment.query.all())
            
            return jsonify(
                {
                    
                    "success": True,
                    "items": current_comments,
                    "total_items": cnt_total_items,
                }
            )
        except Exception as ex:
            
            abort(422)


    @app.route('/admin/comments/<int:item_id>', methods=["POST"])
    @requires_auth('post:comments')
    def add_comment(item_id):
        '''
        add comments to database
        input:
        {
            comment: "",
            item: int,
            rating: float,
            userid: int
        }
        '''
        body = request.get_json()
       
        new_comment = body.get("comment")
        new_rating = body.get("rating")
        updated_item = body.get("item")
        new_userid = body.get("userid")
            
        item = Item.query.filter(Item.id == updated_item).one_or_none()
        
        if item is None:
            abort(404)

        try:
            comment = Comment(comment=new_comment, item=updated_item, rating = new_rating, userid = new_userid)
            comment.insert()
            commit_session()
            current_comments = paginate_comments(request)

            return jsonify(
                {
                    "success": True,
                    "item": updated_item,
                    "comments": current_comments,
                    "total_comments": len(Comment.query.filter(Comment.item == updated_item).all()),
                }
            )
        except Exception as ex:
            abort(422)

    @app.route('/temp/comments/<int:comment_id>', methods=["DELETE"])
    @requires_auth('temp_delete:comments')
    def delete_temp_comment(comment_id):
        '''
        delete comment from temporary table

        input:
        {
            comment_id: int,
        }
        '''
        comment = Temp_comment.query.filter(
            Temp_comment.id == comment_id).one_or_none()

        if comment is None:
            abort(404)

        try:
            comment.delete()
            current_comments = paginate_temp_comments(request)

            return jsonify(
                {
                    "success": True,
                    "deleted": comment_id,
                    "comments": current_comments,
                    "total_comments": len(Comment.query.all()),
                }
            )
        except Exception as ex:
            #print('delete item ', ex)
            abort(422)


    @app.route('/admin/comments/<int:comment_id>', methods=["DELETE"])
    #@requires_auth('delete:comments')
    def delete_comment(comment_id):
        '''
        delete comment from database
        input:
        {
            comment_id: int,
        }
        '''
        comment = Comment.query.filter(
            Comment.id == comment_id).one_or_none()
        print('comment, ', comment)
        if comment is None:
            abort(404)

        try:
            comment.delete()
            commit_session()

            current_comments = paginate_comments(request)

            return jsonify(
                {
                    "success": True,
                    "deleted": comment_id,
                    "current_comments": current_comments,
                    "total_comments": len(Comment.query.all())
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
