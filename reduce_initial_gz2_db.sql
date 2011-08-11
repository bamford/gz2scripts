DELIMITER //
-- *****************************************************************************
-- For full GZ2 dataset this whole procedure takes about two hours on m2xlarge.

drop procedure if exists reduce_initial;
create procedure reduce_initial ()
begin

-- select classifications to consider
create table selected_classifications like juggernaut_production.classifications;
insert into selected_classifications
select *
from juggernaut_production.classifications;
-- where -- project_id = 1 and 
-- application_identifier = 'Galaxy Zoo 2: en';
-- and created_at between CAST('2009-02-16' AS DATETIME) and CAST('2009-03-16' AS DATETIME)

-- select relevent (non-wars) annotations for these classifications
create table `classification_annotations` (
  `classification_id` int(11) not null,
  `annotation_id` int(11) primary key,
  `task_id` int(3) default null,
  `answer_id` int(3) default null,
  `user_id` int(7) default null,
  index (classification_id)
) ;
insert into classification_annotations
-- create table classification_annotations
select annotations.classification_id, annotations.id as annotation_id,
       annotations.task_id, annotations.answer_id,
       selected_classifications.user_id
from selected_classifications
join juggernaut_production.annotations on (selected_classifications.id=annotations.classification_id)
join juggernaut_production.tasks on (tasks.id = annotations.task_id)
where tasks.count is null;

create table `clicks` (
  `asset_id` int(7) not null,
  `classification_id` int(11) not null,
  `annotation_id` int(11) primary key,
  `task_id` int(3) default null,
  `answer_id` int(3) default null,
  `user_id` int(7) default null,
  index (asset_id),
  index (classification_id),
  index (task_id)
);
insert into clicks
select asset_classifications.asset_id, classification_annotations.*
from classification_annotations
join juggernaut_production.asset_classifications on (classification_annotations.classification_id = asset_classifications.classification_id);

drop table last_clicks;
create table `last_clicks` as
select user_id, asset_id, max(classification_id) as classification_id
from clicks
group by user_id, asset_id;

drop table clean_clicks;
create table `clean_clicks` like `clicks`;
insert into clean_clicks
select clicks.*
from last_clicks, clicks
where clicks.classification_id = last_clicks.classification_id;

end//
-- *****************************************************************************
DELIMITER ;
