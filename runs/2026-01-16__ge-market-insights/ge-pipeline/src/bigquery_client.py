import logging
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

try:  # pragma: no cover - import guard
    from google.cloud import bigquery  # type: ignore
    _BQ_IMPORT_OK = True
except Exception:  # pragma: no cover - environment without dependency
    bigquery = None  # type: ignore
    _BQ_IMPORT_OK = False

from .config import Config, load_config

logger = logging.getLogger(__name__)


class BigQueryClient:
    """ADC-first BigQuery client wrapper.

    Behavior:
    - Uses user Application Default Credentials (gcloud auth application-default login).
    - Project ID read from BIGQUERY_PROJECT_ID or BIGQUERY_PROJECT.
    """

    def __init__(self, config: Optional[Config] = None):
        self.config: Config = config or load_config()
        self.client = None  # type: ignore[assignment]
        self.bigquery = bigquery if _BQ_IMPORT_OK else None  # type: ignore[assignment]
        if not _BQ_IMPORT_OK:
            logger.error("google-cloud-bigquery not installed. Run: pip install -r requirements.txt")
            return
        self._init_client()

    def _init_client(self) -> None:
        project_id = self.config.BIGQUERY_PROJECT_ID or None
        try:
            if not _BQ_IMPORT_OK:
                logger.error("google-cloud-bigquery not available; cannot initialize client")
                self.client = None
                return
            self.client = bigquery.Client(project=project_id)  # type: ignore[call-arg]
            logger.info("BigQuery client initialized (ADC) project=%s", project_id)
        except Exception as e:  # pragma: no cover
            logger.exception("Failed to initialize BigQuery client via ADC: %s", e)
            # Provide targeted remediation guidance for missing ADC credentials.
            hints = [
                "Check gcloud active account: gcloud config get-value account",
                "If no application_default_credentials.json exists, run: gcloud auth application-default login",
                "If browser auth fails with redirect_uri error, retry with: gcloud auth application-default login --no-browser",
                "Ensure the chosen Google account has BigQuery permissions on the project (roles/bigquery.readSessionUser at minimum for simple queries).",
                "Confirm project ID is set (env BIGQUERY_PROJECT_ID or config.yaml). Current detected project: %r" % project_id,
            ]
            logger.error("ADC remediation hints:\n- %s", "\n- ".join(hints))
            self.client = None

    def test_query(self) -> Optional[int]:
        if not self.client:
            logger.error("BigQuery client is not initialized")
            return None
        try:
            job = self.client.query("SELECT 1 AS ok")
            df = job.to_dataframe()
            return len(df)
        except Exception as e:  # pragma: no cover
            logger.exception("BigQuery test query failed: %s", e)
            return None

    @property
    def project_id(self) -> Optional[str]:
        return getattr(self.config, "BIGQUERY_PROJECT_ID", None)
