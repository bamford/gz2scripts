PRO WVT_ZOO, counts_per_bin
  ;Perform WVT binning on Galaxy Zoo data to constant counts per bin
  ;Read in the counts image 
  data=mrdfits('../../GalaxyZoo/dr6_zoo_selected_counts.fits', $
                   'COUNTS_ALL_CSUW_OVERSAMPLED') 
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
     ; create mask by smoothing image by 5 pixel boxcar, thresholding,
     ; then applying a 5 pixel morph open operation
     smoothimage = smooth(ctsimage*1.0, 20, /edge_truncate)
     thresh = smoothimage GT 0.5/(3*3)
     ;thresh = ctsimage GT 0.5
     radius = 5 
     strucElem = SHIFT(DIST(2*radius+1), radius, radius) LE radius
     mask = MORPH_CLOSE(thresh, strucElem)
     radius = 10 
     strucElem = SHIFT(DIST(2*radius+1), radius, radius) LE radius
     mask = MORPH_OPEN(mask, strucElem)
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
  mwrfits, binnedimage, 'zoo_wvt_density_all.fits', /create
  mwrfits, binnumber, 'zoo_wvt_bins.fits', /create
  mwrfits, nodes, 'zoo_wvt_nodes.fits', /create
  mwrfits, snmap, 'zoo_wvt_counts_all.fits', /create
  mwrfits, maskarr, 'zoo_wvt_mask.fits', /create
END
