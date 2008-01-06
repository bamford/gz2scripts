;Version 1.0, updated 09/08/2005
;
; INPUT:   
;          BINNUMBER: Either 2d image or 1d pixel list, containing the bin
;                     number of each pixel
;          INPUTSIGNAL: Has to be same size as binnumber
;
; OUTPUT:
;
; RETURNS: array of the same size as BINNUMBER and INPUTIMG, containing the 
;          binned signal 
;
;
;
;---------------------------------------------------------------------------
;
FUNCTION WVT_APPLYBINNING, binnumber, inputsignal, area=area, xraycolor=xraycolor, input2=input2, binvalue=binvalue

  in=inputsignal[*]
  IF keyword_set(xraycolor) THEN in2=input2[*]
  out=in
  class=binnumber[*]

  nbins=max(binnumber)
  binvalue=dblarr(nbins)
  npix=n_elements(in)
  IF NOT(keyword_set(area)) THEN $
    area = HISTOGRAM(class, REVERSE_INDICES=r ,min=1, max=nbins)

  FOR i=0L,nbins-1L DO BEGIN
     IF area[i] NE 0 THEN BEGIN
       w = r[r[i]:r[i+1]-1]
       IF keyword_set(xraycolor) THEN BEGIN        
         binvalue[i]=total(in[w])/total(in2[w])
         out[w]=binvalue[i]
       ENDIF ELSE BEGIN
         binvalue[i]=total(in[w])/area[i]   
         out[w]=binvalue[i]
       ENDELSE
     ENDIF
  ENDFOR

  binnedsignal=inputsignal
  binnedsignal[*]=out
  return, binnedsignal
END

