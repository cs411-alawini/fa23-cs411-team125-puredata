from django.shortcuts import render
from app.utility import only_executeSQL, executeSQL
from django.contrib.auth.decorators import login_required
from app import utility
import datetime
from collections import defaultdict



# Create your views here.

@login_required
def home(request):

    print

    user_name = request.user
    user_id = request.user.id

    if not user_id:
        return render(request, 'registration/login.html', context)

    song_history = get_song_history(user_id)
    song_recommendations =  get_song_recommendations(user_id)
    playlists = get_user_playlists(user_id)
    similar_curated_playlists = get_similar_curated_playlists(user_id)

    context = {
        'song_history': song_history,
        'song_recommendations': song_recommendations,
        'user_name': user_name,
        'user_id': user_id,
        'playlists': dict(playlists),
        'similar_curated_playlists': dict(similar_curated_playlists)
    }

    if request.method == 'GET':
        return render(request, 'home/home_page.html', context)
    
@login_required
def search_box(request):

    song_list = get_song_list_for_search()
    popular_songs = get_popular_songs()
    trending_songs = get_trending_songs()

    if request.method == 'GET':
        song_list = get_song_list_for_search()
        popular_songs = get_popular_songs()
        trending_songs = get_trending_songs()
        context = {
            'song_autocomplete' : song_list,
            'searched_song': None,
            'popular_songs': popular_songs,
            'trending_songs': trending_songs
        }

        return render(request, 'home/search_box.html', context)
    
    if request.method == 'POST':
        song_list = get_song_list_for_search()

        song_name = request.POST.get('song_name')
        searched_song = get_searched_song(song_name)

        print(searched_song)

        context = {
            'song_autocomplete' : song_list,
            'searched_song': searched_song,
            'popular_songs': popular_songs,
            'trending_songs': trending_songs
        }

        return render(request, 'home/search_box.html', context)
    
@login_required
def redirect_song(request, song_id):
    user_name = request.user
    user_id = get_user_id(user_name)

    res = add_song_to_history(user_id, song_id)
    song_history = get_song_history(user_id)
    song_recommendations =  get_song_recommendations(user_id)

    context = {
        'song_history': song_history,
        'song_recommendations': song_recommendations,
        'user_name': user_name,
        'user_id': user_id
    }

    return render(request, 'home/song_page_placeholder.html', context)

@login_required
def add_playlist_song(request):
    context = {}
    return render(request, 'home/add_playlist.html', context)



@login_required
def add_song_to_playlist(request, song_id):
    user_name = request.user
    user_id = get_user_id(user_name)

    song_name = get_song_name(song_id)

    playlists = get_user_playlists(user_id)

    context = {
        'user_playlists': dict(playlists),
        'song_id': song_id,
        'song_name': song_name
    }

    
    return render(request, 'home/add_to_playlist.html', context)

@login_required
def add_song_to_this_playlist(request, song_id, playlist_id):
    res = add_song_to_user_playlist(song_id, playlist_id)

    user_name = request.user
    user_id = get_user_id(user_name)

    song_name = get_song_name(song_id)
    playlists = get_user_playlists(user_id)

    context = {
        'user_playlists': dict(playlists),
        'song_id': song_id,
        'song_name': song_name,
        'playlist_already_exists': False
    }

    return render(request, 'home/add_to_playlist.html', context)
    

@login_required
def add_playlist(request, song_id):
    if request.method == 'POST':
        user_name = request.user
        user_id = get_user_id(user_name)

        song_name = get_song_name(song_id)

        playlist_name = request.POST.get('playlist_name')
        added_playlist_id = add_playlist_for_user(user_id, playlist_name) 

        if added_playlist_id == None:
            playlists = get_user_playlists(user_id)

            context = {
                'user_playlists': dict(playlists),
                'song_id': song_id,
                'playlist_already_exists': True,
                'song_name': song_name
            }

            return render(request, 'home/add_to_playlist.html', context)

        added_playlist_song = add_song_to_user_playlist( song_id, added_playlist_id)

        playlists = get_user_playlists(user_id)

        context = {
                'user_playlists': dict(playlists),
                'song_id': song_id,
                'playlist_already_exists': False
            }
        
    return render(request, 'home/add_to_playlist.html', context)

@login_required
def delete_playlist(request, song_id, playlist_id):

    user_name = request.user
    user_id = get_user_id(user_name)

    song_name = get_song_name(song_id)

    delete_this_playlist(playlist_id)
    playlists = get_user_playlists(user_id)

    context = {
            'user_playlists': dict(playlists),
            'song_id': song_id,
            'playlist_already_exists': False,
            'song_name': song_name
        }
    
    return render(request, 'home/add_to_playlist.html', context)


# Helper functions 

def get_song_history(user_id):

    song_history = executeSQL(f"""select
	distinct s.song_name,
	s.id,
	s.song_genre, 
	s.artist,
	s.album_name,
	s.duration_ms                   
    from song_history sh
	left outer join song s on sh.song_id = s.id
    where
	sh.user_id = '{user_id}'
    limit 10""")
    
    return song_history    

def get_song_recommendations(user_id):
    song_recommendations = executeSQL(f"""select
        distinct s.song_name,
        s.id,
        s.song_genre, 
        s.artist,
        s.album_name,
        s.duration_ms
    from
        recommendation r
    left outer join song s on
        r.song_id = s.id
    where
        user_id = '{user_id}'""")
    
    return song_recommendations

