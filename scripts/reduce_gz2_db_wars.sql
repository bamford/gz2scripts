DELIMITER //
-- *****************************************************************************
create procedure reduce_wars ()
begin

-- -- probably already created by reduce
-- -- select classifications to consider
-- create table selected_classifications like juggernaut_production.classifications;
-- insert into selected_classificationsmysql5 -A -u steven -p reduction
-- select *
-- from juggernaut_production.classifications
-- where -- project_id = 1 and 
-- application_identifier = 'Galaxy Zoo 2: en';

-- select relevent (non-wars) annotations for these classifications
create table `wars_classification_annotations` (
  `classification_id` int(11) not null,
  `annotation_id` int(11) primary key,
  `task_id` int(3) default null,
  `value` text default null,
  `user_id` int(7) default null,
  index (classification_id)
) ;
insert into wars_classification_annotations
select annotations.classification_id, annotations.id as annotation_id,
       annotations.task_id, annotations.value,
       selected_classifications.user_id
from selected_classifications
join juggernaut_production.annotations on (selected_classifications.id=annotations.classification_id)
join juggernaut_production.tasks on (tasks.id = annotations.task_id)
where tasks.count is not null;


create table `wars_clicks` (
  `classification_id` int(11) not null,
  `annotation_id` int(11) not null,
  `task_id` int(3) default null,
  `user_id` int(7) default null,
  `winner` int(7) default null,
  `loser` int(7) default null,
  `weight` float(3,2) default null,
  index (classification_id),
  index (task_id)
);
insert into wars_clicks
select distinct wars_classification_annotations.classification_id,
       wars_classification_annotations.annotation_id, wars_classification_annotations.task_id,
       wars_classification_annotations.user_id,
       substring_index(wars_classification_annotations.value, '>', 1) as winner,
       substring_index(wars_classification_annotations.value, '>', -1) as loser,
       weight
from wars_classification_annotations
join juggernaut_production.asset_classifications on (wars_classification_annotations.classification_id = asset_classifications.classification_id)
join user_weights on (user_weights.user_id = wars_classification_annotations.user_id)
where stripe82_coadd = 0;

create table `wars_count_wins` (
  `task_id` int(3),
  `battle_bin` int(7),
  `asset_id` int(7),
  `count` int(9),
  `weight` float(11,2),
  index (asset_id),
  index (task_id)
);
insert into wars_count_wins
select
task_id as task_id,
battle_bin as battle_bin,
winner as asset_id,
count(*) as count,
sum(weight) as weight
from wars_clicks
join juggernaut_production.assets on (winner = assets.id)
group by task_id, battle_bin, asset_id
with rollup;


end//
-- *****************************************************************************
DELIMITER ;
