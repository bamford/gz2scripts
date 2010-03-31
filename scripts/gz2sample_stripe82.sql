----------------------------------------------------------------------
-- Create coadd-depth selected sample
----------------------------------------------------------------------

-- get required data from PhotoPrimary
-- reject objects which are flagged as
-- SATURATED, BRIGHT, or (BLENDED and not NODEBLEND)
-- also make any pre-selection cuts
GO -- IN STRIPE82 CONTEXT
SELECT
objID, run, rerun, camcol, field, obj, ra, dec, petroR50_r, petroR90_r,
petroMag_u, petroMag_g, petroMag_r, petroMag_i, petroMag_z,
petroMagErr_u, petroMagErr_g, petroMagErr_r, petroMagErr_i, petroMagErr_z,
psfMag_r, fiberMag_r, deVMag_r, deVMagErr_r, expMag_r, expMagErr_r, fracDeV_r,
(petroMag_r + 2.5*log10(6.283185*power(petroR50_r, 2))) as mu50_r,
extinction_u, extinction_g, extinction_r, extinction_i, extinction_z,
rowc_u, colc_u, rowc_g, colc_g, rowc_r,
colc_r, rowc_i, colc_i, rowc_z, colc_z,
flags_r
INTO gz2_coadd_s82_stage1
FROM stripe82.PhotoPrimary
WHERE run in (106,206) --COADD RUNS
AND petroMag_r < 19.9 --TWO MAGS FAINTER THAN LEGACY
AND (psfMag_r - petroMag_r > 0.15) -- NORMAL S/G SEPARATION
AND ((flags_r & 0x70000000) > 0) --BINNED1 OR BINNED2 OR BINNED4
AND ((flags_r & 0x40000) = 0) --NOT SATURATED

-- calculate cmodel mags
GO -- IN MYDB CONTEXT (having previously defined cmodel functions)
SELECT objid,
dbo.calc_cmodel(deVMag_r, expMag_r, fracDev_r, 1.2e-10) as cmodelMag_r,
dbo.calc_cmodelerr(deVMagErr_r, expMagErr_r, deVMag_r, expMag_r,
    fracDev_r, 1.2e-10) as cmodelMagErr_r
INTO gz2_coadd_s82_stage2
FROM gz2_coadd_s82_stage1

-- perform star-galaxy separation
-- perform magnitude cut 
-- perform surface brightness cut
GO -- IN MYDB CONTEXT
SELECT S1.*, S2.cmodelMag_r, S2.cmodelMagErr_r
INTO gz2_coadd_s82_stage3
FROM gz2_coadd_s82_stage1 as S1, gz2_coadd_s82_stage2 as S2
WHERE (psfMag_r - cmodelMag_r >= 0.24)
AND (petroMag_r <= 19.77) --TWO MAGS FAINTER THAN LEGACY
AND (mu50_r <= 25.0) --TWO MAGS FAINTER THAN LEGACY
AND S1.objid = S2.objid

-- Note Ubercal correction no longer required - dr7 default is ubercal

-- add redshifts to table where available

GO -- IN DR7 CONTEXT
SELECT ra, dec, z, zErr, zConf, specclass
INTO dr7_SpecObj_s82
FROM dr7.SpecObj
WHERE (dec > -1.2585 AND dec < 1.2588)
AND (ra > 309.13 OR ra < 59.77)

GO -- IN DR7 CONTEXT - split as together times out
SELECT G.*, S.z as redshift, S.zErr as redshiftErr, S.specclass
INTO gz2_coadd_s82_stage4_17
FROM (SELECT * FROM mydb.gz2_coadd_s82_stage3 WHERE petroMag_r < 17) AS G
LEFT JOIN mydb.dr7_SpecObj_s82 AS S
ON (dbo.fDistanceEq(S.ra, S.dec, G.ra, G.dec) < 0.02)

GO -- IN DR7 CONTEXT - split as together times out
SELECT G.*, S.z as redshift, S.zErr as redshiftErr, S.specclass
INTO gz2_coadd_s82_stage4_18
FROM (SELECT * FROM mydb.gz2_coadd_s82_stage3 WHERE petroMag_r >= 17 and petroMag_r < 18) AS G
LEFT JOIN mydb.dr7_SpecObj_s82 AS S
ON (dbo.fDistanceEq(S.ra, S.dec, G.ra, G.dec) < 0.02)

