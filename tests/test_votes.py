import pytest

from app import models


@pytest.fixture
def test_vote(test_posts, db_session, test_user):
    new_vote = models.Vote(post_id=test_posts[3].id, user_id=test_user["id"])
    db_session.add(new_vote)
    db_session.commit()

    return new_vote


def test_vote_on_post(authorized_client, test_posts):
    vote_data = {"post_id": test_posts[0].id, "vote_dir": 1}
    response = authorized_client.post("/vote", json=vote_data)
    assert response.status_code == 201


def test_vote_twice_on_post(authorized_client, test_posts, test_vote):
    response = authorized_client.post(
        "/vote", json={"post_id": test_posts[3].id, "vote_dir": 1}
    )
    assert response.status_code == 409


def test_delete_vote(authorized_client, test_posts, test_vote):
    response = authorized_client.post(
        "/vote", json={"post_id": test_posts[3].id, "vote_dir": 0}
    )
    assert response.status_code == 201


def test_delete_vote_which_does_not_exist(authorized_client, test_posts):
    response = authorized_client.post(
        "/vote", json={"post_id": test_posts[3].id, "vote_dir": 0}
    )
    assert response.status_code == 404


def test_vote_on_post_which_does_not_exist(authorized_client, test_posts):
    response = authorized_client.post(
        "/vote", json={"post_id": 999999999, "vote_dir": 1}
    )
    assert response.status_code == 404


def test_unauthorized_user_vote(client, test_posts):
    response = client.post("/vote", json={"post_id": test_posts[3].id, "vote_dir": 1})
    assert response.status_code == 401
