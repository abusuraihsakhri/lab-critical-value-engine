"use strict";
/* Standalone demonstration mirroring Python's generic worker rules.
   The thresholds have no clinical validity. No data is transmitted. */
const demoKeywordPattern = /DISCORDANT|ANOMALY|MUTANT|VIOLATION|FAIL|REJECT/;
let evaluated = 0;
let alertsTotal = 0;

function localEvaluation(payload) {
  const alerts = [];
  if (payload.primary_metric > 25) {
    alerts.push({origin_worker:"InvariantQCWorker", urgency:"ELEVATED_RISK",
      summary:"Generic primary metric exceeds demonstration limit (25)"});
  }
  if (payload.is_critical_flag || payload.secondary_metric > 12) {
    alerts.push({origin_worker:"SafetyEscalationWorker",
      urgency:payload.is_critical_flag ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      summary:"Synthetic critical flag or secondary index exceeds demonstration limit (12)"});
  }
  if (demoKeywordPattern.test(payload.status_descriptor.toUpperCase())) {
    alerts.push({origin_worker:"ProtocolConformanceWorker", urgency:"ELEVATED_RISK",
      summary:"Descriptor contains a demonstration anomaly keyword"});
  }
  const critical = alerts.filter(a => a.urgency === "CRITICAL_STAT_PANIC").length;
  return {
    mode:"BROWSER_DEMONSTRATION_ONLY",
    disclaimer:"Generic example rules only. Not validated for patient care.",
    task_id:payload.task_id,
    target_identifier:payload.target_identifier,
    overall_urgency:critical ? "CRITICAL_STAT_PANIC" : alerts.length ? "ELEVATED_RISK" : "ROUTINE",
    integrity_status:critical ? "RECALIBRATION_REQUIRED" : alerts.length ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
    total_alerts:alerts.length,
    critical_alerts_count:critical,
    alerts,
    audit_hash:null,
    audit_note:"No cryptographic signature or persistent audit record was created"
  };
}

function runAudit() {
  const get = id => document.getElementById(id);
  const output = get("outputConsole");
  const primaryString = get("primary_metric").value.trim();
  const secondaryString = get("secondary_metric").value.trim();
  const primary = Number(primaryString);
  const secondary = Number(secondaryString);
  if (!primaryString || !secondaryString ||
      !Number.isFinite(primary) || !Number.isFinite(secondary)) {
    output.textContent = "Enter valid finite numbers for both demonstration metrics.";
    return;
  }
  const payload = {
    task_id:get("task_id").value.trim(),
    target_identifier:get("target_id").value.trim(),
    primary_metric:primary,
    secondary_metric:secondary,
    status_descriptor:get("status_descriptor").value.trim(),
    is_critical_flag:get("is_critical").checked
  };
  if (!payload.task_id || !payload.target_identifier || !payload.status_descriptor) {
    output.textContent = "Fill in all synthetic identifier and descriptor fields.";
    return;
  }
  const result = localEvaluation(payload);
  evaluated++;
  alertsTotal += result.total_alerts;
  output.textContent = JSON.stringify(result, null, 2);
  get("m-tasks").textContent = String(evaluated);
  get("m-audit").textContent = String(alertsTotal);
}

document.getElementById("run-audit").addEventListener("click", runAudit);
