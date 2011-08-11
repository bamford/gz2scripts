DELIMITER //
-- *****************************************************************************
drop procedure if exists reduce_iter;
create procedure reduce_iter ()
begin

-- note that the GZ2 database contains three clicks with answer_id = null
-- these are removed by this query

drop table if exists `click_counts`;
create table `click_counts` (
  `asset_id` int(7),
  `task_id` int(3),
  `answer_id` int(3),
  `count` int(5),
  `weight` float(8,3),
  index (asset_id),
  index (task_id)
);
insert into click_counts
select asset_id as asset_id, task_id as task_id, answer_id as answer_id,
       count(*) as count, sum(user_weights.weight) as weight
from reduction.clean_clicks as C
join user_weights on (user_weights.user_id = C.user_id)
where C.answer_id is not null
group by asset_id, task_id, answer_id
with rollup;

drop table if exists `click_totals`;
create table `click_totals` (
  `asset_id` int(7) not null,
  `task_id` int(3) not null,
  `answer_id` int(3) default null,
  `count` int(5) default null,
  `weight` float(8,3) default null,
  index (asset_id),
  index (task_id)
);
insert into click_totals
select *
from click_counts
where answer_id is null and task_id is not null;

drop table if exists `click_fractions`;
create table `click_fractions` (
  `asset_id` int(7) not null,
  `task_id` int(3) not null,
  `answer_id` int(3) default null,
  `count` int(5) default null,
  `weight` float(8,3) default null,
  `fraction` float(4,3) default null,
  `weighted_fraction` float(4,3) default null,
  index (asset_id),
  index (task_id)
);
insert into click_fractions
select C.*,
       (case when T.count < 1 then 0 else C.count / T.count end) as fraction,
       (case when T.weight < 1 then 0 else C.weight / T.weight end) as weighted_fraction
from click_counts as C, click_totals as T
where C.answer_id is not null
and C.task_id = T.task_id
and C.asset_id = T.asset_id;

drop table if exists `click_consistency`;
create table `click_consistency` (
  `annotation_id` int(11) primary key,
  `asset_id` int(7) not null,
  `task_id` int(3) not null,
  `user_id` int(7) not null,
  `consistency` float(4,3) default null,
  index (asset_id),
  index (task_id),
  index (user_id)
);
insert into click_consistency
select C.annotation_id, C.asset_id, C.task_id, MIN(C.user_id) as user_id,
       AVG(2*(C.answer_id = F.answer_id)*(weighted_fraction - 0.5) + 1.0 - weighted_fraction) as consistency
from reduction.clean_clicks as C,
click_fractions as F
where C.task_id = F.task_id
and C.asset_id = F.asset_id
group by C.annotation_id;

drop table if exists `click_fraction_consistency`;
create table `click_fraction_consistency` (
  `asset_id` int(7) not null,
  `task_id` int(3) not null,
  `average` float(4,3) default null,
  `stddev` float(4,3) default null,
  index (asset_id),
  index (task_id)
);
insert into click_fraction_consistency
select asset_id, task_id, avg(consistency) as average, stddev(consistency) as stddev
from click_consistency
group by asset_id, task_id;

drop table if exists `user_consistency`;
create table `user_consistency` (
  `user_id` int(7) primary key,
  `average` float(4,3),
  `stddev` float(4,3),
  `num_classifications` int(7)
);
insert into user_consistency
select user_id, avg(consistency) as average, stddev(consistency) as stddev,
       count(*) as num_classifications
from click_consistency
group by user_id;

drop table if exists click_fraction_consistency_histo;
create table click_fraction_consistency_histo
select round(average, 2) as rounded_consistency, count(*) as count
from click_fraction_consistency group by rounded_consistency;

drop table if exists click_fraction_consistency_cumhisto;
create table click_fraction_consistency_cumhisto
select b.*, sum(a.count) as cumcount, sum(a.count)/total.count as cumfrac
from click_fraction_consistency_histo as a, click_fraction_consistency_histo as b,
     (select sum(count) as count from click_fraction_consistency_histo) as total
where a.rounded_consistency <= b.rounded_consistency
group by b.rounded_consistency;

drop table if exists user_consistency_histo;
create table user_consistency_histo
select round(average, 2) as rounded_consistency,
       count(*) as count, avg(num_classifications) as avg_num_classifications
from user_consistency group by rounded_consistency;

drop table if exists user_consistency_cumhisto;
create table user_consistency_cumhisto
select b.*, sum(a.count) as cumcount, sum(a.count)/total.count as cumfrac
from user_consistency_histo as a, user_consistency_histo as b,
     (select sum(count) as count from user_consistency_histo) as total
where a.rounded_consistency <= b.rounded_consistency
group by b.rounded_consistency;

end//
-- *****************************************************************************
DELIMITER ;
