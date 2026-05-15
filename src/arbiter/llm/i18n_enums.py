"""LLM schema enum i18n translation layer.

Internal data flow (Pydantic models, JSON API, Zod contracts) remains English.
This module translates enum values to the target locale only for LLM
interaction, then maps the LLM response back to English before Pydantic
validation.

To add a new locale or extend existing mappings, edit the translation
 dictionaries below and register them in ``ENUM_REGISTRY``.
"""

from __future__ import annotations

import copy
from typing import Any, TypeVar, cast

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Translation dictionaries: English enum value -> Chinese display value
# ---------------------------------------------------------------------------

SEMANTIC_UNIT_TYPE_I18N: dict[str, str] = {
    "definition": "定义",
    "obligation": "义务",
    "prohibition": "禁止",
    "procedure": "程序",
    "exception": "例外",
    "condition": "条件",
    "reporting": "报告",
    "threshold": "阈值",
    "authorization": "授权",
    "liability": "责任",
    "general": "一般",
    "unknown": "未知",
}

DOCUMENT_STATUS_I18N: dict[str, str] = {
    "official": "正式",
    "draft_for_comment": "征求意见",
    "deprecated": "已废止",
    "unknown": "未知",
}

PARSE_STATUS_I18N: dict[str, str] = {
    "parsed": "已解析",
    "partial": "部分解析",
    "needs_review": "待审阅",
    "failed": "失败",
}

REVIEW_STATUS_I18N: dict[str, str] = {
    "needs_review": "待审阅",
    "approved": "已批准",
    "rejected": "已拒绝",
    "superseded": "已替代",
}

DOCUMENT_SOURCE_TYPE_I18N: dict[str, str] = {
    "external_regulation": "外部法规",
    "internal_policy": "内部制度",
    "unknown": "未知",
}

ISSUER_TYPE_I18N: dict[str, str] = {
    "government_regulator": "政府监管机构",
    "self_regulatory_organization": "自律组织",
    "internal_org": "内部组织",
    "external_other": "其他外部组织",
    "joint_issuers": "联合发布方",
    "unknown": "未知",
}

SOURCE_LOCATION_KIND_I18N: dict[str, str] = {
    "page_number": "页码",
    "line_number": "行号",
    "paragraph_index": "段落索引",
    "heading_path": "标题路径",
    "unknown": "未知",
}

VALIDATION_SEVERITY_I18N: dict[str, str] = {
    "info": "信息",
    "warning": "警告",
    "error": "错误",
}

EXTRACTION_METHOD_I18N: dict[str, str] = {
    "deterministic": "确定性",
    "llm_assisted": "LLM辅助",
    "mixed": "混合",
}

RELATION_KIND_I18N: dict[str, str] = {
    "definition_applies": "定义适用",
    "exception_to": "例外于",
    "condition_for": "条件为",
    "procedure_for": "程序为",
    "cross_reference": "交叉引用",
    "other_dependency": "其他依赖",
}

UNIT_KIND_I18N: dict[str, str] = {
    "part": "部分",
    "chapter": "章",
    "section": "节",
    "article": "条",
    "paragraph": "段落",
    "item": "项",
    "subitem": "子项",
    "appendix": "附录",
    "unknown": "未知",
}

TARGET_SCOPE_I18N: dict[str, str] = {
    "same_document": "同文档",
    "external_document": "外部文档",
    "unknown": "未知",
}

RESOLUTION_STATUS_I18N: dict[str, str] = {
    "resolved": "已解决",
    "unresolved": "未解决",
    "ambiguous": "模糊",
}

CATEGORY_SCHEME_I18N: dict[str, str] = {
    "external_regulation_type": "外部法规类型",
    "internal_policy_type": "内部制度类型",
    "business_domain": "业务领域",
    "compliance_topic": "合规主题",
    "custom": "自定义",
}

STAGE_I18N: dict[str, str] = {
    "input": "输入",
    "document": "文档",
    "unit": "单元",
    "semantic": "语义",
    "reference": "引用",
    "dependency": "依赖",
    "output": "输出",
}

