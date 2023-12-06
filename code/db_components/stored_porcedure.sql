CREATE DEFINER=`root`@`%` PROCEDURE `playground`.`generate_recommendations_adv`(in inp_user_id varchar(26))
begin
	
	declare randomness int default 2;
	declare fixed int default 8;
	declare user_activity int default 0;

	select count(1)
	from song_history sh 
	where user_id = inp_user_id
	into user_activity;

	if user_activity < 10 then
		set randomness = 6;
		set fixed = 4;
	end if;
	
	-- DELETE old recommendations from the recommendation table
	
	delete from playground.recommendation
	where user_id = inp_user_id;

	-- INSERT new recommendations to the recommendation table
	insert into recommendation (user_id,
		song_id,
		recommended_timestamp)
	with tmp 
	as (
	select
		user_id,
		song_id,
		cosine_sim,
		popularity,
		avg_rating,
		current_timestamp() as recommended_timestamp 
	from
		(
		select
			distinct a.id as song_id,
			rev.avg_rating,
			a.popularity,
			rec.user_id,
			round((a.popularity * rec.popularity + a.danceability * rec.danceability + a.energy * rec.energy + a.loudness * rec.loudness + a.mode * rec.mode + a.speechiness * rec.speechiness + a.acousticness * rec.acousticness + a.instrumentalness * rec.instrumentalness + a.liveness * rec.liveness + a.valence * rec.valence + a.tempo * rec.tempo)/ (sqrt(power(truncate(a.popularity, 2), 2) + power(truncate(a.danceability, 2), 2) + power(truncate(a.energy, 2), 2) + power(truncate(a.loudness, 2), 2) + power(truncate(a.mode, 2), 2) + power(truncate(a.speechiness, 2), 2) + power(truncate(a.acousticness, 2), 2) + power(truncate(a.instrumentalness, 2), 2) + power(truncate(a.liveness, 2), 2) + power(truncate(a.valence, 2), 2) + power(truncate(a.tempo, 2), 2)) * sqrt(power(truncate(rec.popularity, 2), 2) + power(truncate(rec.danceability, 2), 2) + power(truncate(rec.energy, 2), 2) + power(truncate(rec.loudness, 2), 2) + power(truncate(rec.mode, 2), 2) + power(truncate(rec.speechiness, 2), 2) + power(truncate(rec.acousticness, 2), 2) + power(truncate(rec.instrumentalness, 2), 2) + power(truncate(rec.liveness, 2), 2) + power(truncate(rec.valence, 2), 2) + power(truncate(rec.tempo, 2), 2))), 2) cosine_sim
		from
			song a
		join
	     (
			select
				s.*,
				r.user_id
			from
				song s
			join
	        (
				select
					distinct song_id,
					user_id,
					listened_timestamp
				from
					song_history
				where
					user_id = inp_user_id
			order by
				listened_timestamp) as r on
			s.id = r.song_id
		limit 3) as rec on
		a.song_genre = rec.song_genre
	left join 
	(
		select
			r.song_id,
			avg(r.song_rating) as avg_rating
		from
			review r
		group by
			r.song_id
	) as rev on
		rev.song_id = a.id
	where
		a.id not in
	   (
		select
			id
		from
			song
		where
			id in
	        (
			select
				distinct song_id
			from
				song_history
			where
				user_id = inp_user_id))) as a
	order by
		cosine_sim desc,
		popularity desc,
		avg_rating desc
	limit 100)
	select a.user_id,
	a.song_id,
	a.recommended_timestamp
	from ((select 
		user_id,
		song_id,
		recommended_timestamp
	from tmp 
	order by cosine_sim desc,
		popularity desc,
		avg_rating desc
	limit fixed)
	union
	(select 
		user_id,
		song_id,
		recommended_timestamp
	from tmp
	order by rand()
	limit randomness)) as a;

end