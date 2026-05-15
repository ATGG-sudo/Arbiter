from __future__ import annotations

import builtins
import json
from typing import Any, Literal

import pytest
from pydantic import create_model

from arbiter.llm.i18n_enums import (
    ENUM_REGISTRY,
    SEMANTIC_UNIT_TYPE_I18N,
    translate_response_enums,
    translate_schema_enums,
)
from arbiter.schemas.regulation_structuring import (
    DocumentClassificationDraft,
    SemanticUnitDraft,
)


class TestTranslateSchemaEnums:
    def test_translates_semantic_unit_type_enum(self) -> None:
        schema = SemanticUnitDraft.model_json_schema()
        translated, reverse_maps = translate_schema_enums(schema)

        # The original schema should not be mutated
        original_enum = schema["$defs"]["SemanticUnitType"]["enum"]
        assert set(original_enum) == set(SEMANTIC_UNIT_TYPE_I18N)

        # Translated schema should contain Chinese values
        translated_enum = translated["$defs"]["SemanticUnitType"]["enum"]
        assert "定义" in translated_enum
        assert "义务" in translated_enum
        assert "禁止" in translated_enum
        assert "未知" in translated_enum
        assert "definition" not in translated_enum

        # Reverse map should be present without depending on Pydantic path names.
        assert any(
            reverse_map.get("定义") == "definition"
            and reverse_map.get("义务") == "obligation"
            for reverse_map in reverse_maps.values()
        )

    def test_adds_locale_hint_to_description(self) -> None:
        schema = SemanticUnitDraft.model_json_schema()
        translated, _ = translate_schema_enums(schema)

        desc = translated["$defs"]["SemanticUnitType"].get("description", "")
        assert "枚举值已本地化为中文" in desc

    def test_leaves_non_enum_fields_intact(self) -> None:
        schema = SemanticUnitDraft.model_json_schema()
        translated, _ = translate_schema_enums(schema)

        # Property keys and types remain unchanged
        assert "properties" in translated
        assert "unit_type" in translated["properties"]
        assert "summary" in translated["properties"]

    def test_returns_empty_reverse_maps_for_no_matches(self) -> None:
        # A schema with an enum that has no registered translation
        schema = {
            "type": "object",
            "properties": {
                "color": {
                    "type": "string",
                    "enum": ["red", "green", "blue"],
                }
            },
        }
        translated, reverse_maps = translate_schema_enums(schema)

        assert translated["properties"]["color"]["enum"] == ["red", "green", "blue"]
        assert reverse_maps == {}

    def test_translates_const_values(self) -> None:
        model = create_model(
            "ConstModel",
            content_type=(Literal["normalized_text"], "normalized_text"),
        )
        schema = model.model_json_schema()
        translated, reverse_maps = translate_schema_enums(schema)

        assert translated["properties"]["content_type"]["const"] == "规范化文本"

        result = translate_response_enums(
            {"content_type": "规范化文本", "notes": "规范化文本"},
            reverse_maps,
        )
        assert result == {
            "content_type": "normalized_text",
            "notes": "规范化文本",
        }


class TestTranslateResponseEnums:
    def test_translates_chinese_enum_values_back_to_english(self) -> None:
        _, reverse_maps = translate_schema_enums(SemanticUnitDraft.model_json_schema())
        data = {
            "unit_type": "义务",
            "summary": "这是一个中文摘要",
            "definitions": ["定义1", "定义2"],
        }
        result = translate_response_enums(data, reverse_maps)

        assert result["unit_type"] == "obligation"
        assert result["summary"] == "这是一个中文摘要"
        assert result["definitions"] == ["定义1", "定义2"]

    def test_does_not_translate_free_text_exact_enum_matches(self) -> None:
        _, reverse_maps = translate_schema_enums(SemanticUnitDraft.model_json_schema())
        data = {
            "unit_type": "义务",
            "summary": "未知",
            "definitions": ["定义"],
            "evidence_text": ["未知", "待审阅"],
            "review_status": "待审阅",
        }

        result = translate_response_enums(data, reverse_maps)

        assert result["unit_type"] == "obligation"
        assert result["review_status"] == "needs_review"
        assert result["summary"] == "未知"
        assert result["definitions"] == ["定义"]
        assert result["evidence_text"] == ["未知", "待审阅"]

    def test_leaves_unmatched_strings_unchanged(self) -> None:
        reverse_maps = {
            "root.unit_type": {
                "定义": "definition",
            }
        }
        data = {"unit_type": "不存在的中文", "summary": "不受影响"}
        result = translate_response_enums(data, reverse_maps)

        assert result["unit_type"] == "不存在的中文"
        assert result["summary"] == "不受影响"

    def test_handles_nested_structures(self) -> None:
        reverse_maps = {
            "root.semantic_draft.review_status": {
                "待审阅": "needs_review",
            },
            "root.list[].review_status": {
                "待审阅": "needs_review",
            }
        }
        data = {
            "semantic_draft": {
                "review_status": "待审阅",
            },
            "list": [{"review_status": "待审阅"}],
        }
        result = translate_response_enums(data, reverse_maps)

        assert result["semantic_draft"]["review_status"] == "needs_review"
        assert result["list"][0]["review_status"] == "needs_review"

    def test_translates_items_and_anyof_without_touching_sibling_text(self) -> None:
        schema = {
            "type": "object",
            "properties": {
                "statuses": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["needs_review", "approved", "rejected", "superseded"],
                    },
                },
                "maybe_status": {
                    "anyOf": [
                        {
                            "type": "string",
                            "enum": [
                                "needs_review",
                                "approved",
                                "rejected",
                                "superseded",
                            ],
                        },
                        {"type": "null"},
                    ]
                },
                "notes": {"type": "array", "items": {"type": "string"}},
            },
        }
        translated, reverse_maps = translate_schema_enums(schema)
        data = {
            "statuses": ["待审阅", "已批准"],
            "maybe_status": "已拒绝",
            "notes": ["待审阅"],
        }

        result = translate_response_enums(data, reverse_maps)

        assert "待审阅" in translated["properties"]["statuses"]["items"]["enum"]
        assert result == {
            "statuses": ["needs_review", "approved"],
            "maybe_status": "rejected",
            "notes": ["待审阅"],
        }

    def test_returns_data_unchanged_when_reverse_maps_empty(self) -> None:
        data = {"unit_type": "obligation"}
        result = translate_response_enums(data, {})
        assert result == data


