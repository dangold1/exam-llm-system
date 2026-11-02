import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    AzureOpenAI,
    OpenAIError,
    RateLimitError,
)
from pydantic import ValidationError

from .models import GradeResult, GradingError
from .prompt_builder import build_messages, build_schema_repair_user_message

log = logging.getLogger(__name__)

_TRANSIENT_NETWORK = (APITimeoutError, APIConnectionError, RateLimitError)


def _strip_env(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.strip().strip('"').strip("'")


def _azure_api_key() -> Optional[str]:
    key = _strip_env(os.getenv("AZURE_OPENAI_API_KEY")) or _strip_env(os.getenv("AZURE_OPENAI_KEY"))
    return key or None


def _azure_api_version() -> str:
    return (
        _strip_env(os.getenv("AZURE_OPENAI_API_VERSION"))
        or _strip_env(os.getenv("AZURE_OPENAI_VERSION"))
        or _strip_env(os.getenv("OPENAI_API_VERSION"))
        or "2024-12-01-preview"
    )


def _normalize_azure_endpoint(raw: str) -> str:
    """SDK expects resource base URL (e.g. https://resource.openai.azure.com/), not a full chat/completions path."""
    s = _strip_env(raw)
    if not s:
        return s
    parsed = urlparse(s)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}/"
    return s if s.endswith("/") else f"{s}/"


def _extract_json_object(text: str) -> str:
    """Strip fences and isolate the outermost JSON object."""
    s = text.strip()
    if "```" in s:
        start = s.find("```")
        rest = s[start + 3 :]
        if rest.lstrip().lower().startswith("json"):
            nl = rest.find("\n")
            rest = rest[nl + 1 :] if nl != -1 else rest
        end = rest.find("```")
        if end != -1:
            s = rest[:end].strip()
    first = s.find("{")
    last = s.rfind("}")
    if first == -1 or last == -1 or last <= first:
        raise json.JSONDecodeError("No JSON object found in model output", s, 0)
    return s[first : last + 1]


def _is_transient_api_error(exc: BaseException) -> bool:
    if isinstance(exc, _TRANSIENT_NETWORK):
        return True
    if isinstance(exc, APIStatusError):
        return exc.status_code in (500, 502, 503, 504)
    return False


def _optional_grading_seed(question_id: Optional[int]) -> Optional[int]:
    """If GRADING_SEED is set, return an int for chat.completions seed (deployment-dependent)."""
    raw = _strip_env(os.getenv("GRADING_SEED", ""))
    if not raw:
        return None
    try:
        base = int(raw)
    except ValueError:
        log.warning("GRADING_SEED must be an integer; ignoring")
        return None
    mix = _strip_env(os.getenv("GRADING_SEED_INCLUDE_QUESTION_ID", "")).lower() in (
        "1",
        "true",
        "yes",
    )
    if mix and question_id is not None:
        return (base + int(question_id)) % (2**31 - 1)
    return base


