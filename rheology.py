import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import fsolve


def single_test_n(df, start, end, drop_columns):
    '''
    This function returns a single test from Jenny Bennett's overall rheology
    protocol for PXP shear-thinning hydrogels. There are a total of 7 tests in
    the following order: time sweep, frequency sweep, time sweep, strain sweep,
    time sweep, cyclic strain sweep, shear thinning test.

    Parameters
    ----------
    df: pandas dataframe
        read from excel file from overall test

    start: int
        row start of interval on excel spreadsheet

    end: int
        row end of interval on excel spreadsheet

    drop_columns: list
        list of column names in df to be dropped (columns with text or invalid
        data for interval)

    '''
    rheo_test = df[start-2:end-1].drop(columns=drop_columns).apply(pd.to_numeric)
    return rheo_test


def test_dict_n(df, start, end, drop_columns):
    '''
    This function returns a dictionary containing multiple tests for a single
    sample in Jenny Bennett's overall rheology protocol for PXP shear-thinning
    hydrogels.

    Parameters
    ----------
    df: pandas dataframe
        read from excel file from overall test

    start: int
        row start of interval on excel spreadsheet

    end: int
        row end of interval on excel spreadsheet

    drop_columns: list
        list of column names in df to be dropped (columns with text or invalid
        data for interval)

    '''
    rheo_data = {} # empty dictionary for tests

    # loop through each test using start/end points
    n = 0
    for s, e in zip(start, end):
        rheo_data[n] = single_test_n(df, s, e, drop_columns)
        n = n + 1
    return rheo_data


def all_tests_n(df):
    '''
    This function returns a dictionary containing all tests from a single
    sample (n) in Jenny Bennett's overall rheology protocol for PXP hydrogels.

    Paramters
    ---------
    df: pandas dataframe
        read from excel file from overall test

    Returns
    -------
    rheo_data: dict
        {0: time sweep, 1: frequency sweep, 2: time sweep, 3: strain sweep, 4:
        time sweep, 5: cyclic strain sweep, 6: shear thinning}
    '''
    # 1: time sweep, 2: frequency sweep, 3: time sweep, 4: strain sweep, 5: time sweep
    drop_columns = ['Status', 'Viscosity', 'Speed'] # columns containing text or no measurement in tests 1-6
    start_1to5 = [3, 94, 140, 231, 358] # where each test begins in excel
    end_1to5 = [82, 124, 218, 343, 437] # where each test ends in excel
    rheo_data = test_dict_n(df, start_1to5, end_1to5, drop_columns)

    # 6: cyclic strain sweep
    start_css = [452, 1065, 1099, 1711, 1745, 2357, 2391, 3003, 3037] # where each period begins in excel
    end_css = [1051, 1083, 1697, 1729, 2343, 2375, 2989, 3021, 3635] # where each period ends in excel
    rheo_data_css = test_dict_n(df, start_css, end_css, drop_columns)
    # create list of css periods
    objs = []
    for n in range(len(start_css)):
        objs.append(rheo_data_css[n])

    # combine cyclic strain sweep periods and add to final dictionary
    rheo_data[5] = pd.concat(objs, axis=0, join='outer', ignore_index=False,
                             keys=None,levels=None, names=None,
                             verify_integrity=False, copy=True)

    # 7: shear thinning
    drop_columns_2 = ['Storage Modulus', 'Loss Modulus', 'Angular Frequency', 'Status'] # columns to be dropped with no data
    rheo_data[6] = single_test_n(df, 3651, 3678, drop_columns_2)

    # create zoomed in cyclic strain sweep
    objs_zoom = [rheo_data_css[0][499:], rheo_data_css[1], rheo_data_css[2][:100]]

    # combine zoom cyclic strain sweep periods and add to final dictionary
    rheo_data[7] = pd.concat(objs_zoom, axis=0, join='outer', ignore_index=False,
                             keys=None,levels=None, names=None,
                             verify_integrity=False, copy=True)

    return rheo_data


def all_tests(df1, df2=pd.DataFrame([]), df3=pd.DataFrame([]), df4=pd.DataFrame([]), df5=pd.DataFrame([])):
    out = []

    n1 = all_tests_n(df1)
    out.append(n1)

    if df2.empty==False:
        n2 = all_tests_n(df2)
        out.append(n2)

    if df3.empty==False:
        n3 = all_tests_n(df3)
        out.append(n3)

    if df4.empty==False:
        n4 = all_tests_n(df4)
        out.append(n4)

    if df5.empty==False:
        n5 = all_tests_n(df5)
        out.append(n5)

    return out


def single_test_avg_var(group, column, test):
    '''
    This function uses rheology data from Jenny Bennett's overall rheology
    protocol for PXP shear-thinning hydrogels. It returns a dataframe
    containing multiple samples and their average from the same test.

    Parameters
    ----------
    group: list of dictionaries from rheology.all_tests_n
        ex. txt = [rheology.all_tests_n(df_n1), rheology.all_tests_n(df_n2)]

    column: str
        column interested in extracting, ex. 'Storage Modulus'

    test: int
        call the test from group dictionary, ex. 0
    '''
    test_avg = pd.DataFrame() # create empty dataframe

    # loop through each n in group using specified column and test
    for n in range(len(group)):
        test_avg[column, 'n', n+1] = group[n][test][column]

    # take average value across a row
    test_avg['Mean'] = test_avg.mean(axis=1)
    return test_avg


def single_test_avg(var, group, test):
    '''
    This function uses rheology data from Jenny Bennett's overall rheology
    protocol for PXP shear-thinning hydrogels. It returns a dataframe
    containing average data from a single test with multiple samples.

    Parameters
    ----------
    group: list of dictionaries from rheology.all_tests_n
        ex. txt = [rheology.all_tests_n(df_n1), rheology.all_tests_n(df_n2)]

    var: list, str
        columns/variables interested in extracting, ex. ['Time', 'Storage
        Modulus', 'Loss Modulus']

    test: int
        call the test from group dictionary, ex. 0
    '''
    var_test = {}

    for v in var:
        var_test[v] = single_test_avg_var(group, v, test)


    avg_test = pd.DataFrame()

    for v in var:
        avg_test[v] = var_test[v]['Mean']

    return avg_test