class TestI18nEndToEnd:
    def test_zh_locale_translates_enum_in_prompt_and_response(self) -> None:
        from arbiter.llm import OpenAICompatibleModelProvider

        captured: dict[str, Any] = {}

        def transport(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
            captured["payload"] = payload
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "unit_type": "义务",
                                    "summary": "未知",
                                    "definitions": ["定义"],
                                    "evidence_text": ["待审阅"],
                                    "review_status": "待审阅",
                                },
                                ensure_ascii=False,
                            )
                        }
                    }
                ]
            }

        provider = OpenAICompatibleModelProvider(
            api_key="test-key",
            base_url="https://example.test",
            model="test-model",
            transport=transport,
            locale="zh",
        )

        result = provider.structured_output(
            schema=SemanticUnitDraft,
            prompt="提取语义结构",
            context={},
        )

        assert result is not None
        assert result.unit_type.value == "obligation"
        assert result.summary == "未知"
        assert result.definitions == ["定义"]
        assert result.evidence_text == ["待审阅"]
        assert result.review_status.value == "needs_review"

        # Verify the prompt schema contains Chinese enum values
        system_content = captured["payload"]["messages"][0]["content"]
        assert "义务" in system_content
        assert "定义" in system_content
        assert "待审阅" in system_content

    def test_en_locale_leaves_enum_unchanged(self) -> None:
        from arbiter.llm import OpenAICompatibleModelProvider

        captured: dict[str, Any] = {}

        def transport(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
            captured["payload"] = payload
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "unit_type": "obligation",
                                    "summary": "English summary",
                                    "review_status": "needs_review",
                                }
                            )
                        }
                    }
                ]
            }

        provider = OpenAICompatibleModelProvider(
            api_key="test-key",
            base_url="https://example.test",
            model="test-model",
            transport=transport,
            locale="en",
        )

        result = provider.structured_output(
            schema=SemanticUnitDraft,
            prompt="Extract semantic structure",
            context={},
        )

        assert result is not None
        assert result.unit_type.value == "obligation"

        # Verify the prompt schema still uses English enum values
        system_content = captured["payload"]["messages"][0]["content"]
        assert "obligation" in system_content
        assert "义务" not in system_content

    @pytest.mark.parametrize("locale", ["en", "", None])
    def test_default_locale_paths_do_not_import_i18n_module(
        self, monkeypatch: pytest.MonkeyPatch, locale: str | None
    ) -> None:
        from arbiter.llm import OpenAICompatibleModelProvider

        real_import = builtins.__import__

        def guarded_import(name: str, *args: Any, **kwargs: Any) -> Any:
            if name == "arbiter.llm.i18n_enums":
                raise AssertionError("i18n module should not load for en locale")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", guarded_import)

        provider = OpenAICompatibleModelProvider(
            api_key="test-key",
            base_url="https://example.test",
            model="test-model",
            transport=lambda _payload, _headers: {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "unit_type": "obligation",
                                    "summary": "English summary",
                                    "review_status": "needs_review",
                                }
                            )
                        }
                    }
                ]
            },
            locale=locale,
        )

        result = provider.structured_output(
            schema=SemanticUnitDraft,
            prompt="Extract semantic structure",
            context={},
        )

        assert result is not None
        assert result.unit_type.value == "obligation"


class TestRegistryUniqueness:
    def test_all_enum_registries_have_unique_key_sets(self) -> None:
        """Ensure no two registries share the exact same set of English keys,
        otherwise _match_registry could pick the wrong translation."""
        seen: set[frozenset[str]] = set()
        for registry in ENUM_REGISTRY:
            key_set = frozenset(registry.keys())
            assert key_set not in seen, f"Duplicate enum key set found: {set(key_set)}"
            seen.add(key_set)

    def test_no_colliding_translations_across_registries(self) -> None:
        """Ensure a Chinese translation maps back to exactly one English value
        across all registries.  Otherwise translate_response_enums could
        mis-translate."""
        unified: dict[str, str] = {}
        for registry in ENUM_REGISTRY:
            for en, zh in registry.items():
                if zh in unified:
                    assert unified[zh] == en, (
                        f"Translation collision: '{zh}' maps to both "
                        f"'{unified[zh]}' and '{en}'"
                    )
                else:
                    unified[zh] = en
