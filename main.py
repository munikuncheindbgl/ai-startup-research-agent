from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

load_dotenv()

client = OpenAI()
tavily = TavilyClient()

# Get startup information
idea = input("Enter your startup idea: ")
market = input("Enter your target market: ")

# Step 1: Ask the LLM to create a research plan
print("\nCreating research plan...")

response = client.responses.create(
    model="gpt-5-mini",
    input=f"""
Analyze this startup idea:

Startup idea: {idea}
Target market: {market}

Create a research plan with exactly these sections:
1. Market
2. Competitors
3. Pricing
4. Business models
5. Customer
6. Risks
"""
)

print("\nRESEARCH PLAN\n")
print(response.output_text)

# Step 2: Define research queries
queries = [
    f"{idea} {market} market size trends",
   f"{idea} {market} competitors",
f"coffee subscription India",
f"coffee subscription box India",
f"monthly coffee subscription India",
f"single origin coffee subscription India",
f"specialty coffee subscription India",
f"coffee club India",
f"coffee discovery subscription India",
f"coffee monthly delivery India",
f"Indian specialty coffee roasters subscription",
f"Indian single origin coffee brands",
f"coffee subscription startups",
    f"{idea} {market} pricing",
    f"{idea} {market} business model",
    f"{idea} {market} customers",
    f"{idea} {market} risks challenges",
]

# Step 3: Search the web
all_results = []

print("\nSTARTING WEB RESEARCH...\n")

for i, query in enumerate(queries, start=1):
    print(f"Search {i}/6: {query}")

    try:
        results = tavily.search(
            query,
            max_results=10,
            timeout=15
        )

        all_results.append(results)

        print(f"✓ Search {i} complete")

    except Exception as e:
        print(f"✗ Search {i} failed: {e}")

print("\nRESEARCH COMPLETE")
print("Successful searches:", len(all_results))

# Step 4: Combine research results
research_text = ""

for i, results in enumerate(all_results, start=1):
    research_text += f"\n\nRESEARCH AREA {i}\n"

    for result in results.get("results", [])[:3]:
        research_text += (
            f"\nTITLE: {result.get('title', '')}"
            f"\nURL: {result.get('url', '')}"
            f"\nCONTENT: {result.get('content', '')[:1000]}\n"
        )

# Step 5: Ask the LLM to analyze the research
print("\nSending research to AI for analysis...")

summary = client.responses.create(
    model="gpt-5-mini",
    input=f"""
You are a startup research analyst.

Startup idea:
{idea}

Target market:
{market}

Below is web research collected across multiple research areas:

{research_text}

Create an evidence-backed startup research report with these sections:

1. Market
2. Competitors
3. Pricing
4. Business models
5. Customers
6. Risks
7. Key opportunities
8. Questions that require further research

For important claims:
- cite the source URL provided in the research
- clearly distinguish facts from interpretation
- do not invent information
- identify gaps where the research is insufficient
"""
)

print("\nAI RESEARCH REPORT\n")
print(summary.output_text)

gap_analysis = client.responses.create(
    model="gpt-5-mini",
    input=f"""
Review the following startup research report.

Startup idea:
{idea}

Target market:
{market}

Research report:
{summary.output_text}

Identify the most important unanswered questions that prevent us
from making a confident business decision.

For each gap, provide:
1. The unanswered question
2. Why the information matters
3. What type of source would provide reliable evidence

Focus especially on:
- India-specific market data
- Indian competitors and pricing
- Customer willingness to pay
- Supplier and sourcing costs
- Shipping and fulfillment costs
- Unit economics
- Regulations
- Customer retention/churn

Do not invent answers. Only identify information that is genuinely missing
or insufficiently supported.
"""
)

print("\nRESEARCH GAPS\n")
print(gap_analysis.output_text)

competitor_extraction = client.responses.create(
    model="gpt-5-mini",
    input=f"""
You are a competitive intelligence analyst.

Startup idea:
{idea}

Target market:
{market}

Below are the web research results collected by the research agent:

{research_text}

Extract EVERY distinct competitor or competing business mentioned
in the research.

For each competitor, provide:

1. Company/brand name
2. Country
3. Competitor type:
   - Direct
   - Indirect
   - Substitute
   - International benchmark
4. What they sell
5. Subscription model, if known
6. Price, if known
7. Source URL

Rules:
- Do not invent competitors.
- Do not omit a competitor simply because it was mentioned only once.
- Remove duplicate mentions of the same company.
- If information is unavailable, write "Unknown".
- Return one competitor per numbered item.
"""
)

print("\nCOMPETITOR DATABASE\n")
print(competitor_extraction.output_text)

missing_competitors = client.responses.create(
    model="gpt-5-mini",
    input=f"""
You are a competitive intelligence researcher.

Startup:
{idea}

Target market:
{market}

Competitors already discovered:
{competitor_extraction.output_text}

Your task is NOT to summarize these competitors.

Instead, identify what types of competitors may still be missing.

Think systematically across:

1. Indian coffee subscription companies
2. Indian specialty coffee roasters offering subscriptions
3. Indian single-origin coffee sellers
4. Indian coffee discovery boxes
5. Indian coffee clubs
6. International coffee subscription companies
7. Single-origin discovery subscriptions
8. Coffee marketplaces
9. Premium coffee gifting subscriptions
10. Adjacent products that could substitute for this product

Generate 20 NEW web-search queries that are likely to discover
competitors NOT already present in the list.

Rules:
- Do not repeat existing competitors.
- Do not give competitor names.
- Return only the 20 search queries.
- Make the queries diverse and specific.
"""
)

print("\nMISSING COMPETITOR SEARCH QUERIES\n")
print(missing_competitors.output_text)