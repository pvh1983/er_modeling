import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

'''

'''

#
# ifile = r'../input/stream.csv'
ifile = r'../input/hru_params2.csv'
df_org = pd.read_csv(ifile)
print(f'Reading file {ifile} \n')
df = df_org[df_org['ISEG'] != 0]

# MODFLOW paramete
nrows, ncols = 419, 328


# drop duplicate cells to get SEG and connected SEG
col_tmp = ['ISEG', 'OUTSEG', 'IUPSEG', 'MAXREACH']
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
ofile = '../output/sfr/east_river.sfr'
fid = open(ofile, 'w')
# Write Date Set 1c
fid.write("%d\t%d\t%d\t%d\t%d\t%f\t%d\t%d\t\n" % (NSTRM, NSS, NSFRPAR,
                                                  NPARSEG, CONST, DLEAK, ISTCB1, ISTCB2))


# Prepare Data Set 2 (SEG and REACH)
cols = ['KRCH', 'IRCH', 'JRCH', 'ISEG', 'IREACH', 'RCHLEN']
df_seg_rch_loc = df[cols]
#df2 = pd.DataFrame(columns=cols)
for i in range(NSEG):
    segi = df_seg_rch_loc[df_seg_rch_loc['ISEG'] == i+1]
    segi = segi.sort_values(by='IREACH')
#    df2.loc[i, 'KRCH'] = df['KRCH'].iloc[i]
#    df2.loc[i, 'IRCH'] = df['IRCH'].iloc[i]
#    df2.loc[i, 'JRCH'] = df['JRCH'].iloc[i]
#    df2.loc[i, 'ISEG'] = df['ISEG'].iloc[i]
#    df2.loc[i, 'IREACH'] = df['IREACH'].iloc[i]
#    df2.loc[i, 'RCHLEN'] = df['RCHLEN'].iloc[i]
    fid.write(segi.to_string(index=False, header=False))
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