def all_tests_avg(group):
    '''
    This function uses rheology data from Jenny Bennett's overall rheology
    protocol for PXP shear-thinning hydrogels. It returns a dictionary
    containing dataframes of average data from all tests with multiple samples.

    Parameters
    ----------
    group: list of dictionaries from rheology.all_tests_n
        ex. txt = [rheology.all_tests_n(df_n1), rheology.all_tests_n(df_n2)]
    '''
    all_tests_avg = {}

    var_ts = ['Time', 'Storage Modulus', 'Loss Modulus']
    var_fs = ['Angular Frequency', 'Storage Modulus', 'Loss Modulus']
    var_ss = ['Strain', 'Storage Modulus', 'Loss Modulus']
    var_st = ['Shear Rate', 'Viscosity']

    for i in (0, 2, 4, 5, 7):
        all_tests_avg[i] = single_test_avg(var_ts, group, i)

    all_tests_avg[1] = single_test_avg(var_fs, group, 1)
    all_tests_avg[3] = single_test_avg(var_ss, group, 3)
    all_tests_avg[6] = single_test_avg(var_st, group, 6)

    return all_tests_avg


def graph_modulus(df, x, y1, y2, y1legend, y2legend, ylabel, xlabel, xscale, title):
    '''
    This function graphs a rheology dataframe from "OverallTest_Jenny"
    oscillating tests using storage modulus and loss modulus.

    Parameters
    ----------
    df : dataframe
        Pandas dataframe from a single segment in overall rheology (e.g first
        time sweep test, 80 measuring points)

    x : column in dataframe, str
        Column contained in the dataframe df to be used as x values (e.g.
        'Time')

    y1 : column in dataframe, str
        Column contained in the dataframe df to be used as y1 values (e.g.
        'Storage Modulus')

    y2 : column in dataframe, str
        Column contained in the dataframe df to be used as y2 values (e.g.
        'Loss Modulus')

    y1legend : str
        String for labeling y1 in the legend

    y2 legend : str
        String for labeling y2 in the legend

    ylabel :  str
        String for labeling y axis

    xlabel : str
        String for labeling x axis

    xscale : "log" or "linear"

    title : str
        String for labeling the grpah title

    Returns
    -------
    Graph of y1 and y2 vs x.

    Example
    -------
    df = TS_1
    x = 'Time'
    y1 = 'Storage Modulus'
    y2 = 'Loss Modulus'
    y1legend = "G' Storage Modulus"
    y2legend = 'G" Loss Modulus'
    ylabel = 'G\' and G\" [Pa]'
    xlabel = 'Time [s]'
    title = 'Interval 1: Time Sweep, 10rad/s, 5% Strain'

    graph_modulus(df, x, y1, y2, y1legend, y2legend, ylabel, xlabel, title)
    '''

    # create figure for graphing
    fig, ax = plt.subplots(figsize=(6, 6))

    # graph y1 points and line
    df.plot(y=y1, x=x, kind='scatter', c='r', ax=ax, label=y1legend)
    df.plot(y=y1, x=x, kind='line', c='r', ax=ax, linewidth=0.5,
            label='')

    # graph loss modulus points and line
    df.plot(y=y2, x=x, kind='scatter', c='b', ax=ax, label=y2legend)
    df.plot(y=y2, x=x, kind='line', c='b', ax=ax, linewidth=0.5,
            label='')

    # legend location and change yscale to log
    plt.legend(loc='lower left', fontsize=14, framealpha=10)
    plt.yscale("log")
    plt.xscale(xscale)

    # set axis parameters
    ax.set_ylim(10**1, 10**4)
    ax.set_ylabel(ylabel, fontsize=18)
    ax.set_xlabel(xlabel, fontsize=18)
    ax.tick_params(length=7, labelsize=14)
    ax.tick_params(which='minor', length=4)
    ax.set_title(title, fontsize=20)

    # set axis on top layer and non transparent
    ax.set_zorder(1)
    ax.set_frame_on(True)

    return


def graph_viscosity(df, x, y1, y1legend, ylabel, xlabel, xscale, title):
    '''
    This function graphs a rheology dataframe from "OverallTest_Jenny"
    rotational tests using viscosity and shear rate.

    Parameters
    ----------
    df : dataframe
        Pandas dataframe from a single segment in overall rheology (e.g first
        time sweep test, 80 measuring points)

    x : column in dataframe, str
        Column contained in the dataframe df to be used as x values (e.g.
        'Time')

    y1 : column in dataframe, str
        Column contained in the dataframe df to be used as y1 values (e.g.
        'Storage Modulus')

    y1legend : str
        String for labeling y1 in the legend

    ylabel :  str
        String for labeling y axis

    xlabel : str
        String for labeling x axis

    xscale : "log" or "linear"

    title : str
        String for labeling the grpah title

    Returns
    -------
    Graph of y1 vs x.

    Example
    -------
    df = ST_7
    x = 'Shear rate'
    y1 = 'Viscosity'
    y1legend = "Viscosity"
    ylabel = 'Viscosity [Pa*s]'
    xlabel = 'Shear Rate [1/s]'
    title = 'Interval 7: Shear Thinning'

    graph_viscosity(df, x, y1, y1legend, ylabel, xlabel, title)
    '''

    # create figure for graphing
    fig, ax = plt.subplots(figsize=(6, 6))

    # graph y1 points and line
    df.plot(y=y1, x=x, kind='scatter', c='r', ax=ax, label=y1legend)
    df.plot(y=y1, x=x, kind='line', c='r', ax=ax, linewidth=0.5,
            label='')

    # graph loss modulus points and line
    df.plot(y=y2, x=x, kind='scatter', c='b', ax=ax, label=y2legend)
    df.plot(y=y2, x=x, kind='line', c='b', ax=ax, linewidth=0.5,
            label='')

    # legend location and change yscale to log
    plt.legend(loc='upper right', fontsize=14, framealpha=10)
    plt.yscale("log")
    plt.xscale(xscale)

    # set axis parameters
    ax.set_ylim(10**0, 10**4)
    ax.set_ylabel(ylabel, fontsize=18)
    ax.set_xlabel(xlabel, fontsize=18)
    ax.tick_params(length=7, labelsize=14)
    ax.tick_params(which='minor', length=4)
    ax.set_title(title, fontsize=20)

    # set axis on top layer and non transparent
    ax.set_zorder(1)
    ax.set_frame_on(True)

    return


