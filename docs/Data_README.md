# NYC Subway Delay Predictor Data

## Historical Data Sets
For model development and training, this project will require historical data.  As no realtime data has been collected and archived, this project will use historical data provided by the MTA

### MTA Alert Archive
https://m.mymtaalerts.com/archive

Web form for viewing historical MTA alerts.  As there seems to be no easily downloadable archive, a web scraper is needed.  I used [Selenium](https://www.selenium.dev/) with Chromium to scrape this data in monthly chunks and dumped to csv.  Please find example csv's included in the <code>data/alerts</code> directory.

Look at [AlertScraper.ipynb](../Notebooks/AlertScraper.ipynb) for an example of how to do this.

### Subway Data Archive
http://web.mta.info/developers/data/archives.html

This is an archive of GTFS protobufs sampled sub-minutely from August 2018 - June 2019.  Data is available for the ACE, BDFM, NQRW, J and G [train lines](https://new.mta.info/maps/subway/lines).  This dataset is extremely large, so only directions for downloading and processing are included.

These are bundled into monthly zip files containing daily directories.  Unfortunately, the layouts and zip formats are somewhat irregular, so this is a more manual process.

Once decompressed, the directory layout looks like so:

<code>
201811/
    20181101/
        gtfs_ace_20181101_041943.gtfs
        gtfs_ace_20181101_041958.gtfs
        gtfs_ace_20181101_042013.gtfs
        gtfs_ace_20181101_042043.gtfs
etc...
</code>

Each of these <code>.gtfs</code> files is a [Protocol Buffer](https://developers.google.com/protocol-buffers/docs/overview) specified by Google to relay transit data.  After the required [protobuf specifications](#MTA-GTFS-Specification) are downloaded, and compiled, parsing the protobufs is relatively straightforward.

For illustration, I have computed the observed time until the next train in units of minutes, effectively ground truth for this project, and written it to <code>data/status/train_wait.h5</code> For illustration, this only includes data for Northbound N trains at Times Square 42nd St during approximate peak usage 06:00AM - 21:00PM.

Look at [StatusExtractor.ipynb](../Notebooks/StatusExtractor.ipynb) for some help unzipping all these archives.

### Data validation
- **Sanity check arrival time statistics**

First look at the values for the next arrival time to make sure things look somewhat reasonable.

```python
import pandas as pd
train_wait = pd.read_csv(data_dir + '/train_wait.csv')
train_wait.minutes.mean()
```
<code>
1.624859646691777
</code>

This looks reasonable enough, as trains can arrive pretty quickly during rush hour, and our data is only limited to peak usage.

- **Komolgorov-Smirnov test for significance**

Show that <code>train_wait</code> following a delay alert is on average greater than <code>train_wait</code> without an alert.

Why not a T-test?  The T-test assumes that both distributions have identical variances [[1]](#footnote_1).  It seems reasonable to assume that there will be larger tails on the distribution of <code>wait_time</code>'s when there are delays, lending itself better to the Komolgorov-Smirnov test[[2]](#footnote_2).  Additionally, since we expect that the MTA alerts should cause an increase in train wait time, if anything, the <code>greater</code> one sided parameter will be used.[[3]](#footnote_3)

```python
import pandas as pd
from scipy.stats import ks_2samp

# Load alert data
alert_dir = '/data/alerts'
alert_files = glob.glob(os.path.abspath(os.path.join(alert_dir, 'raw_alerts_*.csv')))
alert_list = []
for f in alert_files:
    alert_list.append(pd.read_csv(f))
alert_df = pd.concat(alert_list)
alert_df.index = alert_df.Date.map(pd.to_datetime)
alert_df.drop(columns=['Date'], inplace=True)
alert_df.sort_index(inplace=True)

# Load train wait times
pd.read_hdf('data/status/train_wait.h5', key='df')

# Filter relevant alerts
train_alerts = alert_df.loc[alert_df.Subject.str.match(r'.* N(?:(, )|( and)).*')]

# Create a mask of all observed waits for MINUTE_DURATION minutes after an alert
MINUTE_DURATION = 30
alert_mask = pd.DataFrame(index=train_wait.index, columns=['alerted'])
alert_mask[:] = False
for i,t in enumerate(train_alerts.loc[train_wait.index[0]:train_wait.index[-1]].index):
    ts = pd.Timestamp(t, tz='US/Eastern')
    alert_mask.loc[ts:ts+pd.Timedelta(MINUTE_DURATION, unit='m')] = True

    
# Calculate kstest
print(ks_2samp(train_wait[alert_mask.alerted].dropna(), train_wait[~alert_mask.alerted].dropna(), alternative='greater'))
```
returns: Ks_2sampResult(statistic=0.04527045178935629, pvalue=0.006969013428867737)

This seems to reject the null hypothesis with a low pvalue (<1%) and ks-stat.  This indicates that the wait time for trains in the 30 minutes after an alert are significantly different.

## Realtime Data Sets
Following completion of modelling and validation, the trained system can be applied to realtime data for realtime predictions.  The majority of this project will require the use of historical data archives, however, it is imperative there are realtime equivalents of the archived data.

### [Realtime MTA Data Feeds](https://datamine.mta.info/list-of-feeds)
These are also available as protobufs that can be accessed in realtime, however you must first apply for an access key.

### [Realtime MTA Service Status](http://web.mta.info/status/serviceStatus.txt)
Updates are also available for subscription via [MTA Home Page](https://new.mta.info/).  However, these are in an XML-like markup and will require a different parser from that used in the web scraping.
    

## Metadata

Additional metadata is also required for interpreting the data from the feeds, and interpreting the relevance of provided alerts

### [MTA Feed Metadata](http://web.mta.info/developers/data/nyct/subway/google_transit.zip)
    - Information for interpreting values in subway data, such as mapping station IDs to human readable values
### [MTA GTFS Specification](https://api.mta.info/nyct-subway.proto.txt)
    - In addition to the base [GTFS realtime specification](https://developers.google.com/transit/gtfs-realtime/gtfs-realtime.proto)


[1]<a id="footnote_1"> https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.ttest_ind.html </a>

[2] <a id="footnote_2">https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.kstest.html</a>

[3] <a id="footnote_3">https://stats.idre.ucla.edu/other/mult-pkg/faq/general/faq-what-are-the-differences-between-one-tailed-and-two-tailed-tests/</a>
