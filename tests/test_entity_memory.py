from app.domain.entities import EntityMemory


def test_entity_memory_extracts_amount_dates_and_glossary_terms():
    memory = EntityMemory()
    memory.update("OnPoint GMV Q1 đạt 150 tỷ với CREA và Opollo.")

    entities = memory.as_dict()

    assert "OnPoint" in entities["org_names"]
    assert "GMV" in entities["org_names"]
    assert "Q1" in entities["dates"]
    assert "150 tỷ" in entities["amounts"]


def test_prompt_fragment_groups_session_entities():
    memory = EntityMemory()
    memory.update("Nguyen Van A nói doanh thu 12/2026 đạt 20 triệu.")

    prompt = memory.to_prompt_fragment()

    assert "20 triệu" in prompt
    assert "12/2026" in prompt
