from funcs_er import *
import os
from scipy.stats import linregress
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
#import seaborn as sns
# sns.set()

'''
This file:
- Use REACHINPUT: The method for invoking the options to specify streambed properties
                  by reach or to simulate unsaturated flow beneath streams (REACHINPUT)

'''
# cd c:\Users\hpham\Documents\P34_East_River\es_scripts\scripts\

# Choose run options:
opt_check_flow_downhill = False

# Specify input files
# ifile = r'../input/stream.csv'
ifile = r'../input/hru_params2.csv'
df_org = pd.read_csv(ifile)
print(f'\nReading file {ifile} \n')
df = df_org[df_org['ISEG'] != 0]

# Speficy ouput files
ofile = '../output/sfr/east_river.sfr'  # sfr MODFLOW file

# Create an folder to save figures
odir = '../output/regres_figs/'
gen_outdir(odir)


# MODFLOW parameters
nrows, ncols = 419, 328

# Plot parameters
sz = 30
pad_val = 2  # how far from tick_label to ax
# Get rid of max 20 plot warning
mpl.rcParams['figure.max_open_warning'] = 1000
plt.grid(color='#e6e6e6', linestyle='-', linewidth=0.5, axis='both')

# drop duplicate cells to get SEG and connected SEG
col_tmp = ['ISEG', 'OUTSEG', 'IUPSEG', 'MAXREACH', 'DEM_ADJ']

# Get unique ???
df_tmp = df[col_tmp]
dfSEG = df_tmp.drop_duplicates(subset=['ISEG', 'OUTSEG', 'IUPSEG'])
dfSEG = dfSEG.reset_index()

NSTRM = dfSEG['MAXREACH'].sum()  # the number of stream reaches
NSEG = dfSEG.shape[0]
NSS = dfSEG.shape[0]  # the number of stream segments
NSFRPAR = 0  # the number of stream parameters
NPARSEG = 0  # the number of stream-segment definitions associated with all parameters
CONST = 86400  # used in calculating stream depth for stream reach
# the closure tolerance for stream depth used to calculate leakage
# between each stream reach and active model cell
DLEAK = 0.0001
ISTCB1 = 40  # a flag for writing stream-aquifer leakage values
# a flag for writing to a separate formatted file all information
# on inflows and outflows from each reach
ISTCB2 = -3

'''
ISFROPT: An integer value that defines the format of the input data and whether or not unsaturated flow is
simulated beneath streams. Unsaturated flow is simulated for ISFROPT ≥ 2; unsaturated flow is not simulated for
ISFROPT = 0 or 1. Optional variables NSTRAIL, ISUZN, and NSFRSETS also must be specified if ISFROPT>1.
Values of ISFROPT are defined as follows:
'''
ISFROPT = 2

NSTRAIL = 10  # An integer value that is the number of trailing wave increments used to represent a trailing wave

# ISUZN An integer value that is the maximum number of vertical cells used to the define the unsaturated
# zone beneath a stream reach. If ICALC is 1 for all segments then ISUZN should be set to 1.
ISUZN = 1
# An integer value that is the maximum number of different sets of trailing waves used to allocate arrays.
NSFRSETS = 30
# IRTFLG An integer value that indicates the method of transient streamflow routing.
IRTFLG = 0
# NUMTIM An integer value equal to the number of sub time steps used to route streamflow.
NUMTIM = 1
# WEIGHT A real number equal to the time weighting factor used to calculate the change in channel storage.
WEIGHT = 0.7
# FLWTOL A real number equal to the streamflow tolerance for convergence of the kinematic wave equation
# used for transient streamflow routing.
FLWTOL = 0.01


# Write to file
fid = open(ofile, 'w')

#
fid.write("%s\n" % ('REACHINPUT'))

# Write Date Set 1c
fid.write("%d\t%d\t%d\t%d\t%d\t%f\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%6.3f\t%6.3f\t\n" % (NSTRM, NSS, NSFRPAR,
                                                                                        NPARSEG, CONST, DLEAK, ISTCB1, ISTCB2, ISFROPT, NSTRAIL, ISUZN, NSFRSETS, IRTFLG, NUMTIM, WEIGHT, FLWTOL))


# Prepare Data Set 2 (SEG and REACH)
# KRCH IRCH JRCH ISEG IREACH RCHLEN {STRTOP} {SLOPE} {STRTHICK} {STRHC1} {THTS}
# {THTI} {EPS} {UHC}
cols = ['KRCH', 'IRCH', 'JRCH', 'ISEG', 'IREACH',
        'RCHLEN', 'DEM_ADJ']
df_seg_rch_loc = df[cols]
#df2 = pd.DataFrame(columns=cols)

# {STRTOP} {SLOPE} {STRTHICK} {STRHC1} {THTS} {THTI} {EPS} {UHC}
df_seg_rch_loc['STRM_SLOPE'] = 0.01  # The stream slope across the reach (>0)
df_seg_rch_loc['STRTHICK'] = 0.5  # The thickness of the streambed (meters)
# STRHC1 The hydraulic conductivity of the streambed (m/day)
df_seg_rch_loc['STRHC1'] = 1
# THTS The saturated volumetric water content in the unsaturated zone
df_seg_rch_loc['THTS'] = 0.15
# THTI The initial volumetric water content.
df_seg_rch_loc['THTI'] = 0.15
# EPS A real number equal to the Brooks-Corey exponent
df_seg_rch_loc['EPS'] = 3.5  # NOT SURE
# UHC A real number equal to the vertical saturated hydraulic conductivity of the unsaturated zone.
df_seg_rch_loc['UHC'] = 2.5  # NOT SURE