TARGET_TYPE_I18N: dict[str, str] = {
    "document": "文档",
    "unit": "单元",
    "semantic_draft": "语义草稿",
    "reference_candidate": "引用候选",
    "dependency_edge": "依赖边",
    "pipeline_output": "管道输出",
    "unknown": "未知",
}

FILE_TYPE_I18N: dict[str, str] = {
    "pdf": "PDF",
    "docx": "Word",
    "markdown": "Markdown",
    "text": "文本",
}

CONTENT_TYPE_I18N: dict[str, str] = {
    "normalized_text": "规范化文本",
    "markdown": "Markdown",
}

# ---------------------------------------------------------------------------
# Registry: all translation dictionaries used for schema matching.
#
# When walking a JSON Schema, if an ``enum`` array's values exactly match the
# keys of a registered dict, that dict is used to translate the enum.
# ---------------------------------------------------------------------------

ENUM_REGISTRY: list[dict[str, str]] = [
    SEMANTIC_UNIT_TYPE_I18N,
    DOCUMENT_STATUS_I18N,
    PARSE_STATUS_I18N,
    REVIEW_STATUS_I18N,
    DOCUMENT_SOURCE_TYPE_I18N,
    ISSUER_TYPE_I18N,
    SOURCE_LOCATION_KIND_I18N,
    VALIDATION_SEVERITY_I18N,
    EXTRACTION_METHOD_I18N,
    RELATION_KIND_I18N,
    UNIT_KIND_I18N,
    TARGET_SCOPE_I18N,
    RESOLUTION_STATUS_I18N,
    CATEGORY_SCHEME_I18N,
    STAGE_I18N,
    TARGET_TYPE_I18N,
    FILE_TYPE_I18N,
    CONTENT_TYPE_I18N,
]

_LOCALE_HINT = "(枚举值已本地化为中文，请使用上述中文值输出)"


def _validate_enum_registry() -> None:
    """Fail fast if registered enum translations would be ambiguous."""
    seen_key_sets: set[frozenset[str]] = set()
    translated_to_english: dict[str, str] = {}

    for translation in ENUM_REGISTRY:
        key_set = frozenset(translation)
        if key_set in seen_key_sets:
            raise ValueError(f"Duplicate enum key set found: {set(key_set)}")
        seen_key_sets.add(key_set)

        for english, translated in translation.items():
            existing = translated_to_english.get(translated)
            if existing is not None and existing != english:
                raise ValueError(
                    "Ambiguous enum translation: "
                    f"{translated!r} maps to both {existing!r} and {english!r}"
                )
            translated_to_english[translated] = english


_validate_enum_registry()

_REGISTRY_BY_KEYS: list[tuple[frozenset[str], dict[str, str]]] = [
    (frozenset(translation), translation) for translation in ENUM_REGISTRY
]
_REGISTRY_BY_TRANSLATED_VALUES: list[tuple[frozenset[str], dict[str, str]]] = [
    (frozenset(translation.values()), translation) for translation in ENUM_REGISTRY
]
_TRANSLATED_VALUE_TO_ENGLISH: dict[str, str] = {
    translated: english
    for translation in ENUM_REGISTRY
    for english, translated in translation.items()
}


def _build_reverse_map(translation: dict[str, str]) -> dict[str, str]:
    """Build a reverse map from translated value back to the English key."""
    return {v: k for k, v in translation.items()}


def _match_registry(enum_values: list[Any]) -> dict[str, str] | None:
    """Find a registered translation dict whose keys exactly match *enum_values*."""
    if not all(isinstance(value, str) for value in enum_values):
        return None
    enum_set = frozenset(enum_values)
    for key_set, trans in _REGISTRY_BY_KEYS:
        if key_set == enum_set:
            return trans
    return None


def _match_const(value: Any) -> dict[str, str] | None:
    """Return a one-value translation map for a single-value Literal const."""
    if not isinstance(value, str):
        return None

    translated_values = {
        translation[value] for translation in ENUM_REGISTRY if value in translation
    }
    if not translated_values:
        return None
    if len(translated_values) > 1:
        raise ValueError(f"Ambiguous const translation for {value!r}")
    return {value: translated_values.pop()}


