const scanBtn = document.getElementById("scanBtn");
const lastScanEl = document.getElementById("lastScan");
const devicesList = document.getElementById("devicesList");
const alertsPanel = document.getElementById("alertsPanel");
const alertsList = document.getElementById("alertsList");
const riskCard = document.getElementById("riskCard");

const deviceTemplate = document.getElementById("deviceTemplate");
const portTemplate = document.getElementById("portTemplate");
const alertTemplate = document.getElementById("alertTemplate");

function setScanning(isScanning) {
  scanBtn.disabled = isScanning;
  scanBtn.classList.toggle("scanning", isScanning);
  scanBtn.querySelector(".label").textContent = isScanning ? "Scanning…" : "Scan now";
}

async function runScan() {
  setScanning(true);
  lastScanEl.textContent = "Scanning your network…";
  try {
    const res = await fetch("/api/scan");
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      lastScanEl.textContent = err.error || "Scan failed.";
      return;
    }
    const data = await res.json();
    render(data);
  } catch (e) {
    lastScanEl.textContent = "Couldn't reach the scanner. Is the server running?";
  } finally {
    setScanning(false);
  }
}

function render(data) {
  lastScanEl.textContent = `Last scanned ${data.timestamp}`;

  // Summary
  document.getElementById("statDevices").textContent = data.summary.device_count;
  document.getElementById("statPorts").textContent = data.summary.total_ports;
  document.getElementById("statHighRisk").textContent = data.summary.high_risk;
  document.getElementById("statRisk").textContent = data.summary.overall_risk;
  riskCard.dataset.risk = data.summary.overall_risk;

  // Alerts
  renderAlerts(data.alerts);

  // Devices
  renderDevices(data.devices);
}

function renderAlerts(alerts) {
  alertsList.innerHTML = "";
  const rows = [];

  if (alerts.has_baseline) {
    alerts.new.forEach((ip) => rows.push({ kind: "new", text: `New device joined your network: ${ip}`, icon: "⚠️" }));
    alerts.missing.forEach((ip) => rows.push({ kind: "missing", text: `Device no longer seen: ${ip}`, icon: "ℹ️" }));
  }

  if (rows.length === 0) {
    alertsPanel.hidden = true;
    return;
  }

  alertsPanel.hidden = false;
  rows.forEach((row) => {
    const node = alertTemplate.content.cloneNode(true);
    const el = node.querySelector(".alert-row");
    el.dataset.kind = row.kind;
    el.querySelector(".alert-icon").textContent = row.icon;
    el.querySelector(".alert-text").textContent = row.text;
    alertsList.appendChild(node);
  });
}

function renderDevices(devices) {
  devicesList.innerHTML = "";

  if (!devices || devices.length === 0) {
    devicesList.innerHTML = '<p class="empty-state">No devices responded on your network.</p>';
    return;
  }

  devices.forEach((device) => {
    const node = deviceTemplate.content.cloneNode(true);
    const card = node.querySelector(".device-card");
    card.querySelector(".device-name").textContent = device.name;
    card.querySelector(".device-ip").textContent = device.ip;

    const portCount = device.ports.length;
    card.querySelector(".port-count").textContent =
      portCount === 0 ? "No open ports" : `${portCount} open port${portCount > 1 ? "s" : ""}`;

    const portsList = card.querySelector(".ports-list");

    if (portCount === 0) {
      portsList.innerHTML = '<p class="empty-state">Nothing responded on the ports we checked.</p>';
    } else {
      device.ports.forEach((port) => portsList.appendChild(buildPortRow(port)));
    }

    card.querySelector(".device-header").addEventListener("click", () => {
      card.classList.toggle("open");
      const body = card.querySelector(".device-body");
      body.style.maxHeight = card.classList.contains("open") ? body.scrollHeight + "px" : "0";
    });

    devicesList.appendChild(node);
  });
}

function buildPortRow(port) {
  const node = portTemplate.content.cloneNode(true);
  const row = node.querySelector(".port-row");
  row.dataset.risk = port.risk;

  row.querySelector(".port-number").textContent = `Port ${port.port}`;
  row.querySelector(".port-service").textContent = port.service;
  row.querySelector(".port-risk-label").textContent = port.risk;
  row.querySelector(".port-description").textContent = port.description || "";
  row.querySelector(".port-advice").textContent = port.advice ? `What to do: ${port.advice}` : "";

  const bannerEl = row.querySelector(".port-banner");
  if (port.banner) {
    bannerEl.textContent = `Service said: ${port.banner}`;
  } else {
    bannerEl.remove();
  }

  return node;
}

scanBtn.addEventListener("click", runScan);
window.addEventListener("DOMContentLoaded", runScan);
