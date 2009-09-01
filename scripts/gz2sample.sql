-- get required data from PhotoPrimary
-- reject objects which are flagged as
-- SATURATED, BRIGHT, or (BLENDED and not NODEBLEND)
-- also make any pre-selection cuts
GO -- IN DR7 CONTEXT
SELECT 
G.objID, run, rerun, camcol, field, obj, ra, dec, petroR50_r, petroR90_r,
petroMag_u, petroMag_g, petroMag_r, petroMag_i, petroMag_z,
petroMagErr_u, petroMagErr_g, petroMagErr_r, petroMagErr_i, petroMagErr_z,
psfMag_r, fiberMag_r, deVMag_r, deVMagErr_r, expMag_r, expMagErr_r, fracDeV_r,
(petroMag_r + 2.5*log10(6.283185*power(petroR50_r, 2))) as mu50_r,
extinction_u, extinction_g, extinction_r, extinction_i, extinction_z,
rowc_u, colc_u, rowc_g, colc_g, rowc_r,
colc_r, rowc_i, colc_i, rowc_z, colc_z,
flags_r
INTO gz2_dr7_legacy_stage1
FROM dr7.PhotoPrimary as P, dr7.FieldQA as F
WHERE petroMag_r < 17.9 AND (psfMag_r - petroMag_r > 0.15)
AND ((flags_r & 0x70000000) > 0) --BINNED1 OR BINNED2 OR BINNED4
AND ((flags_r & 0x40000) = 0) --NOT SATURATED
AND (P.fieldID = F.fieldID)
AND (F.InLegacy = 1)

-- calculate cmodel mags
GO -- IN MYDB CONTEXT
SELECT objid,
dbo.calc_cmodel(deVMag_r, expMag_r, fracDev_r, 1.2e-10) as cmodelMag_r,
dbo.calc_cmodelerr(deVMagErr_r, expMagErr_r, deVMag_r, expMag_r,
    fracDev_r, 1.2e-10) as cmodelMagErr_r
INTO gz2_dr7_legacy_stage2
FROM gz2_dr7_legacy_stage1

-- perform star-galaxy separation
-- perform magnitude cut 
-- perform surface brightness cut
GO
SELECT S1.*, S2.cmodelMag_r, S2.cmodelMagErr_r
INTO gz2_dr7_legacy_stage3
FROM gz2_dr7_legacy_stage1 as S1, gz2_dr7_legacy_stage2 as S2
WHERE (psfMag_r - cmodelMag_r >= 0.24)
AND (petroMag_r <= 17.77)
AND (mu50_r <= 23.0)
AND S1.objid = S2.objid
-- OPTIONALLY to better match mgs sample for testing:
-- include all low SB galaxies with sufficiently bright fiber mags
-- OR (fiberMag_r <= 19.0))

-- Note Ubercal correction no longer required - dr7 default is ubercal

-- add redshifts to table where available
-- excluding duplicates
GO
SELECT *
INTO gz2_dr7_legacy_stage4
FROM
(
    SELECT G.*, S.z as redshift, S.zErr as redshiftErr, S.specclass,
    ROW_NUMBER() OVER(PARTITION BY G.objid ORDER BY S.zErr) AS best
    FROM gz2_dr7_legacy_stage3 as G
    LEFT JOIN dr7.SpecObj as S on (S.bestObjID = G.objID)
) AS X
WHERE best = 1

----------------------------------------------------------------------
-- Create final GZ2 samples
----------------------------------------------------------------------

-- select objects brighter than r = 17 and larger than 3 arcsec
GO
SELECT *
INTO gz2_dr7_legacy
FROM gz2_dr7_legacy_stage4
WHERE (petroMag_r - extinction_r) <= 17
AND petroR90_r >= 3
AND (((redshift > 0.0005) AND (redshift < 0.25)) OR redshift IS NULL)
AND objid NOT IN (SELECT objid FROM gz1_sdk80)

-- divide into original GZ2 objects and extras
GO
SELECT *
INTO gz2_dr7_legacy_original
FROM gz2_dr7_legacy
WHERE objid in (SELECT objid from gz2sample_finaldr7_legacy_bug)
GO
SELECT *
INTO gz2_dr7_legacy_extra
FROM gz2_dr7_legacy
WHERE objid not in (SELECT objid from gz2sample_finaldr7_legacy_bug)

-- comparative sample is built from a subset of main sample with
-- redshifts.  Size and luminosity outliers are also excluded later.
GO
SELECT *
INTO gz2_dr7_legacy_comp
FROM gz2_dr7_legacy
WHERE redshift IS NOT NULL
