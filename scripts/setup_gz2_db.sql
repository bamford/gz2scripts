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
--GRANT ALL ON reduction_pl_de.* TO 'steven'@'%';
--GRANT ALL ON reduction_pl_de2.* TO 'steven'@'%';
--GRANT ALL ON reduction_pl_de3.* TO 'steven'@'%';
GRANT FILE ON *.* TO 'steven'@'%';

CREATE USER 'steven'@'localhost' IDENTIFIED BY 'hRs3mo2';
GRANT SELECT ON juggernaut_production.* TO 'steven'@'localhost';
GRANT ALL ON reduction.* TO 'steven'@'localhost';
GRANT ALL ON reduction2.* TO 'steven'@'localhost';
GRANT ALL ON reduction3.* TO 'steven'@'localhost';
--GRANT ALL ON reduction_pl_de.* TO 'steven'@'localhost';
--GRANT ALL ON reduction_pl_de2.* TO 'steven'@'localhost';
--GRANT ALL ON reduction_pl_de3.* TO 'steven'@'localhost';
GRANT FILE ON *.* TO 'steven'@'localhost';

GRANT ALL ON *.* TO 'zoodb'@'%';
GRANT ALL ON *.* TO 'zoodb'@'localhost';

create database reduction;
create database reduction2;
create database reduction3;
--create database reduction_pl_de;
--create database reduction_pl_de2;
--create database reduction_pl_de3;

