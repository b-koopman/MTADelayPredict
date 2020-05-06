# Background

The New York City subway is huge in terms of the number of subway rail cars.

>The MTA network has the nation’s largest bus fleet and more subway and commuter rail cars than all other U.S. transit systems combined [[1]](#footnote_1)

I live in New York City, and am exposed to the benefits of this extensive, 24 hour system, as well as the inconveniences of unexpected train delays.
Unfortunately, with a 24 hour subway system, using aging signal systems, in some cases from the 1930's, there are many delays[2]. Additionally, as ridership has increased over the years, crowding can simply cause delays.[3](#footnote_3) Now, there are estimated train arrival times available on train platforms[[4]](#footnote_4), however, from personal experience, these generally don't work well when there are delays.

# Problem

>When there is a delay, how long can I expect to wait until the next train?

In my experience, the displayed expected arrival times, when available, become unreliable when there is a delay, or in some cases stop providing estimated arrival times, and instead just announce "Delay" instead of the usual "N minutes".  I want to answer the question of "What does this delay mean for the arrival time of the next train?".  More precisely stated, "Given that a delay has been announced by the MTA within the last hour, when will the next train come to the train platform I am waiting on?"


# Proposed Solution

I propose using a supervised machine learning approach to provide an estimate of minutes until a next train arrives following the departure of the previous train.  This estimate can easily be compared to actual train arrival times in order to quantify performance.

In order to provide appropriate scope, limiting project risk and providing proof of concept, the proposed deliverable is an estimator that provides real-time predicted wait time until next train for the Northbound platform at Times Square 42nd St. on the NYC N line[[5]](#footnote_5) when there are announced delays.  This will be deployed to AWS Sagemaker with a web-app front-end in order to access relevant predictions within the current minute.  It is expected there will be a clear roadmap for future work to extend the model to platforms and trains upon completion of this project.


# Datasets and Inputs

For input, modeling will require at the very least, train arrival times for a given train line, as well as timestamped MTA Alerts to categorize the time periods when delays occur.  As train data is provided in a realtime feed format.

## Historical Data
For research, I will require historical data.  As I have not been collecting and archiving realtime data, this project will use historical data provided by the MTA.  These datasets include sub-minutely information on current train location and scheduled arrival times, as well as timestamped status alerts for delays.  There are equivalent realtime feeds also available from the MTA for use in the deployed realtime system.

- [MTA Alert Archive](https://m.mymtaalerts.com/archive)
    - Web form for viewing historical MTA alerts
- [Subway Data Archive](http://web.mta.info/developers/data/archives.html)
    - archive of GTFS protobufs from August 2018 - June 2019

## Inputs
Using the above datasets, some light processing will be required to extract features and the predicted value for training.  Please see the [README](README.md) for information on accessing historical data.  Initial model inputs will be features related to alert message content, time of day and location of the next expected train


## Benchmark Model

A proposed benchmark is the scheduled train arrival time for the next expected train, as provided in the gtfs realtime feed.  For a single train traveling along a line, the scheduled arrival time for each stop is available within the gtfs feed.  It seems reasonable to compare any improvements in predicting train arrivals against the current production system in place.


## Evaluation Metrics
 
Model performance will be evaluated on the test data set.  The proposed metric for evaluating overall model performance and performance of the benchmark is <img src="https://render.githubusercontent.com/render/math?math=RMSE">.  <img src="https://render.githubusercontent.com/render/math?math=RMSE"> will be helpful, as it will provide errors in units of the predicted variable, as it takes the square root of the <img src="https://render.githubusercontent.com/render/math?math=MSE"> metric[[6]](#footnote_6).  In this particular case, the $RMSE$ metric will be in units of minutes, this is much easier to think about and provides a more meaningful metric in this case.

An additional metric for validating the fitted model is <img src="https://render.githubusercontent.com/render/math?math=R_{adj}^{2}"> (adjusted <img src="https://render.githubusercontent.com/render/math?math=R^{2}">)  [[7]](#footnote_7).  This effectively shows the "goodness of fit" for regressive models.[[8]](#footnote_8)

## Design and Process

In order to bisect the problem into more manageable pieces and increase chance of success, initial development will focus on only predicting Northbound N trains at Times Square, 42nd street.  It is expected that the modeling approach should be transferable to other stops, and even other trains.

### Proof of concept
Much of this development process will be designed around "failing early" and speed of deployment of a proof of concept.  In short, spending time up-front developing an over-engineered infrastructure is useless if the data is unusable, or the model is not performant.  For ease of development and cost reduction, initial data exploration and model development will be performed on a local workstation.  With this in mind, the system can easily be migrated to AWS Sagemaker using the artifacts from a locally trained model.

- **Data exploration and validation**

After downloading data, immediately demonstrate that data contains reasonable values, and that status alerts have a meaningful relationship with train delay time.
For a more in-depth discussion regarding data sources, please see the data [README](#docs/Data_README.md).

- **Model Selection**

While estimator selection fall within the scope of work for this project, I propose using a modeling approach that prioritizes attribution, in order to better understand on an intuitive level what affects delays.  Initial investigation will begin with using a [scikit- learn Decision Tree Regressor](https://scikit-learn.org/stable/modules/tree.html#regression), as this can be considered white box with easy attribution.[[9]](#footnote_9)

- **Feature selection and tuning**

This project will begin investigation focused on scikit-learn[[10]](#footnote_10) ensemble regression models, with initial attention to [RandomForestRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html).

Feature selection will be performed through recursive feature elimination with cross validation[[11]](#footnote_11) using <img src="https://render.githubusercontent.com/render/math?math=R^{2}"> as the scoring criteria in order to evaluate goodness of fit while adjusting for <img src="https://render.githubusercontent.com/render/math?math=R^{2}"> inflation due to number of features[[6]]($footnote_6)[[7]](#footnote_7)


### Deployment
Once the proof of concept model meets or exceeds performance of the benchmark model, as measured by $RMSE$, the model should be deployed and an initial realtime demo system should be integrated.  Again, early development of these realtime components will help identify any issues with the system prior to investing additional modeling effort. See [*Fig. 1*](#fig_1) for proposed system diagram.

### Continued Development

Modeling improvements can be made in a local or AWS development environment while still iteratively deploying model improvements.  Also critical for this process is access to captured realtime data and evaluation of model performance on the captured realtime data.



<p>Fig. 1</p>
<img src="docs/files/Proposed System.bmp">

# References
[1]<a id="footnote_1">https://new.mta.info/about-us/the-mta-network</a>

[2]<a id="footnote_2">https://www.nytimes.com/2019/09/23/nyregion/nyc-mta-subway-signals.html</a>

[3]<a id="footnote_3">https://www.nytimes.com/interactive/2017/06/28/nyregion/subway-delays-overcrowding.html </a>

[4]<a id="footnote_4">https://ny.curbed.com/2018/1/2/16840622/mta-nyc-subway-countdown-clock-installation-finished</a>

[5]<a id="footnote_5">http://web.mta.info/nyct/service/nline.htm</a>

[6]<a id="footnote_6">https://en.wikipedia.org/wiki/Root-mean-square_deviation</a>

[7]<a id="footnote_7">https://en.wikipedia.org/wiki/Coefficient_of_determination#Adjusted_R2</a>

[8]<a id="footnote_8">https://en.wikipedia.org/wiki/Coefficient_of_determination#Interpretation</a>

[9]<a id="footnote_9">https://scikit-learn.org/stable/modules/tree.html </a>

[10]<a id="footnote_10">https://scikit-learn.org/</a>

[11]<a id="footnote_11">https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.RFECV.html</a>
