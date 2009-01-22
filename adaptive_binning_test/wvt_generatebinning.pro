FUNCTION WVT_ASSIGN_TO_BIN, x, y, xnode, ynode, SNnode
  ; Assigns each pixel to the S/N weighted closest pixel 
  ; i.e. this constructs the weighted voronoi tesselation
  ; Note: SNnode is the square of the weight!
  tmp = min(((x-xnode)^2+(y-ynode)^2)*SNnode, index)
  RETURN, index[0]
END

PRO WVT_GENERATEBINNING, xnode, ynode, weight, binnumber, outmask, do_pixellist=do_pixellist, x=x, y=y

  IF keyword_set(do_pixellist) THEN BEGIN  
    binnumber=lonarr(n_elements(x))
    FOR i=0L, n_elements(x)-1L DO BEGIN 
      binnumber[i]=wvt_assign_to_bin(x[i], y[i], xnode, ynode, weight^2)+1L  
    ENDFOR
  ENDIF ELSE BEGIN
    dim=size(outmask,/dimensions)
    binnumber=dblarr(dim[0],dim[1])
    FOR i=0L, dim[0]-1L DO BEGIN
    FOR j=0L, dim[1]-1L DO BEGIN
      IF outmask[i,j] NE 0 THEN $
        binnumber[i,j]=wvt_assign_to_bin(i, j, xnode, ynode, weight^2)+1L  
    ENDFOR
    ENDFOR
  ENDELSE

  

END

