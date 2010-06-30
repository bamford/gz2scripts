
select application_identifier, count(*) as count 
from juggernaut_production.classifications 
group by application_identifier;
----->
-- +------------------------+----------+
-- | application_identifier | count    |
-- +------------------------+----------+
-- | NULL                   |        4 | 
-- | Galaxy Zoo 2: de       |    72129 | 
-- | Galaxy Zoo 2: en       | 15917591 | 
-- | Galaxy Zoo 2: es       |      197 | 
-- | Galaxy Zoo 2: fr       |        6 | 
-- | Galaxy Zoo 2: pl       |   349926 | 
-- | iPhone/iPod Touch v1.0 |      445 | 
-- +------------------------+----------+

