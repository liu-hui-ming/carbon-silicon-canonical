# ERRATUM-004 静态复核用重建稿（复核人：qiongzhu 2026-10-22）
# 依据创立人送达文本去 markdown 污染后重建；仅用于 E20 可解析性验证
from enum import Enum

class GateDecision(Enum):
    PASS_WITHIN_DOMAIN = "PASS_WITHIN_DOMAIN"
    PASS_WITH_LIMITS = "PASS_WITH_LIMITS"
    PASS_WITH_LIMITS_FINAL = "PASS_WITH_LIMITS_FINAL"
    HOLD_FOR_EVIDENCE = "HOLD_FOR_EVIDENCE"
    REJECT_CLAIM = "REJECT_CLAIM"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    PIPELINE_VIOLATION = "PIPELINE_VIOLATION"

class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class RoutePath(Enum):
    E_EMPIRICAL = "E_EMPIRICAL"
    F_FORMAL = "F_FORMAL"
    N_NORMATIVE = "N_NORMATIVE"
    H_HYBRID = "H_HYBRID"

class Target:
    def __init__(self):
        self.name = None
        self.is_measurable_comparable = False

class ModelApprox:
    def __init__(self):
        self.approx_name = None
        self.matches_declared_domain = False

class NumericStat:
    def __init__(self):
        self.converged = False
        self.stat_reliability_passed = False

class IndependentTestSet:
    def __init__(self):
        self.test_name = None
        self.passed = False

class CrossScaleBridge:
    def __init__(self):
        self.evidence_name = None
        self.validated = False
        self.cross_scale_not_applicable_declared = False

class FinalClaim:
    def __init__(self):
        self.claim_text = None
        self.strictly_within_evidence = False

class NARecord:
    def __init__(self):
        self.gate_id = None
        self.approve_reason = None
        self.approver = None
        self.approver_role = None
        self.auth_snapshot_version = None

class Limitation:
    def __init__(self, gate_id, message, severity):
        self.gate_id = gate_id
        self.message = message
        self.severity = severity

class TrustedAuthSource:
    def __init__(self, auth_snapshot_version, approver_role_map):
        self.auth_snapshot_version = auth_snapshot_version
        self.approver_role_map = approver_role_map
    def get_role(self, approver):
        return self.approver_role_map.get(approver, None)

class AuditContext:
    def __init__(self):
        self.proposition = None
        self.target = Target()
        self.variables = []
        self.eval_function = None
        self.exclusions = []
        self.stakeholders = []
        self.auth_basis = None
        self.space_scale = None
        self.time_window = None
        self.system_boundary = None
        self.initial_state = None
        self.external_inputs = []
        self.proposition_nature = None
        self.route_path = None
        self.model_approx = ModelApprox()
        self.numeric_stability = NumericStat()
        self.independent_test_set = IndependentTestSet()
        self.cross_scale_bridge_evidence = CrossScaleBridge()
        self.final_claim_text = FinalClaim()
        self.gate_history = []
        self.limitations = []
        self.meta_rule_audit_answers = dict()
        self.rule_change_records = []
        self.split_empirical_and_normative_chain = False
        self.na_records = []
        self.pending_na_reason = None
        self.pending_na_approver = None
        self.trusted_auth_source = None

NA_WHITELIST = {"G5", "G7"}
NA_AUTH_ROLE_TABLE = {
    "G5": ["AUDITOR", "SENIOR_REVIEWER"],
    "G7": ["AUDITOR", "SENIOR_REVIEWER"],
}
G0_REQUIRED_KEYS = [
    "Q1_self_consistent", "Q2_auditable", "Q3_version_traceable",
    "Q4_evidence_bounded", "Q5_falsifiable", "Q6_domain_declared",
    "Q7_no_unsupported_extrapolation", "Q8_chain_separated",
]

