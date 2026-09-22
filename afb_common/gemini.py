"""Shared Gemini extraction runner for the afb-extract-* skills.

Vertex AI by default (project/location from config); resumable (skips Filenames already
in the output CSV); throttled; supports --dry-run (no API calls) and --limit N.
Imported lazily so the non-Gemini skills never need the google libraries.
"""
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
from tenacity import retry, wait_exponential, stop_after_attempt

from .config import CONFIG, ROOT
from .io import save_csv

G = CONFIG["gemini"]
V = CONFIG["video"]
KEY = CONFIG["columns"]["key"]


def make_client():
    from google import genai
    if G.get("auth_method") == "api_key":
        key = (ROOT / G["api_key_file"]).read_text(encoding="utf-8").strip()
        return genai.Client(api_key=key)
    return genai.Client(vertexai=True, project=G["project"], location=G["location"])


def gcs_uri(filename):
    return f"gs://{V['gcs_bucket']}/{V['gcs_prefix']}/" + V["filename_pattern"].format(Filename=str(filename))


def _load_done(out_path):
    if Path(out_path).exists():
        try:
            prev = pd.read_csv(out_path, dtype={KEY: str})
            return prev, set(prev[KEY].astype(str))
        except Exception:
            pass
    return None, set()


def run_extraction(df, build_contents, schema, system_prompt, out_path, feature_map, log,
                   dry_run=False, limit=None, workers=1):
    """Resumable extraction loop.

    df            rows to process (already filtered to the relevant subset)
    build_contents(row, types) -> list passed as `contents` to generate_content
    feature_map   {pydantic_field: output_column}
    """
    from google.genai import types

    prev, done = _load_done(out_path)
    todo = df[~df[KEY].astype(str).isin(done)].reset_index(drop=True)
    if limit is not None:
        todo = todo.head(limit)
    log.info(f"{len(df)} target rows | {len(done)} already done | {len(todo)} to process"
             + (f" (limit={limit})" if limit else "") + f" | workers={workers}")

    if dry_run:
        log.info("DRY RUN — request preview for up to 3 rows, NO API calls")
        log.info(f"model={G['model']} temperature={G['temperature']} thinking_budget={G['thinking_budget']}")
        log.info(f"system_prompt: {len(system_prompt)} chars | schema fields: {list(schema.model_fields)}")
        for _, row in todo.head(3).iterrows():
            parts = []
            for c in build_contents(row, types):
                if isinstance(c, str):
                    parts.append(f"text[{len(c)}c]:{c[:60].replace(chr(10),' ')}")
                else:
                    fd = getattr(c, "file_data", None)
                    vm = getattr(c, "video_metadata", None)
                    parts.append(f"video:{getattr(fd,'file_uri','?')}"
                                 + (f"@{vm.end_offset}" if vm and getattr(vm, "end_offset", None) else ""))
            log.info(f"  {row[KEY]} -> {parts}")
        log.info(f"would write {out_path} cols={[KEY] + list(feature_map.values())}")
        return

    client = make_client()

    @retry(wait=wait_exponential(multiplier=10, min=10, max=60),
           stop=stop_after_attempt(G["max_retries"]), reraise=True)
    def _call(contents):
        resp = client.models.generate_content(
            model=G["model"], contents=contents,
            config={"system_instruction": system_prompt, "response_mime_type": "application/json",
                    "response_schema": schema, "temperature": G["temperature"],
                    "max_output_tokens": G["max_output_tokens"],
                    "thinking_config": {"thinking_budget": G["thinking_budget"]}})
        if resp.parsed is not None:
            return resp.parsed.model_dump()
        return json.loads(resp.text or "{}")

    prev_df = prev if prev is not None else pd.DataFrame()
    results, lock = [], threading.Lock()
    counters = {"ok": 0, "err": 0}
    total = len(todo)

    def process(row):
        fid = str(row[KEY])
        try:
            res = _call(build_contents(row, types))
            rec = {KEY: fid, **{col: res.get(field) for field, col in feature_map.items()}}
            is_err = False
        except Exception as e:
            rec = {KEY: fid, **{col: f"ERROR: {str(e)[:80]}" for col in feature_map.values()}}
            is_err = True
            log.warning(f"  {fid}: {type(e).__name__}: {str(e)[:120]}")
        time.sleep(G["rate_limit_sleep_sec"])  # throttle inside each worker
        with lock:
            results.append(rec)
            counters["err" if is_err else "ok"] += 1
            n = len(results)
            if n % 25 == 0 or n == total:
                save_csv(pd.concat([prev_df, pd.DataFrame(results)], ignore_index=True), out_path)
                log.info(f"  progress {n}/{total} (ok={counters['ok']} err={counters['err']})")

    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        list(ex.map(process, [row for _, row in todo.iterrows()]))

    save_csv(pd.concat([prev_df, pd.DataFrame(results)], ignore_index=True), out_path)
    log.info(f"done: {counters['ok']} ok, {counters['err']} errors -> {out_path}")
