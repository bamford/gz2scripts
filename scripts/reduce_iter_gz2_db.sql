DELIMITER //
-- *****************************************************************************
create procedure reduce ()
begin

-- select classifications to consider
create table selected_classifications like juggernaut_production.classifications;
insert into selected_classifications
select *
from juggernaut_production.classifications
where -- project_id = 1 and 
application_identifier = 'Galaxy Zoo 2: en';
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

create table `clicks_original` (
  `asset_id` int(7) not null,
  `classification_id` int(11) not null,
  `annotation_id` int(11) primary key,
  `task_id` int(3) default null,
  `answer_id` int(3) default null,
  `user_id` int(7) default null,
  `weight` float(3,2) default null,
  index (asset_id),
  index (classification_id),
  index (task_id)
);
insert into clicks_original
select asset_classifications.asset_id, classification_annotations.*, weight
from classification_annotations
join juggernaut_production.asset_classifications on (classification_annotations.classification_id = asset_classifications.classification_id)
join user_weights on (user_weights.user_id = classification_annotations.user_id)
where stripe82 = 0 and stripe82_coadd = 0 and extra_original = 0;

create table `clicks_stripe82` (
  `asset_id` int(7) not null,
  `classification_id` int(11) not null,
  `annotation_id` int(11) primary key,
  `task_id` int(3) default null,
  `answer_id` int(3) default null,
  `user_id` int(7) default null,
  `weight` float(3,2) default null,
  index (asset_id),
  index (classification_id),
  index (task_id)
);
insert into clicks_stripe82
select asset_classifications.asset_id, classification_annotations.*, weight
from classification_annotations
join juggernaut_production.asset_classifications on (classification_annotations.classification_id = asset_classifications.classification_id)
join user_weights on (user_weights.user_id = classification_annotations.user_id)
where stripe82 = 1 and stripe82_coadd = 0 and extra_original = 0;

create table `clicks_extra` (
  `asset_id` int(7) not null,
  `classification_id` int(11) not null,
  `annotation_id` int(11) primary key,
  `task_id` int(3) default null,
  `answer_id` int(3) default null,
  `user_id` int(7) default null,
  `weight` float(3,2) default null,
  index (asset_id),
  index (classification_id),
  index (task_id)
);
insert into clicks_extra
select asset_classifications.asset_id, classification_annotations.*, weight
from classification_annotations
join juggernaut_production.asset_classifications on (classification_annotations.classification_id = asset_classifications.classification_id)
join user_weights on (user_weights.user_id = classification_annotations.user_id)
where stripe82 = 0 and stripe82_coadd = 0 and extra_original = 1;

create table `clicks_coadd` (
  `asset_id` int(7) not null,
  `classification_id` int(11) not null,
  `annotation_id` int(11) primary key,
  `task_id` int(3) default null,
  `answer_id` int(3) default null,
  `user_id` int(7) default null,
  `weight` float(3,2) default null,
  index (asset_id),
  index (classification_id),
  index (task_id)
);
insert into clicks_coadd
select asset_classifications.asset_id, classification_annotations.*, weight
from classification_annotations
join juggernaut_production.asset_classifications on (classification_annotations.classification_id = asset_classifications.classification_id)
join user_weights on (user_weights.user_id = classification_annotations.user_id)
where stripe82 = 0 and stripe82_coadd = 1 and extra_original = 0;

create table `click_counts` (
  `asset_id` int(7),
  `task_id` int(3),
  `answer_id` int(3),
  `count` int(5),
  `weight` float(7,2),
  index (asset_id),
  index (task_id)
);
insert into click_counts
select asset_id as asset_id, task_id as task_id, answer_id as answer_id,
       count(*) as count, sum(weight) as weight
from (select * from clicks_original UNION 
      select * from clicks_extra UNION 
      select * from clicks_stripe82 UNION
      select * from clicks_coadd) as X
join user_weights on (user_weights.user_id = X.user_id)
group by asset_id, task_id, answer_id
with rollup;

create table `click_totals` (
  `asset_id` int(7) not null,
  `task_id` int(3) not null,
  `answer_id` int(3) default null,
  `count` int(5) default null,
  `weight` float(7,2) default null,
  index (asset_id),
  index (task_id)
);
insert into click_totals
select *
from click_counts
where answer_id is null and task_id is not null;

create table `click_fractions` (
  `asset_id` int(7) not null,
  `task_id` int(3) not null,
  `answer_id` int(3) default null,
  `count` int(5) default null,
  `weight` float(3,2) default null,
  `fraction` float(3,2) default null,
  `weighted_fraction` float(3,2) default null,
  index (asset_id),
  index (task_id)
);
insert into click_fractions
select C.*,
       (case when T.count < 1 then 0 else C.count / T.count end) as fraction,
       (case when T.weight < 1 then 0 else C.weight / T.weight end) as weighted_fraction
from click_counts as C, click_totals as T
where C.task_id = T.task_id
and C.asset_id = T.asset_id;

create table `click_consistency` (
  `annotation_id` int(11) primary key,
  `asset_id` int(7) not null,
  `task_id` int(3) not null,
  `user_id` int(7) not null,
  `consistency` float(3,2) default null,
  index (asset_id),
  index (task_id),
  index (user_id)
);
insert into click_consistency
select C.annotation_id, C.asset_id, C.task_id, MIN(C.user_id) as user_id,
       AVG(2*(C.answer_id = F.answer_id)*(weighted_fraction - 0.5) + 1.0 - weighted_fraction) as consistency
from clicks as C, click_fractions as F
where C.task_id = F.task_id
and C.asset_id = F.asset_id
group by C.annotation_id;

create table `click_fraction_consistency` (
  `asset_id` int(7) not null,
  `task_id` int(3) not null,
  `average` float(3,2) default null,
  `stddev` float(3,2) default null,
  index (asset_id),
  index (task_id)
);
insert into click_fraction_consistency
select asset_id, task_id, avg(consistency) as average, stddev(consistency) as stddev
from click_consistency
group by asset_id, task_id;

create table `user_consistency` (
  `user_id` int(7) primary key,
  `average` float(3,2),
  `stddev` float(3,2),
  `num_classifications` int(7)
);
insert into user_consistency
select user_id, avg(consistency) as average, stddev(consistency) as stddev, count(*) as num_classifications
from click_consistency
group by user_id;

create table click_fraction_consistency_histo
select average as rounded_consistency, count(*) as count
from click_fraction_consistency group by rounded_consistency;

create table click_fraction_consistency_cumhisto
select b.*, sum(a.count) as cumcount, sum(a.count)/total.count as cumfrac
from click_fraction_consistency_histo as a, click_fraction_consistency_histo as b,
     (select sum(count) as count from click_fraction_consistency_histo) as total
where a.rounded_consistency <= b.rounded_consistency
group by b.rounded_consistency;

create table user_consistency_histo
select average as rounded_consistency, count(*) as count, avg(num_classifications) as avg_num_classifications
from user_consistency group by rounded_consistency;

create table user_consistency_cumhisto
select b.*, sum(a.count) as cumcount, sum(a.count)/total.count as cumfrac
from user_consistency_histo as a, user_consistency_histo as b,
     (select sum(count) as count from user_consistency_histo) as total
where a.rounded_consistency <= b.rounded_consistency
group by b.rounded_consistency;

end//
-- *****************************************************************************
DELIMITER ;
