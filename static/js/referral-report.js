// ✅ 初始排序設定
let currentSort = "name";

function onCodeChange() {
  const code = document.getElementById('referralCode').value;
  document.getElementById('tokenBlock').classList.toggle('hidden', !code);
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleString('zh-TW');
}

function getBadge(type, value) {
  const map = {
    financial: {
      paid: `<span class="badge badge-paid">已付款</span>`,
      unpaid: `<span class="badge badge-unpaid">未付款</span>`,
      pending: `<span class="badge badge-pending">待付款</span>`,
      refunded: `<span class="badge badge-refunded">已退款</span>`
    },
    fulfillment: {
      fulfilled: `<span class="badge badge-fulfilled">已出貨</span>`,
      unfulfilled: `<span class="badge badge-unfulfilled">未出貨</span>`,
      restocked: `<span class="badge badge-restocked">已退貨</span>`
    },
    system: {
      valid: `<span class="badge badge-ok" title="系統記錄為有效訂單">✅</span>`,
      cancelled: `<span class="badge badge-fail" title="取消或不列入統計">❌</span>`
    }
  };
  return map[type][value] || "-";
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
  document.getElementById("statsNote").classList.add("hidden");

  const url = `http://127.0.0.1:5000/orders?referral_code=${code}&access_token=${token}&created_at_min=${start.replace('T', ' ')}&created_at_max=${end.replace('T', ' ')}`;

  fetch(url)
    .then(res => res.json())
    .then(data => {
      if (data.message) {
        alert(data.message);
        document.getElementById("stats").innerHTML = "⚠️ 無符合的訂單";
        return;
      }

      renderTable(data);
      renderStats(data);
      renderSKUStats(data);
      window._csvData = data;
      window._csvMeta = { code, start, end };
    });
}

function renderTable(data) {
  const tbody = document.querySelector("#results tbody");
  tbody.innerHTML = "";

  data.forEach(order => {
    const row = document.createElement("tr");

    const systemStatus = order.is_cancelled || order.financial_status === "refunded"
      ? "cancelled" : "valid";

    row.innerHTML = `
      <td>${order.order_number}</td>
      <td>${formatDate(order.created_at)}</td>
      <td>${order.total_price}</td>
      <td>${getBadge("financial", order.financial_status)}</td>
      <td>${getBadge("fulfillment", order.fulfillment_status)}</td>
      <td>${getBadge("system", systemStatus)}</td>
      <td>${order.remark || ""}</td>
    `;
    tbody.appendChild(row);
  });
}

function renderStats(data) {
  const validOrders = data.filter(o =>
    o.financial_status === "paid" &&
    o.is_cancelled === false &&
    o.is_refunded === false
  );

  const count = validOrders.length;
  const total = validOrders.reduce((sum, o) => sum + parseFloat(o.total_price), 0);
  const shipping = validOrders.reduce((sum, o) => sum + parseFloat(o.shipping_fee || 0), 0);

  const statsBox = document.getElementById("stats");
  statsBox.innerHTML =
    count > 0
      ? `📊 統計：共 <b>${count}</b> 筆有效訂單（已付款＋未退款＋未取消），總金額：<b>NT$ ${total.toFixed(0)}</b>，總運費：<b>NT$ ${shipping.toFixed(0)}</b>`
      : `📊 沒有符合條件的訂單（已付款＋未退款＋未取消）`;

  document.getElementById("statsNote").classList.remove("hidden");
}