def _match_translated_registry(enum_values: list[Any]) -> dict[str, str] | None:
    if not all(isinstance(value, str) for value in enum_values):
        return None
    enum_set = frozenset(enum_values)
    for translated_set, trans in _REGISTRY_BY_TRANSLATED_VALUES:
        if translated_set == enum_set:
            return trans
    return None


def _reverse_map_for_translated_node(node: dict[str, Any]) -> dict[str, str] | None:
    enum_values = node.get("enum")
    if isinstance(enum_values, list) and enum_values:
        trans = _match_translated_registry(enum_values)
        if trans:
            return _build_reverse_map(trans)

    const_value = node.get("const")
    if isinstance(const_value, str):
        english = _TRANSLATED_VALUE_TO_ENGLISH.get(const_value)
        if english is not None:
            return {const_value: english}

    return None


def _add_locale_hint(node: dict[str, Any]) -> None:
    existing_desc = node.get("description", "")
    node["description"] = (
        f"{existing_desc}\n{_LOCALE_HINT}".strip() if existing_desc else _LOCALE_HINT
    )


def _unescape_json_pointer_part(part: str) -> str:
    return part.replace("~1", "/").replace("~0", "~")


def _resolve_ref(ref: str, root: dict[str, Any]) -> dict[str, Any] | None:
    if not ref.startswith("#/"):
        return None

    current: Any = root
    for part in ref[2:].split("/"):
        part = _unescape_json_pointer_part(part)
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current if isinstance(current, dict) else None


def _schema_path_from_ref(ref: str) -> str:
    if not ref.startswith("#/"):
        return ref
    parts = [_unescape_json_pointer_part(part) for part in ref[2:].split("/")]
    return "root." + ".".join(parts)


def _merge_reverse_map(
    reverse_maps: dict[str, dict[str, str]],
    path: str,
    new_reverse: dict[str, str],
) -> None:
    existing = reverse_maps.get(path)
    if existing is None:
        reverse_maps[path] = dict(new_reverse)
        return

    merged = dict(existing)
    for translated, english in new_reverse.items():
        if translated in merged and merged[translated] != english:
            raise ValueError(
                "Ambiguous response enum translation at "
                f"{path}: {translated!r} maps to both "
                f"{merged[translated]!r} and {english!r}"
            )
        merged[translated] = english
    reverse_maps[path] = merged


