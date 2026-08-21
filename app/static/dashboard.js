let assets = [];
let selectedAssetId;
const $ = (id) => document.getElementById(id);

async function api(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) throw Error(await response.text());
  return response.json();
}

function healthClass(health) {
  return health < 45 ? "bad" : health < 70 ? "warn" : "good";
}

function priorityClass(priority) {
  return String(priority || "low").toLowerCase();
}

function percentage(value) {
  return value == null ? "--" : `${(value * 100).toFixed(1)}%`;
}

function number(value, decimals = 0) {
  return value == null ? "--" : Number(value).toFixed(decimals);
}

function renderMetrics(metrics) {
  $("assets").textContent = metrics.assets;
  $("predicted").textContent = `${metrics.predicted} assessed by model`;
  $("critical").textContent = metrics.critical;
  $("high").textContent = metrics.high;
  $("health").textContent = number(metrics.average_health, 1);
  $("failure").textContent = percentage(metrics.average_failure_probability);
}

function renderFleet() {
  const cards = $("cards");
  cards.innerHTML = "";
  assets.forEach((asset) => {
    const card = document.createElement("button");
    card.className = `asset-card${asset.id === selectedAssetId ? " selected" : ""}`;
    card.type = "button";
    card.innerHTML = `<span><span class="asset-name">${asset.name}</span><span class="asset-location">${asset.type} / ${asset.location}</span></span><span class="asset-score ${healthClass(asset.health_index ?? 0)}">${number(asset.health_index)}</span><span class="asset-meta"><span class="priority ${priorityClass(asset.priority)}">${asset.priority}</span> RUL ${number(asset.rul_hours)} h · risk ${percentage(asset.failure_probability)}</span>`;
    card.addEventListener("click", () => selectAsset(asset.id));
    cards.appendChild(card);
  });
}

