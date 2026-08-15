const form = document.getElementById("expense-form");
const formError = document.getElementById("form-error");
const tbody = document.getElementById("expense-tbody");
const emptyState = document.getElementById("empty-state");
const totalAmountEl = document.getElementById("total-amount");
const dateInput = document.getElementById("date");

const CHART_COLORS = [
  "#3bb273", "#4d9de0", "#e15554", "#e1b12c",
  "#9b59b6", "#1abc9c", "#e67e22",
];

let chart;

function formatCurrency(value) {
  return value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatDate(isoDate) {
  const [year, month, day] = isoDate.split("-");
  return `${day}/${month}/${year}`;
}

async function fetchExpenses() {
  const res = await fetch("/api/expenses");
  const expenses = await res.json();
  renderExpenses(expenses);
}

async function fetchSummary() {
  const res = await fetch("/api/summary");
  const summary = await res.json();
  renderSummary(summary);
}

function renderExpenses(expenses) {
  tbody.innerHTML = "";
  emptyState.style.display = expenses.length ? "none" : "block";

  for (const expense of expenses) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${formatDate(expense.date)}</td>
      <td>${expense.description}</td>
      <td>${expense.category}</td>
      <td>${formatCurrency(expense.amount)}</td>
      <td><button class="delete-btn" data-id="${expense.id}" title="Remover">✕</button></td>
    `;
    tbody.appendChild(tr);
  }
}

function renderSummary(summary) {
  totalAmountEl.textContent = formatCurrency(summary.total);

  const labels = Object.keys(summary.by_category);
  const values = Object.values(summary.by_category);

  if (chart) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = values;
    chart.update();
    return;
  }

  chart = new Chart(document.getElementById("category-chart"), {
    type: "doughnut",
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: CHART_COLORS }],
    },
    options: {
      plugins: {
        legend: { labels: { color: "#f2f2f2" } },
      },
    },
  });
}

async function refresh() {
  await Promise.all([fetchExpenses(), fetchSummary()]);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError.textContent = "";

  const payload = {
    description: document.getElementById("description").value,
    amount: document.getElementById("amount").value,
    category: document.getElementById("category").value,
    date: dateInput.value,
  };

  const res = await fetch("/api/expenses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    formError.textContent = data.error || "Erro ao adicionar gasto";
    return;
  }

  form.reset();
  await refresh();
});

tbody.addEventListener("click", async (event) => {
  const button = event.target.closest(".delete-btn");
  if (!button) return;

  await fetch(`/api/expenses/${button.dataset.id}`, { method: "DELETE" });
  await refresh();
});

refresh();
