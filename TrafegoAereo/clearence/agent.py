import asyncio
import random
from typing import Any, Literal

from google.adk.agents.context import Context
from google.adk.agents.llm_agent import Agent
from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel, Field


# ----------------------------------------------------------------------
# 1. Structured Output Schema
# ----------------------------------------------------------------------
class ClearanceOutput(BaseModel):
    Message: str = Field(
        description="Transmissão radiotelefônica do controlador ATC no padrão MCA 100-16."
    )


# ----------------------------------------------------------------------
# 2. Callback de Inicialização de Estado da Sessão
# ----------------------------------------------------------------------
async def initialize_flight_state(callback_context: Context) -> None:
    """Garante que a máquina de estados inicie em 'request_flight_plan'."""
    if "flight_phase" not in callback_context.state:
        callback_context.state["flight_phase"] = "request_flight_plan"
        callback_context.state["callsign"] = None
        callback_context.state["origin"] = None
        callback_context.state["flight_level"] = None
        callback_context.state["atis_info"] = None
        callback_context.state["ready_for_copy_prompt"] = False


# ----------------------------------------------------------------------
# 3. Ferramentas de Transição do Graph / State Machine
# ----------------------------------------------------------------------
def validate_flight_plan_request(
    callsign: str,
    origin: str,
    flight_level: str,
    atis_info: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Valida se os dados obrigatórios do plano de voo foram informados.

    Fase: request_flight_plan -> awaiting_copy

    Args:
        callsign: Indicativo de chamada da aeronave (ex: GOL 1234, TAM 3456).
        origin: Aeródromo de origem, pátio ou posição informado pelo piloto.
        flight_level: Nível de voo pretendido (ex: FL350, FL100).
        atis_info: Letra ou código da informação ATIS ciente (ex: Bravo, Charlie).
    """
    faltantes = []
    if not origin or origin.strip().lower() in ("desconhecido", "none", "", "null"):
        faltantes.append("origem/pátio")
    if not flight_level or flight_level.strip().lower() in ("desconhecido", "none", "", "null"):
        faltantes.append("nível de voo")
    if not atis_info or atis_info.strip().lower() in ("desconhecido", "none", "", "null"):
        faltantes.append("confirmação da informação ATIS atual")

    if faltantes:
        tool_context.state["flight_phase"] = "request_flight_plan"
        return {
            "status": "pending_data",
            "flight_phase": "request_flight_plan",
            "missing_fields": faltantes,
            "instruction": (
                f"Faltam dados obrigatórios: {', '.join(faltantes)}. "
                f"Solicite ao piloto apenas essas informações faltantes."
            ),
        }

    # Todos os requisitos preenchidos
    tool_context.state["callsign"] = callsign
    tool_context.state["origin"] = origin
    tool_context.state["flight_level"] = flight_level
    tool_context.state["atis_info"] = atis_info
    tool_context.state["flight_phase"] = "awaiting_copy"

    return {
        "status": "data_complete",
        "flight_phase": "awaiting_copy",
        "instruction": (
            f"Dados validados com sucesso para {callsign}. "
            f"Acione imediatamente a ferramenta wait_and_prepare_copy."
        ),
    }


async def wait_and_prepare_copy(tool_context: ToolContext) -> dict[str, Any]:
    """Executa a espera operacional de 10 a 15 segundos simulando o processamento do ATC.

    Fase: awaiting_copy
    """
    wait_time = random.uniform(10, 15)
    await asyncio.sleep(wait_time)

    callsign = tool_context.state.get("callsign", "Aeronave")
    tool_context.state["ready_for_copy_prompt"] = True

    return {
        "status": "ready_for_copy",
        "waited_seconds": round(wait_time, 1),
        "flight_phase": "awaiting_copy",
        "instruction": (
            f"Coordenação ATC concluída após {round(wait_time, 1)}s. "
            f"Pergunte imediatamente ao piloto: '{callsign}, pronto para cópia?'"
        ),
    }


def review_flight_plan(
    decision: Literal["approved", "refused"],
    reason: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Revisa o plano de voo e define se ele é aprovado ou recusado.

    Fase: Transiciona para 'flight_plan_approved' ou 'flight_plan_refused'.

    Args:
        decision: 'approved' se o plano está regular, ou 'refused' se há divergências.
        reason: Justificativa da decisão (se recusado, motivo da recusa; se aprovado, rota/nível/transponder).
    """
    callsign = tool_context.state.get("callsign", "Aeronave")

    if decision == "approved":
        tool_context.state["flight_phase"] = "flight_plan_approved"
        return {
            "status": "flight_plan_approved",
            "flight_phase": "flight_plan_approved",
            "instruction": (
                f"Plano aprovado. Emita a autorização ATC completa no padrão MCA 100-16 "
                f"para {callsign}: limite da autorização, rota, nível autorizado, "
                f"procedimento de saída (SID), código transponder e solicite cotejamento."
            ),
        }
    else:
        tool_context.state["flight_phase"] = "flight_plan_refused"
        return {
            "status": "flight_plan_refused",
            "flight_phase": "flight_plan_refused",
            "reason": reason,
            "instruction": (
                f"Plano recusado. Informe o piloto: '{callsign}, plano de voo recusado, "
                f"impossível [MOTIVO].' e solicite correção ou revisão."
            ),
        }


# ----------------------------------------------------------------------
# 4. Agente Principal (root_agent)
# ----------------------------------------------------------------------
root_agent = Agent(
    model="gemini-3.8-flash",
    name="clearance_delivery_agent",
    description=(
        "Simulador educacional da posição Autorização de Tráfego (Clearance Delivery) "
        "com arquitetura em grafo de estados (flight_phase) e fraseologia MCA 100-16/2025."
    ),
    instruction="""
# IDENTIDADE E PAPEL

Você é um controlador de tráfego aéreo virtual responsável pela posição de Autorização de Tráfego (Clearance Delivery) de um aeródromo brasileiro, utilizando a fraseologia do MCA 100-16/2025 do DECEA.
Você atua estritamente em uma SIMULAÇÃO EDUCACIONAL.

# MÁQUINA DE ESTADOS / GRAPH AGENT

Você é estritamente orientado pelo estado atual da sessão: **flight_phase = {flight_phase}**.

As 4 fases operacionais são:

### 1. FASE: request_flight_plan
- **Objetivo**: Garantir que o piloto forneceu todos os 3 requisitos obrigatórios:
  1. Origem (ou posição/pátio no aeródromo)
  2. Nível de voo solicitado (FL)
  3. Confirmação da informação ATIS atual (ex: 'informação Bravo')
- **Ação**:
  - Quando o piloto solicitar autorização ou plano de voo, chame SEMPRE a ferramenta `validate_flight_plan_request`.
  - Se faltar qualquer um dos 3 dados, solicite apenas as informações ausentes.
  - Se todos os dados forem validados, a ferramenta transiciona para `awaiting_copy`. Chame a ferramenta `wait_and_prepare_copy` para realizar a espera operacional (10 a 15s) e pergunte imediatamente ao piloto: "[INDICATIVO], pronto para cópia?".

### 2. FASE: awaiting_copy
- **Objetivo**: Aguardar a confirmação de que o piloto está pronto para cópia para avançar à revisão e emissão.
- **Ação**:
  - Quando o piloto responder que está pronto para cópia ("pronto", "pronto cópia", etc.), transicione para a fase de revisão e emissão da autorização (`review_flight_plan`).

### 3. FASE: flight_plan_approved OU flight_plan_refused
- **Objetivo**: Revisar o plano e emitir a autorização ou a recusa.
- **Ação**:
  - Chame a ferramenta `review_flight_plan` com `decision='approved'` ou `decision='refused'`.
  - Se `flight_plan_approved`: emita a autorização completa conforme o MCA 100-16 (indicativo, limite, rota autorizada, nível autorizado, saída SID, transponder) e termine solicitando o cotejamento.
  - Se `flight_plan_refused`: transmita a recusa justificada e instrua o piloto a rever o plano.

# REGRAS DE FRASEOLOGIA (MCA 100-16/2025)

1. Seja breve, técnico, claro e formal.
2. Nunca use termos informais ("OK", "beleza", "bom dia").
3. Nunca invente dados que não foram passados ou gerados pelas ferramentas.
4. Produza exclusivamente a fala do controlador de tráfego aéreo no campo `Message`.
""",
    tools=[
        validate_flight_plan_request,
        wait_and_prepare_copy,
        review_flight_plan,
    ],
    output_schema=ClearanceOutput,
    before_agent_callback=initialize_flight_state,
)
