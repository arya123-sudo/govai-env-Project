import { useEffect, useState, useRef } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";

// ── tiny helpers ──────────────────────────────────────────────────────────────
const riskLabel = (r) =>
  r > 0.7 ? "CRITICAL" : r > 0.4 ? "ELEVATED" : "CLEAR";

const riskColor = (r) =>
  r > 0.7 ? "var(--red)" : r > 0.4 ? "var(--amber)" : "var(--green)";

const fmt = (n) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);

// ── components ────────────────────────────────────────────────────────────────
function StatCard({ label, value, sub, accent }) {
  return (
    <div className="stat-card" style={{ "--accent-col": accent }}>
      <span className="stat-label">{label}</span>
      <span className="stat-value">{value}</span>
      {sub && <span className="stat-sub">{sub}</span>}
      <div className="stat-bar" />
    </div>
  );
}

function RiskMeter({ value }) {
  const pct = Math.round(value * 100);
  const col = riskColor(value);
  return (
    <div className="risk-meter">
      <div
        className="risk-fill"
        style={{ width: `${pct}%`, background: col }}
      />
      <span className="risk-pct" style={{ color: col }}>
        {pct}%
      </span>
    </div>
  );
}

function CitizenCard({ citizen, idx }) {
  const [expanded, setExpanded] = useState(false);
  const eligible = citizen.income < 20000 && citizen.fraud_risk < 0.5;

  return (
    <div
      className={`citizen-card ${expanded ? "expanded" : ""}`}
      style={{ animationDelay: `${idx * 60}ms` }}
      onClick={() => setExpanded((v) => !v)}
    >
      {/* top row */}
      <div className="card-top">
        <div className="avatar">
          {citizen.name.split(" ").map((w) => w[0]).join("").slice(0, 2)}
        </div>
        <div className="card-meta">
          <span className="card-name">{citizen.name}</span>
          <span className="card-region">{citizen.region}</span>
        </div>
        <span
          className="badge"
          style={{
            background: riskColor(citizen.fraud_risk) + "22",
            color: riskColor(citizen.fraud_risk),
            border: `1px solid ${riskColor(citizen.fraud_risk)}55`,
          }}
        >
          {riskLabel(citizen.fraud_risk)}
        </span>
      </div>

      {/* collapsed preview */}
      <div className="card-preview">
        <RiskMeter value={citizen.fraud_risk} />
      </div>

      {/* expanded details */}
      {expanded && (
        <div className="card-details">
          <div className="detail-row">
            <span>Income</span>
            <span className="detail-val">{fmt(citizen.income)}</span>
          </div>
          <div className="detail-row">
            <span>Fraud Score</span>
            <span className="detail-val" style={{ color: riskColor(citizen.fraud_risk) }}>
              {citizen.fraud_risk.toFixed(2)}
            </span>
          </div>
          <div className="detail-row">
            <span>Eligibility</span>
            <span
              className="detail-val"
              style={{ color: eligible ? "var(--green)" : "var(--red)" }}
            >
              {eligible ? "✓ Eligible" : "✗ Not Eligible"}
            </span>
          </div>
          <div className="detail-row">
            <span>ID</span>
            <span className="detail-val mono">#{String(citizen.id).padStart(5, "0")}</span>
          </div>
        </div>
      )}
    </div>
  );
}