def gate_G0_meta_rule_audit(ctx):
    for key in G0_REQUIRED_KEYS:
        if key not in ctx.meta_rule_audit_answers:
            ctx.gate_history.append(("G0", GateDecision.HOLD_FOR_EVIDENCE, "G0 missing: %s" % key))
            return GateDecision.HOLD_FOR_EVIDENCE
        val = ctx.meta_rule_audit_answers[key]
        if not isinstance(val, bool):
            ctx.gate_history.append(("G0", GateDecision.HOLD_FOR_EVIDENCE, "G0 type: %s" % key))
            return GateDecision.HOLD_FOR_EVIDENCE
        if val is False:
            ctx.gate_history.append(("G0", GateDecision.REJECT_CLAIM, "G0 fail: %s" % key))
            return GateDecision.REJECT_CLAIM
    ctx.gate_history.append(("G0", GateDecision.PASS_WITHIN_DOMAIN, "G0 pass"))
    return GateDecision.PASS_WITHIN_DOMAIN

def gate_G1_target_gate(ctx):
    if ctx.target.name is None:
        ctx.gate_history.append(("G1", GateDecision.HOLD_FOR_EVIDENCE, "target undefined"))
        return GateDecision.HOLD_FOR_EVIDENCE
    if not ctx.target.is_measurable_comparable:
        lim = Limitation("G1", "target not measurable", Severity.MEDIUM)
        ctx.limitations.append(lim)
        ctx.gate_history.append(("G1", GateDecision.PASS_WITH_LIMITS, lim.message))
        return GateDecision.PASS_WITH_LIMITS
    ctx.gate_history.append(("G1", GateDecision.PASS_WITHIN_DOMAIN, "G1 pass"))
    return GateDecision.PASS_WITHIN_DOMAIN

def gate_G2_model_domain(ctx):
    if ctx.model_approx.approx_name is None:
        ctx.gate_history.append(("G2", GateDecision.HOLD_FOR_EVIDENCE, "approx undefined"))
        return GateDecision.HOLD_FOR_EVIDENCE
    if not ctx.model_approx.matches_declared_domain:
        lim = Limitation("G2", "approx domain mismatch", Severity.HIGH)
        ctx.limitations.append(lim)
        ctx.gate_history.append(("G2", GateDecision.PASS_WITH_LIMITS, lim.message))
        return GateDecision.PASS_WITH_LIMITS
    ctx.gate_history.append(("G2", GateDecision.PASS_WITHIN_DOMAIN, "G2 pass"))
    return GateDecision.PASS_WITHIN_DOMAIN

def gate_G3_numeric_stat(ctx):
    if not ctx.numeric_stability.converged:
        ctx.gate_history.append(("G3", GateDecision.HOLD_FOR_EVIDENCE, "not converged"))
        return GateDecision.HOLD_FOR_EVIDENCE
    if not ctx.numeric_stability.stat_reliability_passed:
        lim = Limitation("G3", "stat reliability limited", Severity.MEDIUM)
        ctx.limitations.append(lim)
        ctx.gate_history.append(("G3", GateDecision.PASS_WITH_LIMITS, lim.message))
        return GateDecision.PASS_WITH_LIMITS
    ctx.gate_history.append(("G3", GateDecision.PASS_WITHIN_DOMAIN, "G3 pass"))
    return GateDecision.PASS_WITHIN_DOMAIN

def gate_G4_independent_verify(ctx):
    if ctx.independent_test_set.test_name is None:
        ctx.gate_history.append(("G4", GateDecision.HOLD_FOR_EVIDENCE, "testset undefined"))
        return GateDecision.HOLD_FOR_EVIDENCE
    if not ctx.independent_test_set.passed:
        ctx.gate_history.append(("G4", GateDecision.REJECT_CLAIM, "independent verify failed"))
        return GateDecision.REJECT_CLAIM
    ctx.gate_history.append(("G4", GateDecision.PASS_WITHIN_DOMAIN, "G4 pass"))
    return GateDecision.PASS_WITHIN_DOMAIN

