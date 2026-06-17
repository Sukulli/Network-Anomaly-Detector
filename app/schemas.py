from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dur: float = Field(..., ge=0)
    proto: str
    service: str
    state: str
    spkts: int = Field(..., ge=0)
    dpkts: int = Field(..., ge=0)
    sbytes: int = Field(..., ge=0)
    dbytes: int = Field(..., ge=0)
    rate: float = Field(..., ge=0)
    sttl: int = Field(..., ge=0)
    dttl: int = Field(..., ge=0)
    sload: float = Field(..., ge=0)
    dload: float = Field(..., ge=0)
    sloss: int = Field(..., ge=0)
    dloss: int = Field(..., ge=0)
    sinpkt: float = Field(..., ge=0)
    dinpkt: float = Field(..., ge=0)
    sjit: float = Field(..., ge=0)
    djit: float = Field(..., ge=0)
    swin: int = Field(..., ge=0)
    stcpb: int = Field(..., ge=0)
    dtcpb: int = Field(..., ge=0)
    dwin: int = Field(..., ge=0)
    tcprtt: float = Field(..., ge=0)
    synack: float = Field(..., ge=0)
    ackdat: float = Field(..., ge=0)
    smean: int = Field(..., ge=0)
    dmean: int = Field(..., ge=0)
    trans_depth: int = Field(..., ge=0)
    response_body_len: int = Field(..., ge=0)
    ct_srv_src: int = Field(..., ge=0)
    ct_state_ttl: int = Field(..., ge=0)
    ct_dst_ltm: int = Field(..., ge=0)
    ct_src_dport_ltm: int = Field(..., ge=0)
    ct_dst_sport_ltm: int = Field(..., ge=0)
    ct_dst_src_ltm: int = Field(..., ge=0)
    is_ftp_login: int = Field(..., ge=0)
    ct_ftp_cmd: int = Field(..., ge=0)
    ct_flw_http_mthd: int = Field(..., ge=0)
    ct_src_ltm: int = Field(..., ge=0)
    ct_srv_dst: int = Field(..., ge=0)
    is_sm_ips_ports: int = Field(..., ge=0)


class PredictionResponse(BaseModel):
    prediction: int
    prediction_label: str
    attack_probability: float
    threshold: float
    model_name: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str | None = None
    generated_at: str | None = None
    threshold: float | None = None