class AzureOpenAIGrader:
    """Thin adapter over AzureOpenAI chat completions. Transport + retry only."""

    def __init__(
        self,
        client: Optional[AzureOpenAI] = None,
        deployment: Optional[str] = None,
        max_retries: int = 2,
    ):
        self.deployment = deployment or _strip_env(os.getenv("AZURE_OPENAI_DEPLOYMENT")) or "gpt-5-nano"
        self.max_retries = max_retries
        self._client = client or self._build_client()

    @staticmethod
    def _build_client() -> AzureOpenAI:
        endpoint = _normalize_azure_endpoint(os.getenv("AZURE_OPENAI_ENDPOINT"))
        api_key = _azure_api_key()
        ad_token = _strip_env(os.getenv("AZURE_OPENAI_AD_TOKEN")) or None
        api_version = _azure_api_version()
        if not endpoint:
            raise OpenAIError(
                "Set AZURE_OPENAI_ENDPOINT in python/server/.env "
                "(resource base URL, e.g. https://<resource>.openai.azure.com/)"
            )
        if not api_key and not ad_token:
            raise OpenAIError(
                "Set AZURE_OPENAI_KEY or AZURE_OPENAI_API_KEY in python/server/.env "
                "(Azure Portal → your OpenAI resource → Keys). "
                "Alternatively set AZURE_OPENAI_AD_TOKEN for token-based auth."
            )
        kwargs: Dict[str, Any] = dict(
            azure_endpoint=endpoint,
            api_version=api_version,
        )
        if api_key:
            kwargs["api_key"] = api_key
        else:
            kwargs["azure_ad_token"] = ad_token
        return AzureOpenAI(**kwargs)

    def grade_one(
        self,
        question_id: int,
        question_text: str,
        rubric: str,
        student_answer: str,
        max_score: int = 10,
    ) -> GradeResult:
        messages: List[Dict[str, str]] = list(
            build_messages(question_id, question_text, rubric, student_answer, max_score)
        )

        last_reason = "unknown"
        for attempt in range(self.max_retries + 1):
            try:
                raw = self._call(messages, question_id=question_id)
                payload = _extract_json_object(raw)
                parsed = json.loads(payload)
                parsed["question_id"] = question_id
                parsed["max_score"] = max_score
                parsed["grading_status"] = "ok"
                return GradeResult.model_validate(parsed)
            except _TRANSIENT_NETWORK as e:
                last_reason = f"transient: {type(e).__name__}"
                log.warning(
                    "Grading retry %d/%d for q=%s (%s)",
                    attempt + 1,
                    self.max_retries + 1,
                    question_id,
                    last_reason,
                )
            except APIError as e:
                if _is_transient_api_error(e):
                    code = getattr(e, "status_code", "?")
                    last_reason = f"transient-api: status={code}"
                    log.warning(
                        "Grading retry %d/%d for q=%s (%s: %s)",
                        attempt + 1,
                        self.max_retries + 1,
                        question_id,
                        last_reason,
                        e,
                    )
                else:
                    log.error("Grading permanent API error for q=%s: %s", question_id, e)
                    raise GradingError(f"api-error: {e}") from e
            except (json.JSONDecodeError, ValidationError) as e:
                last_reason = f"invalid-output: {type(e).__name__}: {e}"
                log.warning(
                    "Grading retry %d/%d for q=%s (%s)",
                    attempt + 1,
                    self.max_retries + 1,
                    question_id,
                    last_reason,
                )
                messages = messages + [{"role": "user", "content": build_schema_repair_user_message(max_score)}]

            if attempt < self.max_retries:
                time.sleep(0.5 * (3**attempt))

        raise GradingError(last_reason)

    def _call(self, messages: List[Dict[str, str]], question_id: Optional[int] = None) -> str:
        # Omit temperature: gpt-5-nano only allows service default.
        kwargs: Dict[str, Any] = dict(
            model=self.deployment,
            messages=messages,
            response_format={"type": "json_object"},
        )
        # Default 0 = omit cap. Low caps (e.g. 900) can yield empty assistant content on
        # reasoning-style models: internal reasoning may consume the budget before JSON is emitted.
        # To cap output, set GRADING_MAX_COMPLETION_TOKENS>=2048 for gpt-5-class deployments.
        mct_raw = _strip_env(os.getenv("GRADING_MAX_COMPLETION_TOKENS", "0"))
        try:
            mct = int(mct_raw) if mct_raw else 0
        except ValueError:
            mct = 0
        if mct > 0:
            kwargs["max_completion_tokens"] = mct

        re_eff = _strip_env(os.getenv("GRADING_REASONING_EFFORT", ""))
        if re_eff in ("none", "minimal", "low", "medium", "high", "xhigh"):
            kwargs["reasoning_effort"] = re_eff

        verb = _strip_env(os.getenv("GRADING_VERBOSITY", ""))
        if verb in ("low", "medium", "high"):
            kwargs["verbosity"] = verb

        seed_val = _optional_grading_seed(question_id)
        if seed_val is not None:
            kwargs["seed"] = seed_val

        try:
            resp = self._client.chat.completions.create(**kwargs)
        except TypeError:
            kwargs.pop("response_format", None)
            kwargs.pop("max_completion_tokens", None)
            kwargs.pop("reasoning_effort", None)
            kwargs.pop("verbosity", None)
            kwargs.pop("seed", None)
            resp = self._client.chat.completions.create(**kwargs)
        except APIError as e:
            msg = str(e).lower()
            if "response_format" in msg:
                kwargs.pop("response_format", None)
                resp = self._client.chat.completions.create(**kwargs)
            elif "max_completion_tokens" in msg or "max_tokens" in msg:
                kwargs.pop("max_completion_tokens", None)
                resp = self._client.chat.completions.create(**kwargs)
            elif "reasoning_effort" in msg or "verbosity" in msg:
                kwargs.pop("reasoning_effort", None)
                kwargs.pop("verbosity", None)
                resp = self._client.chat.completions.create(**kwargs)
            elif "seed" in msg:
                kwargs.pop("seed", None)
                resp = self._client.chat.completions.create(**kwargs)
            else:
                raise
        choice = resp.choices[0]
        msg = choice.message
        content = (msg.content or "").strip()
        log.debug(
            "chat.completion q=%s id=%s finish_reason=%s content_len=%s",
            question_id,
            getattr(resp, "id", None),
            choice.finish_reason,
            len(content),
        )
        preview_len_raw = _strip_env(os.getenv("GRADING_LOG_COMPLETION_PREVIEW", "0"))
        try:
            preview_len = int(preview_len_raw) if preview_len_raw else 0
        except ValueError:
            preview_len = 0
        if preview_len > 0 and content:
            log.info(
                "chat.completion preview q=%s: %s",
                question_id,
                content[:preview_len],
            )
        if not content:
            usage = getattr(resp, "usage", None)
            log.warning(
                "Empty assistant content (q=%s): completion_id=%s finish_reason=%s refusal=%r usage=%s",
                question_id,
                getattr(resp, "id", None),
                choice.finish_reason,
                msg.refusal,
                usage,
            )
        return content
