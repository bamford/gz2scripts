-- mysql -A -u steven --password=hRs3mo2 reduction
-- OR
-- mysql5 -A -u steven --password=hRs3mo2 -h $EC2URL reduction

use reduction;
-- use reduction_pl_de;

-- initial user weights
drop table if exists user_weights;
create table `user_weights` (
  `user_id` int(11) primary key,
  `weight` float(4,3) default null
);
insert into user_weights
select id as user_id, 1.0 as weight
from juggernaut_production.users;
-- full takes 5 sec

-- do single stage reduction

source /vol/scripts/reduce_initial_gz2_db.sql
source /vol/scripts/reduce_iter_gz2_db.sql
-- source /vol/scripts/reduce_initial_gz2_db_pl_de.sql
-- source /vol/scripts/reduce_iter_gz2_db_pl_de.sql

call reduce_initial();
-- call reduce_initial_pl_de();

call reduce_iter();
-- call reduce_iter_pl_de();

-- can now iterate, down-weighting inconsistent users

use reduction2;
-- use reduction_pl_de2;
source scripts/reduce_iter_gz2_db.sql
-- source /vol/scripts/reduce_iter_gz2_db_pl_de.sql

create table `user_weights` (
  `user_id` int(11) primary key,
  `weight` float(4,3) default null
);
insert into user_weights
select user_id, least(1.0, power((average/0.6), 8.5)) as weight
from reduction.user_consistency;
-- from reduction_pl_de.user_consistency_vs_en;

call reduce_iter();
-- call reduce_iter_pl_de();


use reduction3;
source scripts/reduce_iter_gz2_db.sql

create table `user_weights` (
  `user_id` int(11) primary key,
  `weight` float(4,3) default null
);
insert into user_weights
select user_id, least(1.0, power((average/0.6), 8.5)) as weight
from reduction2.user_consistency;

call reduce_iter();

-- potentially could quite easily include a timescale,
-- (but processing would take much longer)
-- i.e. instead of down-weighting bad users, down-weight bad user-weeks!

