#!/usr/bin/env python3
"""
Build a TaskFlow import CSV from the Graylinx X Harshan tracker data.

Validated against the live TaskFlow API (sumukhmr.pythonanywhere.com):
  team            -> "Engineering" (user's team) on every row
  sub_category    -> Engineering functions only: Backend / Frontend /
                     Infrastructure/DevOps / Mobile / Data
  status          -> todo / progress / review / blocked / just / pushed_dev / done
  priority        -> low / medium / high
  quadrant        -> q1..q4
  type            -> "task"
  assigned_to     -> "Harshan Aiyappa" (confirmed real user)

Sources:
  ../works.csv        -> projects + milestones
  ../engagement.csv   -> day-by-day engagement log

Framing rule: crisp, positive, impact-oriented copy. Real numbers only
(commit counts, deliverables, dates) presented as accomplishments.
"""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORKS = os.path.join(ROOT, "works.csv")
ENGAGE = os.path.join(ROOT, "engagement.csv")
OUT = os.path.join(HERE, "taskflow_import.csv")

ASSIGNEE = "Harshan Aiyappa"
TEAM = "Engineering"
CATCH_ALL = "Infrastructure/DevOps"   # closest-fit for non-build days
TODAY = "2026-06-16"

HEADER = [
    "title", "description", "team", "sub_category", "assigned_to", "priority",
    "status", "quadrant", "due_date (YYYY-MM-DD)", "start_date (YYYY-MM-DD)",
    "type", "notes",
]

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def human_list(items):
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def map_status(raw):
    s = (raw or "").strip().lower()
    if s == "done":
        return "done"
    if s in ("active", "ongoing", "paused"):
        return "progress"
    if s == "planned":
        return "todo"
    return "progress"


def due_from_end(end):
    end = (end or "").strip()
    return end if DATE_RE.match(end) else ""


