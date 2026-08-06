'use strict';

/* Colors for each water quality class returned by the ML model. */
const QUALITY_COLORS = {
  Baik: '#1a7f37',
  Sedang: '#9a6700',
  Buruk: '#cf222e',
  'Not predicted': '#8c959f',
};

/* Maps a model label to its badge CSS class. */
const BADGE_CLASS = {
  Baik: 'badge badge-good',
  Sedang: 'badge badge-moderate',
  Buruk: 'badge badge-poor',
};

const REFRESH_INTERVAL_MS = 60000;

let trendChart = null;
let distributionChart = null;

Chart.defaults.color = '#656d76';
Chart.defaults.borderColor = '#d8dee4';
Chart.defaults.font.family =
  '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
Chart.defaults.font.size = 11;

/** Fetch JSON from an API endpoint and unwrap the `data` envelope. */
async function fetchData(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('HTTP ' + response.status);
  }
  const payload = await response.json();
  return payload.data;
}

/** Format an ISO timestamp using the Indonesian locale. */
function formatDateTime(isoString) {
  return isoString ? new Date(isoString).toLocaleString('id-ID') : '';
}

/** Populate the summary cards with the latest sensor reading. */
async function loadSummaryCards() {
  const data = await fetchData('/latest_reading');
  const qualityCell = document.getElementById('val-qual');

  if (!data.reading) {
    qualityCell.textContent = 'Belum ada data';
    return;
  }

  const reading = data.reading;
  document.getElementById('val-ph').textContent = reading.ph.toFixed(2);
  document.getElementById('val-temp').innerHTML =
    reading.temp.toFixed(2) + '<span class="unit">&deg;C</span>';
  document.getElementById('val-turb').innerHTML =
    reading.turbidity.toFixed(2) + '<span class="unit">NTU</span>';
  document.getElementById('val-time').textContent =
    formatDateTime(reading.timestamp);

  if (reading.predicted_quality) {
    const badge = document.createElement('span');
    badge.className = BADGE_CLASS[reading.predicted_quality] || 'badge';
    badge.textContent = reading.predicted_quality;
    qualityCell.replaceChildren(badge);
  } else {
    qualityCell.textContent = '\u2013';
  }
}

/** Render the line chart of hourly averaged sensor values. */
async function loadTrendChart() {
  const hours = document.getElementById('range').value;
  const data = await fetchData('/trend?hours=' + hours);
  const points = data.trend;

  if (trendChart) {
    trendChart.destroy();
  }

  trendChart = new Chart(document.getElementById('chart-trend'), {
    type: 'line',
    data: {
      labels: points.map((point) => point.hour.slice(5)),
      datasets: [
        {
          label: 'pH',
          data: points.map((point) => point.avg_ph),
          borderColor: '#0969da',
          backgroundColor: 'rgba(9, 105, 218, 0.08)',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3,
        },
        {
          label: 'Temperatur (\u00B0C)',
          data: points.map((point) => point.avg_temp),
          borderColor: '#cf222e',
          backgroundColor: 'rgba(207, 34, 46, 0.08)',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3,
        },
        {
          label: 'Kekeruhan (NTU)',
          data: points.map((point) => point.avg_turbidity),
          borderColor: '#1a7f37',
          backgroundColor: 'rgba(26, 127, 55, 0.08)',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          position: 'bottom',
          labels: { boxWidth: 10, padding: 12, usePointStyle: true },
        },
      },
      scales: {
        x: { ticks: { maxRotation: 0, autoSkipPadding: 24 } },
        y: { beginAtZero: false },
      },
    },
  });
}

/** Render the doughnut chart of water quality class distribution. */
async function loadDistributionChart() {
  const data = await fetchData('/quality_distribution');
  const labels = Object.keys(data.distribution);
  const counts = Object.values(data.distribution);

  if (distributionChart) {
    distributionChart.destroy();
  }

  distributionChart = new Chart(document.getElementById('chart-dist'), {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [
        {
          data: counts,
          backgroundColor: labels.map(
            (label) => QUALITY_COLORS[label] || '#8c959f'
          ),
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '60%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { boxWidth: 10, padding: 12, usePointStyle: true },
        },
        tooltip: {
          callbacks: {
            label: (context) =>
              context.label +
              ': ' +
              context.raw +
              ' (' +
              data.percentage[context.label] +
              '%)',
          },
        },
      },
    },
  });
}

/** Load every dashboard component and update the status label. */
async function loadDashboard() {
  const status = document.getElementById('status');
  status.textContent = 'Memuat\u2026';
  status.classList.remove('error');

  try {
    await Promise.all([
      loadSummaryCards(),
      loadTrendChart(),
      loadDistributionChart(),
    ]);
    status.textContent =
      'Diperbarui ' + new Date().toLocaleTimeString('id-ID');
  } catch (error) {
    status.textContent = 'Gagal memuat data: ' + error.message;
    status.classList.add('error');
  }
}

document.getElementById('range').addEventListener('change', loadTrendChart);

loadDashboard();
setInterval(loadDashboard, REFRESH_INTERVAL_MS);