def graph_modulus_comparison(df1, x, y1, y2, y1legend_df1, y2legend_df1, ylabel, xlabel, xscale, title, s=50, l=1, df2=pd.Series([]), y1legend_df2='', y2legend_df2='', df3=pd.Series([]), y1legend_df3='', y2legend_df3='', df4=pd.Series([]), y1legend_df4='', y2legend_df4='',ss=False):
    '''
    This function graphs a comparison of rheology dataframes from
    "OverallTest_Jenny" oscillating tests using storage modulus and
    loss modulus.

    Parameters
    ----------
    df1 : dataframe
        Pandas dataframe from a single segment in overall rheology (e.g first
        time sweep test, 80 measuring points)

    df2 : dataframe
        Pandas dataframe from a single segment in overall rheology (e.g first
        time sweep test, 80 measuring points)

    df3/df4 : dataframe (optional)
        Pandas dataframe from a single segment in overall rheology (e.g first
        time sweep test, 80 measuring points)

    x : column in dataframe, str
        Column contained in the dataframe df to be used as x values (e.g.
        'Time')

    y1 : column in dataframe, str
        Column contained in the dataframe df to be used as y1 values (e.g.
        'Storage Modulus')

    y2 : column in dataframe, str
        Column contained in the dataframe df to be used as y2 values (e.g.
        'Loss Modulus')

    y1legend_df1 : str
        String for labeling y1_df1 in the legend

    y2legend_df1 : str
        String for labeling y2_df1 in the legend

    y1legend_df2 : str
        String for labeling y1_df2 in the legend

    y2legend_df2 : str
        String for labeling y2_df2 in the legend

    ylabel :  str
        String for labeling y axis

    xlabel : str
        String for labeling x axis

    xscale : "log" or "linear"

    title : str
        String for labeling the grpah title

    ss : True/False
        Changes x range for strain sweep (10-500% strain)

    Returns
    -------
    Graph of y1 and y2 vs x.

    Example
    -------
    df = TS_1
    x = 'Time'
    y1 = 'Storage Modulus'
    y2 = 'Loss Modulus'
    y1legend = "G' Storage Modulus"
    y2legend = 'G" Loss Modulus'
    ylabel = 'G\' and G\" [Pa]'
    xlabel = 'Time [s]'
    title = 'Interval 1: Time Sweep, 10rad/s, 5% Strain'

    graph_modulus(df, x, y1, y2, y1legend, y2legend, ylabel, xlabel, title)
    '''
    # create figure for graphing
    fig, ax = plt.subplots(figsize=(6, 6))

    # graph storage modulus points and line df1
    df1.plot(y=y1, x=x, kind='scatter', c='red', ax=ax, s=s, label=y1legend_df1, zorder=9)
    df1.plot(y=y1, x=x, kind='line', c='red', ax=ax, linewidth=1,
            label='', zorder=10)
    # graph loss modulus points and line df1
    df1.plot(y=y2, x=x, kind='scatter', c='pink', marker="$\u25EF$",
             ax=ax, s=s, label=y2legend_df1, zorder=1)
    df1.plot(y=y2, x=x, kind='line', style='--', c='pink', ax=ax, linewidth=l,
            label='', zorder=2)

    if df2.empty==False:
        # graph storage modulus points and line df2
        df2.plot(y=y1, x=x, kind='scatter', c='blue', ax=ax, s=s, label=y1legend_df2, zorder=11)
        df2.plot(y=y1, x=x, kind='line', c='blue', ax=ax, linewidth=l,
                label='', zorder=12)
        # graph loss modulus points and line df2
        df2.plot(y=y2, x=x, kind='scatter', c='lightblue', marker="$\u25EF$",
                 ax=ax, s=s, label=y2legend_df2, zorder=3)
        df2.plot(y=y2, x=x, kind='line', style='--', c='lightblue', ax=ax, linewidth=l,
                 label='', zorder=4)

    if df3.empty==False:
        # graph storage modulus points and line df3
        df3.plot(y=y1, x=x, kind='scatter', c='forestgreen', ax=ax, s=s, label=y1legend_df3, zorder=13)
        df3.plot(y=y1, x=x, kind='line', c='forestgreen', ax=ax, linewidth=l,
                label='', zorder=14)
        # graph loss modulus points and line df3
        df3.plot(y=y2, x=x, kind='scatter', c='lightgreen', marker="$\u25EF$",
                 ax=ax, s=s, label=y2legend_df3, zorder=5)
        df3.plot(y=y2, x=x, kind='line', style='--', c='lightgreen', ax=ax, linewidth=l,
                 label='', zorder=6)

    if df4.empty==False:
        # graph storage modulus points and line df3
        df4.plot(y=y1, x=x, kind='scatter', c='orange', ax=ax, s=s, label=y1legend_df4, zorder=15)
        df4.plot(y=y1, x=x, kind='line', c='orange', ax=ax, linewidth=l,
                label='', zorder=16)
        # graph loss modulus points and line df3
        df4.plot(y=y2, x=x, kind='scatter', c='navajowhite', marker="$\u25EF$",
                 ax=ax, s=s, label=y2legend_df4, zorder=7)
        df4.plot(y=y2, x=x, kind='line', style='--', c='navajowhite', ax=ax, linewidth=l,
                 label='', zorder=8)

    # legend location and change yscale to log
    plt.legend(loc='center left', fontsize=14, framealpha=10, bbox_to_anchor=(1, 0.5))
    plt.yscale("log")
    plt.xscale(xscale)

    # set axis parameters
    if ss==True: # change x limit for strain sweep
        ax.set_xlim(50, 500)
        ax.set_ylim(50, 10000)
    else:
        ax.set_ylim(10**1, 10**4)
    ax.set_ylabel(ylabel, fontsize=18)
    ax.set_xlabel(xlabel, fontsize=18)
    ax.tick_params(length=7, labelsize=14)
    ax.tick_params(which='minor', length=4)
    ax.set_title(title, fontsize=20)

    # set axis on top layer and non transparent
    ax.set_zorder(1)
    ax.set_frame_on(True)

    return


