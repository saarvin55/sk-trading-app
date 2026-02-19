"""
SK Capitalz Trading (SK)
No Emotions, Just Charts

HOME:
- Premium Month Calendar
- Green = profit day, Red = loss day, Neutral = no trades / zero
- Month summary: Total Trades, Total Profit, Total Loss, Month P/L
- Tap a day -> premium popup with FULL day details (trades + entries)

Add Trade:
- Enter P/L per entry -> auto totals

Manage Trades:
- Edit / Lock / Delete

Data stored in trades.db (rewriting code will NOT remove your trades).
"""

from __future__ import annotations

import sqlite3
import calendar as pycal
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

DB_PATH = "trades.db"
APP_SHORT_NAME = "SK"
APP_TITLE = "SK Capitalz Trading"
APP_TAGLINE = "No Emotions, Just Charts"


# =========================
# Page + Premium CSS
# =========================
st.set_page_config(page_title=APP_SHORT_NAME, layout="wide")

st.markdown(
    """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {padding-top: 1.0rem; padding-bottom: 1.2rem; max-width: 1480px;}

.sk-title {text-align:center; font-weight: 950; letter-spacing: 0.6px; margin-bottom: 0.15rem;}
.sk-tagline {text-align:center; font-size: 1.02rem; font-weight: 780; opacity: 0.78; margin-top: 0;}
.sk-divider {margin: 0.85rem 0 1.05rem 0; opacity: 0.22;}

.kpi-label {font-size: 0.86rem; opacity: 0.72; font-weight: 850;}
.kpi-value {font-size: 1.55rem; font-weight: 980; letter-spacing: 0.2px; margin-top: 3px;}
.kpi-chip {display:inline-block; padding: 3px 10px; border-radius: 999px; font-size: 0.78rem; font-weight: 950; opacity: 0.95;}
.chip-green {background: rgba(0,255,140,0.14); border: 1px solid rgba(0,255,140,0.28);}
.chip-red {background: rgba(255,80,80,0.14); border: 1px solid rgba(255,80,80,0.28);}
.chip-neutral {background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12);}

.cal-grid {display:grid; grid-template-columns: repeat(7, 1fr); gap: 12px;}
.cal-head {font-weight: 950; text-align:center; padding: 6px 0; opacity: 0.72; letter-spacing: 0.4px;}

.cal-card{
  border-radius: 16px;
  min-height: 112px;
  padding: 12px 12px 10px 12px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.02);
  position: relative;
}

.cal-empty{
  border-radius: 16px;
  min-height: 112px;
  border: 1px dashed rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.01);
  opacity: 0.16;
}

.cal-profit{
  border: 1px solid rgba(0,255,140,0.40) !important;
  background: radial-gradient(1200px 160px at 10% 10%, rgba(0,255,140,0.20), rgba(255,255,255,0.02)) !important;
  box-shadow: inset 0 0 0 1px rgba(0,255,140,0.12) !important;
}

.cal-loss{
  border: 1px solid rgba(255,80,80,0.42) !important;
  background: radial-gradient(1200px 160px at 10% 10%, rgba(255,80,80,0.18), rgba(255,255,255,0.02)) !important;
  box-shadow: inset 0 0 0 1px rgba(255,80,80,0.12) !important;
}

.cal-neutral{
  border: 1px solid rgba(255,255,255,0.10) !important;
  background: rgba(255,255,255,0.02) !important;
}

.cal-today{
  outline: 2px solid rgba(212,175,55,0.62);
  outline-offset: 2px;
}

.cal-daynum{
  font-weight: 980;
  font-size: 18px;
  opacity: 0.95;
}

.cal-pnl{
  margin-top: 16px;
  font-weight: 980;
  font-size: 16px;
}

.cal-trades{
  position: absolute;
  right: 12px;
  bottom: 10px;
  font-size: 12px;
  opacity: 0.68;
  font-weight: 900;
}

.cal-btn > button{
  width: 100%;
  border-radius: 16px !important;
  padding: 0px !important;
  min-height: 112px !important;
  background: transparent !important;
  border: none !important;
}

.cal-btn > button:hover{filter: brightness(1.06);}
.cal-btn > button:active{transform: scale(0.995);}

.modal-wrap{
  padding: 6px 2px 2px 2px;
}
.modal-kpis{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}
.modal-card{
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.02);
  padding: 10px;
}
.modal-k{font-size: 12px; opacity: 0.70; font-weight: 850;}
.modal-v{font-size: 16px; font-weight: 980; margin-top: 4px; white-space: nowrap;}

.trade-card{
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.02);
  padding: 12px;
  margin-bottom: 12px;
}
.trade-top{
  display:flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
}
.trade-title{
  font-weight: 950;
  font-size: 15px;
}
.trade-sub{
  opacity: 0.72;
  font-size: 12px;
  font-weight: 800;
  margin-top: 3px;
}
.trade-total{
  font-weight: 980;
  font-size: 16px;
  white-space: nowrap;
}
.entry-row{
  display:flex;
  justify-content: space-between;
  gap: 10px;
  border-top: 1px solid rgba(255,255,255,0.07);
  padding: 8px 0;
}
.entry-left{
  font-weight: 900;
  opacity: 0.85;
}
.entry-right{
  font-weight: 980;
  white-space: nowrap;
}
.green{color:#00ff8c;}
.red{color:#ff5050;}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<h1 class="sk-title" style="color:#D4AF37;">{APP_TITLE}</h1>
<p class="sk-tagline">{APP_TAGLINE}</p>
<hr class="sk-divider"/>
""",
    unsafe_allow_html=True,
)


