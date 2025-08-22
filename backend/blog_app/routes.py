from flask import request, jsonify, Blueprint, current_app 
# **关键修改：从通用 models 包导入 Post 模型**
from models.blog import Post
from database import db 

blog_bp = Blueprint('blog_bp', __name__, url_prefix='/api')

# --- API Endpoints ---

@blog_bp.route('/posts', methods=['GET'])
def get_posts():
    """
    Retrieves a list of all blog posts.
    """
    current_app.logger.info("Received GET request for all posts.")
    posts = Post.query.all()
    posts_data = [post.to_dict() for post in posts]
    current_app.logger.info(f"Returning {len(posts_data)} posts.")
    return jsonify(posts_data)

@blog_bp.route('/posts', methods=['POST'])
def create_post():
    """
    Creates a new blog post.
    Expects JSON data in the request body.
    """
    data = request.get_json()
    current_app.logger.info(f"Received POST request to create a new post with data: {data}")
    if not data:
        current_app.logger.warning("Invalid JSON data received for post creation.")
        return jsonify({"error": "Invalid JSON data"}), 400

    title = data.get('title')
    excerpt = data.get('excerpt')
    content = data.get('content')
    image_url = data.get('imageUrl') 

    if not title or not content:
        current_app.logger.warning("Missing title or content for new post.")
        return jsonify({"error": "Title and content are required"}), 400

    new_post = Post(
        title=title,
        excerpt=excerpt,
        content=content,
        image_url=image_url, 
        views=0 
    )
    db.session.add(new_post)
    db.session.commit()
    current_app.logger.info(f"Post '{title}' created successfully with ID: {new_post.id}")

    return jsonify({"message": "Post created successfully", "id": new_post.id}), 201

@blog_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """
    Retrieves a single blog post by its ID and increments its view count.
    """
    current_app.logger.info(f"Received GET request for post ID: {post_id}")
    post = db.session.get(Post, post_id) 
    
    if post is None:
        current_app.logger.warning(f"Post with ID {post_id} not found.")
        return jsonify({"error": "Post not found"}), 404
    
    current_app.logger.info(f"Post '{post.title}' (ID: {post_id}) current views: {post.views}")

    if post.views is None:
        current_app.logger.info(f"Initializing views for post ID {post_id} from None to 0.")
        post.views = 0
        
    post.views += 1
    current_app.logger.info(f"Post '{post.title}' (ID: {post_id}) new views (before commit): {post.views}")
    db.session.commit() 
    current_app.logger.info(f"Views for post ID {post_id} committed to DB. Final views: {post.views}")

    return jsonify(post.to_dict())

@blog_bp.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Updates an existing blog post.
    Expects JSON data in the request body.
    """
    current_app.logger.info(f"Received PUT request to update post ID: {post_id}")
    post = db.session.get(Post, post_id)
    
    if post is None:
        current_app.logger.warning(f"Post with ID {post_id} not found for update.")
        return jsonify({"error": "Post not found"}), 404
    
    data = request.get_json()
    if not data:
        current_app.logger.warning("Invalid JSON data received for post update.")
        return jsonify({"error": "Invalid JSON data"}), 400

    # Update fields if provided
    if 'title' in data:
        post.title = data['title']
    if 'excerpt' in data:
        post.excerpt = data['excerpt']
    if 'content' in data:
        post.content = data['content']
    if 'imageUrl' in data:
        post.image_url = data['imageUrl']
    
    db.session.commit()
    current_app.logger.info(f"Post '{post.title}' (ID: {post_id}) updated successfully")
    
    return jsonify({"message": "Post updated successfully", "post": post.to_dict()})

@blog_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Deletes a blog post by its ID.
    """
    current_app.logger.info(f"Received DELETE request for post ID: {post_id}")
    post = db.session.get(Post, post_id)
    
    if post is None:
        current_app.logger.warning(f"Post with ID {post_id} not found for deletion.")
        return jsonify({"error": "Post not found"}), 404
    
    post_title = post.title  # Store title for logging before deletion
    db.session.delete(post)
    db.session.commit()
    current_app.logger.info(f"Post '{post_title}' (ID: {post_id}) deleted successfully")
    
    return jsonify({"message": "Post deleted successfully"})
