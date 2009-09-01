PRO WVT_GZ2
  ;Perform WVT binning on Galaxy Zoo 2 data to constant counts per bin
  ; for normal
  ;counts_per_bin = 200
  ; for coadd
  counts_per_bin = 50
  ;Read in the counts image
  ; for normal
  ;data=mrdfits('../gz2sample_final_abs_regions_counts.fits', $
  ;                 'simple_bin_counts') 
  ; for coadd
  data=mrdfits('../gz2sample_final_stripe82_coadd_abs_regions_counts.fits', $
                   'simple_bin_counts') 
  dim = size(data, /dimensions)
  binnedimage = fltarr(dim)
  binnumber = intarr(dim)
  maskarr = intarr(dim)
  snmap = fltarr(dim)
  maxnodes = floor(total(data)/4/counts_per_bin)
  print, 'maxnodes', maxnodes
  nodes = fltarr(maxnodes, 2, dim[2])
  targetSN = sqrt(counts_per_bin)
  max_area = !pi*5^2   ;with 5x oversampling, a circle radius 1 original bins
  FOR zi=0,dim[2]-1 DO BEGIN
     print, 'zi =', zi
     ctsimage = data[*,*,zi]
     sum = total(ctsimage)
     IF sum LT 1 THEN CONTINUE
     signal = ctsimage
     noise = sqrt(ctsimage)
     ; create mask by smoothing image, thresholding,
     ; then applying morphological operations
     smoothimage = smooth(ctsimage*1.0, 20, /edge_truncate)
     thresh = smoothimage GT 0.5/(3*3)
     ;thresh = ctsimage GT 0.5
     radius = 5 
     strucElem = SHIFT(DIST(2*radius+1), radius, radius) LE radius
     mask = MORPH_CLOSE(thresh, strucElem)
     radius = 10 
     strucElem = SHIFT(DIST(2*radius+1), radius, radius) LE radius
     mask = MORPH_OPEN(mask, strucElem)
     ;print, signal
     ;print, noise
     ;print, mask
     ;radius = 5
     ;strucElem = SHIFT(DIST(2*radius+1), radius, radius) LE radius
     ;strucElem = REPLICATE(1,20,20)
     ;mask = DILATE(mask, strucElem)
     ;mask = thresh
     ;Perform the binning, with target signal-to-noise
     wvt_image, signal, noise, targetSN, binim, xnode, ynode, $
                plotit=0, binnumber=binno, snbin=snbin, mask=mask
                ;max_area=max_area
     binnedimage[*,*,zi] = binim
     binnumber[*,*,zi] = binno
     snmap[*,*,zi] = snbin[binno]
     nnodes = size(xnode, /dimensions)
     nodes[0:nnodes-1,0,zi] = xnode
     nodes[0:nnodes-1,1,zi] = ynode
     maskarr[*,*,zi] = mask
  ENDFOR
  ;max_area=max_area
  ;Save the output in another fits image
  ; for normal
  ;mwrfits, binnedimage, '../gz2_wvt_density_all.fits', /create
  ;mwrfits, binnumber, '../gz2_wvt_bins.fits', /create
  ;mwrfits, nodes, '../gz2_wvt_nodes.fits', /create
  ;mwrfits, snmap, '../gz2_wvt_counts_all.fits', /create
  ;mwrfits, maskarr, '../gz2_wvt_mask.fits', /create
  ; for coadd
  mwrfits, binnedimage, '../gz2_coadd_wvt_density_all.fits', /create
  mwrfits, binnumber, '../gz2_coadd_wvt_bins.fits', /create
  mwrfits, nodes, '../gz2_coadd_wvt_nodes.fits', /create
  mwrfits, snmap, '../gz2_coadd_wvt_counts_all.fits', /create
  mwrfits, maskarr, '../gz2_coadd_wvt_mask.fits', /create
END
