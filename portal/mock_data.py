"""Mock data for TDoc documents and chat sessions."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
MD_DIR = PROJECT_ROOT / "artifacts" / "output" / "markdown"
HTML_DIR = PROJECT_ROOT / "artifacts" / "output" / "html"


@dataclass
class TDoc:
    id: str
    title: str
    source_file: str
    file_type: str
    meeting: str
    agenda_item: str
    mock_content: str = ""
    available: bool = False
    html_path: str = ""
    md_path: str = ""

    def __post_init__(self) -> None:
        if not self.html_path:
            self.html_path = str(HTML_DIR / f"{self.id}_{self.source_file}.html")
        if not self.md_path:
            self.md_path = str(MD_DIR / f"{self.id}_{self.source_file}.md")
        if not self.available:
            self.available = Path(self.md_path).exists()


@dataclass
class ChatSession:
    session_id: str
    doc_ids: list[str]
    created_at: datetime
    last_updated: datetime
    title: str
    preview: str
    messages: list[dict] = field(default_factory=list)


_MOCK_CONTENT_BEAMFORMING = """
R1-2501001: Uplink Beam Management Enhancement Proposal

This contribution proposes enhancements to uplink beam management procedures
for NR in Release 18. The key proposal is to introduce a UE-initiated beam
failure recovery mechanism for the uplink, complementing the existing downlink
beam failure recovery defined in 3GPP TS 38.213.

Section 3.1 - Problem Statement:
Current NR specifications define beam failure recovery (BFR) only for the
downlink direction. In mmWave deployments operating above 24 GHz, uplink
beam quality can degrade independently from downlink due to asymmetric
blockage conditions and device orientation. Measurements collected from
field trials indicate that 23% of uplink failures occur without a
corresponding downlink beam failure event.

Section 3.2 - Proposed Solution:
The UE monitors a set of reference signals (RS) configured by the gNB for
uplink beam quality assessment. When the measured uplink beam quality falls
below threshold Q_UL_fail for duration T_UL_fail, the UE initiates an
uplink BFR procedure by transmitting a BFR-PUCCH on a pre-configured
resource. The gNB responds with a new uplink spatial filter configuration.

Section 3.3 - Simulation Results:
System-level simulations using 3D-UMa channel model (IMT-2020 parameters)
show a 31% reduction in uplink outage probability at cell edge when UL-BFR
is enabled compared to the baseline without UL-BFR.
"""

_MOCK_CONTENT_MIMO = """
R1-2502034: Multi-Panel MIMO Codebook Design for FR2-2

This document proposes a codebook structure for multi-panel antenna
configurations operating in the FR2-2 frequency range (52.6 - 71 GHz).

Section 2 - Background:
3GPP Release 17 introduced multi-panel codebooks for FR1 and FR2-1.
Extension to FR2-2 requires consideration of the higher path loss,
larger antenna arrays (typically 256 elements or more), and the increased
sensitivity to inter-panel phase coherence errors at higher frequencies.

Section 3 - Codebook Structure:
The proposed codebook adopts a two-stage structure:
- Stage 1 (wideband): Selects a subset of 4 DFT beams per panel
- Stage 2 (subband): Selects beam combining coefficients and inter-panel
  phase adjustment values from a 4-bit quantized set

The phase adjustment codebook uses a non-uniform quantization scheme
optimized for the expected phase error distribution at 60 GHz, which
follows a wrapped Gaussian distribution with sigma = 12 degrees.

Section 4 - Link-Level Performance:
Link-level simulations demonstrate 2.4 dB SNR gain over Release 17
single-panel codebook at 64-element per panel configuration under
CDL-A channel model with 4 GHz bandwidth.
"""

_MOCK_CONTENT_SCHEDULING = """
R1-2503218: Enhanced HARQ-ACK Feedback for XR Traffic

This contribution addresses HARQ-ACK feedback overhead reduction for
Extended Reality (XR) traffic profiles, targeting the video streaming
use case with frame rates of 60-120 fps.

Section 1 - Motivation:
XR downlink traffic is characterized by periodic high-throughput bursts
aligned to video frame boundaries, interspersed with periods of low
activity. Existing HARQ-ACK mechanisms configured for peak throughput
result in excessive feedback overhead during low-activity periods,
consuming uplink resources that could be used more efficiently.

