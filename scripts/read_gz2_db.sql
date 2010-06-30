-- ssh -i GZ.pem root@$EC2URL
-- mysql -A -u zoodb -p juggernaut_production
-- OR
-- mysql5 -A -u zoodb -p -h $EC2URL juggernaut_production

-- the following grants only possible when connecting from other host
-- as zoodb@localhost does not have sufficient permissions!
CREATE USER 'steven'@'%' IDENTIFIED BY 'hRs3mo2';
GRANT SELECT ON juggernaut_production.* TO 'steven'@'%';
GRANT ALL ON reduction.* TO 'steven'@'%';
GRANT ALL ON reduction2.* TO 'steven'@'%';
GRANT ALL ON reduction3.* TO 'steven'@'%';
GRANT ALL ON reduction_pl_de.* TO 'steven'@'%';
GRANT ALL ON reduction_pl_de2.* TO 'steven'@'%';
GRANT ALL ON reduction_pl_de3.* TO 'steven'@'%';
GRANT FILE ON *.* TO 'steven'@'%';

CREATE USER 'steven'@'localhost' IDENTIFIED BY 'hRs3mo2';
GRANT SELECT ON juggernaut_production.* TO 'steven'@'localhost';
GRANT ALL ON reduction.* TO 'steven'@'localhost';
GRANT ALL ON reduction2.* TO 'steven'@'localhost';
GRANT ALL ON reduction3.* TO 'steven'@'localhost';
GRANT ALL ON reduction_pl_de.* TO 'steven'@'localhost';
GRANT ALL ON reduction_pl_de2.* TO 'steven'@'localhost';
GRANT ALL ON reduction_pl_de3.* TO 'steven'@'localhost';
GRANT FILE ON *.* TO 'steven'@'localhost';

GRANT ALL ON *.* TO 'zoodb'@'%';
GRANT ALL ON *.* TO 'zoodb'@'localhost';

create database reduction;
create database reduction2;
create database reduction3;
create database reduction_pl_de;
create database reduction_pl_de2;
create database reduction_pl_de3;
quit;

-- mysql -A -u steven --password=hRs3mo2 reduction
-- OR
-- mysql5 -A -u steven --password=hRs3mo2 -h $EC2URL reduction

use reduction;
-- use reduction_pl_de;

-- initial user weights
create table `user_weights` (
  `user_id` int(11) primary key,
  `weight` float(3,2) default null
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
  `weight` float(3,2) default null
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
  `weight` float(3,2) default null
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
  `weight` float(3,2) default null,
  `fraction` float(3,2) default null,
  `weighted_fraction` float(3,2) default null,
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
from click_fractions
left join juggernaut_production.assets on (assets.id = click_fractions.asset_id)
where answer_id is not null;

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

SELECT * INTO OUTFILE '/vol/lib/mysql/wars_battles.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction.wars_battles;

SELECT * INTO OUTFILE '/vol/lib/mysql/clicks.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction.clicks;

SELECT * INTO OUTFILE '/vol/lib/mysql/gz2results_pl_de.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction_pl_de3.gz2results;

SELECT * INTO OUTFILE '/vol/lib/mysql/click_fraction_consistency_vs_en_cumhisto1_pl_de.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction_pl_de.click_fraction_consistency_vs_en_cumhisto;

SELECT * INTO OUTFILE '/vol/lib/mysql/user_consistency_vs_en_cumhisto1_pl_de.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction_pl_de.user_consistency_vs_en_cumhisto;

SELECT * INTO OUTFILE '/vol/lib/mysql/click_fraction_consistency_vs_en_cumhisto2_pl_de.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction_pl_de2.click_fraction_consistency_vs_en_cumhisto;

SELECT * INTO OUTFILE '/vol/lib/mysql/user_consistency_vs_en_cumhisto2_pl_de.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction_pl_de2.user_consistency_vs_en_cumhisto;

SELECT * INTO OUTFILE '/vol/lib/mysql/click_fraction_consistency_vs_en_cumhisto3_pl_de.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction_pl_de3.click_fraction_consistency_vs_en_cumhisto;

SELECT * INTO OUTFILE '/vol/lib/mysql/user_consistency_vs_en_cumhisto3_pl_de.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction_pl_de3.user_consistency_vs_en_cumhisto;

SELECT * INTO OUTFILE '/vol/lib/mysql/wars_battles_pl_de.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction_pl_de.wars_battles;

SELECT * INTO OUTFILE '/vol/lib/mysql/clicks_pl_de.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
LINES TERMINATED BY '\n'
FROM reduction_pl_de.clicks;