def graph_recovery_comparison(df1, x, y1, y2, y1legend_df1, y2legend_df1, ylabel, xlabel, xscale, title, s=50, df2=pd.Series([]), y1legend_df2='', y2legend_df2='', df3=pd.Series([]), y1legend_df3='', y2legend_df3='', df4=pd.Series([]), y1legend_df4='', y2legend_df4='', zoom=False):
    '''
    This function graphs a comparison of rheology dataframes from
    "OverallTest_Jenny" oscillating tests using storage modulus and
    loss modulus in cyclic strain tests.

    Parameters
    ----------
    df1 : dataframe
        Pandas dataframe from a single segment in overall rheology (e.g first
        time sweep test, 80 measuring points)

    df2 : dataframe
        Pandas dataframe from a single segment in overall rheology (e.g first
        time sweep test, 80 measuring points)

    df3 : dataframe (optional)
        Pandas dataframe from a single segment in overall rheology (e.g first
        time sweep test, 80 measuring points)

    x : column in dataframe, str
        Column contained in the dataframe df to be used as x values (e.g.
        'Time')

    y1 : column in dataframe, str
        Column contained in the dataframe df to be used as y1 values (e.g.
        'Storage Modulus')

    y2 : column in dataframe, str
        Column contained in the dataframe df to be used as y2 values (e.g.
        'Loss Modulus')

    y1legend_df1 : str
        String for labeling y1_df1 in the legend

    y2legend_df1 : str
        String for labeling y2_df1 in the legend

    y1legend_df2 : str
        String for labeling y1_df2 in the legend

    y2legend_df2 : str
        String for labeling y2_df2 in the legend

    ylabel :  str
        String for labeling y axis

    xlabel : str
        String for labeling x axis

    xscale : "log" or "linear"

    title : str
        String for labeling the grpah title

    Returns
    -------
    Graph of y1 and y2 vs x.

    Example
    -------
    df = TS_1
    x = 'Time'
    y1 = 'Storage Modulus'
    y2 = 'Loss Modulus'
    y1legend = "G' Storage Modulus"
    y2legend = 'G" Loss Modulus'
    ylabel = 'G\' and G\" [Pa]'
    xlabel = 'Time [s]'
    title = 'Interval 1: Time Sweep, 10rad/s, 5% Strain'

    graph_modulus(df, x, y1, y2, y1legend, y2legend, ylabel, xlabel, title)
    '''
    # convert to minutes
    x_min = 'Time (min)'

    if zoom == False:
        df1[x_min] = (df1[x] - df1[x][450])/60
        if df2.empty==False:
            df2[x_min] = (df2[x] - df2[x][450])/60
        if df3.empty==False:
            df3[x_min] = (df3[x] - df3[x][450])/60
        if df4.empty==False:
            df4[x_min] = (df4[x] - df4[x][450])/60

        fs = 8

    else:

        df1[x_min] = (df1[x] - df1[x][949])/60
        if df2.empty==False:
            df2[x_min] = (df2[x] - df2[x][949])/60
        if df3.empty==False:
            df3[x_min] = (df3[x] - df3[x][949])/60
        if df4.empty==False:
            df4[x_min] = (df4[x] - df4[x][949])/60

        fs = 6

    # create figure for graphing
    fig, ax = plt.subplots(figsize=(fs, fs))

    # highlight high strain regions
    if zoom == False:
        st1 = (4898 - 3098)/60
        end1 = (4955 - 3098)/60

        st2 = (6758 - 3098)/60
        end2 = (6815 - 3098)/60

        st3 = (8618 - 3098)/60
        end3 = (8675 - 3098)/60

        st4 = (10478 - 3098)/60
        end4 = (10535 - 3098)/60

        plt.axvspan(st1, end1, color='lightgray', zorder=0)
        plt.axvspan(st2, end2, color='lightgray', zorder=0)
        plt.axvspan(st3, end3, color='lightgray', zorder=0)
        plt.axvspan(st4, end4, color='lightgray', zorder=0)

    else:
        st1 = (4898 - 4595)/60
        end1 = (4955 - 4595)/60

        plt.axvspan(st1, end1, color='lightgray', zorder=0)

    # graph storage modulus points and line df1
    df1.plot(y=y1, x=x_min, kind='scatter', c='r', ax=ax, s=s, label=y1legend_df1, zorder=5)
    df1.plot(y=y1, x=x_min, kind='line', c='r', ax=ax, linewidth=0.5,
            label='', zorder=5)
    # graph loss modulus points and line df1
    df1.plot(y=y2, x=x_min, kind='scatter', c='pink', marker="$\u25EF$",
             ax=ax, s=s, label=y2legend_df1, zorder=1)
    df1.plot(y=y2, x=x_min, kind='line', c='pink', ax=ax, linewidth=0.5,
            label='', zorder=1)

    if df2.empty==False:
        # graph storage modulus points and line df2
        df2.plot(y=y1, x=x_min, kind='scatter', c='b', ax=ax, s=s, label=y1legend_df2, zorder=6)
        df2.plot(y=y1, x=x_min, kind='line', c='b', ax=ax, linewidth=0.5,
                 label='', zorder=6)
        # graph loss modulus points and line df2
        df2.plot(y=y2, x=x_min, kind='scatter', c='lightblue', marker="$\u25EF$",
                 ax=ax, s=s, label=y2legend_df2, zorder=2)
        df2.plot(y=y2, x=x_min, kind='line', c='lightblue', ax=ax, linewidth=0.5,
                 label='', zorder=2)

    if df3.empty==False:
        # graph storage modulus points and line df3
        df3.plot(y=y1, x=x_min, kind='scatter', c='forestgreen', ax=ax, s=s, label=y1legend_df3, zorder=7)
        df3.plot(y=y1, x=x_min, kind='line', c='forestgreen', ax=ax, linewidth=0.5,
                label='', zorder=7)
        # graph loss modulus points and line df3
        df3.plot(y=y2, x=x_min, kind='scatter', c='lightgreen', marker="$\u25EF$",
                 ax=ax, s=s, label=y2legend_df3, zorder=3)
        df3.plot(y=y2, x=x_min, kind='line', c='lightgreen', ax=ax, linewidth=0.5,
                 label='', zorder=3)

    if df4.empty==False:
        # graph storage modulus points and line df3
        df4.plot(y=y1, x=x_min, kind='scatter', c='orange', ax=ax, s=s, label=y1legend_df4, zorder=8)
        df4.plot(y=y1, x=x_min, kind='line', c='orange', ax=ax, linewidth=0.5,
                label='', zorder=8)
        # graph loss modulus points and line df3
        df4.plot(y=y2, x=x_min, kind='scatter', c='navajowhite', marker="$\u25EF$",
                 ax=ax, s=s, label=y2legend_df4, zorder=4)
        df4.plot(y=y2, x=x_min, kind='line', c='navajowhite', ax=ax, linewidth=0.5,
                 label='', zorder=4)

    # set axis parameters
    ax.set_ylim(-1, 10**5)
    ax.set_ylabel(ylabel, fontsize=18)
    ax.set_xlabel(xlabel, fontsize=18)
    ax.tick_params(length=7, labelsize=14)
    ax.tick_params(which='minor', length=4)
    ax.set_title(title, fontsize=20)
    ax.set_yscale('symlog')
    ax.set_xscale(xscale)

    # set axis on top layer and non transparent
    ax.set_zorder(1)
    ax.set_frame_on(True)

    # legend location and change yscale to log
    plt.legend(loc='center left', fontsize=14, framealpha=10, bbox_to_anchor=(1, 0.5))

    return


