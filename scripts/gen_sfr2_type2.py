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

'''
# cd c:\Users\hpham\Documents\P34_East_River\es_scripts\scripts\

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
pad_val = 2  # how far from a xtick_label to ax
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

# Write to file
fid = open(ofile, 'w')
# Write Date Set 1c
fid.write("%d\t%d\t%d\t%d\t%d\t%f\t%d\t%d\t\n" % (NSTRM, NSS, NSFRPAR,
                                                  NPARSEG, CONST, DLEAK, ISTCB1, ISTCB2))


# Prepare Data Set 2 (SEG and REACH)
cols = ['KRCH', 'IRCH', 'JRCH', 'ISEG', 'IREACH', 'RCHLEN', 'DEM_ADJ']
df_seg_rch_loc = df[cols]
#df2 = pd.DataFrame(columns=cols)

for i in range(NSEG):
    # for i in range(313, 314, 1):
    fig, ax = plt.subplots(1, 2)
    fig.set_size_inches(10, 4)

    segi = df_seg_rch_loc[df_seg_rch_loc['ISEG'] == i+1]
#    print(segi)
    segi_sorted = segi.sort_values(by='IREACH')  # Back later
#    print(segi)
    if segi.shape[0] > 1:
        check_DEM_ADJ = segi_sorted['DEM_ADJ'].diff()
        #print(f'Dimension of check_DEM_ADJ={check_DEM_ADJ.shape[0]}')

        max_change_DEM_ADJ = max(check_DEM_ADJ[1:])

        if max_change_DEM_ADJ >= 0:
            print(f'\nWARNING: i={i}, max_change_DEM_ADJ={max_change_DEM_ADJ}')
            #

        # PLOT
        # Linear regression
        y = segi_sorted['DEM_ADJ'].copy()
        npoints = len(y)
        x = range(1, npoints+1, 1)
        #print(f'{y} \n')
        #ax[0].plot(x, y, 'o', )

        ax[0].scatter(x, y, s=sz, facecolors='#a6dba0',
                      edgecolors='#008837', linewidth=0.25, alpha=1, zorder=0)
        ax[0].set_title(f'ISEG={i}')
        ax[0].tick_params(axis="x", direction="in", pad=pad_val)
        ax[0].tick_params(axis="y", direction="in", pad=pad_val)

        # Fit and plot
        if npoints >= 3:
            m, b = fit_line2(x, y)
            # could be just 2 if you are only drawing a straight line...
            N = 100
            points = np.linspace(min(x), max(x), N)
            ax[0].plot(points, m*points + b, linewidth=0.5,
                       alpha=0.5, zorder=1)  # Line plot

            ax[0].set_xlabel('IREACH ID')
            ax[0].set_ylabel('ISEG Elevation (m)')

            # Subplot2: Adjust elevations and plot
            '''
            y_new = m*x + b
            ax[0].scatter(x, y_new, s=sz, facecolors='#253494',
                          edgecolors='#2c7fb8', linewidth=0.1, alpha=1, zorder=2)

            ax[0].set_xlabel('IREACH ID')
            ax[0].set_ylabel('ISEG Elevation (m)')
            '''
        else:
            print(
                f'\nWARNING: Skip regression analysis for REACH ID = {i+1} because npoints <= 3')

#            plt.show()

        # Save figures
        ofile = odir + 'SEG_' + str(i+1).rjust(2, '0') + '.png'
        fig.savefig(ofile, dpi=100, transparent=False, bbox_inches='tight')

    else:
        print(f'\nATTENTION: Found only one SEGMENT for REACH ID {i+1}.')

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
# Prepare Data Set 6
IRDFLG = 0  # printing input data specified for this stress period
IPTFLG = 0  # printing streamflow-routing results during this stress period
ICALC = 0  # method used to calculate stream depth in this segment
# OUTSEG = 999  # the downstream stream segment that receives tributary inflow from the last downstream reach of this segment
# the upstream segment from which water is diverted (or withdrawn) to supply inflow to this stream segment
# IUPSEG = 999
FLOW = 100  # streamflow (L3/T)
# the volumetric rate of the diffuse overland runoff
# that enters the stream segment (L3/T)
RUNOFF = 10
# the volumetric rate per unit area of water removed by evapotranspiration
# directly from the stream channel (L3/T)
ETSW = 1
# the volumetric rate per unit area of water added by precipitation
# directly on the stream channel (L3/T)
PPTSW = 0.5
# -----------------------------------------------------------------------------
# HCOND1: Hydraulic conductivity of the streambed at the upstream end of this segment (L3/T)
HCOND1 = 1  # m3/day
# Thickness of streambed material at the upstream end of this segment (L3/T)
THICKM1 = 5  # m
# Elevation of the top of the streambed at the upstream end of this segment (L)
ELEVUP = 100  # meter
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
WIDTH2 = 100  # meter
# DEPTH2: Average depth of water in the channel at the downstream end of this segment (L)
DEPTH2 = 100  # meter


#
'''
col2 = ['NSEG', 'ICALC', 'OUTSEG', 'IUPSEG', 'FLOW', 'RUNOFF', 'ETSW', 'PPTSW']
df6 = pd.DataFrame(columns=col2)
for i in range(NSEG):
    df6.loc[i, 'NSEG'] = dfSEG['ISEG'].iloc[i]
    df6.loc[i, 'ICALC'] = ICALC
    df6.loc[i, 'OUTSEG'] = dfSEG['OUTSEG'].iloc[i]
    df6.loc[i, 'IUPSEG'] = dfSEG['IUPSEG'].iloc[i]
    df6.loc[i, 'FLOW'] = FLOW
    df6.loc[i, 'RUNOFF'] = RUNOFF
    df6.loc[i, 'ETSW'] = ETSW
    df6.loc[i, 'PPTSW'] = PPTSW
