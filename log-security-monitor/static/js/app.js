const analyzeBtn = document.getElementById("analyze-btn");
const clearBtn = document.getElementById("clear-btn");
const analyzeStatus = document.getElementById("analyze-status");
const severityFilter = document.getElementById("severity-filter");
const tbody = document.getElementById("alert-tbody");
const emptyState = document.getElementById("empty-state");
const totalAlertsEl = document.getElementById("total-alerts");
const topIpsList = document.getElementById("top-ips-list");

const SEVERITY_LABELS = { low: "Baixa", medium: "Média", high: "Alta" };
const TYPE_LABELS = {
  failed_login: "Falha de login",
  invalid_user: "Usuário inválido",
  brute_force: "Força bruta",
  possible_compromise: "Possível comprometimento",
};
const SEVERITY_COLORS = { low: "#4d9de0", medium: "#e1b12c", high: "#e15554" };

let chart;

function formatDateTime(isoString) {
  const d = new Date(isoString);
  return d.toLocaleString("pt-BR");
}

async function fetchAlerts() {
  const severity = severityFilter.value;
  const url = severity ? `/api/alerts?severity=${severity}` : "/api/alerts";
  const res = await fetch(url);
  const alerts = await res.json();
  renderAlerts(alerts);
}

async function fetchSummary() {
  const res = await fetch("/api/summary");
  const summary = await res.json();
  renderSummary(summary);
}

function renderAlerts(alerts) {
  tbody.innerHTML = "";
  emptyState.style.display = alerts.length ? "none" : "block";

  for (const alert of alerts) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${formatDateTime(alert.occurred_at)}</td>
      <td><span class="badge ${alert.severity}">${SEVERITY_LABELS[alert.severity] || alert.severity}</span></td>
      <td>${TYPE_LABELS[alert.alert_type] || alert.alert_type}</td>
      <td>${alert.source_ip}</td>
      <td>${alert.username || "—"}</td>
      <td>${alert.message}</td>
    `;
    tbody.appendChild(tr);
  }
}

function renderSummary(summary) {
  totalAlertsEl.textContent = summary.total;

  topIpsList.innerHTML = "";
  for (const entry of summary.top_ips) {
    const li = document.createElement("li");
    li.innerHTML = `<span>${entry.ip}</span><span>${entry.count}</span>`;
    topIpsList.appendChild(li);
  }

  const labels = Object.keys(summary.by_severity).map((s) => SEVERITY_LABELS[s] || s);
  const values = Object.values(summary.by_severity);
  const colors = Object.keys(summary.by_severity).map((s) => SEVERITY_COLORS[s] || "#999");

  if (chart) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = values;
    chart.update();
    return;
  }

  chart = new Chart(document.getElementById("severity-chart"), {
    type: "doughnut",
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: colors }],
    },
    options: {
      plugins: {
        legend: { labels: { color: "#f2f2f2" } },
      },
    },
  });
}

async function refresh() {
  await Promise.all([fetchAlerts(), fetchSummary()]);
}

analyzeBtn.addEventListener("click", async () => {
  analyzeStatus.textContent = "Analisando...";
  const res = await fetch("/api/analyze", { method: "POST" });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    analyzeStatus.textContent = data.error || "Erro ao analisar logs";
    return;
  }

  const data = await res.json();
  analyzeStatus.textContent = `${data.lines_processed} linhas processadas, ${data.alerts_found} alertas encontrados.`;
  await refresh();
});

clearBtn.addEventListener("click", async () => {
  await fetch("/api/alerts", { method: "DELETE" });
  analyzeStatus.textContent = "Alertas limpos.";
  await refresh();
});

severityFilter.addEventListener("change", fetchAlerts);

refresh();