const SKU_MAP = {
  "LA02-4566": "除菌去漬洗衣精（蔚藍海岸）",
  "LA02-4580": "除菌去漬洗衣精（氣泡香檳）",
  "LA02-4573": "除菌去漬洗衣精（法式馬卡龍）",
  "LA02-4597": "除菌去漬洗衣精（無香料）",
  "LA03-4603": "除菌去漬洗衣精補充包（蔚藍海岸）",
  "LA03-4627": "除菌去漬洗衣精補充包（氣泡香檳）",
  "LA03-4610": "除菌去漬洗衣精補充包（法式馬卡龍）",
  "LA03-4634": "除菌去漬洗衣精補充包（無香料）",
  "LA02-0029": "香氛柔軟精（蔚藍海岸）",
  "LA02-0074": "香氛柔軟精補充包（蔚藍海岸）",
  "LA02-1514": "香氛柔軟精（氣泡香檳）",
  "LA02-1521": "香氛柔軟精補充包（氣泡香檳）",
  "LA02-0043": "香氛柔軟精（法式馬卡龍）",
  "LA02-0098": "香氛柔軟精補充包（法式馬卡龍）",
  "LA02-2801": "精緻衣物洗衣精（蔚藍海岸）",
  "LA02-2863": "精緻衣物洗衣精（氣泡香檳）",
  "LA02-2832": "精緻衣物洗衣精（法式馬卡龍）",
  "LA02-0173": "柔氛噴霧（蔚藍海岸）",
  "LA02-1538": "柔氛噴霧（氣泡香檳）",
  "LA02-0197": "柔氛噴霧（法式馬卡龍）",
  "LA02-0418": "柔氛噴霧補充包（蔚藍海岸）",
  "LA02-1545": "柔氛噴霧補充包（氣泡香檳）",
  "LA02-0432": "柔氛噴霧補充包（法式馬卡龍）",
  "LA02-2351": "室內擴香（蔚藍海岸）",
  "LA02-2368": "室內擴香補充包（蔚藍海岸）",
  "LA02-2399": "室內擴香（氣泡香檳）",
  "LA02-2405": "室內擴香補充包（氣泡香檳）",
  "LA02-2375": "室內擴香（法式馬卡龍）",
  "LA02-2382": "室內擴香補充包（法式馬卡龍）",
  "LA02-3729": "To the Moon衣物柔軟精（清鈴恬木）",
  "LA02-9510": "To the Moon衣物柔軟精（澄柑暖木）",
  "LA02-3743": "To the Moon織品噴霧（清鈴恬木）",
  "LA02-9534": "To the Moon織品噴霧（澄柑暖木）"
};

/* function renderSKUStats(data) {
  document.querySelector(".sort-bar").classList.remove("hidden");
  const skuCount = {};
  const validOrders = data.filter(o =>
    o.financial_status === "paid" &&
    o.is_cancelled === false &&
    o.is_refunded === false
  );

  validOrders.forEach(order => {
    const items = order.line_items || [];
    items.forEach(item => {
      const sku = item.sku;
      const qty = parseInt(item.quantity) || 0;
      if (!sku) return;

      const units = sku.split(",");
      units.forEach(unit => {
        const [baseSku, multiplier] = unit.split("*");
        const count = parseInt(multiplier || "1") * qty;
        if (!skuCount[baseSku]) skuCount[baseSku] = 0;
        skuCount[baseSku] += count;
      });
    });
  });

  const tbody = document.querySelector("#skuStatsTable tbody");
  tbody.innerHTML = "";

  let sorted = Object.entries(skuCount);
  if (currentSort === "count") {
    sorted.sort((a, b) => b[1] - a[1]);
  } else if (currentSort === "name") {
    sorted.sort((a, b) => {
      const nameA = SKU_MAP[a[0]] || a[0];
      const nameB = SKU_MAP[b[0]] || b[0];
      return nameA.localeCompare(nameB, "zh-Hant");
    });
  }

  sorted.forEach(([sku, qty]) => {
    const tr = document.createElement("tr");
    const name = SKU_MAP[sku] || "❓ 未知品項";
    tr.innerHTML = `<td>${name}</td><td>${sku}</td><td>${qty}</td>`;
    tbody.appendChild(tr);
  });

  document.getElementById("skuStatsBox").classList.remove("hidden");
} // 客戶並未確認要使用 */

/*function onChangeSKUSort() {
  currentSort = document.getElementById("skuSortSelect").value;
  renderSKUStats(window._csvData || []);
} // 客戶並未確認要使用 */

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
  document.getElementById("skuSortSelect").value = "name";
  currentSort = "name";
};