function renderPriorities() {
  const table = $("table");
  table.innerHTML = "";
  [...assets].sort((left, right) => (left.health_index ?? 101) - (right.health_index ?? 101)).forEach((asset) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${asset.name}</td><td>${asset.location}</td><td class="value-${healthClass(asset.health_index ?? 0)}">${number(asset.health_index)}</td><td>${percentage(asset.failure_probability)}</td><td>${number(asset.rul_hours)} h</td><td>${number(asset.anomaly_score, 3)}</td><td>${number(asset.data_quality, 2)}</td><td>${number(asset.drift_score, 2)}</td><td><span class="priority ${priorityClass(asset.priority)}">${asset.priority}</span></td>`;
    table.appendChild(row);
  });
  $("priority-count").textContent = `${assets.length} assets`;
}

function renderPicker() {
  const picker = $("asset");
  picker.innerHTML = "";
  assets.forEach((asset) => {
    const option = document.createElement("option");
    option.value = asset.id;
    option.textContent = asset.name;
    picker.appendChild(option);
  });
  picker.value = selectedAssetId;
}

function drawChart(rows) {
  const canvas = $("chart");
  const context = canvas.getContext("2d");
  const width = canvas.clientWidth || 640;
  const height = 230;
  const ratio = window.devicePixelRatio || 1;
  canvas.width = width * ratio;
  canvas.height = height * ratio;
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  context.clearRect(0, 0, width, height);
  const values = rows.slice(-72).map((row) => row.temperature);
  if (!values.length) return;
  const min = Math.floor(Math.min(...values) - 2);
  const max = Math.ceil(Math.max(...values) + 2);
  const left = 41;
  const right = 18;
  const top = 24;
  const bottom = 28;
  context.strokeStyle = "#d8e2d8";
  context.lineWidth = 1;
  for (let step = 0; step < 4; step += 1) {
    const y = top + (step * (height - top - bottom)) / 3;
    context.beginPath();
    context.moveTo(left, y);
    context.lineTo(width - right, y);
    context.stroke();
    context.fillStyle = "#78857e";
    context.font = "10px DM Mono";
    context.fillText(`${(max - ((max - min) * step) / 3).toFixed(0)}°`, 5, y + 3);
  }
  context.strokeStyle = "#0d5c4b";
  context.lineWidth = 2.2;
  context.beginPath();
  values.forEach((value, index) => {
    const x = left + (index * (width - left - right)) / Math.max(1, values.length - 1);
    const y = top + ((max - value) * (height - top - bottom)) / (max - min || 1);
    if (index) context.lineTo(x, y); else context.moveTo(x, y);
  });
  context.stroke();
  context.fillStyle = "#527064";
  context.font = "10px DM Mono";
  context.fillText("72 latest readings · temperature", left, height - 9);
}

function renderModel(model) {
  $("model-version").textContent = model.version || "--";
  $("govmodel").textContent = model.version || "--";
  const run = model.latest_run;
  $("model").innerHTML = run ? `<div class="model-stat"><span>Accuracy</span><b>${percentage(run.accuracy)}</b></div><div class="model-stat"><span>F1 score</span><b>${percentage(run.f1)}</b></div><div class="model-stat"><span>ROC AUC</span><b>${percentage(run.roc_auc)}</b></div><div class="model-stat"><span>Training samples</span><b>${run.samples}</b></div>` : "<p class=\"panel-copy\">No model run recorded.</p>";
  const importance = $("importance");
  importance.innerHTML = "";
  const features = model.feature_importance || [];
  const peak = Math.max(...features.map((feature) => feature.importance || 0), 1);
  features.slice(0, 5).forEach((feature) => {
    const item = document.createElement("div");
    item.className = "importance-item";
    item.innerHTML = `<span>${feature.feature}</span><span class="importance-bar"><i style="width:${((feature.importance || 0) / peak) * 100}%"></i></span><b>${number(feature.importance, 2)}</b>`;
    importance.appendChild(item);
  });
}

async function selectAsset(assetId) {
  if (!assetId) return;
  selectedAssetId = Number(assetId);
  renderFleet();
  renderPicker();
  const asset = assets.find((item) => item.id === selectedAssetId);
  $("telemetry-title").textContent = asset ? `${asset.name} telemetry` : "Asset telemetry";
  drawChart(await api(`/api/assets/${selectedAssetId}/telemetry`));
}

async function refresh() {
  try {
    const dashboard = await api("/api/dashboard");
    assets = dashboard.assets;
    selectedAssetId = assets.some((asset) => asset.id === selectedAssetId) ? selectedAssetId : assets[0]?.id;
    renderMetrics(dashboard.metrics);
    renderFleet();
    renderPriorities();
    renderPicker();
    await selectAsset(selectedAssetId);
    renderModel(await api("/api/model/status"));
    $("refreshed").textContent = `Updated ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
  } catch (error) {
    $("result").textContent = error.message;
  }
}

$("asset").addEventListener("change", (event) => selectAsset(event.target.value));
document.querySelectorAll("[data-s]").forEach((button) => {
  button.addEventListener("click", async () => {
    document.querySelectorAll("[data-s]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    button.disabled = true;
    try {
      const result = await api(`/api/scenarios/${button.dataset.s}`, { method: "POST" });
      $("result").textContent = `${result.scenario.replaceAll("_", " ")} completed for ${result.predictions.length} assets.`;
      await refresh();
    } catch (error) {
      $("result").textContent = error.message;
    } finally {
      button.disabled = false;
    }
  });
});
$("reset").addEventListener("click", async () => {
  try {
    await api("/api/demo/reset", { method: "POST" });
    $("result").textContent = "Laboratory reset to baseline telemetry.";
    await refresh();
  } catch (error) {
    $("result").textContent = error.message;
  }
});
window.addEventListener("resize", () => selectedAssetId && selectAsset(selectedAssetId));
refresh();
setInterval(refresh, 15000);