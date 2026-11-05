
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# -------------------------------
# AUDITMASTER SECURITY DASHBOARD
# -------------------------------

st.set_page_config(
    page_title="AuditMaster Security Dashboard",
    page_icon="🛡️",
    layout="wide"
)

PROMETHEUS_URL = "http://192.168.56.11:9090"

st.title("🛡️ AuditMaster Security Dashboard")
st.caption("Centralized Linux Security Auditing and Monitoring Platform")

st.sidebar.title("Dashboard Settings")
PROMETHEUS_URL = st.sidebar.text_input(
    "Prometheus URL",
    PROMETHEUS_URL
)

refresh = st.sidebar.selectbox(
    "Refresh Interval",
    ["Off", "10 seconds", "30 seconds"]
)

def query_prometheus(query):
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        if data["status"] == "success":
            return data["data"]["result"]
    except Exception:
        return []

    return []


def query_range(query):
    try:
        end = time.time()
        start = end - 300

        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query_range",
            params={
                "query": query,
                "start": start,
                "end": end,
                "step": "15s"
            },
            timeout=10
        )
        response.raise_for_status()

        return response.json()["data"]["result"]
    except Exception:
        return []


def get_value(query):
    result = query_prometheus(query)

    if result:
        return float(result[0]["value"][1])

    return None


def show_status(title, query):
    value = get_value(query)

    if value is None:
        st.metric(title, "No Data")
    elif value == 1:
        st.metric(title, "ACTIVE")
    else:
        st.metric(title, "INACTIVE")


def show_chart(title, query, suffix=""):
    result = query_range(query)

    if not result:
        st.warning(f"{title}: No data available")
        return

    rows = []

    for series in result:
        for timestamp, value in series["values"]:
            try:
                rows.append({
                    "Time": pd.to_datetime(
                        float(timestamp), unit="s"
                    ),
                    "Value": float(value),
                    "Series": series.get("metric", {}).get(
                        "device", "System"
                    )
                })
            except (ValueError, TypeError):
                continue

    if rows:
        df = pd.DataFrame(rows)

        fig = px.line(
            df,
            x="Time",
            y="Value",
            color="Series",
            title=title
        )

        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=50, b=10)
        )

        if suffix:
            fig.update_yaxes(title=suffix)

        st.plotly_chart(fig, use_container_width=True)


# -------------------------------
# CONNECTION STATUS
# -------------------------------

connection = query_prometheus("up")

if connection:
    st.success("Prometheus Connected")
else:
    st.error(
        "Prometheus connection failed. "
        "Check whether your Ubuntu VM is running."
    )

st.divider()

# -------------------------------
# SECURITY SERVICES
# -------------------------------

st.header("🔐 Security Services Status")

c1, c2 = st.columns(2)

with c1:
    show_status(
        "Auditd Service",
        "auditmaster_auditd_status"
    )

with c2:
    show_status(
        "Samba Service",
        "auditmaster_samba_status"
    )

st.divider()

# -------------------------------
# DEPARTMENT PERMISSIONS
# -------------------------------

st.header("🏢 Department Folder Permissions")

departments = query_prometheus(
    "auditmaster_department_permission_status"
)

if departments:
    rows = []

    for item in departments:
        labels = item.get("metric", {})
        value = float(item["value"][1])

        rows.append({
            "Department": labels.get("department", "Unknown"),
            "Permission Status": (
                "Correct" if value == 1 else "Check Required"
            ),
            "Value": value
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Department permission metrics unavailable")

st.divider()

# -------------------------------
# SYSTEM MONITORING
# -------------------------------

st.header("📊 System Monitoring")

cpu_query = (
    '100 - (avg by (instance) '
    '(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
)

memory_query = (
    '100 * (1 - (node_memory_MemAvailable_bytes / '
    'node_memory_MemTotal_bytes))'
)

disk_query = (
    '100 * (1 - (node_filesystem_avail_bytes'
    '{mountpoint="/",fstype!="rootfs"} / '
    'node_filesystem_size_bytes'
    '{mountpoint="/",fstype!="rootfs"}))'
)

uptime_query = "(time() - node_boot_time_seconds) / 3600"

a, b, c, d = st.columns(4)

with a:
    value = get_value(cpu_query)
    st.metric("CPU Usage", f"{value:.2f}%" if value is not None else "No Data")

with b:
    value = get_value(memory_query)
    st.metric("Memory Usage", f"{value:.2f}%" if value is not None else "No Data")

with c:
    value = get_value(disk_query)
    st.metric("Disk Usage", f"{value:.2f}%" if value is not None else "No Data")

with d:
    value = get_value(uptime_query)
    st.metric("System Uptime", f"{value:.2f} hrs" if value is not None else "No Data")

st.divider()

# -------------------------------
# PERFORMANCE GRAPHS
# -------------------------------

st.header("📈 Performance Monitoring")

show_chart("CPU Usage", cpu_query, "%")
show_chart("Memory Usage", memory_query, "%")
show_chart("Disk Usage", disk_query, "%")

st.divider()

# -------------------------------
# NETWORK MONITORING
# -------------------------------

st.header("🌐 Network Traffic")

col1, col2 = st.columns(2)

with col1:
    show_chart(
        "Network Receive Traffic",
        'rate(node_network_receive_bytes_total{device!="lo"}[5m])',
        "Bytes/sec"
    )

with col2:
    show_chart(
        "Network Transmit Traffic",
        'rate(node_network_transmit_bytes_total{device!="lo"}[5m])',
        "Bytes/sec"
    )

st.divider()

# -------------------------------
# SECURITY MONITORING NOTES
# -------------------------------

st.header("🛡️ Additional Security Controls")

st.info(
    "Auditd monitors file activity. "
    "AIDE provides file integrity checking. "
    "Disk quota enforces storage limits. "
    "Ansible automates security configuration."
)

st.caption(
    "Note: AIDE scan results and disk quota usage "
    "are not yet exported as Prometheus metrics. "
    "They are not displayed as live status here."
)

st.caption("AuditMaster | Linux Security Monitoring Project")

if refresh != "Off":
    seconds = 10 if refresh == "10 seconds" else 30
    time.sleep(seconds)
    st.rerun()
