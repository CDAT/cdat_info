#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 13:32:12 2018

Paul J. Durack 27th August 2018

This script replicates the threads issue

PJD 27 Aug 2018     - Created small test case for threads

@author: durack1
"""
from __future__ import print_function
import os
# Numpy multithread control
# https://stackoverflow.com/questions/8365394/set-environment-variable-in-python-script
# https://github.com/CDAT/cdms/issues/264
os.environ['OPENBLAS_NUM_THREADS'] = '1' # visible in this process + all children
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1' ; # https://stackoverflow.com/questions/17053671/python-how-do-you-stop-numpy-from-multithreading
os.environ['NUMEXPR_NUM_THREADS'] = '1' ; # https://groups.google.com/a/continuum.io/forum/#!topic/anaconda/c8bvcJtGlzg
# https://github.com/conda/conda/issues/6787
# https://github.com/conda/conda/issues/7040
import datetime,gc,sys #shlez,pdb ; #resource
import cdms2 as cdm
os.environ['UVCDAT_ANONYMOUS_LOG'] = 'no' ; # force cdat_info to be ignored
import cdutil as cdu
import MV2 as mv
import numpy as np
from cdms2.selectors import Selector
import cdat_info

# Numpy initialisation and multithread control
np.set_printoptions(precision=4)

# Set nc4 compressed as outputs
cdm.setCompressionWarnings(0) ; # Suppress warnings
cdm.setNetcdfShuffleFlag(0)
cdm.setNetcdfDeflateFlag(1)
cdm.setNetcdfDeflateLevelFlag(9)
cdm.setAutoBounds(1) ; # Ensure bounds on time and depth axes are generated

timeFormat = datetime.datetime.now().strftime("%y%m%d")
print('PID:',str(os.getpid())) ; # Returns calling python instance, so master also see os.getppid() - Parent

#%%
# Declare input data and their variable
inFiles = [
['NODC',os.path.join(cdat_info.get_sampledata_path(),'180808_NODC_annual_temperature_anomaly_1955-2017_0-2000m.nc'),'temperature_anomaly'],
]

outPath = 'test_out'

# Specify depth
depths = ['0-700','700-2000']

# Declare constants
earth_total_area_m2     = 510.072e12 ; # ocean_area = 350.392e12 - 68.7% - Ishii grid
land_total_area_m2      = 148.940e12 ; # land 29.2%
ocean_total_area_m2     = 361.132e12 ; # water 70.8%
for loop in range(0,10):
    print('loop:',loop)
    for count,input in enumerate(inFiles):
        print('* processing ',input[0])
        uF      = cdm.open(input[1])
        grid    = uF(input[2],slice(0,1),slice(0,1),squeeze=1) ; # Assume time,depth,lat,lon
        area    = cdu.area_weights(grid) ; # Returns a fraction
        aream2  = area*earth_total_area_m2
        print('ocean area:      ',aream2.sum(),'m^2')
        print('Earth ocean area:',ocean_total_area_m2,'m^2')
        #continue
        # Create outfile
        outFile = os.path.join(outPath,'_'.join([timeFormat,input[0],'0to700And700to2000m.nc']))
        print(outFile)
        #continue
        if os.path.exists(outFile):
            print('** File exists.. removing **')
            os.remove(outFile)
        #fOut = cdm.open(outFile,'w')

        # Determine inputs
        testAxes = uF[input[2]]
        sizes = testAxes.shape
        timeAx = testAxes.getTime()

        # If NODC load climatology
        if input[0] == 'NODC':
            climInfile = os.path.join(cdat_info.get_sampledata_path(),'woa13_decav_t00_01.nc')
            cF = cdm.open(climInfile)
            climDepths = cF.getAxis('depth').getData()
            anomDepths = uF.getAxis('level').getData()
            commonLevels = np.intersect1d(climDepths,anomDepths)
            clim = cF('t_an') ; #,level=commonLevels)
            inds = []
            for x,val in enumerate(commonLevels):
                 inds.append(np.where(climDepths==commonLevels[x])[0][0])
            climTrim = np.take(clim,inds,axis=1)
            climTrim = cdm.createVariable(climTrim,id='climTrim',missing_value=1e20)
            climTrim.setAxis(0,clim.getAxis(0))
            climTrim.setAxis(1,uF.getAxis('level'))
            climTrim.setAxis(2,uF.getAxis('latitude'))
            climTrim.setAxis(3,uF.getAxis('longitude'))
            del(clim,inds,x,val,commonLevels,anomDepths,climDepths,climInfile) ; gc.collect()
            cF.close()

        # Now compute from timeseries - lines 231-257 from /export/gleckler1/processing/ohc_deep/compute_ts/calculate_OHC.py
        # Preallocate outputs
        intTempUpper,intTempIntermed,intTempCUpper,intTempCIntermed, \
        aveTempUpper,aveTempIntermed,aveTempCUpper,aveTempCIntermed = [np.ones(sizes[0],dtype='float64')*1e20 for _ in range(8)]
        for i in range(sizes[0]):
            print('i:',i)
            for depth in depths:
                depthBounds         = depth.split('-')
                depthSel            = Selector(level=(np.int(depthBounds[0]),np.int(depthBounds[1])))
                thetao              = uF(input[2],time=slice(i,i+1))(depthSel)
                time                = thetao.getTime()
                thetao              = thetao.astype('float64')
                levs                = thetao.getAxis(1)
                lbs                 = levs.getBounds()
                if input[0] == 'NODC':
                    thetao = thetao + climTrim(depthSel) ; # Add offset
                lbs[len(levs)-1,1]  = depthBounds[1]
                levs.setBounds(lbs)
                thetao.setAxis(1,levs)
                if not thetao.max() > 50. and not thetao.mean() > 265.:
                    to      = thetao
                    thetao  = thetao+273.15 ; # Test and inflate C -> K
                else:
                    to      = thetao-273.15 ; # Otherwise convert K -> C
                intThetao       = cdu.averager(thetao,axis=1,weights='weighted',action='sum')(squeeze=1)
                intThetaoArea   = mv.multiply(intThetao,aream2)
                intTo           = cdu.averager(to,axis=1,weights='weighted',action='sum')(squeeze=1)
                intToArea       = mv.multiply(intTo,aream2)
                if depth == '0-700':
                    intTempUpper[i]         = mv.sum(intThetaoArea)
                    aveTempUpper[i]         = mv.average(thetao)
                    intTempCUpper[i]        = mv.sum(intToArea)
                    aveTempCUpper[i]        = mv.average(to)
                else:
                    intTempIntermed[i]      = mv.sum(intThetaoArea)
                    aveTempIntermed[i]      = mv.average(thetao)
                    intTempCIntermed[i]     = mv.sum(intToArea)
                    aveTempCIntermed[i]     = mv.average(to)
                    print(' '.join([input[0],format(i,'03d'),str(time.asComponentTime()).ljust(22),
                    '0to700:',str("%.4e" % intTempUpper[i]),'-',str("%.3f" % aveTempCUpper[i]),'degC (0to700)',
                    '- 700to2000:',str("%.4e" % intTempIntermed[i]),'-',str("%.3f" % aveTempCIntermed[i]),'degC (700to2000)',
                    '-',str("%.3e" % mv.average(aream2)),'area (m^2)']))
        #pdb.set_trace() ; # Provides a 'keyboard' like command
        intTempUp   = cdm.createVariable(intTempUpper,id='thetaoInteg_0to700',missing_value=1e20)
        intTempLo   = cdm.createVariable(intTempIntermed,id='thetaoInteg_700to2000',missing_value=1e20)
        aveTempUp   = cdm.createVariable(aveTempUpper,id='thetaoAve_0to700',missing_value=1e20)
        aveTempLo   = cdm.createVariable(aveTempIntermed,id='thetaoAve_700to2000',missing_value=1e20)
        intTempCUp  = cdm.createVariable(intTempUpper,id='toInteg_0to700',missing_value=1e20)
        intTempCLo  = cdm.createVariable(intTempIntermed,id='toInteg_700to2000',missing_value=1e20)
        aveTempCUp  = cdm.createVariable(aveTempUpper,id='toAve_0to700',missing_value=1e20)
        aveTempCLo  = cdm.createVariable(aveTempIntermed,id='toAve_700to2000',missing_value=1e20)
        intTempUp.setMissing(1e20)
        intTempLo.setMissing(1e20)
        intTempUp.units         = 'K'
        intTempLo.units         = 'K'
        intTempUp.long_name     = 'volume_integrated_temperature'
        intTempLo.long_name     = 'volume_integrated_temperature'
        aveTempUp.setMissing(1e20)
        aveTempLo.setMissing(1e20)
        aveTempUp.units         = 'K'
        aveTempLo.units         = 'K'
        aveTempUp.long_name     = 'volume_averaged_temperature'
        aveTempLo.long_name     = 'volume_averaged_temperature'
        intTempCUp.setMissing(1e20)
        intTempCLo.setMissing(1e20)
        intTempCUp.units        = 'deg_C'
        intTempCLo.units        = 'deg_C'
        intTempCUp.long_name    = 'volume_integrated_temperature'
        intTempCLo.long_name    = 'volume_integrated_temperature'
        aveTempCUp.setMissing(1e20)
        aveTempCLo.setMissing(1e20)
        aveTempCUp.units        = 'deg_C'
        aveTempCLo.units        = 'deg_C'
        aveTempCUp.long_name    = 'volume_averaged_temperature'
        aveTempCLo.long_name    = 'volume_averaged_temperature'
        t = timeAx.clone() ; # Recreate new editable time axis, rather than pointer
        if input[0] in ['NODC','UCSD']:
            #pdb.set_trace()
            t.units = timeAx.units ; # Weirdly for UCSD the .clone() command fails to copy the units
        t.toRelativeTime('days since 2000-1-1') ; # Redirect this to new timeAx variable
        t.id = 'time' ; # Fix upper case instances
        intTempUp.setAxis(0,t)
        intTempLo.setAxis(0,t)
        aveTempUp.setAxis(0,t)
        aveTempLo.setAxis(0,t)
        intTempCUp.setAxis(0,t)
        intTempCLo.setAxis(0,t)
        aveTempCUp.setAxis(0,t)
        aveTempCLo.setAxis(0,t)
        uF.close()