// ── main ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [citizens, setCitizens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [search, setSearch] = useState("");
  const [filterRisk, setFilterRisk] = useState("all");
  const [formOpen, setFormOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const toastTimer = useRef(null);

  const [formData, setFormData] = useState({
    name: "", income: "", fraud_risk: "", region: "",
  });

  useEffect(() => { fetchCitizens(); }, []);

  const notify = (msg, type = "success") => {
    clearTimeout(toastTimer.current);
    setToast({ msg, type });
    toastTimer.current = setTimeout(() => setToast(null), 3200);
  };

  const fetchCitizens = async () => {
    setLoading(true);
    try {
      const { data } = await axios.get(`${API}/citizens`);
      setCitizens(data);
    } catch {
      notify("Could not reach backend.", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) =>
    setFormData((p) => ({ ...p, [e.target.name]: e.target.value }));

  const addCitizen = async () => {
    if (!formData.name || !formData.income || !formData.fraud_risk || !formData.region) {
      notify("All fields are required.", "error");
      return;
    }
    setSubmitting(true);
    try {
      await axios.post(`${API}/citizens`, {
        name: formData.name,
        income: parseFloat(formData.income),
        fraud_risk: parseFloat(formData.fraud_risk),
        region: formData.region,
      });
      await fetchCitizens();
      setFormData({ name: "", income: "", fraud_risk: "", region: "" });
      setFormOpen(false);
      notify("Citizen record added.");
    } catch {
      notify("Failed to add citizen.", "error");
    } finally {
      setSubmitting(false);
    }
  };

  // derived
  const filtered = citizens.filter((c) => {
    const q = search.toLowerCase();
    const matchSearch =
      c.name.toLowerCase().includes(q) || c.region.toLowerCase().includes(q);
    const matchRisk =
      filterRisk === "all" ? true :
      filterRisk === "critical" ? c.fraud_risk > 0.7 :
      filterRisk === "elevated" ? c.fraud_risk > 0.4 && c.fraud_risk <= 0.7 :
      c.fraud_risk <= 0.4;
    return matchSearch && matchRisk;
  });

  const highRisk = citizens.filter((c) => c.fraud_risk > 0.7).length;
  const eligible = citizens.filter((c) => c.income < 20000 && c.fraud_risk < 0.5).length;
  const avgIncome = citizens.length
    ? citizens.reduce((s, c) => s + c.income, 0) / citizens.length
    : 0;

  return (
    <>
      {/* ── global styles ── */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
          --bg:       #080b10;
          --surface:  #0d1117;
          --surface2: #111827;
          --border:   #1f2937;
          --border2:  #374151;
          --text:     #c9d1d9;
          --muted:    #6b7280;
          --heading:  #f0f6fc;
          --green:    #3fba74;
          --amber:    #f59e0b;
          --red:      #f87171;
          --blue:     #60a5fa;
          --accent:   #7c3aed;
          --accent2:  #a78bfa;
          font-family: 'Syne', sans-serif;
        }

        body { background: var(--bg); color: var(--text); min-height: 100vh; overflow-x: hidden; }

        /* ── layout ── */
        .shell { display: flex; flex-direction: column; min-height: 100vh; }

        /* ── navbar ── */
        .nav {
          display: flex; align-items: center; justify-content: space-between;
          padding: 0 40px; height: 64px;
          background: #0d111788; backdrop-filter: blur(12px);
          border-bottom: 1px solid var(--border);
          position: sticky; top: 0; z-index: 100;
        }
        .nav-brand {
          display: flex; align-items: center; gap: 12px;
          font-size: 18px; font-weight: 800; color: var(--heading); letter-spacing: -0.5px;
        }
        .nav-brand .dot {
          width: 10px; height: 10px; border-radius: 50%;
          background: var(--accent2); box-shadow: 0 0 10px var(--accent2);
          animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

        .nav-right { display: flex; align-items: center; gap: 12px; }

        .nav-tag {
          font-family: 'JetBrains Mono', monospace;
          font-size: 11px; letter-spacing: 1px; text-transform: uppercase;
          background: var(--accent)22; color: var(--accent2);
          border: 1px solid var(--accent)55; border-radius: 4px; padding: 4px 10px;
        }

        /* ── main content ── */
        .main { flex: 1; padding: 40px; max-width: 1400px; margin: 0 auto; width: 100%; }

        /* ── section heading ── */
        .section-head {
          display: flex; align-items: baseline; gap: 16px; margin-bottom: 24px;
        }
        .section-head h2 {
          font-size: 13px; font-weight: 700; letter-spacing: 2.5px;
          text-transform: uppercase; color: var(--muted);
        }
        .section-head .line { flex: 1; height: 1px; background: var(--border); }

        /* ── stat cards ── */
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 48px; }
        @media(max-width:900px){ .stats{ grid-template-columns: repeat(2,1fr); } }
        @media(max-width:500px){ .stats{ grid-template-columns: 1fr; } }

        .stat-card {
          background: var(--surface); border: 1px solid var(--border);
          border-radius: 16px; padding: 24px; position: relative; overflow: hidden;
          transition: transform 0.2s, border-color 0.2s;
        }
        .stat-card:hover { transform: translateY(-2px); border-color: var(--accent-col, var(--accent)); }
        .stat-bar {
          position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
          background: var(--accent-col, var(--accent));
          box-shadow: 0 0 12px var(--accent-col, var(--accent));
        }
        .stat-label { display: block; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: var(--muted); margin-bottom: 12px; }
        .stat-value { display: block; font-size: 40px; font-weight: 800; color: var(--heading); line-height: 1; letter-spacing: -2px; margin-bottom: 8px; }
        .stat-sub { display: block; font-size: 12px; color: var(--muted); font-family: 'JetBrains Mono', monospace; }

        /* ── toolbar ── */
        .toolbar {
          display: flex; gap: 12px; align-items: center; flex-wrap: wrap;
          margin-bottom: 24px;
        }
        .search-wrap { position: relative; flex: 1; min-width: 200px; }
        .search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--muted); font-size: 14px; pointer-events: none; }
        .search-input {
          width: 100%; background: var(--surface); border: 1px solid var(--border);
          border-radius: 10px; padding: 10px 14px 10px 38px;
          color: var(--heading); font-family: 'Syne', sans-serif; font-size: 14px;
          outline: none; transition: border-color 0.2s;
        }
        .search-input::placeholder { color: var(--muted); }
        .search-input:focus { border-color: var(--accent); }

        .filter-btn {
          padding: 9px 16px; border-radius: 10px; border: 1px solid var(--border);
          background: var(--surface); color: var(--muted);
          font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 600;
          cursor: pointer; transition: all 0.2s; white-space: nowrap;
        }
        .filter-btn.active, .filter-btn:hover { border-color: var(--accent); color: var(--accent2); background: var(--accent)11; }

        .add-btn {
          display: flex; align-items: center; gap: 8px;
          padding: 10px 20px; border-radius: 10px; border: none;
          background: var(--accent); color: #fff;
          font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 700;
          cursor: pointer; transition: all 0.2s; white-space: nowrap;
        }
        .add-btn:hover { background: var(--accent2); transform: translateY(-1px); box-shadow: 0 8px 24px var(--accent)44; }

        /* ── form overlay ── */
        .overlay {
          position: fixed; inset: 0; z-index: 200;
          background: #000000aa; backdrop-filter: blur(6px);
          display: flex; align-items: center; justify-content: center;
          padding: 20px;
          animation: fadeIn 0.2s;
        }
        @keyframes fadeIn { from{opacity:0} to{opacity:1} }

        .form-panel {
          background: var(--surface); border: 1px solid var(--border2);
          border-radius: 20px; padding: 36px; width: 100%; max-width: 480px;
          animation: slideUp 0.25s cubic-bezier(.16,1,.3,1);
        }
        @keyframes slideUp { from{transform:translateY(24px);opacity:0} to{transform:none;opacity:1} }

        .form-title { font-size: 22px; font-weight: 800; color: var(--heading); margin-bottom: 28px; }

        .field { margin-bottom: 16px; }
        .field label { display: block; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }
        .field input {
          width: 100%; background: var(--bg); border: 1px solid var(--border);
          border-radius: 10px; padding: 11px 14px;
          color: var(--heading); font-family: 'Syne', sans-serif; font-size: 14px;
          outline: none; transition: border-color 0.2s;
        }
        .field input::placeholder { color: var(--muted); }
        .field input:focus { border-color: var(--accent); }

        .field-hint { font-size: 11px; color: var(--muted); margin-top: 6px; font-family: 'JetBrains Mono', monospace; }

        .form-actions { display: flex; gap: 12px; margin-top: 28px; }
        .btn-cancel {
          flex: 1; padding: 12px; border-radius: 10px;
          border: 1px solid var(--border2); background: transparent;
          color: var(--muted); font-family: 'Syne', sans-serif;
          font-size: 14px; font-weight: 600; cursor: pointer;
          transition: all 0.2s;
        }
        .btn-cancel:hover { border-color: var(--text); color: var(--text); }
        .btn-submit {
          flex: 2; padding: 12px; border-radius: 10px; border: none;
          background: var(--accent); color: #fff;
          font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 700;
          cursor: pointer; transition: all 0.2s;
        }
        .btn-submit:hover:not(:disabled) { background: var(--accent2); box-shadow: 0 8px 20px var(--accent)44; }
        .btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }

        /* ── citizen grid ── */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }

        .citizen-card {
          background: var(--surface); border: 1px solid var(--border);
          border-radius: 16px; padding: 20px; cursor: pointer;
          transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
          animation: cardIn 0.4s cubic-bezier(.16,1,.3,1) both;
        }
        @keyframes cardIn { from{transform:translateY(16px);opacity:0} to{transform:none;opacity:1} }
        .citizen-card:hover { transform: translateY(-3px); border-color: var(--border2); box-shadow: 0 12px 40px #00000055; }
        .citizen-card.expanded { border-color: var(--accent)66; }

        .card-top { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }

        .avatar {
          width: 44px; height: 44px; border-radius: 12px; flex-shrink: 0;
          background: linear-gradient(135deg, var(--accent), var(--blue));
          display: flex; align-items: center; justify-content: center;
          font-size: 15px; font-weight: 800; color: #fff; letter-spacing: 0.5px;
        }

        .card-meta { flex: 1; min-width: 0; }
        .card-name { display: block; font-size: 15px; font-weight: 700; color: var(--heading); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .card-region { display: block; font-size: 12px; color: var(--muted); margin-top: 2px; font-family: 'JetBrains Mono', monospace; }

        .badge { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; border-radius: 6px; padding: 4px 8px; white-space: nowrap; flex-shrink: 0; }

        /* ── risk meter ── */
        .risk-meter { position: relative; height: 6px; background: var(--border); border-radius: 99px; overflow: visible; }
        .risk-fill { height: 100%; border-radius: 99px; transition: width 0.6s cubic-bezier(.16,1,.3,1); }
        .risk-pct {
          position: absolute; right: 0; top: -20px;
          font-size: 11px; font-weight: 700; font-family: 'JetBrains Mono', monospace;
        }

        /* ── expanded details ── */
        .card-details {
          margin-top: 20px; border-top: 1px solid var(--border);
          padding-top: 16px; display: flex; flex-direction: column; gap: 10px;
          animation: fadeIn 0.2s;
        }
        .detail-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
        .detail-row span:first-child { color: var(--muted); }
        .detail-val { font-weight: 600; color: var(--heading); }
        .mono { font-family: 'JetBrains Mono', monospace; }

        /* ── empty ── */
        .empty {
          grid-column: 1/-1; text-align: center; padding: 80px 20px;
          color: var(--muted); font-size: 15px;
        }

        /* ── skeleton ── */
        .skel { background: linear-gradient(90deg, var(--surface) 25%, var(--surface2) 50%, var(--surface) 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 16px; height: 120px; }
        @keyframes shimmer { from{background-position:200% 0} to{background-position:-200% 0} }

        /* ── toast ── */
        .toast {
          position: fixed; bottom: 32px; right: 32px; z-index: 999;
          background: var(--surface2); border: 1px solid var(--border2);
          border-radius: 12px; padding: 14px 20px; font-size: 14px;
          display: flex; align-items: center; gap: 10px;
          box-shadow: 0 20px 60px #00000066;
          animation: slideToast 0.3s cubic-bezier(.16,1,.3,1);
        }
        @keyframes slideToast { from{transform:translateY(20px);opacity:0} to{transform:none;opacity:1} }
        .toast.success { border-left: 3px solid var(--green); }
        .toast.error { border-left: 3px solid var(--red); }
        .toast-icon { font-size: 16px; }

        /* ── count ── */
        .result-count { font-size: 12px; color: var(--muted); font-family: 'JetBrains Mono', monospace; margin-bottom: 16px; }
      `}</style>

      <div className="shell">
        {/* ── navbar ── */}
        <nav className="nav">
          <div className="nav-brand">
            <div className="dot" />
            GovAI
            <span style={{ fontWeight: 400, color: "var(--muted)", fontSize: 14 }}>/ Dashboard</span>
          </div>
          <div className="nav-right">
            <span className="nav-tag">v2.0</span>
          </div>
        </nav>

        <main className="main">
          {/* ── stats ── */}
          <div className="section-head">
            <h2>Overview</h2><div className="line" />
          </div>
          <div className="stats">
            <StatCard
              label="Total Citizens"
              value={citizens.length}
              sub="in database"
              accent="var(--blue)"
            />
            <StatCard
              label="High Risk Cases"
              value={highRisk}
              sub={`${citizens.length ? ((highRisk / citizens.length) * 100).toFixed(1) : 0}% of total`}
              accent="var(--red)"
            />
            <StatCard
              label="Eligible Citizens"
              value={eligible}
              sub="income < ₹20k & risk < 50%"
              accent="var(--green)"
            />
            <StatCard
              label="Avg. Income"
              value={fmt(avgIncome)}
              sub="across all records"
              accent="var(--amber)"
            />
          </div>

          {/* ── toolbar ── */}
          <div className="section-head">
            <h2>Records</h2><div className="line" />
          </div>
          <div className="toolbar">
            <div className="search-wrap">
              <span className="search-icon">⌕</span>
              <input
                className="search-input"
                placeholder="Search by name or region…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            {["all", "critical", "elevated", "clear"].map((f) => (
              <button
                key={f}
                className={`filter-btn ${filterRisk === f ? "active" : ""}`}
                onClick={() => setFilterRisk(f)}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}

            <button className="add-btn" onClick={() => setFormOpen(true)}>
              + Add Citizen
            </button>
          </div>

          {/* result count */}
          <p className="result-count">
            Showing {filtered.length} of {citizens.length} records
          </p>

          {/* ── grid ── */}
          <div className="grid">
            {loading
              ? Array.from({ length: 6 }).map((_, i) => <div key={i} className="skel" />)
              : filtered.length === 0
              ? <div className="empty">No matching records found.</div>
              : filtered.map((c, i) => (
                  <CitizenCard key={c.id} citizen={c} idx={i} />
                ))}
          </div>
        </main>
      </div>

      {/* ── add form overlay ── */}
      {formOpen && (
        <div className="overlay" onClick={(e) => e.target === e.currentTarget && setFormOpen(false)}>
          <div className="form-panel">
            <h2 className="form-title">Register Citizen</h2>

            <div className="field">
              <label>Full Name</label>
              <input name="name" placeholder="e.g. Priya Sharma" value={formData.name} onChange={handleChange} />
            </div>

            <div className="field">
              <label>Annual Income (₹)</label>
              <input name="income" type="number" placeholder="e.g. 18000" value={formData.income} onChange={handleChange} />
              <p className="field-hint">Threshold for eligibility: ₹20,000</p>
            </div>

            <div className="field">
              <label>Fraud Risk Score</label>
              <input name="fraud_risk" type="number" step="0.01" min="0" max="1" placeholder="0.00 – 1.00" value={formData.fraud_risk} onChange={handleChange} />
              <p className="field-hint">0 = no risk · 0.5 = elevated · 0.7+ = critical</p>
            </div>

            <div className="field">
              <label>Region</label>
              <input name="region" placeholder="e.g. Karnataka" value={formData.region} onChange={handleChange} />
            </div>

            <div className="form-actions">
              <button className="btn-cancel" onClick={() => setFormOpen(false)}>Cancel</button>
              <button className="btn-submit" onClick={addCitizen} disabled={submitting}>
                {submitting ? "Saving…" : "Register Citizen"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── toast ── */}
      {toast && (
        <div className={`toast ${toast.type}`}>
          <span className="toast-icon">{toast.type === "success" ? "✓" : "✕"}</span>
          {toast.msg}
        </div>
      )}
    </>
  );
}
