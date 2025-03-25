function onCodeChange() {
  const code = document.getElementById('referralCode').value;
  document.getElementById('tokenBlock').classList.toggle('hidden', !code);
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleString('zh-TW');
}

function fetchOrders() {
  const code = document.getElementById('referralCode').value;
  const token = document.getElementById('accessToken').value;
  const start = document.getElementById('startTime').value;
  const end = document.getElementById('endTime').value;

  if (!code || !token || !start || !end) {
    alert('請完整填寫所有欄位');
    return;
  }

  document.getElementById("stats").innerHTML = "🔄 查詢中，請稍候...";

  const url = `https://referral-report-api.onrender.com/orders?referral_code=${code}&access_token=${token}&created_at_min=${start.replace('T', ' ')}&created_at_max=${end.replace('T', ' ')}`;

  fetch(url)
    .then(res => res.json())
    .then(data => {
      if (data.message) {
        alert(data.message);
        document.getElementById("stats").innerHTML = "";
        return;
      }

      renderTable(data);
      renderStats(data);
      window._csvData = data;
      window._csvMeta = { code, start, end };
    });
}

function renderTable(data) {
  const tbody = document.querySelector("#results tbody");
  tbody.innerHTML = "";
  data.forEach(order => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${order.order_number}</td>
      <td>${formatDate(order.created_at)}</td>
      <td>${order.total_price}</td>
      <td>${order.financial_status}</td>
      <td>${order.fulfillment_status}</td>
      <td>${order.is_cancelled ? "❌ 已取消" : "✅ 有效"}</td>
      <td>${order.remark || ""}</td>
    `;
    tbody.appendChild(row);
  });
}

function renderStats(data) {
  const paid = data.filter(o => o.financial_status === "paid" && !o.is_cancelled);
  const count = paid.length;
  const total = paid.reduce((sum, o) => sum + parseFloat(o.total_price), 0);
  const shipping = paid.reduce((sum, o) => sum + parseFloat(o.shipping_fee || 0), 0);

  document.getElementById("stats").innerHTML =
    `✅ 共 <b>${count}</b> 筆有效訂單，總金額：<b>NT$ ${total.toFixed(0)}</b>，總運費：<b>NT$ ${shipping.toFixed(0)}</b>`;
}

function exportCSV() {
  const data = window._csvData || [];
  const meta = window._csvMeta || {};
  if (data.length === 0) return alert("沒有資料可匯出");

  const header = ["訂單編號", "成立時間", "金額", "付款狀態", "出貨狀態", "狀態", "備註"];
  const rows = data.map(o => [
    o.order_number,
    formatDate(o.created_at),
    o.total_price,
    o.financial_status,
    o.fulfillment_status,
    o.is_cancelled ? "❌ 已取消" : "✅ 有效",
    o.remark || ""
  ]);

  const csvContent = [header, ...rows].map(e => e.join("\t")).join("\n");
  const bom = new Uint8Array([0xEF, 0xBB, 0xBF]);
  const blob = new Blob([bom, csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);

  const formatForFilename = (datetime) => {
    const d = new Date(datetime);
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    const hh = String(d.getHours()).padStart(2, '0');
    const min = String(d.getMinutes()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}_${hh}${min}`;
  };

  const filename = `referral_orders_${meta.code}_${formatForFilename(meta.start)}_to_${formatForFilename(meta.end)}.csv`;
  link.download = filename;
  link.click();
}


window.onload = () => {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get("referral_code");
  const token = urlParams.get("access_token");

  if (code && token) {
    document.getElementById("referralCodeDisplay").innerText = code;
    document.getElementById("infoBox").classList.remove("hidden");
  }

  if (code) {
    const referralSelect = document.getElementById("referralCode");
    referralSelect.value = code;
    onCodeChange();
  }

  if (token) {
    document.getElementById("accessToken").value = token;
  }

  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0);
  const end = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59);
  document.getElementById("startTime").value = start.toISOString().slice(0, 16);
  document.getElementById("endTime").value = end.toISOString().slice(0, 16);
};
