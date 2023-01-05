from models import commit_session, Category, Item, Temp_comment, Comment

ITEMS_PER_PAGE = 10
TEMP_COMMENTS_PER_PAGE = 5
COMMENTS_PER_PAGE = 5

def paginate_items(request):
    page = request.args.get("page", 1, type=int)
    current_index = page - 1
    items = Item.query.order_by(Item.id).limit(
        ITEMS_PER_PAGE).offset(current_index * ITEMS_PER_PAGE).all()
    return [item.format() for item in items]

def paginate_temp_comments(request):
    page = request.args.get("page", 1, type=int)
    current_index = page - 1
    comments = Temp_comment.query.order_by(Temp_comment.id).limit(
        TEMP_COMMENTS_PER_PAGE).offset(current_index * TEMP_COMMENTS_PER_PAGE).all()
    return [comment.format() for comment in comments]

def paginate_comments(request):
    page = request.args.get("page", 1, type=int)
    current_index = page - 1
    comments = Comment.query.order_by(Comment.id).limit(
        COMMENTS_PER_PAGE).offset(current_index * COMMENTS_PER_PAGE).all()
    return [comment.format() for comment in comments]