def gate_G5_cross_scale(ctx):
    if ctx.cross_scale_bridge_evidence.evidence_name is None:
        if ctx.cross_scale_bridge_evidence.cross_scale_not_applicable_declared:
            return GateDecision.NOT_APPLICABLE
        ctx.gate_history.append(("G5", GateDecision.HOLD_FOR_EVIDENCE, "bridge evidence missing, no N/A declared"))
        return GateDecision.HOLD_FOR_EVIDENCE
    if not ctx.cross_scale_bridge_evidence.validated:
        lim = Limitation("G5", "bridge evidence unvalidated", Severity.MEDIUM)
        ctx.limitations.append(lim)
        ctx.gate_history.append(("G5", GateDecision.PASS_WITH_LIMITS, lim.message))
        return GateDecision.PASS_WITH_LIMITS
    ctx.gate_history.append(("G5", GateDecision.PASS_WITHIN_DOMAIN, "G5 pass"))
    return GateDecision.PASS_WITHIN_DOMAIN

def gate_G6_conclusion_boundary(ctx):
    if ctx.final_claim_text.claim_text is None:
        ctx.gate_history.append(("G6", GateDecision.HOLD_FOR_EVIDENCE, "claim undefined"))
        return GateDecision.HOLD_FOR_EVIDENCE
    if not ctx.final_claim_text.strictly_within_evidence:
        ctx.gate_history.append(("G6", GateDecision.REJECT_CLAIM, "claim out of evidence"))
        return GateDecision.REJECT_CLAIM
    ctx.gate_history.append(("G6", GateDecision.PASS_WITHIN_DOMAIN, "G6 pass"))
    return GateDecision.PASS_WITHIN_DOMAIN

def gate_G7_observation_contract(ctx):
    required_fields = [ctx.target.name, ctx.eval_function, ctx.auth_basis]
    if any(v is None for v in required_fields):
        ctx.gate_history.append(("G7", GateDecision.HOLD_FOR_EVIDENCE, "contract core missing"))
        return GateDecision.HOLD_FOR_EVIDENCE
    if len(ctx.variables) == 0 or len(ctx.stakeholders) == 0:
        lim = Limitation("G7", "contract partial", Severity.MEDIUM)
        ctx.limitations.append(lim)
        ctx.gate_history.append(("G7", GateDecision.PASS_WITH_LIMITS, lim.message))
        return GateDecision.PASS_WITH_LIMITS
    ctx.gate_history.append(("G7", GateDecision.PASS_WITHIN_DOMAIN, "G7 pass"))
    return GateDecision.PASS_WITHIN_DOMAIN

def gate_G8_domain_of_validity(ctx):
    required = [ctx.space_scale, ctx.time_window, ctx.system_boundary, ctx.initial_state]
    if any(v is None for v in required):
        ctx.gate_history.append(("G8", GateDecision.HOLD_FOR_EVIDENCE, "domain declaration insufficient"))
        return GateDecision.HOLD_FOR_EVIDENCE
    out_of_domain_flag = any(
        item.get("out_of_declared_domain", False)
        for item in ctx.external_inputs if isinstance(item, dict)
    )
    if out_of_domain_flag:
        ctx.gate_history.append(("G8", GateDecision.REJECT_CLAIM, "out of declared domain"))
        return GateDecision.REJECT_CLAIM
    ctx.gate_history.append(("G8", GateDecision.PASS_WITHIN_DOMAIN, "G8 pass"))
    return GateDecision.PASS_WITHIN_DOMAIN

def gate_G9_proposition_nature(ctx):
    if ctx.proposition_nature is None:
        ctx.gate_history.append(("G9", GateDecision.HOLD_FOR_EVIDENCE, "nature unclassified"))
        return GateDecision.HOLD_FOR_EVIDENCE
    if ctx.proposition_nature == RoutePath.H_HYBRID and not ctx.split_empirical_and_normative_chain:
        lim = Limitation("G9", "hybrid not split", Severity.HIGH)
        ctx.limitations.append(lim)
        ctx.gate_history.append(("G9", GateDecision.PASS_WITH_LIMITS, lim.message))
        return GateDecision.PASS_WITH_LIMITS
    ctx.gate_history.append(("G9", GateDecision.PASS_WITHIN_DOMAIN, "G9 pass"))
    return GateDecision.PASS_WITHIN_DOMAIN