def get_song_list_for_search():
    song_list = executeSQL("""select
	distinct song_name,
	    id
    from
	    song s""")
    return song_list

def get_user_id(user_name):
    user_ids = executeSQL(f"""select
        id
    from
        `user` u
    where
	name = '{user_name}'""")

    try:
        user_id = user_ids[0]["id"]
    except:
        return None
    
    return user_id



def get_searched_song(song_name):
    searched_song = executeSQL(f"""select
        *
    from
        `song` s
    where
	s.song_name = '{song_name}'""")

    return searched_song[0]
    

def add_song_to_history(user_id, song_id):

    id = utility.encoder_22_characters(song_id) 

    print("user_id", user_id, "song_id", id)

    sql = f"insert into song_history (id, user_id, song_id, listened_timestamp) VALUES ('{id}', '{user_id}', '{song_id}', '{datetime.datetime.now()}')"
    res = only_executeSQL(sql)

    return res


def get_popular_songs():
    popular_songs = executeSQL("""select * from song s 
    order by popularity  desc 
    limit 10
    """)

    return popular_songs


def get_trending_songs():
    trending_songs = executeSQL("""
        select
        s.*
    from
        song_history sh
    left outer join
        song s on s.id = sh.song_id 
    group by song_id 
    order by count(1) desc
    limit 10
        """)

    return trending_songs


def get_user_playlists(user_id):
    user_playlists = executeSQL(f"""
    select p.name,
    p.id as playlist_id,
	p.created_by_user,
	ps.inserted_timestamp,
	s.*
    from playlist p 
    left outer join playlist_song ps on p.id = ps.playlist_id 
    left outer join song s on s.id = ps.song_id 
    where created_by_user = '{user_id}'
    order by p.name, ps.inserted_timestamp desc
    """)

    formatted_playlist = defaultdict(lambda : list())

    for ups in user_playlists:
        p_id = ups["playlist_id"]
        p_name = ups["name"]

        formatted_playlist[(p_id, p_name)].append(ups)

    return formatted_playlist


def add_song_to_user_playlist(song_id, playlist_id):
    sql = f"insert into playlist_song (song_id, playlist_id, inserted_timestamp) VALUES ('{song_id}', '{playlist_id}', '{datetime.datetime.now()}')"
    res = only_executeSQL(sql)

    return res


def add_playlist_for_user(user_id, playlist_name):
    id = utility.encoder_22_characters(playlist_name)

    sql = f"select name from playlist where name = '{playlist_name}' and created_by_user='{user_id}'"
    playlists = executeSQL(sql)

    if len(playlists) != 0:
        return None 

    sql = f"insert into playlist (id, created_by_user, name) VALUES ('{id}', '{user_id}', '{playlist_name}')"
    inserted_playlist = only_executeSQL(sql)

    return id

def get_song_name(song_id):
    song_name = executeSQL(f"select song_name from song where id = '{song_id}'")
    return song_name[0]["song_name"]

def delete_this_playlist(playlist_id):
    res = only_executeSQL(f"delete from playlist where id='{playlist_id}'")
    return res

def get_similar_curated_playlists(user_id):

    print("Called")

    similar_curated_playlist = executeSQL(f"""select rec.*  from (
    select
        playlist_no,
        sum(cosine_sim) as similarity
    from
        (
        select
            rec.playlist_no,
            sh.user_id,
            round((a.popularity * rec.popularity + a.danceability * rec.danceability + a.energy * rec.energy + a.loudness * rec.loudness + a.mode * rec.mode + a.speechiness * rec.speechiness + a.acousticness * rec.acousticness + a.instrumentalness * rec.instrumentalness + a.liveness * rec.liveness + a.valence * rec.valence + a.tempo * rec.tempo)/ (sqrt(power(truncate(a.popularity, 2), 2) + power(truncate(a.danceability, 2), 2) + power(truncate(a.energy, 2), 2) + power(truncate(a.loudness, 2), 2) + power(truncate(a.mode, 2), 2) + power(truncate(a.speechiness, 2), 2) + power(truncate(a.acousticness, 2), 2) + power(truncate(a.instrumentalness, 2), 2) + power(truncate(a.liveness, 2), 2) + power(truncate(a.valence, 2), 2) + power(truncate(a.tempo, 2), 2)) * sqrt(power(truncate(rec.popularity, 2), 2) + power(truncate(rec.danceability, 2), 2) + power(truncate(rec.energy, 2), 2) + power(truncate(rec.loudness, 2), 2) + power(truncate(rec.mode, 2), 2) + power(truncate(rec.speechiness, 2), 2) + power(truncate(rec.acousticness, 2), 2) + power(truncate(rec.instrumentalness, 2), 2) + power(truncate(rec.liveness, 2), 2) + power(truncate(rec.valence, 2), 2) + power(truncate(rec.tempo, 2), 2))), 2) cosine_sim
        from
            song_history sh
        left outer join song a on
            sh.song_id = a.id
        left outer join curated_playlists rec on
            a.song_genre = rec.song_genre
        where
            sh.user_id = '{user_id}') as a
    group by
        playlist_no
    order by
        similarity desc
    limit 3) top_3 left outer join curated_playlists rec on top_3.playlist_no = rec.playlist_no
    """)

    curated_playlist_formatted = defaultdict(lambda :list())

    for playlist in similar_curated_playlist:
        curated_playlist_formatted[playlist["playlist_no"]].append(playlist)

    print(similar_curated_playlist)
    print(curated_playlist_formatted)

    return curated_playlist_formatted