Section 2 - Proposed Mechanism:
A gNB-controlled HARQ-ACK bundling scheme is proposed where the bundling
window W_ack is dynamically adjusted based on the detected XR traffic
pattern. During inter-frame gaps, W_ack is extended to bundle ACKs for
up to 8 consecutive PDSCH transmissions into a single PUCCH occasion.

Section 3 - Standardization Impact:
The proposal requires additions to TS 38.212 (PUCCH format selection),
TS 38.213 (HARQ-ACK timing), and TS 38.331 (RRC configuration of
dynamic bundling parameters). No changes to the physical layer structure
are required.
"""

_MOCK_CONTENT_COVERAGE = """
R1-2504455: Coverage Enhancement for NR RedCap Devices

This contribution proposes coverage enhancement techniques specifically
tailored for NR Reduced Capability (RedCap) devices operating in
sub-6 GHz bands with limited antenna configurations (1 or 2 Rx antennas).

Section 2 - Coverage Challenge Analysis:
RedCap devices are designed for IoT and wearable use cases where form
factor constraints limit antenna gain by 3-6 dB compared to conventional
UE categories. Combined with reduced maximum transmit power (23 dBm vs
26 dBm), the uplink coverage budget for RedCap in rural macro deployments
falls 7-9 dB short of Release 15 NR baseline.

Section 3 - Repetition-Based Enhancement:
The proposal introduces configurable PUSCH repetition with up to 32
repetitions, combined with frequency hopping across the entire system
bandwidth to achieve frequency diversity. A new DMRS bundling scheme
allows the gNB to coherently combine DMRS across repetitions for
improved channel estimation at low SNR.

Section 4 - Evaluation Results:
Coverage simulations using 3GPP Rural Macro channel model show that
the proposed scheme achieves the target 164 dB maximum coupling loss
with a 95th percentile SINR margin of 2.1 dB, meeting the IoT coverage
requirement with a system bandwidth of 20 MHz.
"""

_MOCK_CONTENT_SIDELINK = """
R1-2505677: NR Sidelink Resource Management for V2X Congestion Control

This contribution addresses sidelink channel congestion in dense V2X
deployment scenarios and proposes an enhanced channel busy ratio (CBR)
measurement and resource reservation framework.

Section 3 - Enhanced CBR Measurement:
The existing CBR measurement defined in TS 38.214 uses a fixed sensing
window of 100 ms. This contribution proposes an adaptive sensing window
of 50-200 ms that adjusts based on vehicle speed and message rate, as
the optimal window length for accurate CBR estimation varies significantly
across different mobility scenarios.

Section 4 - Resource Reservation Enhancement:
A new partial sensing scheme is proposed for Mode 2 sidelink operation
where the UE probabilistically selects from the candidate resource set
based on the instantaneous CBR. When CBR exceeds 65%, the reservation
reselection counter is reduced by half to accelerate resource release
and reduce persistent interference.

