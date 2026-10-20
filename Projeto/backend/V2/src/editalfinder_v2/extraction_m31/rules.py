"""Portuguese contextual baseline; literal witnesses, explicitly uncertain roles."""

import re
from datetime import date

from .models import Discovery, ExtractedField, Modality, Segment, Temporal, Witness
from .reader import InputDocument
from .structure import Unit

DATE = r"[0-9]{2}/[0-9]{2}/[0-9]{4}"
MONEY = re.compile(
    r"R\$\s*[0-9]+(?:[.,][0-9]+)*(?:\s*(?:bilhões|bilhão|milhões|milhão|mil|mi|bi)\b)?", re.I
)


def classify(text: str) -> tuple[Discovery, Modality, tuple[str, ...]]:
    """Conjunctions of local instrument, role and access language, never scores."""
    t = text.casefold()
    credit = bool(re.search(r"crédito|empréstimo|financiamento|reembolsável", t))
    grant = bool(re.search(r"bolsas?|subvenção|não reembolsáve|apoio.*pesquisa|chamada.*cnpq", t))
    equity = bool(
        re.search(
            r"venture capital|fip\b|fundo.*investimento|investimentos.*startups|"
            r"startups.*investimento|fundo.{0,100}sócio",
            t,
        )
    )
    # Explicit non-repayable is not a loan merely because of the substring.
    if "não reembols" in t and not re.search(r"empréstimo|linha de crédito", t):
        credit = False
    modes: list[Modality] = []
    for yes, mode in [(credit, "credito"), (grant, "fomento"), (equity, "investimentos")]:
        if yes:
            modes.append(mode)  # type: ignore[arg-type]
    modality: Modality = modes[0] if len(modes) == 1 else "undetermined"
    diagnostics = ("mixed_or_missing_financial_modality",) if len(modes) != 1 else ()
    instrument = bool(modes) or bool(re.search(r"chamada|programa.*inovação", t))
    completed = bool(
        re.search(
            r"já (?:analisad|investid|selecionad)|projetos (?:aprovados|contemplados)|"
            r"celebra[mr].*financiamento|financiamento foi celebrado|"
            r"aprova.*(?:para (?:a empresa|o instituto)|à empresa)|"
            r"resultado.*prêmio|portfólio|portfolio",
            t,
        )
    )
    manager = bool(re.search(r"gestor[ae]?s?|gestão.*fundo", t)) and bool(
        re.search(r"selecion|chamada pública|propostas|critérios", t)
    )
    future_access = bool(
        re.search(
            r"(?:abrirá|abrirão|serão abertas|será aberta).{0,70}(?:inscriç|submiss|candidatur)|"
            r"(?:inscriç|candidatur).{0,60}(?:abrirão|serão abertas)",
            t,
        )
    )
    access = bool(
        re.search(
            r"inscrições\s*:|recebe\s+propostas|submissão (?:de|das) propostas|"
            r"inscrições abertas|inscriç[ãõ].{0,25}startup|"
            r"(?:podem|poderão) solicitar|como solicitar|solicite.{0,25}crédito|"
            r"preencha o formulário de submissão|"
            r"envie.{0,25}(?:proposta|startup)|aplique.{0,20}startup",
            t,
        )
    )
    if completed and not access:
        return (
            "unrelated_or_non_actionable",
            modality,
            diagnostics + ("completed_event_not_new_access",),
        )
    if manager:
        return "opportunity_signal", modality, diagnostics + ("manager_stage_not_startup_access",)
    if future_access and instrument:
        return (
            "announced_future_opportunity",
            modality,
            diagnostics + ("future_access_not_current_open",),
        )
    if access and instrument and modality != "undetermined":
        return (
            "confirmed_opportunity",
            modality,
            diagnostics + ("access_heuristic_not_review_authority",),
        )
    if instrument:
        return "opportunity_signal", modality, diagnostics + ("application_access_not_established",)
    return "abstain", modality, diagnostics + ("insufficient_context",)


