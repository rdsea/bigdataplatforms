"""
Simple example of using pydeequ for analyzing data quality.
Follow the basic guideline and steps in:
https://pydeequ.readthedocs.io/en/latest/README.html#quickstart

The idea of this example is that:
pydeequ APIs are specific and input datasets are also specific,
thus it can consume quite a lot of effort to engineering generic
checks for input datasets.

We can simplify this by using:
- a generic way to specific constraints (e.g., using json)
- using dynamic loading mechanisms to map constraints to the
right APIs
- of course, not all the cases can be done through generic mapping,
so we need to also handle specific cases.

The code, however, just illustrates simple mapping techniques
for basic APIs. It is up to the learner to think how to apply
such techniques for their system.

"""

import argparse
from importlib import import_module
import os
import sys

# just a quick setup as pydeequ needs this environment
os.environ["SPARK_VERSION"] = "3.3"
from pyspark.sql import SparkSession
import pydeequ
from pydeequ.analyzers import *
from pydeequ.profiles import *
from pydeequ.suggestions import *
from pydeequ.checks import *
from pydeequ.verification import *

# Given the idea of a generic way to specify constraint,
# we give here an example for ONU Data (see the readme.md)
# The ONU data has the following columns
# PROVINCECODE,DEVICEID,IFINDEX,FRAME,SLOT,PORT,ONUINDEX,ONUID,TIME,SPEEDIN,SPEEDOUT

"""
for a fast and illustrating example, the specification 
is given in a json object, but one should make it in a file
and load it into spark in the right way
simple mapping:
- analyzer_name to class of AnalyzerObject
https://pydeequ.readthedocs.io/en/latest/pydeequ.html#pydeequ.analyzers.AnalysisRunBuilder.addAnalyzer 
- function_name under check_constraints to function of Check
https://pydeequ.readthedocs.io/en/latest/pydeequ.html#pydeequ.checks.Check

Since we do the mapping is a simple way: 
- the values of analyzer_name and function_name have to be the same in the APIs. 
- params, column names, and other values are based on input datasets.

"""
dq_dsl = {
    "analyzer_constraints": [
        {"analyzer_name": "Size"},
        {"analyzer_name": "Completeness", "params": {"column": "SPEEDIN"}},
    ],
    "check_constraints": [
        {"function_name": "hasSize", "threshold": 3},
        {"function_name": "hasMin", "column_name": "SPEEDIN", "threshold": 0},
        {"function_name": "isComplete", "column_name": "SPEEDIN"},
        {"function_name": "isComplete", "column_name": "SPEEDOUT"},
        {"function_name": "isUnique", "column_name": "ONUID"},
        {
            "function_name": "isContainedIn",
            "column_name": "FRAME",
            "values": ["1", "100"],
        },
        {"function_name": "isNonNegative", "column_name": "PORT"},
    ],
}
if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", help="Input data file")
    args = parser.parse_args()
    INPUT_FILE = args.input_file
    # note the jars configuration, see the readme file
    spark = (
        SparkSession.builder.config("spark.jars.packages", pydeequ.deequ_maven_coord)
        .config("spark.jars.excludes", pydeequ.f2j_maven_coord)
        .appName("cse4640")
        .getOrCreate()
    )
    input_df = spark.read.csv(INPUT_FILE, sep=",", inferSchema=True, header=True)
    input_df.show()
    # FIRST SUB-TUTORIAL: analyze the input data
    # simple way of mapping
    list_of_analyzer = []
    analyzer_constraints = dq_dsl["analyzer_constraints"]
    for analyzer in analyzer_constraints:
        # load analyzeobject from pydeeque
        module = import_module("pydeequ.analyzers")
        analyzerclass = getattr(module, analyzer["analyzer_name"])
        ## instantitate objects based on params
        if "params" in analyzer.keys():
            analyzer_instance = analyzerclass(**analyzer["params"])
        else:
            analyzer_instance = analyzerclass()
        list_of_analyzer.append(analyzer_instance)

    analysis_runner = AnalysisRunner(spark)
    analysis_builder = analysis_runner.onData(input_df)
    for item in list_of_analyzer:
        analysis_builder = analysis_builder.addAnalyzer(item)
    dq_analysis_result = analysis_builder.run()
    dq_analysis_result_df = AnalyzerContext.successMetricsAsDataFrame(
        spark, dq_analysis_result
    )
    dq_analysis_result_df.show()

    # SECOND SUB-TUTORIAL check some constraints
    check_constraints = dq_dsl["check_constraints"]
    check = Check(spark, CheckLevel.Warning, "ONU Check")
    # load corresponding function of Check object based on
    # using input constraints to create check functions
    for constraint in check_constraints:
        if constraint["function_name"] in dir(check):
            func = getattr(check, constraint["function_name"])
            if "threshold" in constraint.keys():
                # threshold is applied for function with lambda
                # not all supported
                if "column_name" in constraint.keys():
                    func(
                        column=constraint["column_name"],
                        assertion=lambda x: x >= constraint["threshold"],
                    )
                else:
                    func(assertion=lambda x: x >= constraint["threshold"])
            elif "column_name" in constraint.keys():
                # for function without threshold but values
                if "values" in constraint.keys():
                    func(constraint["column_name"], constraint["values"])
                else:
                    func(constraint["column_name"])
            else:
                print(f"Currently we have not implemented this {constraint}")
        else:
            print(f'Invalid {constraint["function_name"]} in {dir(check)}')
    dq_check_result = VerificationSuite(spark).onData(input_df).addCheck(check).run()
    dq_check_result_df = VerificationResult.checkResultsAsDataFrame(
        spark, dq_check_result
    )
    dq_check_result_df.show()
    # shutdown according to the pydeeque guideline
    spark.sparkContext._gateway.shutdown_callback_server()
    spark.stop()
