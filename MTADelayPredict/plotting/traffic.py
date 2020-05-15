"""
Plot train traffic for a certain time window
"""
from MTADelayPredict.subway_line import N_STOP_LIST
from MTADelayPredict.utils import stop_info

def plot_traffic(start_time, end_time, schedule_df):
    import matplotlib.pyplot as plt
    import matplotlib.lines as mlines

    font = {'family': 'normal',
            'weight': 'normal',
            'size': 22}

    plt.rc('font', **font)

    ax = None
    for col in schedule_df.columns:
        if col != 'index' and col != 'level_0':
            # g = sns.scatterplot(y='index', x=col, data=schedule_df)
            plot_df = schedule_df[['index', col]].dropna()
            if (plot_df.shape[0] == 0 or plot_df['index'].iloc[-1] < start_time) or (plot_df['index'].iloc[0] > end_time):
                #            print((plot_df['index'].iloc[-1],plot_df['index'].iloc[0]), (start_time, end_time))
                continue

            if ax:
                plot_df.plot(x='index', y=col, ax=ax, figsize=(40, 30), marker='o')
            #            schedule_df[['index', col]].dropna().plot(x='index', y=col, ax=ax,figsize=(40,30), marker='o')
            else:
                ax = plot_df.plot(x='index', y=col, ax=ax, figsize=(40, 30), marker='o')
    #            ax = schedule_df[['index', col]].dropna().plot(x='index', y=col, figsize=(40,30), marker='o')
    ax.set_yticks(ticks=range(len(N_STOP_LIST)))
    ax.set_yticklabels([stop_info.stop_id2name(s) for s in N_STOP_LIST])
    ax.grid(color='g', linestyle='dotted', linewidth=1)
    return ax