def translate_schema_enums(
    schema: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, dict[str, str]]]:
    """Return a deep-copied schema with English enums replaced by Chinese.

    The returned tuple contains:
    1. The translated schema (safe to mutate further).
    2. A flat dictionary of reverse mappings keyed by schema and response paths,
       e.g. ``{"root.unit_type": {"义务": "obligation", ...}}``.
       Callers typically pass this to :func:`translate_response_enums`.
    """
    translated = copy.deepcopy(schema)
    reverse_maps: dict[str, dict[str, str]] = {}

    def _walk_schema(node: Any, path: str, visited: set[int]) -> None:
        if not isinstance(node, dict):
            return
        node_id = id(node)
        if node_id in visited:
            return
        visited.add(node_id)

        ref = node.get("$ref")
        if isinstance(ref, str):
            resolved = _resolve_ref(ref, translated)
            if resolved is not None:
                _walk_schema(resolved, _schema_path_from_ref(ref), visited)

        enum_values = node.get("enum")
        if isinstance(enum_values, list) and enum_values:
            trans = _match_registry(enum_values)
            if trans:
                node["enum"] = [trans.get(v, v) for v in enum_values]
                if node.get("default") in trans:
                    node["default"] = trans[node["default"]]
                _add_locale_hint(node)
                _merge_reverse_map(reverse_maps, path, _build_reverse_map(trans))

        const_value = node.get("const")
        trans_const = _match_const(const_value)
        if trans_const:
            node["const"] = trans_const[const_value]
            if node.get("default") == const_value:
                node["default"] = trans_const[const_value]
            _add_locale_hint(node)
            _merge_reverse_map(reverse_maps, path, _build_reverse_map(trans_const))

        for key in ("properties", "$defs", "definitions", "patternProperties"):
            child = node.get(key)
            if isinstance(child, dict):
                for sub_key, sub_node in child.items():
                    _walk_schema(sub_node, f"{path}.{key}.{sub_key}", visited)

        for key in ("additionalProperties", "propertyNames", "contains", "items"):
            child = node.get(key)
            if isinstance(child, dict):
                _walk_schema(child, f"{path}.{key}", visited)

        prefix_items = node.get("prefixItems")
        if isinstance(prefix_items, list):
            for i, sub in enumerate(prefix_items):
                _walk_schema(sub, f"{path}.prefixItems[{i}]", visited)

        for key in ("anyOf", "oneOf", "allOf"):
            arr = node.get(key)
            if isinstance(arr, list):
                for i, sub in enumerate(arr):
                    _walk_schema(sub, f"{path}.{key}[{i}]", visited)

    def _collect_response_maps(
        node: Any,
        path: str,
        ref_stack: set[str],
    ) -> None:
        if not isinstance(node, dict):
            return

        ref = node.get("$ref")
        if isinstance(ref, str):
            if ref in ref_stack:
                return
            resolved = _resolve_ref(ref, translated)
            if resolved is not None:
                _collect_response_maps(resolved, path, ref_stack | {ref})

        reverse_map = _reverse_map_for_translated_node(node)
        if reverse_map:
            _merge_reverse_map(reverse_maps, path, reverse_map)

        for key in ("anyOf", "oneOf", "allOf"):
            arr = node.get(key)
            if isinstance(arr, list):
                for sub in arr:
                    _collect_response_maps(sub, path, ref_stack)

        properties = node.get("properties")
        if isinstance(properties, dict):
            for prop_name, prop_schema in properties.items():
                _collect_response_maps(prop_schema, f"{path}.{prop_name}", ref_stack)

        items = node.get("items")
        if isinstance(items, dict):
            _collect_response_maps(items, f"{path}[]", ref_stack)

        prefix_items = node.get("prefixItems")
        if isinstance(prefix_items, list):
            for sub in prefix_items:
                _collect_response_maps(sub, f"{path}[]", ref_stack)

        contains = node.get("contains")
        if isinstance(contains, dict):
            _collect_response_maps(contains, f"{path}[]", ref_stack)

        for key in ("additionalProperties", "patternProperties"):
            child = node.get(key)
            if isinstance(child, dict):
                if key == "patternProperties":
                    for sub in child.values():
                        _collect_response_maps(sub, f"{path}.*", ref_stack)
                else:
                    _collect_response_maps(child, f"{path}.*", ref_stack)

    _walk_schema(translated, "root", set())
    _collect_response_maps(translated, "root", set())
    return translated, reverse_maps


def translate_response_enums(
    data: T,
    reverse_maps: dict[str, dict[str, str]],
) -> T:
    """Translate Chinese enum values in an LLM response back to English.

    Only values at schema-derived response paths are translated. Free-text
    fields remain untouched even if their entire value equals a translated enum.
    """
    if not reverse_maps:
        return data

    def _wildcard_reverse(path: str) -> dict[str, str] | None:
        if "." not in path:
            return None
        parent, _ = path.rsplit(".", 1)
        return reverse_maps.get(f"{parent}.*")

    def _walk(node: Any, path: str) -> Any:
        if isinstance(node, dict):
            return {k: _walk(v, f"{path}.{k}") for k, v in node.items()}
        if isinstance(node, list):
            return [_walk(item, f"{path}[]") for item in node]
        if isinstance(node, str):
            reverse_map = reverse_maps.get(path) or _wildcard_reverse(path)
            if reverse_map:
                return reverse_map.get(node, node)
            return node
        return node

    return cast(T, _walk(data, "root"))


__all__ = [
    "ENUM_REGISTRY",
    "translate_response_enums",
    "translate_schema_enums",
]
