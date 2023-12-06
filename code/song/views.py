from django.shortcuts import render, get_object_or_404, redirect
from .forms import ReviewForm, RateReviewForm
from app.utility import only_executeSQL, executeSQL, encoder_22_characters
import uuid
from django.contrib.auth.decorators import login_required
import datetime


all_review_sql = "SELECT content, song_rating, a.id, name, avg_review_rating FROM \
    (SELECT id, AVG(review_rating) AS avg_review_rating, content, song_rating, song_id, r.user_id \
    from review AS r LEFT OUTER JOIN review_rating ON \
    id = review_id \
    GROUP BY id \
    ORDER BY AVG(review_rating) DESC) AS a \
INNER JOIN user \
ON a.user_id = user.id \
WHERE song_id = '{}'"


def get_review_rating(user):
    prev_rating_sql = f"SELECT review_rating FROM review_rating WHERE user_id = '{user.id}'"
    prev_rating = executeSQL(prev_rating_sql)
    return prev_rating

@login_required
def song_detail(request, song_id):
    user = request.user
    song_sql = f"SELECT song_name, artist, album_name, song_genre from song WHERE id = '{song_id}'"
    song_res = executeSQL(song_sql)
    song_res[0]['id'] = song_id
    all_review_res = executeSQL(all_review_sql.format(song_id))

    user_id = user.id
    res = add_song_to_history(user_id, song_id)

    if request.method == 'GET':
        form = ReviewForm()

        return render(request, 'details/song_detail.html', {'song': song_res[0], 'reviews': all_review_res, 'form': form, })

    elif request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            content = form.cleaned_data['content']
            song_rating = form.cleaned_data['song_rating']
            user_id = user.id
            song_id = song_id
            id = str(uuid.uuid4())
            sql = f"INSERT INTO review (id, content, song_rating, user_id, song_id) VALUES ('{id}', '{content}', '{song_rating}', '{user_id}', '{song_id}')"
            res = only_executeSQL(sql) 
        return redirect('song_detail', song_id=song_id)

@login_required
def rate_review(request, review_id):
    user = request.user
    print(user.id)
    review_sql = f"SELECT content, song_rating, name AS username FROM review INNER JOIN user ON user_id = '{user.id}'\
    WHERE review.id = '{review_id}'"
    review_res = executeSQL(review_sql)[0]
    review_res['id'] = review_id
    song_sql = f"SELECT s.id, song_name FROM song AS s INNER JOIN review AS r ON s.id = r.song_id WHERE r.id = '{review_id}'"
    song_res = executeSQL(song_sql)[0]
    review_res['song_name'] = song_res['song_name']
    if request.method == 'GET':
        cur_rating = get_review_rating(user)
        is_rated = 0
        if len(cur_rating) == 0:
            message = {'content':'You have not rated this review before'}
        else:
            is_rated = 1
            message = {'content': f"Your current rating for this review: '{cur_rating[0]['review_rating']}'"}
        form = RateReviewForm()
        return render(request, 'details/rate_review.html', {'review': review_res, 'form': form, 'message':message, 'is_rated':is_rated})
    if request.method == 'POST':
        form = RateReviewForm(request.POST)
        if form.is_valid():
            review_rating = form.cleaned_data['review_rating']
            user_id = user.id
            cur_rating = get_review_rating(user)
            if len(cur_rating) == 0:
                insert_rating_sql = f"INSERT INTO review_rating (review_rating, user_id, review_id) \
                VALUES ('{review_rating}', '{user_id}', '{review_id}')"
                only_executeSQL(insert_rating_sql)
            else:
                update_rating_sql = f"UPDATE review_rating SET review_rating = '{review_rating}' WHERE \
                review_id = '{review_id}' AND user_id = '{user_id}'"
                only_executeSQL(update_rating_sql)
        return redirect('rate_review', review_id=review_id)

@login_required
def delete_rate_review(request, review_id):
    user = request.user
    print(user.id, review_id)
    print("Yes delete is called")
    sql_delete = f"DELETE FROM review_rating WHERE review_id='{review_id}' AND user_id='{user.id}'"
    res = only_executeSQL(sql_delete)
    print(res)
    return redirect('rate_review', review_id=review_id)

            

def add_song_to_history(user_id, song_id):

    id = encoder_22_characters(song_id) 
    print("user_id", user_id, "song_id", id)
    sql = f"insert into song_history (id, user_id, song_id, listened_timestamp) VALUES ('{id}', '{user_id}', '{song_id}', '{datetime.datetime.now()}')"
    res = only_executeSQL(sql)
    return res

