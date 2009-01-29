pro gz2_kcorrect
; loads photometry fits files and runs it through kcorrect.
; Saves output with absmag columns
                                   
; .r   gz2_kcorrect

; File containing redshifts and 
; galactic SDSS-system ubercal ugriz luptitude mags,
; statistical sigma errors and extinction corrections
infilename = '../gz2sample_final.fits'

outfilename = '../gz2sample_final_kcorrect.fits'

; load the fits file. Needs the rsi library installed
data = mrdfits(infilename,1)

; make tag names
mag = 'PETROMAG_'+['U','G','R','I','Z']
magerr = 'PETROMAGERR_'+['U','G','R','I','Z']
extinction = 'EXTINCTION_'+['U','G','R','I','Z']
; name to store into
absmag = 'PETROMAG_M'+['U','G','R','I','Z']
absmagerr = 'PETROMAGERR_M'+['U','G','R','I','Z']

; constants
H0=70 ; km/s/MPc

ngal = N_STRUCT(data)
nmag = N_ELEMENTS(mag)

print, 'ngal = ', ngal

; make arrays of magnitudes and errors
magarr = fltarr(nmag, ngal)
magerrarr = fltarr(nmag, ngal)

; populate magnitude arrays
for m=0, nmag-1 do begin
   magarr[m,*] = data.(where(TAG_NAMES(data) eq mag[m])) $
                 - data.(where(TAG_NAMES(data) eq extinction[m]))
   magerrarr[m,*] = data.(where(TAG_NAMES(data) eq magerr[m]))
endfor

; convert errors to ivar
magivararr=k_sdss_err2ivar(magerrarr)

; set zero ivar for remaining bad measurements
indx=where(magarr eq -9999 and magivararr ne 0., count)
if(count gt 0) then begin
    magivararr[indx] = 0.0
endif

; convert from SDSS luptitudes to maggies
maggies=dblarr(nmag,ngal)
maggies_ivar=dblarr(nmag,ngal)
bvalues=[1.4D-10, 0.9D-10, 1.2D-10, 1.8D-10, 7.4D-10]
for m=0, nmag-1 do begin
    indx=where(magivararr[m,*] ne 0., count)
    if(count gt 0) then begin
       err = 1.0/sqrt(magivararr[m,indx])
       maggies[m,indx] = k_lups2maggies(magarr[m, indx], err, $
                                        maggies_err=merr, $
                                        bvalues=bvalues[m])
       maggies_ivar[m,indx] = 1.0/(merr^2)
    endif
 endfor

; correct to AB maggies
; offsets from http://www.sdss.org/dr6/algorithms/fluxcal.html#sdss2ab
k_abfix, maggies, maggies_ivar, aboff=[-0.04, 0.00, 0.00, 0.00, 0.02]

; make arrays for storing results
;kcorrect = dblarr(nmag,ngal)
;absmagarr = dblarr(nmag,ngal)
;absmagivararr = dblarr(nmag,ngal)

; make mask of objects with and without redshifts
zmask = FINITE(data.redshift)
nozmask = where(~zmask)
zmask = where(zmask)
nzgal = N_ELEMENTS(zmask)
maggies = maggies[*,zmask]
maggies_ivar = maggies_ivar[*,zmask]
redshift = data[zmask].redshift

print, 'nzgal = ', nzgal

;print, maggies
;print, maggies_ivar
;print, data.redshift
;print, ''
;print, zmask
;print, ''
;print, redshift

; load into Blanton's code
; minerrors from http://www.sdss.org/dr6/algorithms/fluxcal.html#ubercal
; output absolute restframe AB (Pogson) magnitudes and ivars
kcorrect, maggies, maggies_ivar, redshift, $
          kcorrect, $
          absmag=absmagarr, amivar=absmagivararr, $
          minerrors=[0.02, 0.01, 0.01, 0.01, 0.01]

; correct cosmology
absmagarr = absmagarr + 5.0*alog10(H0/100.0)

; convert ivars to sigma errors
absmagerrarr = dblarr(nmag,nzgal)
for m=0, nmag-1 do begin
   ok = where(absmagivararr[m,*] GT 0.001)
   absmagerrarr[m,*] = 99999.0
   absmagerrarr[m,ok] = 1.0/SQRT(absmagivararr[m,ok])
endfor

; create new array of structures including absmag tags
absmagstruct = {ABSGAL, petroMag_Mu:0.0, petroMag_Mg:0.0, $
                petroMag_Mr:0.0, petroMag_Mi:0.0, petroMag_Mz:0.0, $
                petroMagErr_Mu:0.0, petroMagErr_Mg:0.0, $
                petroMagErr_Mr:0.0, petroMagErr_Mi:0.0, $
                petroMagErr_Mz:0.0}
datanew = REPLICATE(CREATE_STRUCT(data[0], absmagstruct), ngal)

; populate new array of structures with contents of DATA
ndatatags = N_TAGS(data)
for t=0, ndatatags-1 do begin
   datanew[*].(where(TAG_NAMES(datanew) eq (TAG_NAMES(data))[t])) = data.(t)
endfor

; add absmag fields to new array of structures
for m=0, nmag-1 do begin
   ; need to put in to 1D array before assigning to array of structures
   a = FLTARR(nzgal)
   a[*] = absmagarr[m,*]
   datanew[zmask].(where(TAG_NAMES(datanew) eq absmag[m])) = a
   a[*] = absmagerrarr[m,*]
   datanew[zmask].(where(TAG_NAMES(datanew) eq absmagerr[m])) = a
endfor

; mask out values of objects with no redshift
for m=0, nmag-1 do begin
   datanew[nozmask].(where(TAG_NAMES(datanew) eq absmag[m])) = !VALUES.F_NAN
   datanew[nozmask].(where(TAG_NAMES(datanew) eq absmagerr[m])) = !VALUES.F_NAN
endfor

; save fits file
mwrfits, datanew, outfilename

end
