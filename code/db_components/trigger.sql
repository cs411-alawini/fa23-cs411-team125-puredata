CREATE DEFINER=`root`@`%` TRIGGER `recommend_songs_adv` AFTER INSERT ON `song_history` FOR EACH ROW begin		
		declare most_recent_recommendation_diff integer;
	
		set most_recent_recommendation_diff := (select COALESCE(TIMESTAMPDIFF(minute, max(recommended_timestamp), current_timestamp()), 61)
		from recommendation r 
		where user_id = new.user_id);
	
		if most_recent_recommendation_diff > 60 then
			call generate_recommendations_adv(new.user_id);
       end if;
		
      end