drop table if exists gz2results;
create table `gz2results` (
  `name` text default null,
  `sample` varchar(16) default null,
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
insert into gz2results
select assets.name,
CASE (4*stripe82_coadd + 2*stripe82 + extra_original)
WHEN 0 THEN "original"
WHEN 1 THEN "extra"
WHEN 2 THEN "stripe82"
WHEN 4 THEN "stripe82_coadd"
ELSE "all" END as sample,
click_fractions.*
from reduction3.click_fractions
left join juggernaut_production.assets on (assets.id = click_fractions.asset_id)
where answer_id is not null;

-- generate data on number of classifications as function of time

drop table if exists count_classifications_per_day_tmp;
create table count_classifications_per_day_tmp
select datediff(created_at, '2009-02-16') as day, count(*) as count
from juggernaut_production.classifications
group by day;

drop table if exists count_classifications_per_day;
create table count_classifications_per_day
select b.*, sum(a.count) as cumcount, sum(a.count)/total.count as cumfrac
from count_classifications_per_day_tmp as a, count_classifications_per_day_tmp as b,
     (select sum(count) as count from count_classifications_per_day_tmp) as total
where a.day <= b.day
group by b.day;

drop table if exists count_classifications_per_day_tmp;

-- generate data on number of distinct users each week

drop table if exists count_users_per_week;
create table count_users_per_week
select week, count(*) as count
from 
( select yearweek(created_at) as week, user_id
  from juggernaut_production.classifications
  group by week, user_id ) as X
group by week;

-- generate data on growth in number of users as function of time

drop table if exists count_user_growth_per_day_tmp;
create table count_user_growth_per_day_tmp
select day, count(*) as count
from 
( select min(datediff(created_at, '2009-02-16')) as day, user_id
  from juggernaut_production.classifications
  group by user_id ) as X
group by day;

drop table if exists count_user_growth_per_day;
create table count_user_growth_per_day
select b.*, sum(a.count) as cumcount, sum(a.count)/total.count as cumfrac
from count_user_growth_per_day_tmp as a, count_user_growth_per_day_tmp as b,
     (select sum(count) as count from count_user_growth_per_day_tmp) as total
where a.day <= b.day
group by b.day;

drop table if exists count_user_growth_per_day_tmp;

-- generate data on loss of users as function of time

drop table if exists count_user_loss_per_day_tmp;
create table count_user_loss_per_day_tmp
select day, count(*) as count
from 
( select max(datediff(created_at, '2009-02-16')) as day, user_id
  from juggernaut_production.classifications
  group by user_id ) as X
group by day;

drop table if exists count_user_loss_per_day;
create table count_user_loss_per_day
select b.*, sum(a.count) as cumcount, sum(a.count)/total.count as cumfrac
from count_user_loss_per_day_tmp as a, count_user_loss_per_day_tmp as b,
     (select sum(count) as count from count_user_loss_per_day_tmp) as total
where a.day <= b.day
group by b.day;

drop table if exists count_user_loss_per_day_tmp;

-- generate data on classifications per user

drop table if exists count_classifications_per_user_tmp;
create table count_classifications_per_user_tmp
select user_id, count(*) as count
from juggernaut_production.classifications
group by user_id;

drop table if exists count_classifications_per_user_tmp2;
create table count_classifications_per_user_tmp2
select count as nclassifications, count(*) as nusers, 
       count(*)/totalnusers as fracusers,
       count*count(*)/totalnclassifications as fracclassifications
from count_classifications_per_user_tmp as a,
     (select count(*) as totalnusers,
     	     sum(count) as totalnclassifications
     from count_classifications_per_user_tmp) as total
group by nclassifications;

drop table if exists count_classifications_per_user;
create table count_classifications_per_user
select b.*, sum(a.nusers) as cumnusers,
       sum(a.nusers)/totalnusers as cumfracusers,
       sum(a.nusers*a.nclassifications)/totalnclassifications as cumfracclassifications
from count_classifications_per_user_tmp2 as a, count_classifications_per_user_tmp2 as b,
     (select sum(nusers) as totalnusers,
     	     sum(nclassifications*nusers) as totalnclassifications
     from count_classifications_per_user_tmp2) as total
where a.nclassifications <= b.nclassifications
group by b.nclassifications;

drop table count_classifications_per_user_tmp,
     	   count_classifications_per_user_tmp2;

-- generate data on repeat classifications by same user
drop table if exists repeat_classifications;
create table repeat_classifications
select * from
       (select user_id, asset_id, count(*) as count
       from reduction.clean_clicks
       where task_id = 1
       group by user_id, asset_id) as X
where count > 1;

drop table if exists assets_with_repeat_classifications;
create table assets_with_repeat_classifications
select asset_id, sum(count-1) as count from repeat_classifications
group by asset_id;

drop table if exists users_with_repeat_classifications;
create table users_with_repeat_classifications
select user_id, sum(count-1) as count from repeat_classifications
group by user_id;

-- output to csv

SELECT * INTO OUTFILE '/vol/lib/mysql/gz2results.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction3.gz2results;

SELECT * INTO OUTFILE '/vol/lib/mysql/tasks.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM juggernaut_production.tasks;

SELECT * INTO OUTFILE '/vol/lib/mysql/answers.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM juggernaut_production.answers;

SELECT * INTO OUTFILE '/vol/lib/mysql/click_fraction_consistency_cumhisto1.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction.click_fraction_consistency_cumhisto;

SELECT * INTO OUTFILE '/vol/lib/mysql/user_consistency_cumhisto1.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction.user_consistency_cumhisto;

SELECT * INTO OUTFILE '/vol/lib/mysql/click_fraction_consistency_cumhisto2.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction2.click_fraction_consistency_cumhisto;

SELECT * INTO OUTFILE '/vol/lib/mysql/user_consistency_cumhisto2.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction2.user_consistency_cumhisto;

SELECT * INTO OUTFILE '/vol/lib/mysql/click_fraction_consistency_cumhisto3.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction3.click_fraction_consistency_cumhisto;

SELECT * INTO OUTFILE '/vol/lib/mysql/user_consistency_cumhisto3.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction3.user_consistency_cumhisto;

-- SELECT * INTO OUTFILE '/vol/lib/mysql/wars_battles.csv'
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
-- LINES TERMINATED BY '\n'
-- FROM reduction.wars_battles;

-- SELECT * INTO OUTFILE '/vol/lib/mysql/clicks.csv'
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
-- LINES TERMINATED BY '\n'
-- FROM reduction.clicks;

-- SELECT * INTO OUTFILE '/vol/lib/mysql/gz2results_pl_de.csv'
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
-- LINES TERMINATED BY '\n'
-- FROM reduction_pl_de3.gz2results;

-- SELECT * INTO OUTFILE '/vol/lib/mysql/click_fraction_consistency_vs_en_cumhisto1_pl_de.csv'
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
-- LINES TERMINATED BY '\n'
-- FROM reduction_pl_de.click_fraction_consistency_vs_en_cumhisto;

-- SELECT * INTO OUTFILE '/vol/lib/mysql/user_consistency_vs_en_cumhisto1_pl_de.csv'
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
-- LINES TERMINATED BY '\n'
-- FROM reduction_pl_de.user_consistency_vs_en_cumhisto;

-- SELECT * INTO OUTFILE '/vol/lib/mysql/click_fraction_consistency_vs_en_cumhisto2_pl_de.csv'
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
-- LINES TERMINATED BY '\n'
-- FROM reduction_pl_de2.click_fraction_consistency_vs_en_cumhisto;

-- SELECT * INTO OUTFILE '/vol/lib/mysql/user_consistency_vs_en_cumhisto2_pl_de.csv'
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
-- LINES TERMINATED BY '\n'
-- FROM reduction_pl_de2.user_consistency_vs_en_cumhisto;

-- SELECT * INTO OUTFILE '/vol/lib/mysql/click_fraction_consistency_vs_en_cumhisto3_pl_de.csv'
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
-- LINES TERMINATED BY '\n'
-- FROM reduction_pl_de3.click_fraction_consistency_vs_en_cumhisto;

-- SELECT * INTO OUTFILE '/vol/lib/mysql/user_consistency_vs_en_cumhisto3_pl_de.csv'
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
-- LINES TERMINATED BY '\n'
-- FROM reduction_pl_de3.user_consistency_vs_en_cumhisto;

-- SELECT * INTO OUTFILE '/vol/lib/mysql/wars_battles_pl_de.csv'
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
-- LINES TERMINATED BY '\n'
-- FROM reduction_pl_de.wars_battles;

-- SELECT * INTO OUTFILE '/vol/lib/mysql/clicks_pl_de.csv'
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
-- LINES TERMINATED BY '\n'
-- FROM reduction_pl_de.clicks;

SELECT * INTO OUTFILE '/vol/lib/mysql/count_classifications_per_day.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM count_classifications_per_day;

SELECT * INTO OUTFILE '/vol/lib/mysql/count_users_per_week.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM count_users_per_week;

SELECT * INTO OUTFILE '/vol/lib/mysql/count_user_growth_per_day.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM count_user_growth_per_day;

SELECT * INTO OUTFILE '/vol/lib/mysql/count_user_loss_per_day.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM count_user_loss_per_day;

SELECT * INTO OUTFILE '/vol/lib/mysql/count_classifications_per_user.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM count_classifications_per_user;