Section 5 - Field Trial Validation:
Measurements from a 12-vehicle convoy test on a controlled highway
segment demonstrate a 28% reduction in packet error rate at vehicle
densities above 80 vehicles/km compared to the Release 16 baseline.
"""

_MOCK_SESSIONS_DATA = [
    {
        "title": "Uplink beam failure recovery",
        "preview": "What is the proposed threshold for uplink beam failure detection?",
        "doc_ids": ["R1-2501001"],
        "days_ago": 2,
        "messages": [
            {"role": "user", "content": "What is the proposed threshold for uplink beam failure detection?"},
            {"role": "assistant", "content": "According to R1-2501001, the UE monitors uplink beam quality and initiates recovery when the measured quality falls below threshold **Q_UL_fail** for duration **T_UL_fail**. The specific values of these thresholds are configurable by the gNB. The document reports that enabling UL-BFR reduces uplink outage probability at cell edge by 31% in system-level simulations using the 3D-UMa channel model."},
        ],
    },
    {
        "title": "FR2-2 codebook inter-panel phase",
        "preview": "How does the FR2-2 codebook handle inter-panel phase errors?",
        "doc_ids": ["R1-2502034"],
        "days_ago": 5,
        "messages": [
            {"role": "user", "content": "How does the FR2-2 codebook handle inter-panel phase errors?"},
            {"role": "assistant", "content": "R1-2502034 addresses inter-panel phase coherence errors through a 4-bit quantized phase adjustment codebook in Stage 2 of the two-stage codebook structure. The non-uniform quantization is specifically optimized for the expected phase error distribution at 60 GHz, which follows a wrapped Gaussian distribution with sigma = 12 degrees. This approach achieves a 2.4 dB SNR gain over the Release 17 single-panel codebook in link-level simulations."},
        ],
    },
    {
        "title": "RedCap coverage budget analysis",
        "preview": "What is the coverage deficit for RedCap devices vs baseline NR?",
        "doc_ids": ["R1-2504455"],
        "days_ago": 8,
        "messages": [
            {"role": "user", "content": "What is the coverage deficit for RedCap devices vs baseline NR?"},
            {"role": "assistant", "content": "According to R1-2504455, RedCap devices face a 7-9 dB uplink coverage deficit compared to Release 15 NR baseline in rural macro deployments. This is caused by two factors: form factor constraints limiting antenna gain by 3-6 dB, and reduced maximum transmit power (23 dBm vs 26 dBm for standard UE). The proposed repetition-based enhancement with up to 32 PUSCH repetitions and frequency hopping recovers this deficit, achieving the target 164 dB maximum coupling loss with a 2.1 dB SINR margin."},
        ],
    },
]


def get_mock_documents() -> list[TDoc]:
    """Return a list of mock TDoc records."""
    return [
        TDoc(
            id="R1-2501001",
            title="Uplink Beam Management Enhancement",
            source_file="ul_beam_management",
            file_type="docx",
            meeting="RAN1 #120",
            agenda_item="8.1.1",
            mock_content=_MOCK_CONTENT_BEAMFORMING,
        ),
        TDoc(
            id="R1-2502034",
            title="Multi-Panel MIMO Codebook for FR2-2",
            source_file="mimo_codebook_fr22",
            file_type="docx",
            meeting="RAN1 #120",
            agenda_item="8.2.3",
            mock_content=_MOCK_CONTENT_MIMO,
        ),
        TDoc(
            id="R1-2503218",
            title="Enhanced HARQ-ACK for XR Traffic",
            source_file="harq_xr_traffic",
            file_type="pptx",
            meeting="RAN1 #120",
            agenda_item="8.3.1",
            mock_content=_MOCK_CONTENT_SCHEDULING,
        ),
        TDoc(
            id="R1-2504455",
            title="Coverage Enhancement for NR RedCap",
            source_file="redcap_coverage",
            file_type="docx",
            meeting="RAN1 #120",
            agenda_item="8.4.2",
            mock_content=_MOCK_CONTENT_COVERAGE,
        ),
        TDoc(
            id="R1-2505677",
            title="Sidelink Resource Management for V2X",
            source_file="sidelink_v2x",
            file_type="docx",
            meeting="RAN1 #120",
            agenda_item="8.5.1",
            mock_content=_MOCK_CONTENT_SIDELINK,
        ),
        TDoc(
            id="R1-2506012",
            title="PDSCH Mapping Type C for Low Latency",
            source_file="pdsch_mapping_c",
            file_type="docx",
            meeting="RAN1 #119bis",
            agenda_item="7.1.2",
            mock_content="R1-2506012 proposes a new PDSCH mapping type C targeting sub-1ms user-plane latency for URLLC use cases. The proposal reduces mini-slot duration to 2 OFDM symbols and introduces a new DMRS configuration with front-loaded pilot placement to enable earlier decoding.",
        ),
        TDoc(
            id="R1-2507389",
            title="CSI Reporting Enhancement for High Mobility",
            source_file="csi_high_mobility",
            file_type="docx",
            meeting="RAN1 #119bis",
            agenda_item="7.2.1",
            mock_content="R1-2507389 addresses CSI measurement and reporting accuracy under high Doppler conditions (v > 120 km/h). A Doppler-domain CSI feedback scheme is proposed where the UE reports beam Doppler shift estimates alongside beam amplitude and phase, enabling the gNB to predict beam evolution across scheduling intervals.",
        ),
        TDoc(
            id="R1-2508145",
            title="NR Positioning Accuracy Enhancement",
            source_file="positioning_accuracy",
            file_type="docx",
            meeting="RAN1 #119bis",
            agenda_item="7.3.4",
            mock_content="R1-2508145 proposes enhancements to NR positioning accuracy using a hybrid TDOA/AoA measurement scheme. The document presents simulation results showing sub-meter accuracy for 90% of UEs in dense urban deployments when combining DL-TDOA measurements from 6+ TRPs with AoA estimates from a UE with 4-element antenna array.",
        ),
        TDoc(
            id="R1-2509201",
            title="Power Saving for Massive MIMO",
            source_file="power_saving_mmimo",
            file_type="pptx",
            meeting="RAN1 #119",
            agenda_item="6.1.3",
            mock_content="R1-2509201 proposes dynamic TRP panel shutdown based on spatial traffic distribution. Using beam-domain traffic prediction, inactive antenna panels are powered down during low-load periods, achieving 38% base station power reduction with less than 0.5 dB average throughput degradation.",
        ),
        TDoc(
            id="R1-2510334",
            title="UE Complexity Reduction for Rel-18 Features",
            source_file="ue_complexity_redcap2",
            file_type="docx",
            meeting="RAN1 #119",
            agenda_item="6.2.1",
            mock_content="R1-2510334 analyzes UE implementation complexity for Rel-18 features including enhanced beam management, multi-panel codebooks, and AI/ML-based CSI feedback. The document proposes a feature capability signaling framework allowing network to configure only features within UE's complexity budget.",
        ),
        TDoc(
            id="R1-2511422",
            title="AI/ML for Beam Prediction",
            source_file="aiml_beam_prediction",
            file_type="docx",
            meeting="RAN1 #119",
            agenda_item="6.3.2",
            mock_content="R1-2511422 evaluates AI/ML model architectures for downlink beam prediction. An LSTM-based model trained on historical beam measurement sequences achieves 87% top-1 beam prediction accuracy at 500ms prediction horizon, reducing beam management overhead by 45% in mobility scenarios.",
        ),
        TDoc(
            id="R1-2512567",
            title="TDD UL/DL Configuration Flexibility",
            source_file="tdd_config_flex",
            file_type="xlsx",
            meeting="RAN1 #118",
            agenda_item="5.1.1",
            mock_content="R1-2512567 proposes semi-static TDD pattern reconfiguration with 20ms granularity for adapting to traffic asymmetry. The proposal introduces a new RRC parameter set for defining up to 4 pre-configured TDD patterns that can be switched via MAC-CE, enabling rapid response to DL/UL traffic ratio changes.",
        ),
        TDoc(
            id="R1-2513701",
            title="PDCCH Monitoring Adaptation",
            source_file="pdcch_monitoring",
            file_type="docx",
            meeting="RAN1 #118",
            agenda_item="5.2.3",
            mock_content="R1-2513701 proposes cross-slot PDCCH monitoring relaxation for power-saving. When the network detects UE is in a dormant state (no pending DL data), PDCCH monitoring occasions are reduced from every slot to every 4 slots, saving approximately 22% UE wake-up power with negligible impact on scheduling latency.",
        ),
        TDoc(
            id="R1-2514890",
            title="FR1 Massive MIMO Feedback Compression",
            source_file="fr1_massive_mimo_fb",
            file_type="docx",
            meeting="RAN1 #118",
            agenda_item="5.3.1",
            mock_content="R1-2514890 presents a neural network-based CSI feedback compression scheme for 64-port massive MIMO in FR1. The autoencoder architecture reduces CSI feedback overhead by 8x compared to Type II CSI with less than 0.3 dB beamforming gain loss at 95th percentile.",
        ),
        TDoc(
            id="R1-2515999",
            title="IAB Backhaul Link Optimization",
            source_file="iab_backhaul",
            file_type="docx",
            meeting="RAN1 #118",
            agenda_item="5.4.2",
            mock_content="R1-2515999 addresses integrated access and backhaul (IAB) topology management for multi-hop deployments. A distributed path selection algorithm is proposed where IAB nodes collaboratively optimize backhaul routing based on local link quality measurements and congestion indicators, achieving 19% throughput improvement over static routing.",
        ),
    ]


def get_mock_sessions() -> list[ChatSession]:
    """Return a list of pre-seeded mock chat sessions."""
    now = datetime.now()
    sessions = []
    for i, data in enumerate(_MOCK_SESSIONS_DATA):
        created = now - timedelta(days=data["days_ago"])
        sessions.append(
            ChatSession(
                session_id=str(uuid.uuid4()),
                doc_ids=data["doc_ids"],
                created_at=created,
                last_updated=created + timedelta(minutes=5),
                title=data["title"],
                preview=data["preview"],
                messages=data["messages"],
            )
        )
    return sessions
