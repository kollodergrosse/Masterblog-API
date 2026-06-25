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
    sort_by = request.args.get('sort', '').strip()
    direction = request.args.get('direction', '').strip().lower()
    current_posts = list(POSTS)
    allowed_parameter = ['title', 'content']

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

    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add():
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
    """ Find the book with the id `book_id`.
    If there is no book with this id, return None. """
    return next((post for post in POSTS if post['id'] == post_id), None)


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_book(id):
    post = find_book_by_id(id)

    if post is None:
        return jsonify({"error": "Not found", "message": "Post not Found"}), 404

    POSTS.remove(post)

    return jsonify({"message": f'Post with id {id} has been deleted successfully.'}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update(id):
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
    search_content = request.args.get('content', '').strip()
    search_title = request.args.get('title', '').strip()

    if not search_title and not search_content:
        return jsonify([]), 200

    searched_posts = [post for post in POSTS if search_title and search_title.lower() in post[
        "title"].lower() or search_content and search_content.lower() in post["content"].lower()]

    return jsonify(searched_posts), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
