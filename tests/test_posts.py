import pytest

from app import schemas


def test_get_posts(authorized_client, test_posts):
    response = authorized_client.get("/posts")
    assert response.status_code == 200

    # posts = [schemas.PostOut(**post).dict() for post in response.json()]
    assert len(response.json()) == len(test_posts)


def test_unauthorized_user_get_posts(client):
    response = client.get("/posts")
    assert response.status_code == 401


def test_unauthorized_user_get_post(client, test_posts):
    response = client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401


def test_get_post_which_does_not_exist(authorized_client, test_posts):
    response = authorized_client.get("/posts/99999999999999")
    print(response.json())
    assert response.status_code == 404


def test_get_post(authorized_client, test_posts):
    response = authorized_client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 200

    post = schemas.PostOut(**response.json())
    assert post.Post.id == test_posts[0].id
    assert post.Post.title == test_posts[0].title
    assert post.Post.content == test_posts[0].content


@pytest.mark.parametrize(
    "title, content, published",
    [
        ("awesome new title", "awesome new content", True),
        ("favorite pizza", "I love pepperoni", False),
        ("tallest skyscrapers", "wahoo", True),
    ],
)
def test_create_post(
    authorized_client, test_user, test_posts, title, content, published
):
    post_data = {"title": title, "content": content, "published": published}
    response = authorized_client.post("/posts", json=post_data)
    assert response.status_code == 201

    created_post = schemas.Post(**response.json())
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.user_id == test_user["id"]


def test_create_post_default_published_false(authorized_client, test_user, test_posts):
    response = authorized_client.post(
        "/posts", json={"title": "arbitrary title", "content": "some content"}
    )
    assert response.status_code == 201

    created_post = schemas.Post(**response.json())
    assert created_post.title == "arbitrary title"
    assert created_post.content == "some content"
    assert created_post.published is False
    assert created_post.user_id == test_user["id"]


def test_unauthorized_user_create_post(client, test_posts):
    response = client.post(
        "/posts", json={"title": "arbitrary title", "content": "some content"}
    )
    assert response.status_code == 401


def test_unauthorized_user_delete_post(client, test_posts):
    response = client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401


def test_delete_post_success(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 204


def test_delete_post_which_does_not_exist(authorized_client, test_posts):
    response = authorized_client.delete("/posts/99999999")
    assert response.status_code == 404


def test_delete_other_user_post(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert response.status_code == 403


def test_update_post(authorized_client, test_user, test_posts):
    post_data = {"title": "updated title", "content": "updated content"}
    response = authorized_client.put(f"/posts/{test_posts[0].id}", json=post_data)
    assert response.status_code == 200

    updated_post = schemas.Post(**response.json())
    assert updated_post.title == post_data["title"]
    assert updated_post.content == post_data["content"]


def test_update_other_user_post(authorized_client, test_user, test_user2, test_posts):
    post_data = {"title": "updated title", "content": "updated content"}
    response = authorized_client.put(f"/posts/{test_posts[3].id}", json=post_data)
    assert response.status_code == 403


def test_unauthorized_user_update_post(client, test_posts):
    post_data = {"title": "updated title", "content": "updated content"}
    response = client.put(f"/posts/{test_posts[0].id}", json=post_data)
    assert response.status_code == 401


def test_update_post_which_does_not_exist(authorized_client, test_posts):
    post_data = {"title": "updated title", "content": "updated content"}
    response = authorized_client.put("/posts/99999999999", json=post_data)
    assert response.status_code == 404