def graph_viscosity_comparison(df1, x, y1, y1legend_df1, ylabel, xlabel, xscale, title, df2=pd.Series([]), y1legend_df2='', df3=pd.Series([]), y1legend_df3='', df4=pd.Series([]), y1legend_df4=''):
    '''
    This function graphs a rheology dataframe from "OverallTest_Jenny"
    rotational tests using viscosity and shear rate.

    Parameters
    ----------
    df1 : dataframe
        Pandas dataframe from a single segment in overall rheology (e.g first
        time sweep test, 80 measuring points)

    df2 : dataframe
        Pandas dataframe from a single segment in overall rheology (e.g first
        time sweep test, 80 measuring points)

    x : column in dataframe, str
        Column contained in the dataframe df to be used as x values (e.g.
        'Time')

    y1 : column in dataframe, str
        Column contained in the dataframe df to be used as y1 values (e.g.
        'Storage Modulus')

    y1legend_df1 : str
        String for labeling y1_df1 in the legend

    y1legend_df2 : str
        String for labeling y1_df2 in the legend

    ylabel :  str
        String for labeling y axis

    xlabel : str
        String for labeling x axis

    xscale : "log" or "linear"

    title : str
        String for labeling the grpah title

    Returns
    -------
    Graph of y1 vs x.

    Example
    -------
    df = ST_7
    x = 'Shear rate'
    y1 = 'Viscosity'
    y1legend = "Viscosity"
    ylabel = 'Viscosity [Pa*s]'
    xlabel = 'Shear Rate [1/s]'
    title = 'Interval 7: Shear Thinning'

    graph_viscosity(df, x, y1, y1legend, ylabel, xlabel, title)
    '''

    # create figure for graphing
    fig, ax = plt.subplots(figsize=(6, 6))

    # graph y1 points and line from df1
    df1.plot(y=y1, x=x, kind='scatter', s=50, c='r', ax=ax, label=y1legend_df1)
    df1.plot(y=y1, x=x, kind='line', c='r', ax=ax, linewidth=2,
            label='')

    if df2.empty==False:
        # graph y1 points and line from df2
        df2.plot(y=y1, x=x, kind='scatter', s=50, c='b', ax=ax, label=y1legend_df2)
        df2.plot(y=y1, x=x, kind='line', c='b', ax=ax, linewidth=2,
                 label='')

    if df3.empty==False:
        # graph y1 points and line from df3
        df3.plot(y=y1, x=x, kind='scatter', s=50, c='forestgreen', ax=ax, label=y1legend_df3)
        df3.plot(y=y1, x=x, kind='line', c='forestgreen', ax=ax, linewidth=2,
                 label='')

    if df4.empty==False:
        # graph y1 points and line from df3
        df4.plot(y=y1, x=x, kind='scatter', s=50, c='orange', ax=ax, label=y1legend_df4)
        df4.plot(y=y1, x=x, kind='line', c='orange', ax=ax, linewidth=2,
                 label='')

    # legend location and change yscale to log
    plt.legend(loc='upper right', fontsize=14, framealpha=10)
    plt.yscale("log")
    plt.xscale(xscale)

    # set axis parameters
    ax.set_ylim(10**0, 10**4)
    ax.set_ylabel(ylabel, fontsize=18)
    ax.set_xlabel(xlabel, fontsize=18)
    ax.tick_params(length=7, labelsize=14)
    ax.tick_params(which='minor', length=4)
    ax.set_title(title, fontsize=20)

    # set axis on top layer and non transparent
    ax.set_zorder(1)
    ax.set_frame_on(True)

    return


def storage_modulus(group):
    '''
    This function returns a dataframe summarizing the average storage modulus from Jenny Bennett's
    overall rheology test for shear-thinning PXP hydrogels.

    Parameters
    ----------
    group : list of dictionaries
        each dictionary is from a single n processed in rheology.all_tests_n(df)
        the list includes one dictionary per n

    name : list, str
        names for the output dataframe columns

    Example
    -------
    txt_n1 = rheology.all_tests_n(df_n1)
    txt_n2 = rheology.all_tests_n(df_n2)
    txt_n3 = rheology.all_tests_n(df_n3)

    txt = [txt_n1, txt_n2, txt_n3]
    name = ["n1 G' [Pa]", "n2 G' [Pa]", "n3 G' [Pa]"]

    storage_modulus(txt, name)
    '''
    # average storage modulus for time sweep period 0, 2, 4
    name = ["n1 G' [Pa]", "n2 G' [Pa]", "n3 G' [Pa]", "n4 G' [Pa]", "n5 G' [Pa]"]
    sm = [] # empty list of average G' for all n

    for i in (0, 2): # loop through each period 0, 2, 4
        sm_n = []  # empty list of average G' for single n
        for n in range(len(group)): # loop through each n for each period
            sm_n.append(group[n][i][59:]['Storage Modulus'].mean()) # append mean G'
        sm.append(sm_n)

    sm_df_raw = pd.DataFrame(sm) # G' into dataframe
    sm_df_raw['Test'] = ['Time Sweep 0', 'Time Sweep 2'] # label each row in dataframe

    sm_df_int = sm_df_raw.set_index(sm_df_raw['Test']) # reset index to include label
    sm_df = sm_df_int.drop(['Test'], axis=1) # drop test label column since we used it as index

    for i in range(len(name)):
        sm_df = sm_df.rename(columns={i: name[i]}) # rename columns to include number of n's

    sm_df['Mean'] = sm_df.mean(axis=1) # take the mean from each n in a single period

    sm_final = []
    for i in range(len(group)):
        sm_final.append(sm_df[name[i]].mean())

    return sm_final # return list of average storage modulus per n


