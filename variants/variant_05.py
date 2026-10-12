import re
from decimal import Decimal

PREFIX = {
    "продуктивність": "PERF",
    "доступність": "AVAIL",
    "безпека": "SEC",
    "надійність": "REL",
    "супровідність": "MAINT",
    "гнучкість": "FLEX",
    "сумісність": "COMP",
    "зручність": "USAB",
}


def _clean_text(text: str) -> str:
    """Видаляє крайні пробіли та стискає послідовності пробілів до одного."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text).strip())


def make_scenario(spec: dict, existing_ids: list[str] | None = None) -> dict:
    attribute = spec.get("attribute", "")
    if attribute not in PREFIX:
        raise ValueError(f"Невідомий атрибут: {attribute}")

    prefix = PREFIX[attribute]

    # Розрахунок id
    max_num = 0
    if existing_ids:
        pattern = re.compile(rf"^Q-{re.escape(prefix)}-(\d+)$")
        for eid in existing_ids:
            match = pattern.match(str(eid).strip())
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num

    scenario_id = f"Q-{prefix}-{(max_num + 1):02d}"

    # Очищення текстових полів
    cleaned_source = _clean_text(spec.get("source", ""))
    cleaned_stimulus = _clean_text(spec.get("stimulus", ""))
    cleaned_env = _clean_text(spec.get("environment", ""))
    cleaned_artifact = _clean_text(spec.get("artifact", ""))
    cleaned_response = _clean_text(spec.get("response", ""))

    # Формування міри (measure)
    target = spec.get("target", {})
    metric = _clean_text(target.get("metric", ""))
    raw_val = target.get("value")
    unit = _clean_text(target.get("unit", ""))
    bound = target.get("bound", "max")

    val_dec = Decimal(str(raw_val))

    # Переведення секунд у мілісекунди
    if unit in ("с", "секунд", "секунди", "секунда"):
        val_dec = val_dec * Decimal("1000")
        unit = "мс"

    # Форматування десяткового дробу без експоненційного запису та зайвих нулів
    # :f виводить фіксовану крапку (без 8E+2)
    val_str = f"{val_dec:f}"
    if "." in val_str:
        val_str = val_str.rstrip("0").rstrip(".")
    val_str = val_str.replace(".", ",")

    sign = "≤" if bound == "max" else "≥"

    if metric:
        measure = f"{metric} {sign} {val_str} {unit}"
    else:
        measure = f"{sign} {val_str} {unit}"

    return {
        "id": scenario_id,
        "attribute": attribute,
        "source": cleaned_source,
        "stimulus": cleaned_stimulus,
        "environment": cleaned_env,
        "artifact": cleaned_artifact,
        "response": cleaned_response,
        "measure": measure,
    }


def render_markdown(scenario: dict) -> str:
    lines = [
        f"### {scenario['id']}. {scenario['attribute']}",
        f"- Джерело: {scenario.get('source', '')}",
        f"- Стимул: {scenario.get('stimulus', '')}",
        f"- Середовище: {scenario.get('environment', '')}",
        f"- Артефакт: {scenario.get('artifact', '')}",
        f"- Відповідь: {scenario.get('response', '')}",
        f"- Міра: {scenario.get('measure', '')}",
    ]
    return "\n".join(lines)