GO -- IN DR7 CONTEXT - split as together times out
SELECT G.*, S.z as redshift, S.zErr as redshiftErr, S.specclass
INTO gz2_coadd_s82_stage4_185
FROM (SELECT * FROM mydb.gz2_coadd_s82_stage3 WHERE petroMag_r >= 18 and petroMag_r < 18.5) AS G
LEFT JOIN mydb.dr7_SpecObj_s82 AS S
ON (dbo.fDistanceEq(S.ra, S.dec, G.ra, G.dec) < 0.02)

GO -- IN DR7 CONTEXT - split as together times out
SELECT G.*, S.z as redshift, S.zErr as redshiftErr, S.specclass
INTO gz2_coadd_s82_stage4_190
FROM (SELECT * FROM mydb.gz2_coadd_s82_stage3 WHERE petroMag_r >= 18.5 and petroMag_r < 19.0) AS G
LEFT JOIN mydb.dr7_SpecObj_s82 AS S
ON (dbo.fDistanceEq(S.ra, S.dec, G.ra, G.dec) < 0.02)

GO -- IN DR7 CONTEXT - split as together times out
SELECT G.*, S.z as redshift, S.zErr as redshiftErr, S.specclass
INTO gz2_coadd_s82_stage4_195
FROM (SELECT * FROM mydb.gz2_coadd_s82_stage3 WHERE petroMag_r >= 19.0 and petroMag_r < 19.5) AS G
LEFT JOIN mydb.dr7_SpecObj_s82 AS S
ON (dbo.fDistanceEq(S.ra, S.dec, G.ra, G.dec) < 0.02)

GO -- IN DR7 CONTEXT - split as together times out
SELECT G.*, S.z as redshift, S.zErr as redshiftErr, S.specclass
INTO gz2_coadd_s82_stage4_200
FROM (SELECT * FROM mydb.gz2_coadd_s82_stage3 WHERE petroMag_r >= 19.5 and petroMag_r < 20.0) AS G
LEFT JOIN mydb.dr7_SpecObj_s82 AS S
ON (dbo.fDistanceEq(S.ra, S.dec, G.ra, G.dec) < 0.02)

-- join split tables

GO -- IN MYDB CONTEXT
SELECT * FROM gz2_coadd_s82_stage4_17
INTO gz2_coadd_s82_stage4
UNION
SELECT * FROM gz2_coadd_s82_stage4_18
UNION
SELECT * FROM gz2_coadd_s82_stage4_185
UNION
SELECT * FROM gz2_coadd_s82_stage4_190
UNION
SELECT * FROM gz2_coadd_s82_stage4_195
UNION
SELECT * FROM gz2_coadd_s82_stage4_200

-- excluding duplicates

GO -- IN MYDB CONTEXT
SELECT objid, ROW_NUMBER() OVER(PARTITION BY objid ORDER BY redshiftErr) AS best
INTO gz2_bestspec_s82
FROM gz2_coadd_s82_stage4

GO -- IN MYDB CONTEXT
SELECT G.*
FROM gz2_coadd_s82_stage4 as G, gz2_bestspec_s82 as B
INTO gz2_coadd_s82_stage5
WHERE G.objid = B.objid AND B.best = 1

-- select objects brighter than r = 19 and larger than 3 arcsec
GO
SELECT *
INTO gz2_coadd_s82
FROM gz2_coadd_s82_stage5
WHERE (petroMag_r - extinction_r) <= 17.77
AND petroR90_r >= 3
AND (((redshift > 0.0005) AND (redshift < 0.25)) OR redshift IS NULL)

----------------------------------------------------------------------
-- Create normal-depth selected sample
----------------------------------------------------------------------

