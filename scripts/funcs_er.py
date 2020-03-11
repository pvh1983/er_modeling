import os
import statsmodels.api as sm
from scipy.stats import linregress


def gen_outdir(odir):
    # odir = '../output/check_top_ele'
    if not os.path.exists(odir):  # Make a new directory if not exist
        os.makedirs(odir)
        print(f'\nCreated directory {odir}\n')


def fit_line1(x, y):
    """Return slope, intercept of best fit line."""
    # Remove entries where either x or y is NaN.
    clean_data = pd.concat([x, y], 1).dropna(0)  # row-wise
    (_, x), (_, y) = clean_data.iteritems()
    slope, intercept, r, p, stderr = linregress(x, y)
    return slope, intercept  # could also return stderr


def fit_line2(x, y):
    """Return slope, intercept of best fit line."""
    X = sm.add_constant(x)
    model = sm.OLS(y, X, missing='drop')  # ignores entires where x or y is NaN
    fit = model.fit()
    # could also return stderr in each via fit.bse
    return fit.params[1], fit.params[0]


def check_IREACH(segi, fig, ax):
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
        ofile = odir + 'SEG_' + str(i+1).rjust(3, '0') + '.png'
        fig.savefig(ofile, dpi=100, transparent=False, bbox_inches='tight')

    else:
        print(f'\nATTENTION: Found only one SEGMENT for REACH ID {i+1}.')