# ---------------------------------------------------------------------------
# Per-project: Engineering sub_category + priority + quadrant + positive copy.
# ---------------------------------------------------------------------------
PROJECT = {
    "thermynx": dict(
        subcat="Backend", priority="high", quadrant="q1",
        desc="Architected and built — as sole engineer — an AI-powered HVAC operations platform for the Unicharm facility: FastAPI backend, React/TypeScript frontend, on-prem Ollama LLM inference, RAG over facility documents, work-order automation and an analytics engine.",
        notes="Flagship project — 322 commits. Delivered 18 feature pages and 6 LLM/Claude agents, RAG retrieval over facility documents, an end-to-end work-order workflow, and a chiller/HVAC analytics engine — all on a fully local, on-prem LLM stack. Role: Sole full-stack engineer. Tech: Python / FastAPI / React / TypeScript / Ollama / MySQL / Vite. Progress 70%.",
    ),
    "climastream": dict(
        subcat="Data", priority="medium", quadrant="q2",
        desc="Designed and delivered an end-to-end, production-grade real-time streaming pipeline: Kafka -> TimescaleDB -> Airflow -> FastAPI -> Next.js, complete with a device simulator.",
        notes="Completed end-to-end. Proved the real-time streaming architecture across six microservices (simulator, ingestion, processor, ML scoring, storage, API) in ~4 weeks, 32 commits. Role: Sole engineer. Tech: Python / Kafka / TimescaleDB / Airflow / Next.js / Docker. Delivered 100%.",
    ),
    "omnyx": dict(
        subcat="Backend", priority="high", quadrant="q2",
        desc="Leading the architecture and platform design for the next-generation production platform — the strategic north star that consolidates the POCs: Digital-Twin fault detection, reinforcement-learning optimization, an agentic-AI operations layer and a dual-database (PostgreSQL + TimescaleDB) design.",
        notes="219 commits driving the unified product vision. Established Digital-Twin FDD, RL-based setpoint optimization, an agentic-AI operations layer and a scalable dual-DB architecture. Role: Architecture & platform lead. Tech: Python / React / TypeScript / PostgreSQL / TimescaleDB / Kafka.",
    ),
    "gl-pulse": dict(
        subcat="Infrastructure/DevOps", priority="medium", quadrant="q2",
        desc="Authored the reference architecture and planning documentation unifying ClimaStream, THERMYNX and OMNYX into one cohesive next-generation vision.",
        notes="Consolidated lessons from every POC into 20 architecture documents that anchor the unified platform direction. Role: Author. Progress 60%.",
    ),
    "gl-pbs": dict(
        subcat="Backend", priority="medium", quadrant="q2",
        desc="Led the BACnet device-simulation study — analyzing simulation flow and the Vue 3 simulator dashboard to inform device integration.",
        notes="Delivered BACnet device-simulation analysis and UI study; groundwork ready to extend. Role: Simulation & BACnet analysis. Tech: Vue 3 / BACnet.",
    ),
    "current-works": dict(
        subcat="Data", priority="high", quadrant="q1",
        desc="Sole engineer on the active Graylinx core monorepo — driving Kafka performance/stress testing, cross-machine benchmarking and DB/ETL architecture audits.",
        notes="Scaled Kafka stress tests from 150x to 5000x throughput, delivered cross-machine 24GB vs 8GB performance comparison reports, and produced DB & ETL architecture audits with management-ready summaries (16 commits). Role: Sole engineer. Tech: Node.js / Express / Kafka / MySQL / Python.",
    ),
    "docs": dict(
        subcat="Backend", priority="medium", quadrant="q2",
        desc="Authored and maintain the product and architecture documentation: PRD, the 175-feature Modules & Features inventory and Kafka/stress-test reports.",
        notes="Delivered Graylinx_Modules_and_Features.md (175 phased features) plus PRD v1.0 and the Industrial Platform Master. Role: Author / maintainer.",
    ),
    "selfaware-suite": dict(
        subcat="Backend", priority="medium", quadrant="q2",
        desc="Designed and built a six-product local-AI suite across six repositories: Continuum (HVAC intelligence), AuditShield, Autonomous-Cortex, NeuralPulse, VisioScan and SpatialNexus.",
        notes="94 commits delivering six integrated products, including SelfAware Continuum (Unicharm + Neo4j + pgvector + Ollama). Role: Designer & builder. Tech: React / TypeScript / Python / Neo4j / pgvector / Ollama / Docker.",
    ),
    "farmer-app": dict(
        subcat="Mobile", priority="high", quadrant="q1",
        desc="Built the farm-to-fork traceability platform for NR Group (Nesso) — web admin and mobile app — including an intensive weekend build sprint.",
        notes="191 commits delivering a full farm-to-fork traceability product (dashboard, activities/logging, multi-language, dark mode, mapping) in ~1 week, including a high-output weekend sprint. Role: Builder. Tech: TypeScript / React / Node.js / React Native.",
    ),
    "selfaware-dev-stack": dict(
        subcat="Infrastructure/DevOps", priority="medium", quadrant="q2",
        desc="Authored the canonical local Docker development stack (MySQL, PostgreSQL, Neo4j, Redis) powering the SelfAware products.",
        notes="Delivered one unified dev environment serving 4 products. Role: Author. Tech: Docker / MySQL / PostgreSQL / Neo4j / Redis. Completed 100%.",
    ),
    "mysql-unicharm-proxy": dict(
        title="MySQL Unicharm Proxy",
        subcat="Infrastructure/DevOps", priority="medium", quadrant="q2",
        desc="Built a Docker MySQL port-forwarding utility that streamlined database access; its capability was later consolidated into the unified SelfAware dev stack.",
        notes="Delivered a quick, reliable infra utility whose capability was folded into the broader dev stack. Role: Infra. Tech: Docker / MySQL. Completed 100%.",
    ),
    "python-etl": dict(
        subcat="Data", priority="medium", quadrant="q2",
        desc="Driving the ETL / transformer-layer design — defining conversion workflows and transformer architecture for the data platform.",
        notes="Delivered ETL transformer-layer planning and conversion-workflow design. Role: ETL design. Tech: Python / ETL.",
    ),
    "raspberry": dict(
        title="Edge / IoT (Raspberry Pi) R&D",
        subcat="Infrastructure/DevOps", priority="medium", quadrant="q2",
        desc="Edge / IoT R&D initiative exploring Raspberry Pi-based edge computing for field deployments.",
        notes="Edge-hardware experimentation initiative. Role: Edge R&D. Tech: Raspberry Pi.",
    ),
    "gl-hvac-early": dict(
        subcat="Data", priority="medium", quadrant="q2",
        desc="Built the first Graylinx HVAC data-pipeline prototype (Python) — the foundation that evolved into ClimaStream.",
        notes="Delivered the first HVAC repo (8 commits) that seeded the production streaming pipeline. Role: Prototype builder. Tech: Python. Completed 100%.",
    ),
    "gl-legacy-analysis": dict(
        subcat="Backend", priority="medium", quadrant="q2",
        desc="Audited and documented the Graylinx legacy codebase — the analysis that directly informed the v2 / OMNYX rebuild.",
        notes="Delivered a legacy-code audit (7 commits) that fed the OMNYX architecture. Role: Code audit & documentation. Tech: JavaScript / Node.js. Completed 100%.",
    ),
    "poc-hvac-pipeline": dict(
        subcat="Data", priority="medium", quadrant="q2",
        desc="Built the end-to-end Graylinx HVAC chiller-plant telemetry pipeline and its three POCs: Node.js -> MySQL + Kafka -> MinIO (Parquet) -> Airflow -> ClickHouse -> Grafana, delivering a production-ready v2.",
        notes="Delivered a chiller-plant predictive-maintenance + energy-optimization pipeline: v1 (19 Nov) and production v2 (26 Nov 2025), 12 commits. Three POCs delivered — Ingestion, Data Lake, Analytics. Role: Pipeline engineer. Tech: Node.js / Kafka / MinIO / Parquet / Airflow / ClickHouse / Grafana / Python / Docker. Completed 100%.",
    ),
}