# =========================
# Database
# =========================
def get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            direction TEXT NOT NULL,
            base_lot REAL,
            created_at TEXT NOT NULL,
            locked_at TEXT,
            deleted_at TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS trade_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id INTEGER NOT NULL,
            entry_no INTEGER NOT NULL,
            entry_pnl REAL NOT NULL,
            FOREIGN KEY(trade_id) REFERENCES trades(id)
        )
        """
    )

    conn.commit()
    conn.close()


def clear_cache() -> None:
    fetch_trades.clear()
    fetch_entries.clear()
    trade_total.clear()


@st.cache_data(show_spinner=False)
def fetch_trades() -> List[dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM trades WHERE deleted_at IS NULL ORDER BY trade_date DESC, id DESC")
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]


@st.cache_data(show_spinner=False)
def fetch_entries(trade_id: int) -> List[dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, entry_no, entry_pnl
        FROM trade_entries
        WHERE trade_id = ?
        ORDER BY entry_no ASC
        """,
        (trade_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "entry_no": r[1], "entry_pnl": float(r[2])} for r in rows]


@st.cache_data(show_spinner=False)
def trade_total(trade_id: int) -> float:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(entry_pnl), 0) FROM trade_entries WHERE trade_id = ?", (trade_id,))
    total = cur.fetchone()[0]
    conn.close()
    return float(total)


def add_trade(trade_date: str, symbol: str, direction: str, base_lot: Optional[float], entry_pnls: List[float]) -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO trades (trade_date, symbol, direction, base_lot, created_at, locked_at, deleted_at)
        VALUES (?, ?, ?, ?, ?, NULL, NULL)
        """,
        (trade_date, symbol, direction, base_lot, now_iso()),
    )
    tid = cur.lastrowid

    cur.executemany(
        """
        INSERT INTO trade_entries (trade_id, entry_no, entry_pnl)
        VALUES (?, ?, ?)
        """,
        [(tid, i + 1, float(p)) for i, p in enumerate(entry_pnls)],
    )

    conn.commit()
    conn.close()
    clear_cache()


def update_trade(
    trade_id: int,
    trade_date: str,
    symbol: str,
    direction: str,
    base_lot: Optional[float],
    entry_pnls: List[float],
) -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE trades
        SET trade_date = ?, symbol = ?, direction = ?, base_lot = ?
        WHERE id = ? AND deleted_at IS NULL
        """,
        (trade_date, symbol, direction, base_lot, trade_id),
    )

    cur.execute("DELETE FROM trade_entries WHERE trade_id = ?", (trade_id,))
    cur.executemany(
        """
        INSERT INTO trade_entries (trade_id, entry_no, entry_pnl)
        VALUES (?, ?, ?)
        """,
        [(trade_id, i + 1, float(p)) for i, p in enumerate(entry_pnls)],
    )

    conn.commit()
    conn.close()
    clear_cache()


def soft_delete_trade(trade_id: int) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE trades SET deleted_at = ? WHERE id = ? AND deleted_at IS NULL", (now_iso(), trade_id))
    conn.commit()
    conn.close()
    clear_cache()


def lock_trade(trade_id: int) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE trades SET locked_at = ? WHERE id = ? AND locked_at IS NULL AND deleted_at IS NULL",
        (now_iso(), trade_id),
    )
    conn.commit()
    conn.close()
    clear_cache()


def unlock_trade(trade_id: int) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE trades SET locked_at = NULL WHERE id = ? AND deleted_at IS NULL", (trade_id,))
    conn.commit()
    conn.close()
    clear_cache()


