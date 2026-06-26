from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieve all posts with optional sorting.

    Supports query parameters 'sort' (field to sort by) and 'direction' ('asc' or 'desc').
    Validates parameters and returns a 400 Bad Request if invalid fields or directions
    are provided.

    Query Parameters:
        sort (str): The field to sort by ('title' or 'content').
        direction (str): The sorting order ('asc' or 'desc').

    Returns:
        tuple: JSON response containing the list of posts and the HTTP 200 OK status,
               or an error message with HTTP 400 Bad Request.
    """
    sort_by = request.args.get('sort', None)
    direction = request.args.get('direction', None)
    current_posts = list(POSTS)
    allowed_parameter = ['title', 'content']

    if not sort_by or not direction:
        return jsonify(POSTS), 200

    if direction not in ['asc', 'desc']:
        return jsonify({
            "error": "Bad Request",
            "message": f"Unallowed sorting direction '{direction}'. Allowed is 'asc' or 'desc'."
        }), 400

    if sort_by and sort_by not in allowed_parameter:
        return jsonify({
            "error": "Bad Request",
            "message": f"Unallowed sorting '{sort_by}'. Allowed is: {', '.join(allowed_parameter)}."
        }), 400

    if sort_by and current_posts:
        reverse_order = (direction == 'desc')

        sorted_posts = sorted(current_posts,
                              key=lambda x: x[sort_by].lower() if isinstance(x[sort_by], str) else x[sort_by],
                              reverse=reverse_order)

        return jsonify(sorted_posts), 200


@app.route('/api/posts', methods=['POST'])
def add():
    """
    Create and add a new post.

    Expects a JSON payload containing 'title' and 'content'. Validates that both fields
    are present and non-empty. Automatically increments and assigns a unique ID to the new post.

    JSON Payload:
        title (str): The title of the new post.
        content (str): The body text of the new post.

    Returns:
        tuple: JSON response with the updated list of all posts and HTTP 201 Created status,
               or an error message with HTTP 400 Bad Request if validation fails.
    """
    if request.method == 'POST':
        new_post = request.get_json()

        title = new_post["title"]
        if title == "":
            return jsonify({"error": "Bad request", "message": "'Title' is required."}), 400

        content = new_post['content']
        if content == "":
            return jsonify({"error": "Bad request", "message": "'Content' is required."}), 400

        new_id = POSTS[-1]['id'] + 1 if POSTS else 1

        new_post = {
            "id": new_id,
            "title": title,
            "content": content
        }

        POSTS.append(new_post)

    return jsonify(POSTS), 201


def find_book_by_id(post_id):
    """
    Find a specific post within the POSTS list by its unique ID.

    Args:
        post_id (int): The unique identifier of the post to search for.

    Returns:
        dict or None: The post dictionary if found, otherwise None.
    """
    return next((post for post in POSTS if post['id'] == post_id), None)


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_book(id):
    """
    Delete an existing post by its ID.

    Checks if the post exists. If found, removes it from the global list.
    Otherwise, triggers a 404 Not Found error.

    Args:
        id (int): The unique identifier of the post to delete.

    Returns:
        tuple: JSON confirmation message with HTTP 200 OK status,
               or an error message with HTTP 404 Not Found.
    """
    post = find_book_by_id(id)

    if post is None:
        return jsonify({"error": "Not found", "message": "Post not Found"}), 404

    POSTS.remove(post)

    return jsonify({"message": f'Post with id {id} has been deleted successfully.'}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update(id):
    """
    Update the title and content of an existing post by its ID.

    Expects a JSON payload with the updated 'title' and 'content'. Verifies the existence
    of the post (returns 404 if missing) and applies updates if fields are valid.

    Args:
        id (int): The unique identifier of the post to update.

    JSON Payload:
        title (str): The updated title.
        content (str): The updated content.

    Returns:
        tuple: JSON response with the updated post object and HTTP 200 OK status,
               or an error message with HTTP 404 Not Found.
    """
    post = find_book_by_id(id)
    post_to_update = request.get_json()

    if post is None:
        return jsonify({"error": "Not found", "message": "Post not Found"}), 404

    if post_to_update["title"] == "" or post_to_update["content"] == "":
        pass

    else:
        for post in POSTS:
            if post["id"] == id:
                post["title"] = post_to_update["title"]
                post["content"] = post_to_update["content"]
                return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search():
    """
    Search for posts containing specific text in their title or content.

    Reads 'title' and 'content' from query parameters. If both parameters are empty
    or missing, it immediately returns an empty list. Matches are case-insensitive.

    Query Parameters:
        title (str): Substring to look for in post titles.
        content (str): Substring to look for in post content.

    Returns:
        tuple: JSON response containing a list of matching posts and HTTP 200 OK status.
    """
    search_content = request.args.get('content', '').strip()
    search_title = request.args.get('title', '').strip()

    if not search_title and not search_content:
        return jsonify([]), 200

    searched_posts = [post for post in POSTS if search_title and search_title.lower() in post[
        "title"].lower() or search_content and search_content.lower() in post["content"].lower()]

    return jsonify(searched_posts), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)