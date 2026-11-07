"""Quality gates for the template library.

- every template parses and declares only documented parameters
- every parameter has a description and appears in docs/parameters.md
- every example references templates that exist and passes valid parameters
- no em dashes and no obvious secrets anywhere in the repository
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import gen_param_docs  # noqa: E402

TEMPLATES = gen_param_docs.template_files()
EXAMPLES = sorted((ROOT / "examples").glob("*.yml"))
DOCS_TEXT = (ROOT / "docs" / "parameters.md").read_text(encoding="utf-8")
EXTERNAL_REF = re.compile(r"^(?P<path>.+)@templates$")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def declared(path: Path) -> dict[str, dict]:
    """Parameter name -> definition, read with a real YAML parser."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {p["name"]: p for p in data.get("parameters", [])}


def template_refs(node):
    """Yield (template, parameters) for every `template:` key in a YAML tree."""
    if isinstance(node, dict):
        if isinstance(node.get("template"), str):
            yield node["template"], node.get("parameters", {}) or {}
        for value in node.values():
            yield from template_refs(value)
    elif isinstance(node, list):
        for item in node:
            yield from template_refs(item)


@pytest.mark.parametrize("path", TEMPLATES, ids=rel)
def test_template_parses(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "template must be a mapping"
    assert any(key in data for key in ("stages", "jobs", "steps")), "template has no stages, jobs or steps"


@pytest.mark.parametrize("path", TEMPLATES, ids=rel)
def test_parameters_documented(path):
    header, parsed = gen_param_docs.parse_parameters(path)
    yaml_names = set(declared(path))
    assert {p.name for p in parsed} == yaml_names, "comment parser and YAML parser disagree"
    section = DOCS_TEXT.split(f"## {path.relative_to(ROOT / 'templates').as_posix()}\n", 1)
    assert len(section) == 2, f"{rel(path)} has no section in docs/parameters.md"
    body = section[1].split("\n## ", 1)[0]
    for param in parsed:
        assert param.description, f"{rel(path)}: parameter '{param.name}' needs a comment line above it"
        assert f"| `{param.name}` |" in body, f"{rel(path)}: '{param.name}' missing from docs/parameters.md"


def test_parameter_docs_are_current():
    assert gen_param_docs.render() == DOCS_TEXT, "run: python scripts/gen_param_docs.py"


@pytest.mark.parametrize("path", TEMPLATES, ids=rel)
def test_internal_template_references_exist(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for ref, params in template_refs(data):
        target = (path.parent / ref).resolve()
        assert target.is_file(), f"{rel(path)} references missing template {ref}"
        allowed = declared(target)
        unknown = set(params) - set(allowed)
        assert not unknown, f"{rel(path)} passes unknown parameters {sorted(unknown)} to {ref}"
        missing = {n for n, d in allowed.items() if "default" not in d} - set(params)
        assert not missing, f"{rel(path)} omits required parameters {sorted(missing)} of {ref}"


@pytest.mark.parametrize("path", EXAMPLES, ids=rel)
def test_example_references_exist(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    refs = list(template_refs(data))
    assert refs, "example does not consume any template"
    for ref, params in refs:
        match = EXTERNAL_REF.match(ref)
        assert match, f"{rel(path)}: '{ref}' must use the @templates repository alias"
        target = ROOT / "templates" / Path(match["path"]).relative_to("templates")
        assert target.is_file(), f"{rel(path)} references missing template {ref}"
        allowed = declared(target)
        unknown = set(params) - set(allowed)
        assert not unknown, f"{rel(path)} passes unknown parameters {sorted(unknown)} to {ref}"
        missing = {n for n, d in allowed.items() if "default" not in d} - set(params)
        assert not missing, f"{rel(path)} omits required parameters {sorted(missing)} of {ref}"


@pytest.mark.parametrize("path", EXAMPLES, ids=rel)
def test_example_pins_template_version(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    repos = {r["repository"]: r for r in data["resources"]["repositories"]}
    assert repos["templates"]["ref"].startswith("refs/tags/"), "pin the template repo to a tag"


def text_files():
    skip = {".git", ".pytest_cache", "__pycache__"}
    for path in ROOT.rglob("*"):
        if path.is_file() and path != Path(__file__).resolve() and not skip & set(path.relative_to(ROOT).parts):
            yield path


@pytest.mark.parametrize("path", list(text_files()), ids=rel)
def test_no_em_dash_or_secret(path):
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    assert chr(0x2014) not in text, "em dash found"
    assert "persistCredentials: true" not in text
    assert not re.search(r"(?i)(password|secret|token)\s*:\s*['\"]?[A-Za-z0-9+/=_-]{16,}", text), "possible secret"
    assert "\r\n" not in text, "CRLF line endings"