# =========================
# Helpers
# =========================
def format_money(x: float) -> str:
    sign = "+" if x > 0 else ""
    return f"{sign}${x:,.2f}"


def safe_float(text: str) -> Optional[float]:
    t = (text or "").strip()
    if not t:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def build_daily_map(trades: List[dict]) -> Dict[str, Dict[str, float]]:
    m: Dict[str, Dict[str, float]] = {}
    for t in trades:
        d = t["trade_date"]
        pnl = float(trade_total(t["id"]))
        if d not in m:
            m[d] = {"pnl": 0.0, "trades": 0}
        m[d]["pnl"] += pnl
        m[d]["trades"] += 1
    return m


def month_stats(trades: List[dict], month_start: date) -> Tuple[int, float, float, float]:
    prefix = month_start.strftime("%Y-%m-")
    month_trades = [t for t in trades if t["trade_date"].startswith(prefix)]

    total_trades = len(month_trades)
    total_profit = 0.0
    total_loss = 0.0

    for t in month_trades:
        tt = float(trade_total(t["id"]))
        if tt > 0:
            total_profit += tt
        elif tt < 0:
            total_loss += tt

    month_pnl = total_profit + total_loss
    return total_trades, total_profit, total_loss, month_pnl


def kpi_card(label: str, value: str, chip_text: str, chip_kind: str) -> None:
    chip_class = "chip-neutral"
    if chip_kind == "green":
        chip_class = "chip-green"
    elif chip_kind == "red":
        chip_class = "chip-red"

    st.markdown(
        f"""
<div>
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{value}</div>
  <span class="kpi-chip {chip_class}">{chip_text}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def pnl_class(x: float) -> str:
    if x > 0:
        return "green"
    if x < 0:
        return "red"
    return ""


# =========================
# Premium Day Popup (scrollable + full details)
# =========================
@st.dialog("Day Details", width="large")
def day_popup(day_str: str, trades: List[dict]) -> None:
    day_trades = [t for t in trades if t["trade_date"] == day_str]
    st.markdown(f"### {day_str}")

    if not day_trades:
        st.info("No trades on this date.")
        return

    # Totals
    profit = 0.0
    loss = 0.0
    net = 0.0
    for t in day_trades:
        tt = float(trade_total(t["id"]))
        net += tt
        if tt > 0:
            profit += tt
        elif tt < 0:
            loss += tt

    # KPIs in compact HTML so it won't truncate
    st.markdown(
        f"""
<div class="modal-wrap">
  <div class="modal-kpis">
    <div class="modal-card"><div class="modal-k">Total Trades</div><div class="modal-v">{len(day_trades)}</div></div>
    <div class="modal-card"><div class="modal-k">Total Profit</div><div class="modal-v green">{format_money(profit)}</div></div>
    <div class="modal-card"><div class="modal-k">Total Loss</div><div class="modal-v red">{format_money(loss)}</div></div>
    <div class="modal-card"><div class="modal-k">Net P/L</div><div class="modal-v {pnl_class(net)}">{format_money(net)}</div></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.divider()

    # Trade cards
    for t in day_trades:
        tt = float(trade_total(t["id"]))
        entries = fetch_entries(t["id"])
        entries_count = len(entries)
        base_lot_txt = "" if t.get("base_lot") is None else f"Base Lot: {t['base_lot']}"
        created_txt = (t.get("created_at") or "").replace("T", " ")
        locked_txt = "Yes" if t.get("locked_at") else "No"

        st.markdown(
            f"""
<div class="trade-card">
  <div class="trade-top">
    <div>
      <div class="trade-title">Trade {t['id']} • {t['symbol']} • {t['direction']} • Entries: {entries_count}</div>
      <div class="trade-sub">{base_lot_txt}</div>
      <div class="trade-sub">Created: {created_txt} • Locked: {locked_txt}</div>
    </div>
    <div class="trade-total {pnl_class(tt)}">{format_money(tt)}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        # Entries list
        if entries_count == 0:
            st.info("No entries for this trade.")
        else:
            for e in entries:
                p = float(e["entry_pnl"])
                st.markdown(
                    f"""
<div class="entry-row">
  <div class="entry-left">Entry {int(e["entry_no"])}</div>
  <div class="entry-right {pnl_class(p)}">{format_money(p)}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


# =========================
# App start
# =========================
init_db()
trades = fetch_trades()
daily_map = build_daily_map(trades)

tab_home, tab_add, tab_manage = st.tabs(["Home", "Add Trade", "Manage Trades"])


# =========================
# HOME (Calendar + KPIs + click -> modal)
# =========================
with tab_home:
    st.subheader("Calendar")

    if "cal_month" not in st.session_state:
        st.session_state.cal_month = date.today().replace(day=1)

    month_start: date = st.session_state.cal_month

    nav1, _, nav3 = st.columns([1, 2, 1])
    with nav1:
        if st.button("◀ Prev Month", use_container_width=True):
            st.session_state.cal_month = (month_start.replace(day=1) - timedelta(days=1)).replace(day=1)
            st.rerun()

    with nav3:
        if st.button("Next Month ▶", use_container_width=True):
            st.session_state.cal_month = (month_start + timedelta(days=32)).replace(day=1)
            st.rerun()

    # Month KPIs
    total_trades, total_profit, total_loss, month_pnl = month_stats(trades, month_start)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card("Total Trades (Month)", f"{total_trades}", "Trades", "neutral")
    with k2:
        kpi_card("Total Profit (Month)", format_money(total_profit), "Profit", "green")
    with k3:
        kpi_card("Total Loss (Month)", format_money(total_loss), "Loss", "red")
    with k4:
        kind = "green" if month_pnl > 0 else ("red" if month_pnl < 0 else "neutral")
        kpi_card("P/L (Month)", format_money(month_pnl), "Net", kind)

    st.markdown(f"### {month_start.strftime('%B %Y')}")

    pycal.setfirstweekday(pycal.MONDAY)
    weeks = pycal.monthcalendar(month_start.year, month_start.month)
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    header_html = '<div class="cal-grid">' + "".join([f'<div class="cal-head">{d}</div>' for d in weekdays]) + "</div>"
    st.markdown(header_html, unsafe_allow_html=True)

    today_str = date.today().strftime("%Y-%m-%d")

    # calendar rows
    for week in weeks:
        cols = st.columns(7, gap="small")

        for idx, day_num in enumerate(week):
            with cols[idx]:
                if day_num == 0:
                    st.markdown('<div class="cal-empty"></div>', unsafe_allow_html=True)
                    continue

                d_obj = date(month_start.year, month_start.month, day_num)
                d_str = d_obj.strftime("%Y-%m-%d")

                v = daily_map.get(d_str)
                trades_count = int(v["trades"]) if v else 0
                pnl_val = float(v["pnl"]) if v else 0.0
                has_trades = trades_count > 0

                cls = "cal-neutral"
                if has_trades:
                    cls = "cal-profit" if pnl_val > 0 else ("cal-loss" if pnl_val < 0 else "cal-neutral")

                today_extra = " cal-today" if d_str == today_str else ""

                # draw card content INSIDE the button (no floating overlay = no ghost)
                pnl_txt = format_money(pnl_val)
                pnl_color = "green" if pnl_val > 0 else ("red" if pnl_val < 0 else "")
                trades_txt = f"{trades_count} trade" + ("s" if trades_count != 1 else "")

                if not has_trades:
                    pnl_line = ""
                    trades_line = ""
                else:
                    pnl_line = f'<div class="cal-pnl {pnl_color}">{pnl_txt}</div>'
                    trades_line = f'<div class="cal-trades">{trades_txt}</div>'

                card_html = f"""
<div class="cal-card {cls}{today_extra}">
  <div class="cal-daynum">{day_num}</div>
  {pnl_line}
  {trades_line}
</div>
"""

                # Button acts like clickable cell, but shows ONLY our HTML content
                clicked = st.button("", key=f"open_{d_str}", use_container_width=True, help=d_str)
                st.markdown(f'<div class="cal-btn">{card_html}</div>', unsafe_allow_html=True)

                # Trick: button is invisible overlay; HTML is what you see
                # On click -> open popup
                if clicked:
                    day_popup(d_str, trades)

    st.divider()
    st.caption("skcapitalztrading @ 2026")


# =========================
# ADD TRADE
# =========================
with tab_add:
    st.subheader("Add Trade")
    st.caption("Enter P/L for each entry (negative = loss). Total is calculated automatically.")

    left, right = st.columns([1, 1])
    with left:
        trade_date = st.date_input("Date", value=date.today())
        symbol = st.text_input("Symbol", value="XAUUSD").strip().upper() or "XAUUSD"
        direction = st.selectbox("Direction", ["Buy", "Sell"])
        base_lot_str = st.text_input("Base Lot (optional)", value="0.01")
        base_lot_val = safe_float(base_lot_str)
        if base_lot_str.strip() and base_lot_val is None:
            st.warning("Base Lot must be a number like 0.01 (or leave blank).")
        entries_count = st.number_input("Number of entries", min_value=1, max_value=50, value=4, step=1)

    with right:
        entry_pnls: List[float] = []
        running_total = 0.0
        st.markdown("### Entry P/L Lines")
        for i in range(int(entries_count)):
            val = st.number_input(
                f"Entry {i+1} P/L ($)",
                value=0.0,
                step=0.5,
                format="%.2f",
                key=f"add_entry_{i}",
            )
            entry_pnls.append(float(val))
            running_total += float(val)

        st.markdown("### Trade Total")
        st.metric("Total", format_money(running_total))

    if st.button("✅ Save Trade", use_container_width=True):
        add_trade(trade_date.strftime("%Y-%m-%d"), symbol, direction, base_lot_val, entry_pnls)
        st.success("Saved!")
        st.rerun()


# =========================
# MANAGE TRADES
# =========================
with tab_manage:
    st.subheader("Manage Trades")

    if not trades:
        st.info("No trades to manage yet.")
    else:
        trade_ids = [t["id"] for t in trades]
        trade_id = st.selectbox("Select Trade ID", trade_ids)

        selected_trade = next(t for t in trades if t["id"] == trade_id)
        entries = fetch_entries(trade_id)
        current_total = sum(float(e["entry_pnl"]) for e in entries)
        can_edit = selected_trade["locked_at"] is None

        st.markdown(
            f"**Trade {trade_id}** | Date: {selected_trade['trade_date']} | "
            f"{selected_trade['symbol']} | {selected_trade['direction']} | "
            f"Total: {format_money(current_total)} | Locked: {'Yes' if selected_trade['locked_at'] else 'No'}"
        )

        edit_col, action_col = st.columns([2, 1])

        with edit_col:
            st.markdown("### Edit Trade")

            new_date = st.date_input(
                "Date",
                value=datetime.strptime(selected_trade["trade_date"], "%Y-%m-%d").date(),
                key="edit_date",
                disabled=not can_edit,
            )
            new_symbol = st.text_input(
                "Symbol",
                value=selected_trade["symbol"],
                key="edit_symbol",
                disabled=not can_edit,
            )
            new_dir = st.selectbox(
                "Direction",
                ["Buy", "Sell"],
                index=0 if selected_trade["direction"] == "Buy" else 1,
                key="edit_dir",
                disabled=not can_edit,
            )
            new_base_lot_str = st.text_input(
                "Base Lot (optional)",
                value="" if selected_trade["base_lot"] is None else str(selected_trade["base_lot"]),
                key="edit_lot",
                disabled=not can_edit,
            )
            new_base_lot = safe_float(new_base_lot_str)
            if new_base_lot_str.strip() and new_base_lot is None and can_edit:
                st.warning("Base Lot must be a number like 0.01 (or leave blank).")

            new_count = st.number_input(
                "Entries count",
                min_value=1,
                max_value=50,
                value=len(entries),
                step=1,
                key="edit_count",
                disabled=not can_edit,
            )

            new_entry_pnls: List[float] = []
            running = 0.0
            for i in range(int(new_count)):
                default_val = float(entries[i]["entry_pnl"]) if i < len(entries) else 0.0
                v = st.number_input(
                    f"Entry {i+1} P/L ($)",
                    value=float(default_val),
                    step=0.5,
                    format="%.2f",
                    key=f"edit_entry_{i}",
                    disabled=not can_edit,
                )
                new_entry_pnls.append(float(v))
                running += float(v)

            st.metric("New Total", format_money(running))

            if st.button("💾 Save Changes", disabled=not can_edit, use_container_width=True):
                update_trade(
                    trade_id,
                    new_date.strftime("%Y-%m-%d"),
                    (new_symbol.strip().upper() or "XAUUSD"),
                    new_dir,
                    new_base_lot,
                    new_entry_pnls,
                )
                st.success("Updated!")
                st.rerun()

        with action_col:
            st.markdown("### Actions")

            if selected_trade["locked_at"] is None:
                if st.button("🔒 Lock Trade", use_container_width=True):
                    lock_trade(trade_id)
                    st.success("Locked.")
                    st.rerun()
            else:
                if st.button("🔓 Unlock Trade", use_container_width=True):
                    unlock_trade(trade_id)
                    st.success("Unlocked.")
                    st.rerun()

            st.divider()

            if st.button("🗑 Delete Trade", use_container_width=True):
                soft_delete_trade(trade_id)
                st.success("Deleted.")
                st.rerun()

st.caption("ENGINEERED BY SAARVIN KUMAR")
