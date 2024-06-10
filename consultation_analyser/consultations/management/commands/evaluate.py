import json
import logging
import os
from pathlib import Path
import time
from typing import Optional

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from consultation_analyser.authentication.models import User
from consultation_analyser.consultations import models
from consultation_analyser.consultations.download_consultation import consultation_to_json
from consultation_analyser.consultations.upload_consultation import upload_consultation
from consultation_analyser.pipeline.backends.bertopic import BERTopicBackend
from consultation_analyser.pipeline.backends.dummy_llm_backend import DummyLLMBackend
from consultation_analyser.pipeline.backends.dummy_topic_backend import DummyTopicBackend
from consultation_analyser.pipeline.backends.ollama_llm_backend import OllamaLLMBackend
from consultation_analyser.pipeline.backends.sagemaker_llm_backend import SagemakerLLMBackend
from consultation_analyser.pipeline.processing import process_consultation_themes


logger = logging.getLogger("pipeline")


class Command(BaseCommand):
    help = "Run the pipeline, write evaluation JSON"

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            action="store",
            help="A path to a JSON file containing a ConsultationWithResponses",
            type=str,
        )
        parser.add_argument(
            "--embedding_model",
            action="store",
            help="The embedding model to use in BERTopic. Pass 'fake' to get fake topics",
            type=str,
        )
        parser.add_argument(
            "--llm",
            action="store",
            help="The llm to use for summarising. Will be fake by default. Pass 'sagemaker' or 'ollama/model' to specify a model",
            type=str,
        )
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Whether to delete an existing matching consultation first",
        )
        parser.add_argument(
            "--output_dir",
            action="store",
            help="The output directory - defaults to tmp/eval/$consultation-slug-$unixtime",
        )

    def handle(self, *args, **options):
        logger.info(f"Called evaluate with {options}")

        consultation = self.__load_consultation(input_file=options["input"], clean=options["clean"])
        output_dir = self.__get_output_dir(
            output_dir=options["output_dir"], consultation=consultation
        )
        topic_backend = self.__get_topic_backend(embedding_model=options["embedding_model"], persistence_path=output_dir)
        llm_backend = self.__get_llm(llm_identifier=options["llm"])

        process_consultation_themes(
            consultation, topic_backend=topic_backend, llm_backend=llm_backend
        )

        self.__save_consultation_with_themes(output_dir=output_dir, consultation=consultation)

        logger.info(f"Wrote results to {output_dir}")

    def __load_consultation(self, input_file: str, clean: Optional[bool]):
        if not input_file:
            raise Exception("You need to specify an input file")

        # upload, cleaning if required
        if clean:
            input_json = json.loads(open(input_file).read())
            name = input_json["consultation"]["name"]
            old_consultation = models.Consultation.objects.get(name=name)
            old_consultation.delete()
            logger.info("Removed original consultation")

        try:
            user = User.objects.filter(email="email@example.com").first()
            consultation = upload_consultation(open(input_file), user)
        except IntegrityError as e:
            logger.info(e)
            logger.info(
                "This consultation already exists. To remove it and start with a fresh copy pass --clean."
            )
            exit()

        return consultation

    def __get_topic_backend(self, persistence_path: Path = None, embedding_model: Optional[str] = ""):
        if embedding_model == "fake":
            topic_backend = DummyTopicBackend()
            logger.info("Using fake topic model")
        elif embedding_model:
            topic_backend = BERTopicBackend(
                embedding_model=embedding_model, persistence_path=persistence_path / "bertopic"
            )
        else:
            topic_backend = BERTopicBackend(persistence_path=persistence_path / "bertopic")

        return topic_backend

    def __get_llm(self, llm_identifier: Optional[str] = "fake"):
        if llm_identifier == "fake" or not llm_identifier:
            llm = DummyLLMBackend()
        elif llm_identifier == "sagemaker":
            llm = SagemakerLLMBackend()
        elif llm_identifier.startswith("ollama"):
            model = llm.split("/")[1]
            llm = OllamaLLMBackend(model)
        else:
            raise Exception(f"Invalid --llm specified: {llm_identifier}")

        return llm

    def __get_output_dir(self, consultation: models.Consultation, output_dir: Optional[str] = None):
        if not output_dir:
            output_dir = (
                settings.BASE_DIR / "tmp" / "eval" / f"{consultation.slug}-{int(time.time())}"
            )
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def __save_consultation_with_themes(self, output_dir: Path, consultation: models.Consultation):
        json_with_themes = consultation_to_json(consultation)
        f = open(output_dir / "consultation_with_themes.json", "w")
        f.write(json_with_themes)
        f.close()