def crossover_step1(df, cotype=1):
    '''
    (Step 1/3) This function returns two dataframe entries describing the crossover from a single strain sweep
    in Jenny Bennett's overall rheology test for shear-thinning PXP hydrogels.

    Parameters
    ----------
    df : dataframe
        dataframe from strain sweep with an n of 1

    cotype : int
        1 (strain) or 2 (frequency)

    Example
    -------
    txt_n1 = rheology.all_tests_n(df_n1)

    crossover_step1(txt_n1[3])
    '''
    if cotype==1:
        df['position'] = df['Loss Modulus'] > df['Storage Modulus'] # determine where G" > G'
    else:
        df['position'] = df['Storage Modulus'] > df['Loss Modulus']

    df['pre_position'] = df['position'].shift(1) # determine entry just before G" > G'
    df['crossover'] = np.where(df['position'] == df['pre_position'], False, True) # flag intersection between the two
    df = df.dropna() # drop rows with NaN values

    co_l_in = df.loc[df['crossover'] == True] # store crossover row (low crossover)
    co_l = co_l_in.iloc[-1:]
    index = co_l.index.values # determine index of crossover

    co_h = pd.DataFrame(df.loc[index-1]) # store previous entry before crossover (high crossover)

    return co_l, co_h # return low crossover and high crossover


def crossover_step2(co_l, co_h, cotype=1):
    '''
    (Step 2/3) This function returns the crossover strain% from a single strain sweep
    in Jenny Bennett's overall rheology test for shear-thinning PXP hydrogels.

    Parameters
    ----------
    co_l : dataframe entry from rheology.crossover_step1(df)

    co_h : dataframe entry from rheology.crossover_step1(df)

    cotype : int
        1 (strain) or 2 (frequency)

    Example
    -------
    txt_n1 = rheology.all_tests_n(df_n1)

    co_l, co_h = rheology.crossover_step1(txt_n1[3])

    rheology.crossover_step2(co_l, co_h)
    '''
    if cotype==1:
        a_x = co_h['Strain'].values # define x from high entry
        c_x = co_l['Strain'].values # define x from low entry
    else:
        a_x = co_h['Angular Frequency'].values
        c_x = co_l['Angular Frequency'].values

    a_y = co_h['Storage Modulus'].values # define y from high entry
    a_z = co_h['Loss Modulus'].values # define z from high entry

    c_y = co_l['Storage Modulus'].values # define y from low entry
    c_z = co_l['Loss Modulus'].values # define z from low entry

    # use solver below to interpolate between high and low entries for crossover
    def f(w):
        b_x = w[0] # crossover strain or frequency
        b_y = w[1] # crossover G'
        b_z = w[2] # crossover G"

        # 3 equations and 3 unknowns using loglog scale

        if cotype==1:
            range_x = np.log10(c_x[0] - a_x[0]) # range between high and low x values
            if a_y[0] < c_y[0]:
                range_y = np.log10(c_y[0] - a_y[0]) # range between high and low y values
                f1 = b_y - a_y[0] - 10**((np.log10(b_x - a_x[0])) / range_x*range_y)
            else:
                range_y = np.log10(a_y[0] - c_y[0]) # range between high and low y values
                f1 = b_y - a_y[0] + 10**((np.log10(b_x - a_x[0])) / range_x*range_y)

            if a_z[0] < c_z[0]:
                range_z = np.log10(c_z[0] - a_z[0]) # range between high and low z values
                f2 = b_z - a_z[0] - 10**((np.log10(b_x - a_x[0])) / range_x*range_z)
            else:
                range_z = np.log10(a_z[0] - c_z[0]) # range between high and low z values
                f2 = b_z - a_z[0] + 10**((np.log10(b_x - a_x[0])) / range_x*range_z)
        else:
            range_x = np.log10(a_x[0] - c_x[0]) # range between high and low x values
            if a_y[0] < c_y[0]:
                range_y = np.log10(c_y[0] - a_y[0]) # range between high and low y values
                f1 = b_y - a_y[0] - 10**((np.log10(a_x[0] - b_x)) / range_x*range_y)
            else:
                range_y = np.log10(a_y[0] - c_y[0]) # range between high and low y values
                f1 = b_y - a_y[0] + 10**((np.log10(a_x[0] - b_x)) / range_x*range_y)

            if a_z[0] < c_z[0]:
                range_z = np.log10(c_z[0] - a_z[0]) # range between high and low z values
                f2 = b_z - a_z[0] - 10**((np.log10(a_x[0] - b_x)) / range_x*range_z)
            else:
                range_z = np.log10(a_z[0] - c_z[0]) # range between high and low z values
                f2 = b_z - a_z[0] + 10**((np.log10(a_x[0] - b_x)) / range_x*range_z)

        f3 = b_y - b_z

        return(f1, f2, f3)

    result = fsolve(f, [c_x[0], c_y[0], c_z[0]]) # guess using high values
    crossover = result[0]
    return crossover # return crossover strain%