-- FOR SOUTHERN SAMPLE
-- Execute queries exactly as in gz2sample.sql, but starting with
-- (F.InLegacy != 1) -- to limit to nonlegacy area
-- AND P.b < -20 -- to limit to Southern regions (away from Galactic plane)
-- at end limiting to 17.77
-- and labelling by southern instead of legacy.
-- Results in gz2_dr7_southern

-- FOR JUST STRIPE 82
-- Execute queries exactly as in gz2sample.sql, but starting with
-- AND (dec > -1.2585 AND dec < 1.2588) AND (ra > 309.13 OR ra < 59.77)
-- at end limiting to 17.77
-- and labelling by s82 instead of legacy.
-- Results in gz2_dr7_s82

-- TO COMBINE LEGACY AND STRIPE 82 NORMAL DEPTH CATALOGUES
SELECT *
INTO gz2sample_finaldr7
FROM (
SELECT objID, run, rerun, camcol, field, obj, ra, dec, petroR50_r, petroR90_r,
petroMag_u, petroMag_g, petroMag_r, petroMag_i, petroMag_z,
petroMagErr_u, petroMagErr_g, petroMagErr_r, petroMagErr_i, petroMagErr_z,
psfMag_r, fiberMag_r, deVMag_r, deVMagErr_r, expMag_r, expMagErr_r, fracDeV_r,
(petroMag_r + 2.5*log10(6.283185*power(petroR50_r, 2))) as mu50_r,
extinction_u, extinction_g, extinction_r, extinction_i, extinction_z,
cmodelMag_r, cmodelMagErr_r, redshift, redshiftErr, specclass
FROM gz2sample_finaldr7_legacy
UNION
SELECT objID, run, rerun, camcol, field, obj, ra, dec, petroR50_r, petroR90_r,
petroMag_u, petroMag_g, petroMag_r, petroMag_i, petroMag_z,
petroMagErr_u, petroMagErr_g, petroMagErr_r, petroMagErr_i, petroMagErr_z,
psfMag_r, fiberMag_r, deVMag_r, deVMagErr_r, expMag_r, expMagErr_r, fracDeV_r,
(petroMag_r + 2.5*log10(6.283185*power(petroR50_r, 2))) as mu50_r,
extinction_u, extinction_g, extinction_r, extinction_i, extinction_z,
cmodelMag_r, cmodelMagErr_r, redshift, redshiftErr, specclass
FROM gz2_dr7_s82
) AS X
ORDER BY objID

----------------------------------------------------------------------
-- Get coadd-depth matches for normal-depth selected sample
----------------------------------------------------------------------

-- get coadd neighbours of normal-depth selected objects within R90

GO -- IN MYDB CONTEXT
create table gz2_dr7_s82_nearby
( 
objid_normal bigint, 
ra_normal float,
dec_normal float,
rmag_normal float,
r90_normal float,
distance float,
objid_coadd bigint
) 

GO -- IN STRIPE82 CONTEXT
declare @objid bigint
declare @ra float
declare @dec float
declare @rmag float
declare @r90 float

declare objCurs CURSOR for
  select objid, ra, dec, (petroMag_r - extinction_r) as rmag, petroR90_r as r90
  from mydb.gz2_dr7_s82

open objCurs
fetch next from objCurs into @objid, @ra, @dec, @rmag, @r90
while (@@fetch_status >= 0) begin 
    insert into mydb.gz2_dr7_s82_nearby
    select @objid, @ra, @dec, @rmag, @r90, MATCH.distance, MATCH.objid
    from dbo.fGetNearbyObjEq(@ra, @dec, @r90/60.0) as MATCH
    where run in (106,206) 
    fetch next from objCurs into @objid, @ra, @dec, @rmag, @r90
end 
close objCurs

-- get magnitude differences between coadd neighbours and normal-depth objects

GO -- IN STRIPE82 CONTEXT
select *, (rmag_normal - rmag_coadd) as deltar
into gz2_dr7_s82_nearby_mag
from
(
     select N.*, (P.petroMag_r - P.extinction_r) as rmag_coadd
     from mydb.gz2_dr7_s82_nearby as N, stripe82.PhotoPrimary as P
     where N.objid_coadd = P.objid
) as X

-- calculate figure of merit to use for matching
-- using 1 mag = 0.6 arcsec

