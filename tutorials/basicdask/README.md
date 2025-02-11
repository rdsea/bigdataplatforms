# Some Examples of Dask

[Dask](https://docs.dask.org/en/stable/) can be used for programming data processing functions in a data platform. For example:

- extract and transform data which can be described in DataFrame
- define custom task graphs of data processing.

The examples here illustrate a few aspects that we discuss how Dask supports the embarrassingly parallel model and task graphs for data processing.

## Setup

Setting up Dask can be done by following [the Dask document](https://docs.dask.org/en/stable/install.html).

The libraries required for the code examples can be installed by running rye:
```bash
$rye sync
```

Running the code examples by python, after enabling the environment
```
$python src/...
```
or

```
$rye run python src/...
```

## Examples

We use [taxi data and bts data](../../data/README.md) as examples.

- [DataFrame partitions](src/basicdask/dask_dataframe.py): see how data can be partitioned in Dask.
- [Basic calculation with Dask DataFrame](src/basicdask/dask_taxi_amount_calculation.py): illustrates a simple Dask program that is very similar to pandas in a local machine.
- [Distributed Dask calculation with Dash DataFrame](src/basicdask/dask_distributed_taxi_amount_calculation.py): illustrates using distributed resources for data processing.
- [Using delayed and future features to define a task graph](src/basicdask/dask_delayed_future_ex.py): illustrates delayed and future tasks for customized graphs.