from pathlib import Path
import subprocess


def test_session_01_readout_and_challenge_for_every_switch_pattern():
    app = Path(__file__).resolve().parents[1] / "sessions" / "session-01" / "app.html"
    script = app.read_text(encoding="utf-8").split("<script>", 1)[1].split("</script>", 1)[0]
    harness = r'''
const vm = require("node:vm");
const assert = require("node:assert/strict");
const elements = {};
const context = new Proxy({}, { get: (o, k) => o[k] || (() => {}), set: (o, k, v) => (o[k] = v, true) });
function element(id) {
  return elements[id] || (elements[id] = { id, style: {}, dataset: {}, children: [], listeners: {}, value: "", textContent: "", innerHTML: "", hidden: false,
    className: "", setAttribute(k,v) { this[k] = v; }, getAttribute(k) { return this[k]; }, appendChild(e) { this.children.push(e); },
    addEventListener(k,f) { this.listeners[k] = f; }, querySelector(s) { const id = (this.innerHTML.match(/id="([^"]+)"/) || [])[1]; return element(s === "input" ? id : id + "output"); }, getContext() { return context; } });
}
const document = { title: "Session 1", documentElement: {}, getElementById: element,
  createElement: () => ({ ...element("new"), setAttribute: element("new").setAttribute, addEventListener: element("new").addEventListener }),
  querySelectorAll: () => element("#graphs").children };
const sandbox = { document, window: {}, getComputedStyle: () => ({ getPropertyValue: () => "#000" }),
  matchMedia: () => ({ addEventListener() {} }), Math, String, Object, Array };
vm.runInNewContext(SOURCE, sandbox);
for (let n = 0; n < 16; n++) {
  const bits = n.toString(2).padStart(4, "0");
  for (let i = 0; i < 4; i++) { const id = "b" + (3 - i), slider = element(id); slider.value = bits[i]; slider.listeners.input(); }
  assert.match(element("readout").innerHTML, new RegExp("pattern " + bits + " = " + n + " \\(decimal, hex " + n.toString(16).toUpperCase() + "\\)"));
  assert.equal(element("challenge").dataset.ok, String(n === 13));
  assert.equal(element("challenge").innerHTML.includes("Done!"), n === 13);
}
'''.replace("SOURCE", repr(script))
    result = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr or result.stdout
