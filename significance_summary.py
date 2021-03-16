"""Counts the number of features from each domain that were in significant comparisons above and below a threshold"""

from sys import argv
from pandas import DataFrame, read_csv, Series
from matplotlib.pyplot import subplots, savefig, title as set_title, xlabel, ylabel
from os import mkdir
from os.path import join, isdir

from utils import (
    SIGNIFICANT_FREQUENCIES_CSV_PATH, ADNIMERGE_KEY, EXPRESSION_KEY, MRI_KEY, FREQ_KEY, DOMAIN_KEY, IDX_COL
)

SUMMARY_DIR: str = 'data/significance-summary/'


def main():
    """Main method"""

    alpha: str = argv[1]
    n_histogram_bins: int = int(argv[2])

    if not isdir(SUMMARY_DIR):
        mkdir(SUMMARY_DIR)

    significance_frequencies: str = SIGNIFICANT_FREQUENCIES_CSV_PATH.format(alpha)
    significance_frequencies: DataFrame = read_csv(significance_frequencies)

    print('Number Of Features That Show Up In At Least One Significance Comparison: {} | For Alpha: {}'.format(
        len(significance_frequencies), alpha
    ))

    save_histograms(significance_frequencies=significance_frequencies, n_histogram_bins=n_histogram_bins, alpha=alpha)
    save_table(significance_frequencies=significance_frequencies, alpha=alpha)


def print_count(domain_key: str, counts: dict):
    """Prints the counts above or below the threshold for a given domain"""

    print('{}: {}'.format(domain_key, counts[domain_key]))


def save_histograms(significance_frequencies: DataFrame, n_histogram_bins: int, alpha: str):
    """Saves the histograms for the total set of frequencies and the set for each domain"""

    save_histogram(
        significance_frequencies=significance_frequencies, n_histogram_bins=n_histogram_bins, alpha=alpha,
        title='Total', break_y=True, start_break_count=8000, end_break_count=70000, max_count=78000
    )

    adnimerge_frequencies: DataFrame = significance_frequencies.loc[
        significance_frequencies[DOMAIN_KEY] == ADNIMERGE_KEY
        ]

    save_histogram(
        significance_frequencies=adnimerge_frequencies, n_histogram_bins=n_histogram_bins, alpha=alpha,
        title='ADNIMERGE', break_y=False
    )

    expression_frequencies: DataFrame = significance_frequencies.loc[
        significance_frequencies[DOMAIN_KEY] == EXPRESSION_KEY
    ]

    save_histogram(
        significance_frequencies=expression_frequencies, n_histogram_bins=n_histogram_bins, alpha=alpha,
        title='Gene Expression', break_y=False
    )

    mri_frequencies: DataFrame = significance_frequencies.loc[
        significance_frequencies[DOMAIN_KEY] == MRI_KEY
    ]

    save_histogram(
        significance_frequencies=mri_frequencies, n_histogram_bins=n_histogram_bins, alpha=alpha, title='MRI',
        break_y=True, start_break_count=7000, end_break_count=70000, max_count=77000
    )


def save_histogram(
    significance_frequencies: DataFrame, n_histogram_bins: int, alpha: str, title: str, break_y: bool,
    start_break_count: int = None, end_break_count: int = None, max_count: int = None
):
    """Saves a histogram with a broken y-axis"""

    frequencies: Series = significance_frequencies[FREQ_KEY]

    if break_y:
        broken_y_histogram(
            frequencies=frequencies, n_histogram_bins=n_histogram_bins, title=title, end_break_count=end_break_count,
            max_count=max_count, start_break_count=start_break_count
        )
    else:
        regular_histogram(frequencies=frequencies, n_histogram_bins=n_histogram_bins, title=title)

    xlabel('Comparison Frequency')
    ylabel('Number of Features')

    save_path: str = join(SUMMARY_DIR, 'significant-frequencies-{}-{}'.format(title.lower().replace(' ', ''), alpha))
    savefig(save_path)


def broken_y_histogram(
    frequencies: Series, n_histogram_bins: int, title: str, end_break_count: int, max_count: int, start_break_count: int
):
    """Creates a histogram graph with a broken y-axis"""

    fig, (ax1, ax2) = subplots(2, 1, sharex=True)
    fig.subplots_adjust(hspace=0.08)
    ax1.hist(frequencies, bins=n_histogram_bins)
    ax2.hist(frequencies, bins=n_histogram_bins)
    ax1.set_ylim(end_break_count, max_count)
    ax1.set_title(title)
    ax2.set_ylim(0, start_break_count)


def regular_histogram(frequencies: Series, n_histogram_bins: int, title: str):
    """Creates a histogram without a broken y-axis"""

    _, ax = subplots()
    ax.hist(frequencies, bins=n_histogram_bins)
    set_title(title)


def save_table(significance_frequencies: DataFrame, alpha: str):
    """Counts the the number of features with comparison frequencies that are within certain ranges"""

    freq_thresholds: list = [0, 5, 10, 20, 50, 100, 12017]
    table: DataFrame = make_start_table(freq_thresholds=freq_thresholds)

    for i in range(len(significance_frequencies)):
        row: Series = significance_frequencies.loc[i]
        feature, frequency, domain = row

        for j in range(len(freq_thresholds) - 1):
            threshold1: int = freq_thresholds[j]
            threshold2: int = freq_thresholds[j+1]

            if threshold1 < frequency <= threshold2:
                col_key: str = make_col_key(threshold1=threshold1, threshold2=threshold2)
                table[col_key][domain] += 1
                break
        else:
            assert False, 'the frequency {} for feature {} is not within any of the ranges'.format(frequency, feature)

    save_path: str = join(SUMMARY_DIR, 'feature-counts-{}.csv'.format(alpha))
    table.to_csv(save_path)


def make_start_table(freq_thresholds: list) -> DataFrame:
    """Creates the table with counts of 0"""

    idx_col: list = [ADNIMERGE_KEY, EXPRESSION_KEY, MRI_KEY]

    table: dict = {
        IDX_COL: idx_col
    }

    for j in range(len(freq_thresholds) - 1):
        threshold1: int = freq_thresholds[j]
        threshold2: int = freq_thresholds[j + 1]
        header: str = make_col_key(threshold1=threshold1, threshold2=threshold2)
        table[header] = [0] * len(idx_col)

    table: DataFrame = DataFrame(table)
    table: DataFrame = table.set_index(IDX_COL)
    return table


def make_col_key(threshold1: int, threshold2: int) -> str:
    """Makes a header of the table based on a comparison frequency range"""

    header: str = '{} < f <= {}'.format(threshold1, threshold2)
    return header


if __name__ == '__main__':
    main()