'''
#
fid.write("%d\t%d\t%d\n" % (NSEG, IRDFLG, IPTFLG))

for i in range(NSEG):
    fid.write("%d\t%d\t%d\t%d\t%f\t%f\t%f\t%f\n" % (
        dfSEG['ISEG'].iloc[i], ICALC, dfSEG['OUTSEG'].iloc[i], dfSEG['IUPSEG'].iloc[i], FLOW, RUNOFF, ETSW, PPTSW))
    fid.write("%f\t%f\t%f\t%f\t%f\n" %
              (HCOND1, THICKM1, ELEVUP, WIDTH1, DEPTH1))
    fid.write("%f\t%f\t%f\t%f\t%f\n" %
              (HCOND2, THICKM2, ELEVDN, WIDTH2, DEPTH2))
fid.close()

#df6.to_csv(ofile1, index=False)
print(f'Saved the sfr2 file at {ofile}\n')


'''
# Define variables for Data Set 6
NSEG = 536

iseg = df['ISEG']
iseg_rs = iseg.values.reshape(nrows, ncols)
ireach = df['IREACH']
ireach_rs = ireach.values.reshape(nrows, ncols)
rchlen = df['RCHLEN']
rchlen_rs = rchlen.values.reshape(nrows, ncols)


plt.imshow(iseg_rs)
cols = ['KRCH', 'IRCH', 'JRCH', 'ISEG', 'IREACH', 'RCHLEN']
df_loc = pd.DataFrame(columns=cols)
count = 0
for i in range(nrows):
    for j in range(ncols):
        if iseg_rs[i, j] != 0:
            df_loc.loc[count, 'KRCH'] = 1
            df_loc.loc[count, 'IRCH'] = i+1
            df_loc.loc[count, 'JRCH'] = j+1
            df_loc.loc[count, 'ISEG'] = iseg_rs[i, j]
            df_loc.loc[count, 'IREACH'] = ireach_rs[i, j]
            df_loc.loc[count, 'RCHLEN'] = rchlen_rs[i, j]
            count += 1
ofile1 = '../output/sfr/df_loc.csv'
df_loc.to_csv(ofile1, index=False)
print('Saved the first part of sfr2 at {ofile1} \n')
# Prepare Data Set 6
'''


# REFERENCES
# https://water.usgs.gov/nrp/gwsoftware/modflow2000/MFDOC/index.html?sfr.htm
