# US-002 Entity Memory + Context-Aware Translation

## Status

in_progress

## Lane

high-risk

## Product Contract

After receiving a transcript, the system extracts named entities (persons, amounts, dates, org names) and adds them to session-scoped EntityMemory. EntityMemory plus OnPoint domain glossary are injected into the Claude Haiku system prompt. The backend invokes Claude Haiku 4.5 through Amazon Bedrock Runtime and returns a translation that preserves all entities exactly as spoken.

## Relevant Product Docs

- `docs/product/overview.md`
- `docs/product/evaluation.md`
- `docs/decisions/0007-translation-model.md`
- `docs/decisions/0010-bedrock-claude-access-path.md`

## Acceptance Criteria

- `EntityMemory.update(text)` extracts entities from transcript and merges into session memory.
- `claude_client.translate(text, language, entity_memory)` invokes Amazon Bedrock Runtime and returns `TranslationResult` with `translated` field non-empty.
- Numbers, dates, and proper nouns in source appear verbatim in translation output.
- OnPoint glossary terms (Opollo, CREA, GMV, OnPoint) are never translated — kept as-is.
- Empty/silent transcript skips Claude call entirely — `translate()` not called.
- Bedrock/Claude API errors return `TranslationResult(error=...)` — do not raise.

## Design Notes

- Commands: `EntityMemory.update(text)`, `translate(text, lang, memory) → TranslationResult`
- Queries: `EntityMemory.to_prompt_fragment() → str`
- API: internal only
- Tables: none
- Domain rules:
  - Entity extraction uses regex patterns for VN amounts (`\d+[\s]*(tỷ|triệu|nghìn)`), dates (`Q[1-4]`, `\d{1,2}/\d{4}`), and capitalized proper nouns
  - Glossary is a static seed list in `domain/glossary.py`
- System prompt structure:
  ```
  You are a professional interpreter for OnPoint, a Vietnamese e-commerce company.
  Translate {source_lang} to {target_lang}.
  Preserve exactly: numbers, dates, amounts, proper nouns.
  Do not translate these terms: {glossary_terms}.
  Known entities this session: {entity_memory_fragment}.
  Return only the translated text. No explanation.
  ```

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | `test_entity_memory.py`: entity extraction from sample sentences, glossary term detection |
| Integration | `test_claude_client.py`: Bedrock request/response contract with fixture; credentialed Bedrock call must assert entity preservation before completion |
| E2E | Covered by US-003 |
| Platform | Manual check: speak "doanh thu Q1 đạt 150 tỷ" → EN output must contain "150" and "Q1" |
| Release | `evaluate.py` entity preservation % metric |

## Harness Delta

None expected.

## Evidence

- Bedrock boundary implementation: `app/infrastructure/claude_client.py`
- Deterministic request/response and error tests: `tests/test_claude_client.py`
- Pending: credentialed Bedrock entity-preservation and end-to-end validation.
