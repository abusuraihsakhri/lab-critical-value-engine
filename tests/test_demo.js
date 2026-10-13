"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const source = fs.readFileSync("web/demo.js", "utf8");
const context = {document: {getElementById: () => ({addEventListener: () => {}})}};
vm.createContext(context);
vm.runInContext(source, context);

const payload = {task_id:"T", target_identifier:"SYNTH", primary_metric:1,
                 secondary_metric:1, is_critical_flag:false, status_descriptor:"NOMINAL"};
function evaluate(p) {
  return vm.runInContext("localEvaluation(" + JSON.stringify(p) + ")", context);
}
assert.equal(evaluate(payload).overall_urgency,"ROUTINE");
assert.equal(evaluate({...payload,primary_metric:26}).overall_urgency,"ELEVATED_RISK");
assert.equal(evaluate({...payload,secondary_metric:13}).total_alerts,1);
assert.equal(evaluate({...payload,status_descriptor:"ANOMALY"}).total_alerts,1);
assert.equal(evaluate({...payload,is_critical_flag:true}).overall_urgency,"CRITICAL_STAT_PANIC");
assert.equal(evaluate(payload).audit_hash,null);
console.log("Browser demonstration rule tests passed");
