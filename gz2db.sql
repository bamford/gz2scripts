-- Table containing bin information
CREATE TABLE gz2sample
(
objid BIGINT PRIMARY KEY,
ra FLOAT NOT NULL,
dec FLOAT NOT NULL,
size FLOAT NOT NULL,
redshift FLOAT NULL,
region SMALLINT NOT NULL,
zbin SMALLINT NULL,
wvtbin SMALLINT NULL,
classcount SMALLINT NOT NULL DEFAULT 0
compcount SMALLINT NOT NULL DEFAULT 0
)
GO

BULK INSERT gz2sample
FROM 'gz2sample_db.csv' 
WITH ( FIELDTERMINATOR = ',' )
GO

-- Table containing region information
CREATE TABLE gz2regions
(
regionid SMALLINT PRIMARY KEY,
weight FLOAT NOT NULL DEFAULT 0
)
GO

BULK INSERT gz2sample
FROM 'gz2regions.csv' 
WITH ( FIELDTERMINATOR = ',' )
GO

-- Table for comparison results
CREATE TABLE comparison_results
(
userid INT NOT NULL,
datetime DATETIME NOT NULL,
objid BIGINT NOT NULL,
compid BIGINT NOT NULL,
res SMALLINT NOT NULL,
)
GO

-- Function to get the id of another galaxy in the same comparison bin
-- parameter is objid of main galaxy, returns objid of comparison galaxy
CREATE FUNCTION comparison_id
(@objid BIGINT )
RETURNS BIGINT
AS
BEGIN

declare @compid BIGINT
declare @zbin SMALLINT
declare @wvtbin SMALLINT
declare @region SMALLINT

SET @compid = 0

SELECT @zbin = zbin, @wvtbin = wvtbin
FROM gz2sample
WHERE objid=@objid

SELECT @region = region
FROM gz2regions
WHERE region = 1
-- *** SHOULD BE RANDOMLY SELECTED REGION WITH
-- *** WEIGHTINGS GIVEN IN TABLE gz2regions BUT ONLY
-- *** STARTING WITH ONE REGION SO CAN UPDATE LATER

IF (@wvtbin IS NOT NULL) BEGIN
   SELECT TOP 1 @compid = objid
   FROM  gz2sample
   WHERE zbin = @zbin AND wvtbin = @wvtbin AND objid != @objid
   AND region = @region
   ORDER BY compcount, RAND()
END

RETURN @compid
END
GO

-- Function to get the id of a galaxy to classify
CREATE FUNCTION classify_id
RETURNS BIGINT
AS
BEGIN

declare @classid BIGINT
declare @region SMALLINT

SELECT @region = region
FROM gz2regions
WHERE ***RANDOMLY SELECTED REGION WITH WEIGHTINGS GIVEN IN TABLE gz2regions***

SELECT TOP 1 @classid = objid
FROM  gz2sample TABLESAMPLE(5000 ROWS)
WHERE region = @region
ORDER BY classcount, RAND()

RETURN @classid
END
GO

-- Procedure to store result of a comparison operation
-- parameters are: id of user, id of main galaxy,
-- id of comparison galaxy, and the result:
-- 0 = main galaxy has more prominent feature
-- 1 = comparison galaxy has more prominent feature
CREATE PROCEDURE comparison_result
(@userid INT, @objid BIGINT, @compid BIGINT, @res SMALLINT )
AS
BEGIN

INSERT INTO comparison_results
VALUES (@userid, CURRENT_TIMESTAMP, @objid, @compid, @res)

UPDATE gz2sample
SET compcount = compcount + 1
WHERE objid = @objid OR objid = @compid

END
GO