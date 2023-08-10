import os

from sensai.tracking.mlflow_tracking import MLFlowExperiment
from sensai.util.io import ResultWriter
from sensai.util.logging import datetime_tag
from songpop.features import FeatureName
from sensai.evaluation import ClassificationEvaluationUtil, VectorClassificationModelEvaluatorParams
from sensai.util import logging
from songpop.data import Dataset
from songpop.model_factory import ModelFactory


def main():
    dataset = Dataset(10000)

    # set up (dual) tracking
    experiment_name = f"popularity-classification_{dataset.tag()}"
    run_id = datetime_tag()
    tracked_experiment = MLFlowExperiment(experiment_name, tracking_uri="", context_prefix=run_id + "_",
        add_log_to_all_contexts=True)
    result_writer = ResultWriter(os.path.join("results", experiment_name, run_id))
    logging.add_file_logger(result_writer.path("log.txt"))

    # load dataset
    io_data = dataset.load_io_data()

    # define models to be evaluated
    models = [
        ModelFactory.create_logistic_regression_orig(),
        ModelFactory.create_logistic_regression(),
        ModelFactory.create_knn_orig(),
        ModelFactory.create_knn(),
        ModelFactory.create_random_forest_orig(),
        ModelFactory.create_random_forest(),
        ModelFactory.create_decision_tree_orig(),
        ModelFactory.create_xgb(),
        ModelFactory.create_xgb("-meanArtistFreqPopular", [FeatureName.MEAN_ARTIST_FREQ_POPULAR]),
    ]

    # declare parameters to be used for evaluation, i.e. how to split the data (fraction and random seed)
    evaluator_params = VectorClassificationModelEvaluatorParams(fractional_split_test_fraction=0.3,
        fractional_split_random_seed=42,
        binary_positive_label=dataset.class_positive)

    # use a high-level utility class for evaluating the models, i.e. fitting on the training data and evaluating
    # on the test data provided via the splitting declared above
    ev = ClassificationEvaluationUtil(io_data, evaluator_params=evaluator_params)

    # inject high-level utility objects to track the evaluation of the models
    ev.compare_models(models, tracked_experiment=tracked_experiment, result_writer=result_writer)


if __name__ == '__main__':
    logging.run_main(main)
