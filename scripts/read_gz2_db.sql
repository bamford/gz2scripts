-- ssh -i GZ.pem root@$EC2URL
-- mysql -u zoodb -p juggernaut_production
-- OR
-- mysql5 -A -u zoodb -p -h $EC2URL juggernaut_production

CREATE USER 'steven'@'%' IDENTIFIED BY 'hRs3mo2';
GRANT SELECT ON juggernaut_production.* TO 'steven'@'%';
GRANT ALL ON reduction.* TO 'steven'@'%';

-- the following only possible when connecting from other host
-- as zoodb@localhost does not have sufficient permissions!
CREATE USER 'steven'@'localhost' IDENTIFIED BY 'hRs3mo2';
GRANT SELECT ON juggernaut_production.* TO 'steven'@'localhost';
GRANT ALL ON reduction.* TO 'steven'@'localhost';

create database reduction;
quit;

-- mysql5 -A -u steven -p reduction
-- OR
-- mysql5 -A -u steven --password=hRs3mo2 -h $EC2URL reduction

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

source scripts/reduce_gz2_db.sql

call reduce();

-- can now iterate, down-weighting inconsistent users

truncate table user_weights;
insert into user_weights
select user_id, least(1.0, power((average/0.5), 4)) as weight
from user_consistency;

-- potentially could quite easily include a timescale,
-- i.e. instead of completely rejecting users, reject bad user-weeks!

create table `gz2results` (
  `name` text default null,
  `sample` varchar(16) default null,
  `asset_id` int(11) not null,
  `task_id` int(11) not null,
  `answer_id` int(11) default null,
  `count` int(5) default null,
  `fraction` float(3,2) default null,
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
left join juggernaut_production.assets on (assets.id = click_fractions.asset_id);
-- 1M takes ?? min
-- full takes ?? min

