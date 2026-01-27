import sys
import os
import mlflow
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import (
    ModelTrainerArtifact,
    DataTransformationArtifact,
)
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.ml_utils.metric.classification_metric import (
    get_classification_score,
)
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import (
    load_numpy_array_data,
    save_object,
    load_object,
    evaluate_models,
)

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)

import dagshub


# ✅ SAFE DAGSHUB INITIALIZATION
def init_dagshub():
    try:
        dagshub_token = os.getenv("DAGSHUB_TOKEN")

        if not dagshub_token:
            logging.warning("DAGSHUB_TOKEN not found. Skipping DAGsHub init.")
            return

        dagshub.init(
            repo_owner="SARWAGYASHAH",
            repo_name="Network-Security-",
            mlflow=True,
            token=dagshub_token,
        )

        logging.info("DAGsHub initialized successfully.")

    except Exception as e:
        logging.warning(f"DAGsHub init failed: {e}")


class ModelTrainer:
    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
        data_transformation_artifact: DataTransformationArtifact,
    ):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact

            # ✅ init DAGsHub ONLY when trainer is created
            init_dagshub()

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def track_mlflow(self, best_model, classificationmetric):
        try:
            with mlflow.start_run():
                mlflow.log_metric("f1_score", classificationmetric.f1_score)
                mlflow.log_metric("precision_score", classificationmetric.precision_score)
                mlflow.log_metric("recall_score", classificationmetric.recall_score)
                mlflow.sklearn.log_model(best_model, "model")
        except Exception as e:
            logging.warning(f"MLflow tracking failed: {e}")

    def train_model(self, X_train, y_train, x_test, y_test):
        models = {
            "Random Forest": RandomForestClassifier(verbose=1),
            "Decision Tree": DecisionTreeClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1),
            "Logistic Regression": LogisticRegression(verbose=1),
            "AdaBoost": AdaBoostClassifier(),
        }

        params = {
            "Decision Tree": {
                "criterion": ["gini", "entropy", "log_loss"],
            },
            "Random Forest": {
                "n_estimators": [8, 16, 32, 128, 256],
            },
            "Gradient Boosting": {
                "learning_rate": [0.1, 0.01, 0.05, 0.001],
                "subsample": [0.6, 0.7, 0.75, 0.85, 0.9],
                "n_estimators": [8, 16, 32, 64, 128, 256],
            },
            "Logistic Regression": {},
            "AdaBoost": {
                "learning_rate": [0.1, 0.01, 0.001],
                "n_estimators": [8, 16, 32, 64, 128, 256],
            },
        }

        model_report = evaluate_models(
            X_train=X_train,
            y_train=y_train,
            X_test=x_test,
            y_test=y_test,
            models=models,
            param=params,
        )

        best_model_score = max(model_report.values())
        best_model_name = max(model_report, key=model_report.get)
        best_model = models[best_model_name]

        y_train_pred = best_model.predict(X_train)
        train_metric = get_classification_score(y_train, y_train_pred)
        self.track_mlflow(best_model, train_metric)

        y_test_pred = best_model.predict(x_test)
        test_metric = get_classification_score(y_test, y_test_pred)
        self.track_mlflow(best_model, test_metric)

        preprocessor = load_object(
            self.data_transformation_artifact.transformed_object_file_path
        )

        os.makedirs(
            os.path.dirname(self.model_trainer_config.trained_model_file_path),
            exist_ok=True,
        )

        network_model = NetworkModel(
            preprocessor=preprocessor, model=best_model
        )

        save_object(
            self.model_trainer_config.trained_model_file_path, network_model
        )

        save_object("final_model/model.pkl", best_model)

        return ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=train_metric,
            test_metric_artifact=test_metric,
        )

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            train_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_train_file_path
            )
            test_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_test_file_path
            )

            x_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            x_test, y_test = test_arr[:, :-1], test_arr[:, -1]

            return self.train_model(x_train, y_train, x_test, y_test)

        except Exception as e:
            raise NetworkSecurityException(e, sys)
