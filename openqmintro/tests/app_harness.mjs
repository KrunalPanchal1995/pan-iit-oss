// Loads an app.html in a stub browser and sweeps its sliders. Usage: node app_harness.mjs path/to/app.html
import fs from "node:fs";
import vm from "node:vm";

const html = fs.readFileSync(process.argv[2], "utf8");
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const els = {};
const el = (id) => els[id] || (els[id] = {
  id, innerHTML: "", textContent: "", hidden: false, dataset: {}, value: "", children: [],
  setAttribute() {}, addEventListener() {}, appendChild(c) { this.children.push(c); },
  querySelector: () => el("q"), querySelectorAll: () => [],
});
const ctx = new Proxy({}, { get: (t, k) => (k in t ? t[k] : () => undefined), set: (t, k, v) => { t[k] = v; return true; } });
const canvas = { width: 720, height: 420, getContext: () => ctx, setAttribute() {} };
const sandbox = {
  document: { getElementById: (id) => (id === "c" ? canvas : el(id)), createElement: () => el("new" + Math.random()), querySelectorAll: () => [], documentElement: {} },
  getComputedStyle: () => ({ getPropertyValue: () => "#000" }),
  matchMedia: () => ({ addEventListener() {} }),
  Math, console, isFinite, Object, Array, String, Number, JSON,
};
vm.createContext(sandbox);
vm.runInContext(script, sandbox);
const run = (code) => vm.runInContext(code, sandbox);

const problems = [];
const params = run("PARAMS"), graphs = run("GRAPHS.map(g => g.id)");
const bad = (s) => /NaN|Infinity|undefined/.test(s);
const snapshot = () => {
  const out = {};
  for (const g of graphs) {
    run(`graph = ${JSON.stringify(g)}; draw();`);
    out[g] = el("readout").innerHTML;
    if (bad(out[g])) problems.push(`bad readout in ${g}: ${out[g]}`);
  }
  return out;
};
const def = run("Object.assign({}, DEFAULTS)");
const set = (vals) => run(`setAll(${JSON.stringify(vals)})`);
for (const pick of ["min", "value", "max"]) {          // every control at min, default and max
  const vals = Object.assign({}, def);
  for (const q of params) vals[q.id] = q[pick];
  set(vals);
  snapshot();
}
for (const q of params) {                              // no dead sliders
  set(def);
  const a = JSON.stringify(snapshot());
  set(Object.assign({}, def, { [q.id]: q.value === q.max ? q.min : q.max }));
  const b = JSON.stringify(snapshot());
  if (a === b) problems.push(`slider ${q.id} changes nothing`);
}
set(def);
const sol = run("CHALLENGE_SOLUTION"), test = run("challengeTest");
if (test) {
  if (!test(sol)) problems.push("the stated challenge solution does not pass the challenge test");
  if (test(def)) problems.push("the challenge is already done at the default values");
}
if (process.argv[3]) {                                 // optional: golden values from the Python lesson
  for (const [expr, want, tol] of JSON.parse(process.argv[3])) {
    const got = run(expr);
    if (!(Math.abs(got - want) <= tol * Math.max(1, Math.abs(want)))) problems.push(`golden ${expr}: got ${got}, want ${want}`);
  }
}
if (problems.length) { console.log(problems.join("\n")); process.exit(1); }
console.log("APP OK " + process.argv[2]);