# Engineering function per milestone.
MILESTONE_SUBCAT = {
    "thermynx.1": "Frontend", "thermynx.2": "Backend", "thermynx.3": "Data",
    "thermynx.4": "Backend", "thermynx.5": "Data",
    "climastream.1": "Backend", "climastream.2": "Data", "climastream.3": "Data",
    "climastream.4": "Data", "climastream.5": "Frontend",
    "omnyx.1": "Data", "omnyx.2": "Data", "omnyx.3": "Backend", "omnyx.4": "Data",
    "current-works.1": "Infrastructure/DevOps", "current-works.2": "Infrastructure/DevOps",
    "current-works.3": "Data",
    "selfaware-suite.1": "Data", "selfaware-suite.2": "Backend",
    "selfaware-suite.3": "Backend", "selfaware-suite.4": "Data",
    "selfaware-suite.5": "Frontend", "selfaware-suite.6": "Data",
    "poc-hvac-pipeline.1": "Data", "poc-hvac-pipeline.2": "Data",
    "poc-hvac-pipeline.3": "Data",
}

# Short, presentable parent labels for milestone titles.
SHORT = {
    "thermynx": "THERMYNX", "climastream": "ClimaStream", "omnyx": "OMNYX",
    "current-works": "Current Works in GL", "selfaware-suite": "SelfAware Suite",
    "farmer-app": "Nesso", "poc-hvac-pipeline": "HVAC Pipeline POC",
}


def milestone_verb(status):
    s = (status or "").strip().lower()
    if s == "done":
        return "Delivered"
    if s == "planned":
        return "Designing"
    return "Building"


def build_works_rows():
    rows = []
    projects = {}
    with open(WORKS, newline="", encoding="utf-8-sig") as f:
        records = list(csv.DictReader(f))

    for r in records:
        if r["type"] == "project":
            projects[r["id"]] = r

    for r in records:
        if r["type"] == "project":
            meta = PROJECT.get(r["id"], {})
            rows.append([
                meta.get("title", r["name"]),
                meta.get("desc", r["description"]),
                TEAM, meta.get("subcat", "Backend"), ASSIGNEE,
                meta.get("priority", "medium"), map_status(r["status"]),
                meta.get("quadrant", "q2"),
                due_from_end(r["end"]), r["start"].strip(), "task",
                meta.get("notes", r["highlights"]),
            ])
        else:  # milestone
            parent = projects.get(r["parent_id"], {})
            pmeta = PROJECT.get(r["parent_id"], {})
            short = SHORT.get(r["parent_id"], parent.get("name", r["parent_id"]))
            verb = milestone_verb(r["status"])
            desc = f"{verb}: {r['description']}" if r["description"] else f"{verb} milestone."
            prog = r["progress"].strip()
            note = f"Milestone of {parent.get('name', short)}." + (f" {prog}% complete." if prog else "")
            rows.append([
                f"{short} > {r['name']}", desc, TEAM,
                MILESTONE_SUBCAT.get(r["id"], pmeta.get("subcat", "Backend")),
                ASSIGNEE, pmeta.get("priority", "medium"), map_status(r["status"]),
                pmeta.get("quadrant", "q2"),
                due_from_end(r["end"]), r["start"].strip(), "task", note,
            ])
    return rows


SEG_RE = re.compile(r"^\s*(.+?)\s*\[(\d+)\]:")
TOTAL_RE = re.compile(r"\((\d+)\s*commits?\)")

