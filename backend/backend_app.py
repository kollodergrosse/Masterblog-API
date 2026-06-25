from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add():
    if request.method == 'POST':
        new_post = request.get_json()

        title = new_post["title"]
        if title == "":
            return jsonify("Bad request: 'Title' is required."), 400

        content = new_post['content']
        if content == "":
            return jsonify("Bad request: 'Content' is required."), 400

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
        return jsonify("Post not Found"), 404

    POSTS.remove(post)

    return jsonify({"message": f'Post with id {id} has been deleted successfully.'}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update(id):
    post = find_book_by_id(id)
    post_to_update = request.get_json()

    if post is None:
        return jsonify("Post not Found"), 404

    if post_to_update["title"] == "" or post_to_update["content"] == "":
        pass

    else:
        for post in POSTS:
            if post["id"] == id:
                post["title"] = post_to_update["title"]
                post["content"] = post_to_update["content"]
                return jsonify(post), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