def crossover(group, name, cotype=1):
    '''
    (Step 3/3) This function returns the crossover strain% in a dataframe from all strain sweeps
    in Jenny Bennett's overall rheology test for shear-thinning PXP hydrogels. (multiple ns)

    Parameters
    ----------
    group : list of dictionaries
        each dictionary is from a single n processed in rheology.all_tests_n(df)
        the list includes one dictionary per n

    name : list, str
        names for the output dataframe columns

    cotype : int
        1 (strain) or 2 (frequency)

    Example
    -------
    txt_n1 = rheology.all_tests_n(df_n1)
    txt_n2 = rheology.all_tests_n(df_n2)
    txt_n3 = rheology.all_tests_n(df_n3)

    txt = [txt_n1, txt_n2, txt_n3]
    name = ["n1 Crossover Strain [%]", "n2 Crossover Strain [%]", "n3 Crossover Strain [%]"]

    rheology.crossover(group, name)
    '''
    if cotype==1:
        k = 3
    else:
        k = 1

    co = [] # empty list for crossover from each n
    for n in range(len(group)):
        co_l, co_h = crossover_step1(group[n][k], cotype=cotype) # find low and high values for interpolating crossover
        co_n = crossover_step2(co_l, co_h, cotype=cotype) # interpolate crossover for each n
        co.append(co_n) # input crossover for n into crossover list

    co_df = pd.DataFrame(co).transpose() # turn list of crossovers into dataframe

    if cotype==1:
        co_df['Test'] = ['Strain Sweep 3'] # add test title
    else:
        co_df['Test'] = ['Frequency Sweep 1'] # add test title

    co_df = co_df.set_index(co_df['Test']) # change test title to index
    co_df = co_df.drop(['Test'], axis=1) # remove extra test title column

    for i in range(len(name)):
        co_df = co_df.rename(columns={i: name[i]}) # add names of columns for each n

    co_df['Mean'] = co_df.mean(axis=1) # calculate the mean of each row
    return co_df # return final dataframe summarizing crossover points


def recovery_step1(group, rtype=1):
    '''
    (Step 1/4) This function returns a dictionary of dataframes indicating recovery entry and indexes for each entry
    from cyclic strain sweep in Jenny Bennett's overall rheology test for shear-thinning PXP hydrogels.

    Parameters
    ----------
    group : list of dictionaries
        each dictionary is from a single n processed in rheology.all_tests_n(df)
        the list includes one dictionary per n

    rtype : int
        1 (t1/2 recovery time) or 2 (crossover)

    Example
    -------
    txt_n1 = rheology.all_tests_n(df_n1)
    txt_n2 = rheology.all_tests_n(df_n2)
    txt_n3 = rheology.all_tests_n(df_n3)

    txt = [txt_n1, txt_n2, txt_n3]

    rheology.recovery_step1(txt)
    '''
    for g in group:
        start = [0, 600, 1017, 1218, 1635, 1836, 2253, 2454, 2871]
        end = [600, 619, 1218, 1237, 1836, 1855, 2454, 2473, 3072]
        sm = []
        for s, e in zip(start, end):
            sm.append(g[5][s:e]['Storage Modulus'].mean()) # average G' from interval

        sm_half =[]
        for i in [0, 2, 4, 6]:
            sm_half.append((sm[i] - sm[i+1]) / 2) # half the average G' from difference between intial low and high strain

        sm_h_1 = np.full((1218, 1), sm_half[0])
        sm_h_2 = np.full((618, 1), sm_half[1])
        sm_h_3 = np.full((618, 1), sm_half[2])
        sm_h_4 = np.full((618, 1), sm_half[3])
        sm_half_array = np.concatenate((sm_h_1, sm_h_2, sm_h_3, sm_h_4))

        g[5]['sm_half'] = sm_half_array # insert new column into df to include half G' value

        if rtype==1:
            g[5]['position'] = g[5]['Storage Modulus'] > g[5]['sm_half'] # flag where G' > initial G' 1/2
        else:
            g[5]['position'] = g[5]['Storage Modulus'] > g[5]['Loss Modulus'] # flag where G' > G"

        g[5]['pre_position'] = g[5]['position'].shift(1) # flag next entry
        g[5]['crossover'] = np.where(g[5]['position'] == g[5]['pre_position'], False, True) # flag where it tansitions

    rt = {} # empty recovery dictionary
    for n,g in zip(range(len(group)), group):
        rt_in = g[5].loc[g[5]['crossover'] == True] # locate where G' > initial G' 1/2 or G' > G"
        rt_in2 = rt_in.dropna() # drop NaN rows
        rt[n] = rt_in2[rt_in2.Strain < 400] # include only 5% strain intervals

    indexes = [] # empty list for indexes
    for n in range(len(group)):
        indexes_n = []
        for i in range(len(rt[n])):
            indexes_n.append(rt[n][i:i+1].index.values[0]) # find index for first entry
        indexes.append(indexes_n)

    return rt, indexes # return recovery time dicitonary of dataframes and indexes