# Crisp positive descriptions for remote-coordination days, keyed by project.
DESC_BY_LINK = {
    "gl-pbs": "BACnet device-simulation flow and UI analysis.",
    "omnyx": "OMNYX interface and workflow architecture design.",
    "python-etl": "ETL transformer-layer design and conversion-workflow planning.",
    "current-works": "Platform coordination and architecture planning.",
    "thermynx": "THERMYNX feature development and architecture.",
    "farmer-app": "Nesso platform development.",
}

# Crisp positive descriptions for on-site / discussion days, keyed by date.
ONSITE_DESC = {
    "2026-04-22": "Deployment kickoff and coordination with the Graylinx team.",
    "2026-04-27": "On-site deployment work in Bangalore.",
    "2026-04-28": "On-site engineering work and architecture discussions.",
    "2026-04-29": "On-site engineering work and team coordination.",
    "2026-04-30": "On-site engineering work in Bangalore.",
    "2026-05-04": "HVAC PRD and architecture-module discussions (with Vishnu).",
    "2026-05-05": "PRD planning and module-design discussions.",
    "2026-05-06": "Finalized PRD and architecture workflows.",
    "2026-05-08": "On-site planning session ahead of Vishnu's travel.",
    "2026-05-09": "Architecture discussions and live AI demonstrations.",
}


def parse_derived(note):
    pairs = []
    for seg in note.split(" · "):
        m = SEG_RE.match(seg)
        if m:
            pairs.append((m.group(1).strip(), int(m.group(2))))
    totals = TOTAL_RE.findall(note)
    total = totals and int(totals[-1]) or sum(c for _, c in pairs)
    return pairs, total


def derived_lead(total):
    if total >= 30:
        return "High-output build day"
    if total >= 10:
        return "Strong build day"
    if total >= 3:
        return "Productive build day"
    return "Focused development day"


def city(loc):
    for c in ("Bangalore", "Mysore"):
        if c in loc:
            return c
    return loc.strip()


def build_engagement_rows():
    rows = []
    with open(ENGAGE, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            date = r["date"].strip()
            wt = r["work_type"].strip()
            loc = r["location"].strip()
            src = r["source"].strip()
            note = r["notes"].strip()
            linked = r["linked_project"].strip()

            if wt == "Leave":
                headline = "Planned leave"
                desc = "Planned leave / rest day."
                subcat, prio, quad = CATCH_ALL, "low", "q2"
            elif src == "manual":
                headline = "Engineering hiring — technical interviews (RAPL & Examic)"
                desc = ("Engineering hiring support — conducted technical interviews "
                        "for RAPL and Examic, plus Lingotran platform tasks.")
                subcat, prio, quad = CATCH_ALL, "medium", "q2"
            elif src == "derived":
                pairs, total = parse_derived(note)
                names = [n for n, _ in pairs]
                plural = "s" if total != 1 else ""
                headline = f"{human_list(names)} build — {total} commit{plural}"
                parts = [f"{n} ({c})" for n, c in pairs]
                desc = f"{derived_lead(total)}: {total} commit{plural} across {human_list(parts)}."
                subcat = PROJECT.get(linked, {}).get("subcat", "Backend")
                prio, quad = "high", "q1"
            elif wt in ("Office", "Discussion"):
                headline = f"{'On-site' if wt == 'Office' else 'Discussion'} @ {city(loc)}"
                desc = ONSITE_DESC.get(date, note)
                subcat = PROJECT.get(linked, {}).get("subcat", "Backend")
                prio, quad = "high", "q1"
            else:  # WFH coordination (csv)
                label = SHORT.get(linked, "engineering")
                headline = f"Remote — {label}"
                desc = DESC_BY_LINK.get(linked, "Remote engineering coordination and architecture planning.")
                subcat = PROJECT.get(linked, {}).get("subcat", "Backend")
                prio, quad = "medium", "q2"

            meta = []
            if r["hotel"].strip():
                meta.append(f"Hotel: {r['hotel'].strip()}")
            if r["travel"].strip():
                meta.append(f"Travel: {r['travel'].strip()}")
            ci, co = r["check_in"].strip(), r["check_out"].strip()
            if ci and co and wt != "Leave" and ci.lower() != "leave":
                meta.append(f"{ci}-{co}")
            if linked:
                meta.append(f"Project: {SHORT.get(linked, linked)}")
            notes = " · ".join(meta)

            status = "done" if date < TODAY else "progress"
            rows.append([
                f"{date} — {headline}", desc, TEAM, subcat, ASSIGNEE,
                prio, status, quad, date, date, "task", notes,
            ])
    return rows


def main():
    rows = build_works_rows() + build_engagement_rows()
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