GATE_PIPELINE = [
    ("G0", gate_G0_meta_rule_audit),
    ("G7", gate_G7_observation_contract),
    ("G8", gate_G8_domain_of_validity),
    ("G9", gate_G9_proposition_nature),
    ("G1", gate_G1_target_gate),
    ("G2", gate_G2_model_domain),
    ("G3", gate_G3_numeric_stat),
    ("G4", gate_G4_independent_verify),
    ("G5", gate_G5_cross_scale),
    ("G6", gate_G6_conclusion_boundary),
]

def run_g0_to_g9_audit(ctx):
    for gate_id, gate_func in GATE_PIPELINE:
        lim_before = len(ctx.limitations)
        decision = gate_func(ctx)
        if decision in (GateDecision.HOLD_FOR_EVIDENCE, GateDecision.REJECT_CLAIM):
            ctx.pending_na_reason = None
            ctx.pending_na_approver = None
            return {"final_result": "ABORTED", "abort_reason": decision.value,
                    "history": ctx.gate_history,
                    "limitations": [l.__dict__ for l in ctx.limitations],
                    "na_records": ctx.na_records}
        if decision == GateDecision.NOT_APPLICABLE:
            if gate_id not in NA_WHITELIST:
                ctx.gate_history.append((gate_id, GateDecision.PIPELINE_VIOLATION, "not in NA whitelist"))
                ctx.pending_na_reason = None
                ctx.pending_na_approver = None
                return {"final_result": GateDecision.PIPELINE_VIOLATION.value, "history": ctx.gate_history,
                        "limitations": [l.__dict__ for l in ctx.limitations],
                        "na_records": ctx.na_records}
            reason = ctx.pending_na_reason
            approver = ctx.pending_na_approver
            if not isinstance(reason, str) or reason.strip() == "":
                ctx.gate_history.append((gate_id, GateDecision.PIPELINE_VIOLATION, "NA reason empty"))
                ctx.pending_na_reason = None
                ctx.pending_na_approver = None
                return {"final_result": GateDecision.PIPELINE_VIOLATION.value, "history": ctx.gate_history,
                        "limitations": [l.__dict__ for l in ctx.limitations],
                        "na_records": ctx.na_records}
            if not isinstance(approver, str) or approver.strip() == "":
                ctx.gate_history.append((gate_id, GateDecision.PIPELINE_VIOLATION, "NA approver empty"))
                ctx.pending_na_reason = None
                ctx.pending_na_approver = None
                return {"final_result": GateDecision.PIPELINE_VIOLATION.value, "history": ctx.gate_history,
                        "limitations": [l.__dict__ for l in ctx.limitations],
                        "na_records": ctx.na_records}
            if ctx.trusted_auth_source is None:
                ctx.gate_history.append((gate_id, GateDecision.PIPELINE_VIOLATION, "missing TrustedAuthSource"))
                ctx.pending_na_reason = None
                ctx.pending_na_approver = None
                return {"final_result": GateDecision.PIPELINE_VIOLATION.value, "history": ctx.gate_history,
                        "limitations": [l.__dict__ for l in ctx.limitations],
                        "na_records": ctx.na_records}
            real_role = ctx.trusted_auth_source.get_role(approver.strip())
            if real_role not in NA_AUTH_ROLE_TABLE.get(gate_id, []):
                ctx.gate_history.append((gate_id, GateDecision.PIPELINE_VIOLATION, "approver role no NA auth"))
                ctx.pending_na_reason = None
                ctx.pending_na_approver = None
                return {"final_result": GateDecision.PIPELINE_VIOLATION.value, "history": ctx.gate_history,
                        "limitations": [l.__dict__ for l in ctx.limitations],
                        "na_records": ctx.na_records}
            rec = NARecord()
            rec.gate_id = gate_id
            rec.approve_reason = reason.strip()
            rec.approver = approver.strip()
            rec.approver_role = real_role
            rec.auth_snapshot_version = ctx.trusted_auth_source.auth_snapshot_version
            ctx.na_records.append(rec)
            ctx.gate_history.append((gate_id, GateDecision.NOT_APPLICABLE, rec.approve_reason))
            ctx.pending_na_reason = None
            ctx.pending_na_approver = None
            continue
        if decision == GateDecision.PASS_WITH_LIMITS:
            history_snapshot = ctx.limitations[:lim_before]
            if len(ctx.limitations) < lim_before or ctx.limitations[:lim_before] != history_snapshot:
                ctx.gate_history.append((gate_id, GateDecision.PIPELINE_VIOLATION, "history limitation readonly violated"))
                ctx.pending_na_reason = None
                ctx.pending_na_approver = None
                return {"final_result": GateDecision.PIPELINE_VIOLATION.value, "history": ctx.gate_history,
                        "limitations": [l.__dict__ for l in ctx.limitations],
                        "na_records": ctx.na_records}
            new_lims = ctx.limitations[lim_before:]
            if len(new_lims) == 0:
                ctx.gate_history.append((gate_id, GateDecision.PIPELINE_VIOLATION, "PASS_WITH_LIMITS without new Limitation"))
                ctx.pending_na_reason = None
                ctx.pending_na_approver = None
                return {"final_result": GateDecision.PIPELINE_VIOLATION.value, "history": ctx.gate_history,
                        "limitations": [l.__dict__ for l in ctx.limitations],
                        "na_records": ctx.na_records}
            for lim_item in new_lims:
                if not isinstance(lim_item, Limitation):
                    ctx.gate_history.append((gate_id, GateDecision.PIPELINE_VIOLATION, "not Limitation type"))
                    ctx.pending_na_reason = None
                    ctx.pending_na_approver = None
                    return {"final_result": GateDecision.PIPELINE_VIOLATION.value, "history": ctx.gate_history,
                            "limitations": [l.__dict__ for l in ctx.limitations],
                            "na_records": ctx.na_records}
                if lim_item.gate_id != gate_id:
                    ctx.gate_history.append((gate_id, GateDecision.PIPELINE_VIOLATION, "gate_id mismatch"))
                    ctx.pending_na_reason = None
                    ctx.pending_na_approver = None
                    return {"final_result": GateDecision.PIPELINE_VIOLATION.value, "history": ctx.gate_history,
                            "limitations": [l.__dict__ for l in ctx.limitations],
                            "na_records": ctx.na_records}
                if not isinstance(lim_item.message, str) or lim_item.message.strip() == "":
                    ctx.gate_history.append((gate_id, GateDecision.PIPELINE_VIOLATION, "message empty"))
                    ctx.pending_na_reason = None
                    ctx.pending_na_approver = None
                    return {"final_result": GateDecision.PIPELINE_VIOLATION.value, "history": ctx.gate_history,
                            "limitations": [l.__dict__ for l in ctx.limitations],
                            "na_records": ctx.na_records}
                if not isinstance(lim_item.severity, Severity):
                    ctx.gate_history.append((gate_id, GateDecision.PIPELINE_VIOLATION, "severity not enum"))
                    ctx.pending_na_reason = None
                    ctx.pending_na_approver = None
                    return {"final_result": GateDecision.PIPELINE_VIOLATION.value, "history": ctx.gate_history,
                            "limitations": [l.__dict__ for l in ctx.limitations],
                            "na_records": ctx.na_records}
            continue
    if len(ctx.limitations) > 0:
        final = GateDecision.PASS_WITH_LIMITS_FINAL.value
    else:
        final = GateDecision.PASS_WITHIN_DOMAIN.value
    return {"final_result": final, "history": ctx.gate_history,
            "limitations": [l.__dict__ for l in ctx.limitations],
            "na_records": ctx.na_records}