def recovery_step2(rtime_l, rtime_h, rtime_start, rtype=1):
    '''
    (Step 2/4) This function interpolates between high and low values for t1/2 recovery time in Jenny Bennett's
    overall rheology test for shear-thinning PXP hydrogels.

    Parameters
    ----------
    rtime_l : dictionary containing recovery time low entries for interpolation

    rtime_h : dictionary containing recovery time high entries for interpolation

    rtime_start : dictionary containing recovery time first entries for start time

    rtype : int
        1 (t1/2 recovery time) or 2 (crossover)

    Example
    -------
    rtime_l = {}
    rtime_h = {}
    rtime_start = {}

    j = 0
    ind = indexes[n]
    for i,s in zip(ind,start):
        rtime_l[j] = pd.DataFrame(rt[n].loc[i]).transpose()
        rtime_start[j] = pd.DataFrame(g[5].loc[s]).transpose()
        if rtime_l[j]['Meas. Pts.'].values > 2:
            index = i - 1
            rtime_h[j] = pd.DataFrame(g[5].loc[index]).transpose()
        else:
            rtime_h[j] = pd.DataFrame(g[5].loc[s]).transpose()

    rheology.recovery_step2(rtime_l, rtime_h, rtime_start)
    '''
    a_x = rtime_h['Time'].values # define high x value
    a_y = rtime_h['Storage Modulus'].values # define high y value
    a_z = rtime_h['Loss Modulus'].values # define high z value

    c_x = rtime_l['Time'].values # define low x value
    c_y = rtime_l['Storage Modulus'].values # define low y value
    c_z = rtime_l['Loss Modulus'].values # define low z value

    sm_half = rtime_l['sm_half'].values # define G' 1/2

    # use solver to interpolate for recovery time

    if rtype==1:
        def f(w):
            b_x = w[0] # recovery time
            b_y = w[1] # storage modulus

            range_x = c_x[0] - a_x[0] # range between high and low x values (linear scale)
            range_y = np.log10(c_y[0] - a_y[0]) # range between high and low y values (log scale)

            # 2 equations and 2 unknowns
            f1 = b_y - a_y[0] - 10**(range_y * (b_x - a_x[0]) / range_x)
            f2 = b_y - sm_half[0]

            return(f1, f2)

        result = fsolve(f, [c_x[0], c_y[0]]) # use high values for guess

    else:
        def f(w):
            b_x = w[0] # recovery time
            b_y = w[1] # storage modulus
            b_z = w[2] # loss modulus

            range_x = c_x[0] - a_x[0] # range between high and low x values (linear scale)
            range_y = np.log10(c_y[0] - a_y[0]) # range between high and low y values (log scale)

            # 3 equations and 3 unknowns
            f1 = b_y - a_y[0] - 10**(range_y * (b_x - a_x[0]) / range_x)

            if a_z[0] < c_z[0]:
                range_z = np.log10(c_z[0] - a_z[0]) # range between high and low y values (log scale)
                f2 = b_z - a_z[0] - 10**(range_z * (b_x - a_x[0]) / range_x)
            else:
                range_z = np.log10(a_z[0] - c_z[0]) # range between high and low y values (log scale)
                f2 = b_z - a_z[0] + 10**(range_z * (b_x - a_x[0]) / range_x)

            f3 = b_y - b_z

            return(f1, f2, f3)

        g_x = (a_x[0]+c_x[0])/2
        g_y = (a_y[0]+c_y[0])/2
        g_z = (a_z[0]+c_z[0])/2

        result = fsolve(f, [c_x[0], c_y[0], c_z[0]]) # use avg values for guess

    crossover = result[0] # return recovery time

    start = rtime_start['Time'].values # define where time starts for interval
    recovery = crossover - start[0] # subtract initial time
    return recovery


def recovery_step3(indexes, start, rt, group, rtype=1):
    '''
    (Step 3/4) This function returns a list of t1/2 recovery times from each n in cyclic strain test from
    Jenny Bennett's overall rheology test for shear-thinning PXP hydrogels.

    Parameters
    ----------
    indexes : list of indexes for each entry

    start : list of indexes where each interval starts

    rt : dictionary of dataframes indicating recovery entry

    group : list of dictionaries
        each dictionary is from a single n processed in rheology.all_tests_n(df)
        the list includes one dictionary per n

    rtype : int
        1 (t1/2 recovery time) or 2 (crossover)

    Example
    -------
    txt_n1 = rheology.all_tests_n(df_n1)
    txt_n2 = rheology.all_tests_n(df_n2)
    txt_n3 = rheology.all_tests_n(df_n3)

    txt = [txt_n1, txt_n2, txt_n3]

    start = [1081, 1727, 2373, 3019]

    rt, indexes = rheology.recovery_step1(txt)

    rheology.recovery_step3(indexes, start, rt, txt)
    '''
    rtime_all = [] # empty list for average recovery from all 4 intervals
    for n,g in zip(range(len(group)), group):
        rtime_l = {} # empty dictionary for low recovery time
        rtime_h = {} # empty dictionary for high recovery time
        rtime_start = {} # empty dictionary for recover time start
        recovery_fulltest = [] # empty list for storing each interval

        j = 0
        ind = indexes[n]
        for i,s in zip(ind,start):
            rtime_l[j] = pd.DataFrame(rt[n].loc[i]).transpose() # low value
            rtime_start[j] = pd.DataFrame(g[5].loc[s]).transpose() # start value
            if rtime_l[j]['Meas. Pts.'].values > 2: # if greater then first measuring pt
                index = i - 1
                rtime_h[j] = pd.DataFrame(g[5].loc[index]).transpose() # use previous entry as high value
            else:
                rtime_h[j] = pd.DataFrame(g[5].loc[s]).transpose() # use start value as high value

            rec = recovery_step2(rtime_l[j], rtime_h[j], rtime_start[j], rtype) # recovery from step 2
            recovery_fulltest.append(rec) # store recovery in list

            j = j + 1

            rec_time = np.average(recovery_fulltest) # take average of recovery from all intervals

        rtime_all.append(rec_time) # add average to final list

    return rtime_all # return list of recovery times for each n


def recovery(start, group, name, rtype=1):
    '''
    (Step 4/4) This function returns a dataframe summarizing t1/2 recovery time for Jenny Bennett's overall
    rheology test for shear-thinning PXP hydrogels. (cyclic strain sweep)

    Parameters
    ----------
    start : list of indexes where each interval starts

    group : list of dictionaries
        each dictionary is from a single n processed in rheology.all_tests_n(df)
        the list includes one dictionary per n

    name : list, str
        names for the output dataframe columns

    rtype : int
        1 (t1/2 recovery time) or 2 (crossover)

    Example
    -------
    start = [1081, 1727, 2373, 3019]

    txt_n1 = rheology.all_tests_n(df_n1)
    txt_n2 = rheology.all_tests_n(df_n2)
    txt_n3 = rheology.all_tests_n(df_n3)

    txt = [txt_n1, txt_n2, txt_n3]

    name = ['n1 t1/2 [s]', 'n2 t1/2 [s]', 'n3 t1/2 [s]']

    rheology.recovery(start, txt, name)
    '''
    rt, indexes = recovery_step1(group, rtype) # find recovery time and indexes for each interval
    recovery = recovery_step3(indexes, start, rt, group, rtype) # take average over all intervals for each n
    rec_df = pd.DataFrame(recovery).transpose() # place in dataframe
    rec_df['Test'] = ['Cyclic Strain Sweep 5'] # rename test

    rec_df = rec_df.set_index(rec_df['Test'])
    rec_df = rec_df.drop(['Test'], axis=1)

    for i in range(len(name)):
        rec_df = rec_df.rename(columns={i: name[i]}) # add names for columns (n1, n2, etc.)

    rec_df['Mean'] = rec_df.mean(axis=1) # find mean for recovery time
    return rec_df # return dataframe with recovery time
