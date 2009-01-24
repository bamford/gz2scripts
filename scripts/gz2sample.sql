--GO
--DROP TABLE gz2sample_stage1, gz2sample_stage2, gz2sample_stage4,
--gz2sample_stage5, gz2sample_stage6

--GO
--DROP VIEW gz2sample_stage3, gz2sample_finaldr7, gz2sample_finaldr7comp

-- get required data from PhotoPrimary
-- reject objects which are flagged as
-- SATURATED, BRIGHT, or (BLENDED and not NODEBLEND)
-- also make any pre-selection cuts
GO
SELECT 
objID, run, rerun, camcol, field, obj, ra, dec, petroR50_r, petroR90_r,
petroMag_u, petroMag_g, petroMag_r, petroMag_i, petroMag_z,
petroMagErr_u, petroMagErr_g, petroMagErr_r, petroMagErr_i, petroMagErr_z,
psfMag_r, fiberMag_r, deVMag_r, deVMagErr_r, expMag_r, expMagErr_r, fracDeV_r,
(petroMag_r + 2.5*log10(6.283185*power(petroR50_r, 2))) as mu50_r,
extinction_u, extinction_g, extinction_r, extinction_i, extinction_z,
rowc_u, colc_u, rowc_g, colc_g, rowc_r,
colc_r, rowc_i, colc_i, rowc_z, colc_z
INTO gz2sample_stage1
FROM dr7.PhotoPrimary
WHERE petroMag_r < 17.9 AND (psfMag_r - petroMag_r > 0.15)
AND ((flags_r & 0x70000000) > 0) --BINNED1 OR BINNED2 OR BINNED4
AND ((flags_r & 0x40000) = 0) --NOT SATURATED
AND ((flags_r & 0x2) = 0) --NOT BRIGHT
AND (((flags_r & 0x8) = 0) OR (flags_r & 0x40) > 0) --(NOT BLENDED OR NODEBLEND)
-- DR6: 798683 objects

-- calculate cmodel mags
GO
SELECT *,
dbo.calc_cmodel(deVMag_r, expMag_r, fracDev_r, 1.2e-10) as cmodelMag_r,
dbo.calc_cmodelerr(deVMagErr_r, expMagErr_r, deVMag_r, expMag_r,
    fracDev_r, 1.2e-10) as cmodelMagErr_r
INTO gz2sample_stage2
FROM mydb.gz2sample_stage1

GO
DROP TABLE gz2sample_stage1

-- perform star-galaxy separation
GO
CREATE VIEW gz2sample_stage3 AS
SELECT *
FROM mydb.gz2sample_stage2
WHERE (psfMag_r - cmodelMag_r >= 0.24)
-- DR6: 778358 objects

-- Ubercal correction no longer required - dr7 default is ubercal

-- perform magnitude cut 
-- perform surface brightness cut
GO
SELECT *
INTO gz2sample_stage5
FROM mydb.gz2sample_stage3
WHERE (petroMag_r <= 17.77)
AND (mu50_r <= 23.0)
-- OPTIONALLY to better match mgs sample for testing:
-- include all low SB galaxies with sufficiently bright fiber mags
-- OR (fiberMag_r <= 19.0))
-- DR6: 652803 objects

-- add redshifts to table where available
-- excluding duplicates
GO
SELECT *
FROM
(
    SELECT G.*, S.z as redshift, S.zErr as redshiftErr,
    ROW_NUMBER() OVER(PARTITION BY G.objid ORDER BY S.zErr) AS best
    FROM mydb.gz2sample_stage5 as G
    LEFT JOIN dr7.SpecObj as S on (S.bestObjID = G.objID)
) AS X
INTO gz2sample_stage6
WHERE best = 1

GO
DROP TABLE gz2sample_stage5

----------------------------------------------------------------------
-- Determine effect of various potential further cuts to the sample
----------------------------------------------------------------------

-- count objects with a redshift which implies it is in our own Galaxy
GO SELECT COUNT(*) FROM mydb.gz2sample_stage6
WHERE redshift < 0.0005
-- DR6: 5331 objects (0.8%)
GO SELECT COUNT(*) FROM mydb.gz2sample_stage6
WHERE redshift < 0.001
-- DR6: 5409 objects (0.8%)

-- count objects with a redshift which implies
-- it is too distant for useful classification
GO SELECT COUNT(*) FROM mydb.gz2sample_stage6
WHERE redshift > 0.25
-- DR6: 4130 objects (0.6%)

-- count objects smaller than 3 arcsec
GO SELECT COUNT(*) FROM mydb.gz2sample_stage6
WHERE petroR90_r < 3.0
-- DR6: 21640 objects (3.3%)

-- count objects smaller than 5 arcsec
GO SELECT COUNT(*) FROM mydb.gz2sample_stage6
WHERE petroR90_r < 5.0
-- DR6: 195676 objects (30.0%)

-- count objects fainter than r = 17.0
GO SELECT COUNT(*) FROM mydb.gz2sample_stage6
WHERE petroMag_r > 17.0
-- DR6: 398650 objects (61.1%)

-- count objects fainter than r = 16.5
GO SELECT COUNT(*) FROM mydb.gz2sample_stage6
WHERE petroMag_r > 16.5
-- DR6: 516206 objects (79.1%)

-- count objects classified as star / don't know 
-- by >95% of classifiers in GZ1
GO SELECT COUNT(*) FROM mydb.gz1_sdk95
-- DR6: 5393 objects (0.8%)

-- count objects classified as star / don't know 
-- by >80% of classifiers in GZ1
GO SELECT COUNT(*) FROM mydb.gz1_sdk80
-- DR6: 8104 objects (1.2%)

-- count objects classified as star / don't know 
-- by >50% of classifiers in GZ1
GO SELECT COUNT(*) FROM mydb.gz1_sdk50
-- DR6: 17529 objects (2.7%)

----------------------------------------------------------------------
-- Create final GZ2 samples
----------------------------------------------------------------------

-- select objects brighter than r = 17 and larger than 3 arcsec
GO
SELECT *
INTO gz2sample_finaldr7
FROM mydb.gz2sample_stage6
WHERE (petroMag_r - extinction_r) <= 17
AND petroR90_r >= 3
AND (((redshift > 0.0005) AND (redshift < 0.25)) OR redshift IS NULL)
AND objid NOT IN (SELECT objid FROM gz1_sdk80)
-- DR6: 243064 objects

-- comparative sample is built from a subset of main sample with
-- redshifts.  Size and luminosity outliers are also excluded later.
GO
CREATE VIEW gz2sample_finaldr7comp AS
SELECT *
FROM mydb.gz2sample_finaldr7
WHERE redshift IS NOT NULL
-- DR6:  174269 objects
