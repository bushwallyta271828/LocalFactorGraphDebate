"""The three curve panels (05, 08, 10), drawn from the retained summary.

No simulation or bound fitting happens here.
"""
import math

def plot(report, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import ScalarFormatter, NullLocator
    cells, core_curve = report['cells'], report['core_curve']
    fig, ax = plt.subplots(figsize=(8.1, 5.1))
    hs = [c['h'] for c in cells]
    centers = [c['finite_midpoint'] for c in cells]
    lo, hi = ([c['finite_mean_bounds'][i] for c in cells] for i in (0, 1))
    poplo, pophi = ([c['finite_approx_population_95_bounds'][i] for c in cells] for i in (0, 1))
    core_hs = [c['h'] for c in core_curve]
    cores = [c['core_mean_upper_bound'] for c in core_curve]
    corelo, corehi = ([c['core_approx_population_95_bounds'][i] for c in core_curve] for i in (0,1))
    ax.fill_between(hs, poplo, pophi, color='#2166ac', alpha=.13)
    ax.errorbar(hs, centers, yerr=[[m-l for m,l in zip(centers,lo)], [u-m for m,u in zip(centers,hi)]],
                color='#2166ac', fmt='o-', capsize=3, markersize=4, label='Mean absolute debate error', zorder=3)
    optimized=report.get('core_method')=='optimized'
    label='Mean minimum core oscillation' if optimized else 'Mean core oscillation'
    ax.plot(core_hs, cores, 'o-', color='#c76c27', lw=1.8, markersize=2.5, label=label)
    if optimized and any(c['core_optimization_relative_full_gap']>1e-6 for c in core_curve):
        by_h={c['h']:c for c in core_curve}
        ax.errorbar(hs,[by_h[h]['core_mean_upper_bound'] for h in hs],yerr=[[by_h[h]['core_mean_upper_bound']-by_h[h]['core_mean_lower_bound'] for h in hs],[0]*len(hs)],fmt='none',color='#c76c27',capsize=3)
    if report.get('show_greedy'):
        ax.plot(core_hs,[c['greedy_core_mean_upper_bound'] for c in core_curve],':',color='#777777',lw=1.4,label='Previous greedy core bound')
    ax.fill_between(core_hs, corelo, corehi, color='#c76c27', alpha=.1)
    if report.get('ensemble_bound'):
        ax.plot(core_hs,[c['ensemble_error_upper_bound'] for c in core_curve],
                color='#2b8c67',lw=1.8,label='Ensemble upper bound')
    if report.get('absolute_lower_bound'):
        curve = report['lower_curve']
        ax.plot([c['h'] for c in curve],
                [c['absolute_error_lower_bound'] or math.nan for c in curve],
                color='#8060a9', lw=1.8, label='Expected absolute-error lower bound')
    ax.set(xscale='log', yscale='log', xlabel='Moves per player, h', ylabel='Mean absolute logit error')
    ticks = [h for h in [1,2,5,10,20,50,100,200,500,1000] if min(hs)<=h<=max(hs)]
    ax.set_xticks(ticks or hs)
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.xaxis.set_minor_locator(NullLocator())
    ax.spines[['top','right']].set_visible(False)
    ax.grid(alpha=.18)
    handles, labels = ax.get_legend_handles_labels()
    if report.get('ensemble_bound'):
        index = labels.index('Ensemble upper bound')
        handles.insert(0, handles.pop(index))
        labels.insert(0, labels.pop(index))
    if report.get('absolute_lower_bound'):
        index = labels.index('Expected absolute-error lower bound')
        handles.append(handles.pop(index))
        labels.append(labels.pop(index))
    ax.legend(handles, labels, frameon=False)
    fig.tight_layout()
    fig.savefig(output,dpi=220)
    plt.close(fig)