def predict(
    document: InputDocument, unit: Unit, run_id: str, index: int, reference_date: str
) -> Segment:
    sid = f"segment-{index:04d}"  # local extraction position, never canonical identity
    parts = [document.text[b.start : b.end] for b in unit.blocks]
    local = "\n".join(parts)
    discovery, modality, notes = classify(local)
    witnesses: list[Witness] = []
    fields: list[ExtractedField] = []

    def witness(start: int, end: int, page: int | None) -> Witness:
        p = document.provenance
        return Witness(
            run_id=run_id,
            document_id=p.document_id,
            raw_sha256=p.raw_sha256,
            text_sha256=p.text_sha256,
            segment_id=sid,
            start=start,
            end=end,
            page=page,
            quote=document.text[start:end],
        )

    def add(name: str, original: str, w: Witness) -> None:
        fields.append(ExtractedField(name=name, original=original, witness=w))

    openings: list[date] = []
    deadlines: list[date] = []
    ref = date.fromisoformat(reference_date)
    for block_index, block in enumerate(unit.blocks):
        value = document.text[block.start : block.end]
        low = value.casefold()
        # Whole blocks provide local role context. PDF blocks are page-contained.
        if len(value) > 20000:
            continue
        w = witness(block.start, block.end, block.page)
        if discovery != "abstain":
            witnesses.append(w)
        if block.heading and re.search(r"chamada|finame|programa|fundo|crédito", low):
            add("title", value, w)
        for match in MONEY.finditer(value):
            prefix = low[max(0, match.start() - 100) : match.start()]
            context = low[max(0, match.start() - 120) : min(len(low), match.end() + 120)]
            role = "monetary_expression_unresolved"
            if re.search(r"faturamento|receita anual", context):
                role = "borrower_revenue_requirement"
            elif re.search(r"fundo|fip\b", context) and re.search(
                r"capta|mobiliza|estimativa|capital", context
            ):
                role = "fund_capital_estimate"
            elif re.search(r"por (?:proposta|projeto)|cada (?:proposta|projeto)", context):
                role = "proposal_amount_expression"
            elif re.search(r"orçamento|volume (?:total|inicial)|recursos.{0,25}programa", context):
                role = "program_budget"
            elif modality == "credito" and re.search(
                r"financiamento de até|crédito de até|limite de crédito", prefix
            ):
                role = "credit_limit"
            elif re.search(r"financiamento|aprovou|aprova|celebra", context):
                role = "financing_amount_expression"
            add(role, match.group(), w)
        # Preserve date roles independently, never choose among conflicting values.
        interval = re.search(r"inscrições\s*:\s*(" + DATE + r")\s+a\s+(" + DATE + r")", value, re.I)
        if interval is None and block_index:
            previous = unit.blocks[block_index - 1]
            label = document.text[previous.start : previous.end]
            if re.fullmatch(r"Inscrições\s*:", label, re.I):
                interval = re.fullmatch(r"(" + DATE + r")\s+a\s+(" + DATE + r")", value.strip())
        if interval:
            add("opening_date", interval[1], w)
            add("submission_deadline", interval[2], w)
            try:
                openings.append(date(*map(int, interval[1].split("/")[::-1])))
                deadlines.append(date(*map(int, interval[2].split("/")[::-1])))
            except ValueError:
                notes += ("unparseable_application_date",)
        for match in re.finditer(DATE, value):
            if interval and interval.start() <= match.start() < interval.end():
                continue
            prefix = low[max(0, match.start() - 100) : match.start()]
            role = "unknown_temporal_expression"
            if re.search(r"publicad[oa] em\s*$", prefix):
                role = "publication_date_expression"
            elif re.search(r"resultado|julgamento", prefix):
                role = "selection_result_date_expression"
            elif re.search(r"errata|retifica|anexo.*atualiz", prefix):
                role = "rectification_date_expression"
            elif re.search(
                r"limite para submissão|prazo.*(?:proposta|inscriç)|submissão de propostas até",
                prefix,
            ):
                role = "submission_deadline"
                try:
                    deadlines.append(date(*map(int, match.group().split("/")[::-1])))
                except ValueError:
                    notes += ("unparseable_application_date",)
            add(role, match.group(), w)
        role_patterns = {
            "applicant_requirements": (
                r"quem pode solicitar|(?:destinad[oa]|voltad[oa]).{0,45}(?:empresas|"
                r"pesquisadores|instituições)|(?:podem|poderão) (?:participar|"
                r"solicitar)|possuir o título"
            ),
            "geographic_eligibility": (
                r"(?:empresas|proponentes|instituições).{0,35}(?:sediad[oa]s?|"
                r"localizad[oa]s?).{0,60}"
            ),
            "managing_organization_expression": (
                r"(?:como gestora|gestão do fundo|selecionaram.{0,60}gestora)"
            ),
            "funding_organization_expression": (
                r"(?:realizada pelo|recursos (?:do|da)|financiado pel[oa])"
            ),
            "publishing_organization_expression": r"(?:cnpq|finep|bndes).{0,20}torna pública",
            "beneficiary_expression": r"(?:beneficiar|beneficiadas|contemplad[oa]s|concedido à)",
            "execution_location_expression": r"(?:execução|realização) (?:no|na|em)\b",
            "application_instructions": (
                r"(?:envie|solicite|inscreva|aplique).{0,35}(?:proposta|startup|"
                r"crédito)|podem solicitar"
            ),
            "interest_expression": r"taxa de juros|juros de|selic|custo financeiro",
            "repayment_expression": r"amortização|carência|prazo de (?:pagamento|financiamento)",
            "investment_terms_unresolved": r"valuation|equity|participação acionária",
            "attachment_unavailable": r"anexo|retificação|\.pdf\b",
            "fund_stage_expression": r"estágio de captação|análise, diligência e estruturação",
            "future_event_expression": r"lançamento em|será lançado|iniciará operações",
        }
        for name, pattern in role_patterns.items():
            if re.search(pattern, low):
                add(name, value, w)
    temporal: Temporal = (
        "not_applicable" if discovery == "unrelated_or_non_actionable" else "undetermined"
    )
    if discovery == "confirmed_opportunity":
        if len(set(deadlines)) > 1 or len(set(openings)) > 1:
            notes += ("conflicting_application_dates_no_precedence",)
        elif deadlines and openings and openings[0] <= ref < deadlines[0]:
            temporal = "open"
        elif deadlines and deadlines[0] < ref:
            temporal = "closed"
        elif openings and ref < openings[0]:
            temporal = "future"
    if any(f.name in {"opening_date", "submission_deadline"} for f in fields):
        notes += ("application_stage_and_cutoff_timezone_unverified",)
    return Segment(
        segment_id=sid,
        start=unit.start,
        end=unit.end,
        discovery=discovery,
        modality=modality,
        temporal=temporal,
        fields=tuple(fields),
        witnesses=tuple(witnesses),
        diagnostics=(unit.method,) + notes,
    )