for i in range(NSEG):
    # for i in range(313, 314, 1):

    segi = df_seg_rch_loc[df_seg_rch_loc['ISEG'] == i+1]
#    print(segi)
    segi_sorted = segi.sort_values(by='IREACH')  # Back later
#    print(segi)

    # Check segi to make sure water flows downhill
    if opt_check_flow_downhill:
        fig, ax = plt.subplots(1, 2)
        fig.set_size_inches(10, 4)
        check_IREACH(segi_sorted, fig, ax)

    # Make sure flow run downstream
    # check_IREACH()

#    df2.loc[i, 'KRCH'] = df['KRCH'].iloc[i]
#    df2.loc[i, 'IRCH'] = df['IRCH'].iloc[i]
#    df2.loc[i, 'JRCH'] = df['JRCH'].iloc[i]
#    df2.loc[i, 'ISEG'] = df['ISEG'].iloc[i]
#    df2.loc[i, 'IREACH'] = df['IREACH'].iloc[i]
#    df2.loc[i, 'RCHLEN'] = df['RCHLEN'].iloc[i]
    fid.write(segi_sorted.to_string(index=False, header=False))
    fid.write('\n')

#df2.to_csv(fid, index=False, sep="\t", header=False)
#print('Saved the first part of sfr2 at {ofile1} \n')

#
#
# Prepare Data Set 5 ==========================================================
IRDFLG = 0  # printing input data specified for this stress period
IPTFLG = 0  # printing streamflow-routing results during this stress period
ICALC = 1  # method used to calculate stream depth in this segment

# Prepare Data Set 6 ==========================================================
# OUTSEG = 999  # the downstream stream segment that receives tributary
# inflow from the last downstream reach of this segment
# the upstream segment from which water is diverted (or withdrawn) to
# supply inflow to this stream segment
# IUPSEG = 999
FLOW = 0  # streamflow (L3/T) # Handle by PRMS
# the volumetric rate of the diffuse overland runoff
# that enters the stream segment (L3/T)
RUNOFF = 0  # Handle by PRMS
# the volumetric rate per unit area of water removed by evapotranspiration
# directly from the stream channel (L3/T)
ETSW = 0  # Handle by PRMS
# the volumetric rate per unit area of water added by precipitation
# directly on the stream channel (L/T)
PPTSW = 0.03
# -----------------------------------------------------------------------------
# HCOND1: Hydraulic conductivity of the streambed at the upstream end of this segment (L3/T)
HCOND1 = 1  # m3/day
# Thickness of streambed material at the upstream end of this segment (L3/T)
THICKM1 = 5  # m
# Elevation of the top of the streambed at the upstream end of this segment (L)
ELEVUP = 100  # meter # Not in use here because of using the REACHINPUT option
# WIDTH1: Average width of the stream channel at the upstream end of this segment (L)
WIDTH1 = 100  # meter
# DEPTH1: Average depth of water in the channel at the upstream end of this segment
DEPTH1 = 100  # meter

# HCOND2: Hydraulic conductivity of the streambed at the downstream end of this segment (L3/T)
HCOND2 = 1  # m3/day
# Thickness of streambed material at the downstream end of this segment (L3/T)
THICKM2 = 5  # m
# Elevation of the top of the streambed at the downstream end of this segment (L)
ELEVDN = 100  # meter
# WIDTH2: Average width of the stream channel at the downstream end of this segment (L)
WIDTH2 = 120  # meter
# DEPTH2: Average depth of water in the channel at the downstream end of this segment (L)
DEPTH2 = 100  # meter

# Item 5 Data: ITMP IRDFLG IPTFLG {NP}
fid.write("%d\t%d\t%d\n" % (NSEG, IRDFLG, IPTFLG))

for i in range(NSEG):
    # 6a. Data: NSEG ICALC OUTSEG IUPSEG {IPRIOR} {NSTRPTS} FLOW RUNOFF ETSW PPTSW
            # {ROUGHCH} {ROUGHBK} {CDPTH} {FDPTH} {AWDTH} {BWDTH}
    fid.write("%d\t%d\t%d\t%d\t%f\t%f\t%f\t%f\n" % (
        dfSEG['ISEG'].iloc[i], ICALC, dfSEG['OUTSEG'].iloc[i], dfSEG['IUPSEG'].iloc[i], FLOW, RUNOFF, ETSW, PPTSW))
    fid.write("%6.3f\n" %
              (WIDTH1))
    fid.write("%6.3f\n" %
              (WIDTH2))
    '''
    fid.write("%f\t%f\t%f\t%f\t%f\n" %
              (HCOND1, THICKM1, ELEVUP, WIDTH1, DEPTH1))
    fid.write("%f\t%f\t%f\t%f\t%f\n" %
              (HCOND2, THICKM2, ELEVDN, WIDTH2, DEPTH2))
    '''
fid.write("%s\n" % ('-1	0	0'))

fid.close()

#df6.to_csv(ofile1, index=False)
print(f'Saved the sfr2 file at {ofile}\n')


# REFERENCES
# https://water.usgs.gov/nrp/gwsoftware/modflow2000/MFDOC/index.html?sfr.htm
