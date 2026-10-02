import os
import re
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

load_dotenv()

st.set_page_config(
    page_title="AI Startup Research Agent",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 AI Startup Research Agent")
st.caption("Evidence-backed startup research powered by AI + web search")

# -----------------------------
# API setup
# -----------------------------

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY is missing from your .env file.")
    st.stop()

if not os.getenv("TAVILY_API_KEY"):
    st.error("TAVILY_API_KEY is missing from your .env file.")
    st.stop()

client = OpenAI()
tavily = TavilyClient()

# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:
    st.header("Research Settings")

    model = st.selectbox(
        "AI Model",
        ["gpt-5-mini", "gpt-5"]
    )

    results_per_search = st.slider(
        "Results per search",
        min_value=2,
        max_value=5,
        value=3
    )

# -----------------------------
# Inputs
# -----------------------------

idea = st.text_area(
    "Startup idea",
    value="Coffee subscription from a new origin every month",
    height=100
)

market = st.text_input(
    "Target market",
    value="Premium coffee consumers in India"
)

# -----------------------------
# Research queries
# -----------------------------

research_queries = [
    f"{idea} {market} market size trends",
    f"{idea} {market} competitors",
    f"{idea} {market} pricing",
    f"{idea} {market} business model",
    f"{idea} {market} customers",
    f"{idea} {market} risks challenges",

    "coffee subscription India",
    "coffee subscription box India",
    "monthly coffee subscription India",
    "single origin coffee subscription India",
    "specialty coffee subscription India",
    "coffee club India",
    "coffee discovery subscription India",
    "coffee monthly delivery India",
    "Indian specialty coffee roasters subscription",
    "Indian single origin coffee brands",
    "coffee subscription startups",
]

# -----------------------------
# Helper functions
# -----------------------------

def run_ai(prompt):
    response = client.responses.create(
        model=model,
        input=prompt
    )

    return response.output_text


def clean_queries(text):
    queries = []

    for line in text.splitlines():

        line = re.sub(
            r"^\s*(?:[-*•]|\d+[.)])\s*",
            "",
            line
        ).strip()

        if line and line not in queries:
            queries.append(line)

    return queries


def format_research(results):

    research_text = ""

    for i, result in enumerate(results, start=1):

        research_text += f"\n\nRESEARCH RESULT {i}\n"

        research_text += (
            f"\nTITLE: {result.get('title', '')}"
        )

        research_text += (
            f"\nURL: {result.get('url', '')}"
        )

        research_text += (
            f"\nCONTENT: {result.get('content', '')[:1500]}\n"
        )

    return research_text


# -----------------------------
# Start research
# -----------------------------

if st.button(
    "🚀 Start Research",
    type="primary",
    use_container_width=True
):

    if not idea.strip() or not market.strip():

        st.warning(
            "Please enter both a startup idea and target market."
        )

        st.stop()

    # -------------------------
    # Research plan
    # -------------------------

    with st.status(
        "Researching startup...",
        expanded=True
    ) as status:

        st.write("🧠 Creating research plan...")

        research_plan = run_ai(
            f"""
You are a startup research analyst.

Startup idea:
{idea}

Target market:
{market}

Create a research plan covering:

1. Market
2. Competitors
3. Pricing
4. Business models
5. Customers
6. Risks
7. Unit economics
8. Regulations
9. Distribution

Be concise and systematic.
"""
        )

        # -------------------------
        # Web research
        # -------------------------

        st.write("🌐 Searching the web...")

        all_results = []

        progress = st.progress(0)

        for i, query in enumerate(
            research_queries,
            start=1
        ):

            st.write(
                f"Search {i}/{len(research_queries)}: {query}"
            )

            try:

                results = tavily.search(
                    query,
                    max_results=results_per_search,
                    timeout=20
                )

                all_results.extend(
                    results.get("results", [])
                )

            except Exception as e:

                st.warning(
                    f"Search failed: {query}"
                )

            progress.progress(
                i / len(research_queries)
            )

        research_text = format_research(
            all_results
        )

        # -------------------------
        # AI research report
        # -------------------------

        st.write("📊 Synthesizing research...")

        report = run_ai(
            f"""
You are a startup research analyst.

Startup idea:
{idea}

Target market:
{market}

Research plan:
{research_plan}

Web research:
{research_text}

Create an evidence-backed startup research report.

Sections:

1. Executive Summary
2. Market
3. Competitors
4. Pricing
5. Business Models
6. Customers
7. Unit Economics
8. Distribution
9. Regulations
10. Risks
11. Opportunities
12. Research Gaps

Rules:

- Cite source URLs for important factual claims.
- Distinguish facts from interpretation.
- Do not invent information.
- Clearly identify unsupported claims.
"""
        )

        # -------------------------
        # Competitor extraction
        # -------------------------

        st.write("🏢 Building competitor database...")

        competitors = run_ai(
            f"""
You are a competitive intelligence analyst.

Startup idea:
{idea}

Target market:
{market}

Research:

{research_text}

Extract every distinct relevant competitor.

For each competitor provide:

1. Company / Brand
2. Country
3. Type
   - Direct
   - Indirect
   - Substitute
   - International benchmark
4. What they sell
5. Subscription model
6. Price
7. Source URL
8. Confidence

Rules:

- Do not invent competitors.
- Remove duplicates.
- Do not treat a generic coffee company as a subscription competitor
  unless evidence supports it.
- Exclude irrelevant companies.
- Mark uncertain information as Unknown.
"""
        )

        # -------------------------
        # Missing competitor search
        # -------------------------

        st.write(
            "🔎 Looking for competitors we may have missed..."
        )

        missing_queries_text = run_ai(
            f"""
You are a competitive intelligence researcher.

Startup:
{idea}

Target market:
{market}

Competitors already discovered:

{competitors}

Generate 20 NEW search queries that could discover
competitors missing from the current database.

Cover:

1. Indian coffee subscriptions
2. Indian specialty coffee roasters
3. Single-origin subscriptions
4. Coffee discovery boxes
5. Coffee clubs
6. Premium coffee gifting
7. International coffee subscriptions
8. Coffee marketplaces
9. Adjacent substitutes

Rules:

- Do not give competitor names.
- Return only search queries.
- Each query should be on its own line.
"""
        )

        missing_queries = clean_queries(
            missing_queries_text
        )

        # -------------------------
        # Follow-up research
        # -------------------------

        st.write(
            "🔄 Running follow-up competitor research..."
        )

        followup_results = []

        for query in missing_queries[:20]:

            try:

                results = tavily.search(
                    query,
                    max_results=results_per_search,
                    timeout=20
                )

                followup_results.extend(
                    results.get("results", [])
                )

            except Exception:
                pass

        followup_text = format_research(
            followup_results
        )

        # -------------------------
        # New competitors
        # -------------------------

        new_competitors = run_ai(
            f"""
You are a competitive intelligence analyst.

Startup:
{idea}

Target market:
{market}

Existing competitors:

{competitors}

Additional research:

{followup_text}

Identify NEW relevant competitors.

Do not repeat companies already present.

For each:

1. Company / Brand
2. Country
3. Type
4. What they sell
5. Subscription model
6. Price
7. Source URL
8. Confidence

Do not invent information.

Exclude:

- comparison websites
- equipment vendors
- unrelated companies
- generic cafes

unless evidence shows they compete for the same customer need.
"""
        )

        # -------------------------
        # Gap analysis
        # -------------------------

        st.write(
            "⚠️ Identifying research gaps..."
        )

        gaps = run_ai(
            f"""
You are a startup research analyst.

Startup idea:
{idea}

Target market:
{market}

Research report:

{report}

Competitor database:

{competitors}

New competitor findings:

{new_competitors}

Identify the most important unanswered questions.

For each gap provide:

1. Unanswered question
2. Why it matters
3. Evidence needed
4. Suggested next research action

Focus on:

- India market size
- willingness to pay
- CAC
- LTV
- churn
- sourcing
- shipping
- packaging
- unit economics
- regulations
- recurring payments
- seasonality
- distribution

Do not invent answers.
"""
        )

        status.update(
            label="✅ Research complete!",
            state="complete"
        )

    # -----------------------------
    # Results
    # -----------------------------

    st.success(
        f"Research completed using {len(all_results)} web results."
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Research Report",
            "🏢 Competitors",
            "🔎 Discovery",
            "⚠️ Research Gaps",
            "🧠 Research Plan",
        ]
    )

    with tab1:

        st.markdown(report)

    with tab2:

        st.subheader("Initial Competitor Database")

        st.markdown(competitors)

        st.divider()

        st.subheader("Newly Discovered Competitors")

        st.markdown(new_competitors)

    with tab3:

        st.subheader(
            "Searches used to find missing competitors"
        )

        for query in missing_queries:

            st.write(
                "•",
                query
            )

    with tab4:

        st.markdown(gaps)

    with tab5:

        st.markdown(research_plan)