GO -- IN MYDB CONTEXT
select *, (distance + abs(0.01*deltar)) as FoM, ROW_NUMBER() OVER (PARTITION BY objid_normal ORDER BY distance + abs(0.01*deltar)) as best
into gz2_dr7_s82_nearby_best
from gz2_dr7_s82_nearby_mag

-- add coadd matches to normal-depth catalogue

GO -- IN MYDB CONTEXT
select G.*, objid_coadd, distance, deltar, FoM
into gz2_dr7_s82_match
from gz2_dr7_s82 as G
left join gz2_dr7_s82_nearby_best as B
on (G.objid = B.objid_normal)
where B.best = 1

-- count number of non-matched normal-depth objects

GO -- IN MYDB CONTEXT
select count(*)
from gz2_dr7_s82_match
where objid_coadd is null

-- create table of extra coadd objects
-- (selected by matching to normal-depth sample, but not included in
--  coadd-depth selected sample)

GO -- IN MYDB CONTEXT
select C.*
into gz2_coadd_s82_extra1
from gz2_dr7_s82_match as M, gz2_coadd_s82_stage5 as C
where M.objid_coadd not in (select objid from gz2_coadd_s82)
and M.objid_coadd is not null
and M.objid_coadd = C.objid

GO -- IN STRIPE82 CONTEXT
select objID, run, rerun, camcol, field, obj, ra, dec, petroR50_r, petroR90_r,
petroMag_u, petroMag_g, petroMag_r, petroMag_i, petroMag_z,
petroMagErr_u, petroMagErr_g, petroMagErr_r, petroMagErr_i, petroMagErr_z,
psfMag_r, fiberMag_r, deVMag_r, deVMagErr_r, expMag_r, expMagErr_r, fracDeV_r,
(petroMag_r + 2.5*log10(6.283185*power(petroR50_r, 2))) as mu50_r,
extinction_u, extinction_g, extinction_r, extinction_i, extinction_z,
rowc_u, colc_u, rowc_g, colc_g, rowc_r,
colc_r, rowc_i, colc_i, rowc_z, colc_z,
flags_r
into mydb.gz2_coadd_s82_extra2a
from (select objid_coadd from mydb.gz2_dr7_s82_match) as M,
stripe82.PhotoPrimary as C
where objid_coadd not in (select objid from mydb.gz2_coadd_s82)
and objid_coadd not in (select objid from mydb.gz2_coadd_s82_extra1)
and objid_coadd is not null
and objid_coadd = C.objid

-- calculate cmodel mags
GO -- IN MYDB CONTEXT (having previously defined cmodel functions)
SELECT *,
dbo.calc_cmodel(deVMag_r, expMag_r, fracDev_r, 1.2e-10) as cmodelMag_r,
dbo.calc_cmodelerr(deVMagErr_r, expMagErr_r, deVMag_r, expMag_r,
    fracDev_r, 1.2e-10) as cmodelMagErr_r
INTO gz2_coadd_s82_extra2b
FROM gz2_coadd_s82_extra2a

-- get any available redshifts
GO -- IN DR7 CONTEXT
SELECT G.*, S.z as redshift, S.zErr as redshiftErr, S.specclass
INTO gz2_coadd_s82_extra2
FROM mydb.gz2_coadd_s82_extra2b AS G
LEFT JOIN mydb.dr7_SpecObj_s82 AS S
ON (dbo.fDistanceEq(S.ra, S.dec, G.ra, G.dec) < 0.02)

GO -- IN MYDB CONTEXT
select *
into gz2_coadd_s82_extra
from gz2_coadd_s82_extra1
union
select *
from gz2_coadd_s82_extra2

-- create table with all coadd objects

GO -- IN MYDB CONTEXT
select *
into gz2_coadd_s82_full
from gz2_coadd_s82
union
select *
from gz2_coadd_s82_extra

-- comparative sample is built from a subset of main sample with
-- redshifts.  Size and luminosity outliers are also excluded later.
GO
SELECT *
INTO gz2_coadd_s82_full_comp
FROM gz2_coadd_s82_full
WHERE redshift IS NOT NULL
