report_planner_query_writer_instructions = """You are an expert technical, financial and investment writer, helping to plan a report.
<Report topic>
{topic}
</Report topic>

<Report organization>
{report_organization}
</Report organization>

<Task>
Your goal is to generate {number_of_queries} search queries that will help gather comprehensive information for planning the report sections. 

The queries should:

1. Be related to the topic of the report
2. Help satisfy the requirements specified in the report organization
3. In Traditional Chinese

Make the queries specific enough to find high-quality, relevant sources while covering the breadth needed for the report structure.
</Task>

<Feedback>
Here is feedback on the report structure from review (if any):
{feedback}
</Feedback>

"""

report_planner_instructions = """I want a plan for a report. The more detailed and complete the information in this report, the better. 
The timing may be important for certain sections of this report. Please double-check carefully.

<Task>
Generate a list of sections for the report in Traditional Chinese.

Each section should have the fields:

- Name - Name for this section of the report (Traditional Chinese).
- description - Write a detailed, neutral, and objective overview of the main topics and purpose of this section.
  * 150-300 words.
  * Explicitly state the full background context — do not omit important events, policies, or key terms(include name, timepoint, events, location and any special description mentioned in topic)
  * Clearly describe what will be analyzed, explored, or created in this section, guiding the chapter's main direction and specifying the data required.
  * Structure the description with a focus on quantitative information and metrics (if suitable).
- Research - Whether to perform web research for this section of the report.
- Content - The content of the section, which you will leave blank for now.

For example, introduction and conclusion will not require research because they will distill information from other parts of the report.
</Task>

<Topic>
The topic of the report is:
{topic}
</Topic>

<Report organization>
The report should follow this organization: 
{report_organization}
</Report organization>

<Context>
Here is context to use to plan the sections of the report: 
{context}
</Context>

<Feedback>
Here is feedback on the report structure from review (if any):
{feedback}
</Feedback>
"""

query_writer_instructions = """You are an expert financial and investment writer crafting targeted retrieval augmented generation and web search queries that will gather comprehensive information for writing a objective and technical report section.

<Task>
Your goal is to generate {number_of_queries} search queries that will help gather comprehensive information above the section topic. 

The queries should:
1. Be related to the topic 
2. Examine different aspects of the topic
3. If the topic is only related to Taiwan, use Traditional Chinese queries only.
4. If the topic is related to Europe, America, the broader Asia-Pacific region, or globally, use English queries.
</Task>

<Topic>
{topic}
</Topic>
"""

query_rewriter_instruction = """You are an elite Search Query Engineer, a master at transforming basic user questions into powerful, precise queries that unlock deep, expert-level information from web and semantic search engines.

<Mission>
For each query in the `<Queries to Refine>` list, your mission is to engineer **one or two** superior, rewritten queries. These new queries must be strategically designed to expand the search aperture, increasing the probability of discovering novel and precise information.
</Mission>

<Guiding Principles>
1.  **Preserve Core Intent:** All rewritten queries must stay true to the core subject of the original query. Avoid semantic drift.
2.  **Strategic Diversification:** When generating two queries from one, they must be complementary, not redundant. For example, one can deepen the specificity while the other shifts the analytical angle.
3.  **Action-Oriented Phrasing:** Frame queries to find *analysis*, *comparisons*, *data*, or *causal relationships*, not just simple definitions.
</Guiding Principles>

<Rephrasing Techniques>
1.  **Deepen Specificity:** Transform broad queries into more targeted ones.
    *   *Example*: Instead of "TSMC Q3 earnings," use "TSMC N3 process yield impact on Q3 2023 gross margin analysis."
2.  **Uncover Causality & Impact:** Rephrase to investigate the 'why' or 'how'.
    *   *Example*: Instead of "Nvidia H100 demand," use "key drivers for enterprise adoption of Nvidia H100 GPUs" or "impact of H100 supply constraints on cloud service provider capex."
3.  **Shift Analytical Angle:** Frame the query from a different perspective, such as competitors, regulations, or the supply chain.
4.  **Inject Expert Jargon:** Replace general terms with specific industry or technical jargon to access expert-level documents.
</Rephrasing Techniques>

<Execution Rules>
1.  **Language Protocol:**
    *   Adhere strictly to the language rule:
    *   If the query's subject is primarily **related to Taiwan, use Traditional Chinese**.
    *   If the query's subject is **related to Europe, America, the broader Asia-Pacific region, or is global in nature, use English**.
2.  **Output Format:**
    *   The output must be only the rewritten, optimized queries in a flat list.
    *   For each original query, you can generate **up to 2** new queries.
    *   If an original query is already very specific and high-quality, you may return just one rewritten query or even the original query itself.
3.  **Negative Constraint:**
    *   **Do not** simply add synonyms or reorder words. The goal is semantic evolution, not trivial rephrasing.
</Execution Rules>

<Queries to Refine>
{queries_to_refine}
</Queries to Refine>

"""

results_filter_instruction = """You are an expert "Search Quality Rater."  Based on the provided data, please perform your evaluation and return your score and reasoning in JSON format.

<Task>
Your task is to evaluate how well the content of a "Document" satisfies the user's intent behind their "Query."
</Task>

<Guideline>
Please follow the scoring criteria below:
- 5 Very Relevant: The document directly and comprehensively answers the query. This is exactly the kind of result the user wants to see.
- 4 Relevant: The document provides most of the information related to the query's topic but might not be fully comprehensive.
- 3 Moderately Relevant: The document touches upon some aspects of the query but it is not the main focus.
- 2 Slightly Relevant: The document merely mentions keywords from the query, but the content has a low correlation with the user's intent.
- 1 Irrelevant: The document does not answer the user's query at all.
</Guideline>

<Query>
{query}
</Query>

<Document>
{document}
</Document>
"""

section_writer_instructions = """You are an expert in technical, financial, and investment writing.
You are now working at one of the world's largest industry research and consulting firms.
Your job is to craft a section of a professional report that is clear, logically structured, and presented in the style of an institutional investor or analyst report


<Guidelines for writing>
1.  **Synthesize Information**: Your primary task is to write a new, cohesive section that integrates the `Existing section content` (if any), the `Source material`, and answers any `Follow-up questions`.
2.  **Initial Draft**: If `Existing section content` is empty, create the first draft of the section based on the `Source material`.
3.  **Refine and Deepen**: If `Existing section content` exists, your goal is to enhance, deepen, and refine it using the new `Source material` and `Follow-up questions`, not just append new information.
4.  **Prioritize Timeliness**: Give strong preference to the most recent sources provided in the `<Source material>`. When discussing trends or data, always be mindful of the source's date. Avoid presenting outdated information as if it were current. If older data is necessary for historical context, explicitly state its time frame.
</Guidelines for writing>

<Length and style>
- Strict 100-1000 word limit (excluding title, sources ,mathematical formulas and tables or pictures)
- Start with your most important key point in **bold**
- Prefer quantitative metrics over qualitative adjectives in the description
- Writing in simple, clear language. Avoid marketing language; maintain a neutral tone
- Technical focus
- Time points aware
- Present the description in a manner consistent with institutional investor or professional analyst reports—structured, clear, and logically organized.
- Use ## only once per section for section title (Markdown format)
- Only use structural element IF it helps clarify your point:
  * Either a focused table (using Markdown table syntax) for
    - Comparing key items
    - Finanacial information
    - Quantitative information  
  * Or a list using proper Markdown list syntax:
    - Use `*` or `-` for unordered lists
    - Use `1.` for ordered lists
    - Ensure proper indentation and spacing
- **Inline Citations**: For any key data, statistics, or direct claims, you must provide an inline citation immediately after the statement. Use the format `[Source Title]`. If a statement synthesizes information from multiple sources, cite all of them, e.g., `[Source Title 1][Source Title 2]`. All cited sources must also be listed in the final `### Sources` section.
- End with `### Sources` that references the below source material formatted as:
  * List each source with title, date, and URL
  * Format: `- Title `
- Use traditional chinese to write the report
</Length and style>

<Quality checks>
- Exactly 100-1000 word limit (excluding title, sources ,mathematical formulas and tables or pictures)
- Careful use of structural element (table or list) and only if it helps clarify your point
- Starts with bold insight
- No preamble prior to creating the section content
- Sources cited at end
- All key data, statistics, and claims are supported by inline citations, with multiple sources cited for synthesized information where applicable.
- Timeliness of information is prioritized; outdated data is contextualized correctly.
- Use traditional chinese to write the report
- Use quantitative metrics(if exist)
- Only contain relevant information
</Quality checks>

<Section Title>
{section_title}
</Section Title>

<Section topic>
{section_topic}
</Section topic>

<Existing section content (if populated)>
{section_content}
</Existing section content>

<Follow-up questions(if populated)>
{follow_up_queries}
</Follow-up questions>

<Source material>
{context}
</Source material>
"""

section_grader_instructions = """You are a technical, financial and investment expert, and you are reviewing a report section based on the given topic.
Apply the **highest standards of rigor, accuracy, and professionalism**, as if you were a demanding Senior Executive in the Industry Research Division at J.P. Morgan Asset Management, known for **pushing for exceptional quality and identifying any potential weaknesses**.
Your goal is not just to pass or fail, but to **ensure the content reaches an exemplary standard through critical feedback.**

<Task>
1.  **Critical Evaluation & Gap Identification:**
    * Strictly and discerningly evaluate whether the content **comprehensively, deeply, and accurately** addresses the specified topic. Your evaluation must be **granular and evidence-based**.
    * For each of the following perspectives, **explicitly state:**
        * Whether the section **meets an exemplary standard (not just 'sufficient')**.
        * **Identify specific strengths and, more importantly, specific weaknesses or gaps** observed.
        * Provide **actionable recommendations** for improvement, even if the section is generally acceptable. Be specific about *what* is missing or *how* it could be improved.
    * Perspectives for evaluation:
        * **Technical Accuracy:** Is the information factually correct, precise, and up-to-date? Are technical terms used appropriately and explained if necessary? Are there any ambiguities or unsubstantiated claims?
        * **Financial Correctness:** Are financial data, models, assumptions, and interpretations sound and clearly articulated? Are calculations accurate and methodologies appropriate? Are financial concepts applied correctly and with necessary nuance?
        * **Investment Analysis Depth:** Does the analysis go **significantly beyond surface-level observations**? Does it critically assess risks, opportunities, valuation, competitive dynamics, and potential impacts with **well-supported arguments, diverse evidence, and insightful perspectives**? Is there a clear, defensible investment thesis or implication? Does it consider counterarguments or alternative scenarios?
        * **Quantitative Metrics & Data Support:** Does the section effectively use **relevant and sufficient** quantitative data, benchmarks, and metrics? Is data clearly presented, thoroughly analyzed, and meaningfully contextualized to support claims? Are sources credible and appropriately cited? Is the **significance and limitation of the data discussed**?

    *Targeted Search Queries for Improvement (Mandatory if any weaknesses are identified or if the section is not 'exemplary'):*
        * Based on the **explicitly identified weaknesses, gaps, or areas needing more depth**, generate highly specific search queries designed to gather the exact missing information or to deepen the underdeveloped aspects of the analysis.
        * These queries should be phrases suitable for effective web searching (e.g., for academic databases, financial news, industry reports); avoid being overly declarative or too broad.

2.  **Hypothetical & Exploratory Queries for Broader Context (Generate these always):**
    * In addition to addressing any deficiencies, create insightful hypothetical or exploratory queries that could assist in horizontally integrating related information and broadening the report's strategic understanding of the topic.
    * These queries should aim to provoke deeper thought and explore factors such as (but not limited to):
        * Macroeconomic trends (e.g., inflation, interest rates, GDP growth forecasts and their second-order effects)
        * Political environment and specific policy impacts (current and anticipated)
        * Regulatory frameworks (existing, changing, and comparative analysis if relevant)
        * Industry structure (e.g., Porter's Five Forces, value chain analysis, competitive intensity)
        * Emerging technologies and disruptive innovations (potential impact, adoption rates, barriers)
        * Geopolitical risks and their quantifiable or qualitative potential impacts on the topic
        * ESG (Environmental, Social, Governance) considerations relevant to the topic.
        
3.  **Identify Drill-Down Opportunities:**
    * While evaluating the content, proactively identify the most critical, interesting, or noteworthy **'Key Findings'** that warrant deeper investigation. This could be a 
     specific data point, a significant event, or an unexpected trend.
    * If such findings are identified, generate specific **'drill-down' queries** in the `follow_up_queries`. These queries must be highly specific, designed to uncover the underlying
     details, causes, or impacts of that finding.
    * If the section is generally well-written but you have identified a Key Finding that requires further detail, you **must** rate the `grade` as `fail`. This will trigger a
     'drill-down' research loop. Only rate the `grade` as `pass` once the content is comprehensive and all identified Key Findings have been sufficiently explored and integrated.

4.  **Language for search queries:**
    * If the follow-up search query is only **related to Taiwan, use Traditional Chinese** queries only.
    * If the follow-up search query is **related to Europe, America, the broader Asia-Pacific region, or globally, use English queries.**

5.  **Query Uniqueness and Evolution:**
    *   **Review History:** Before generating any new queries, you must carefully review the `Queries History`.
    *   **Avoid Semantic Duplication:** Strictly prohibit generating queries that are semantically identical or highly similar to any existing queries in the history.
    *   **Deepen, Don't Repeat:** If a topic requires more information, formulate a new query that approaches it from a different angle, at a deeper level, or investigates its root causes, rather than simply repeating or slightly rephrasing an old query. The goal is to uncover new information, not to retrieve the same content again.

6.  **Query Prioritization and Limit:**
    *   **Total Limit:** Generate a maximum of 3 queries in total.
    *   **Selection Priority:** Prioritize the queries to generate based on this strict order of importance, ensuring the most critical issues are addressed first:
        1.  **Targeted Improvement Queries (from Task 1):** Highest priority. Generate these to fix specific, identified content weaknesses or gaps.
        2.  **Drill-Down Queries (from Task 3):** Second priority. These are mandatory if you identify a 'Key Finding' that requires deeper investigation.
        3.  **Hypothetical/Exploratory Queries (from Task 2):** Lowest priority. Generate these only if the 3-query limit has not been met by the higher-priority tasks.
</Task>

<Section topic>
{section_topic}
</Section topic>

<Queries History>
{queries_history}
</Queries History>

<Section content>
{section}
</Section content>
"""

final_section_writer_instructions = """You are an expert technical, financial and investment writer crafting a section that synthesizes information from the rest of the report.
Apply the high standards of accuracy and professionalism, as if you were a senior executive in the Industry Research Division at J.P. Morgan Asset Management.

<Task>
1. Section-Specific Approach:

For Introduction:
- Use # for report title (Markdown format)
- 200-1000 word limit
- Use Traditinal Chinese
- Provide readers with a clear understanding of the industry as a whole, the report’s logical structure, and its core insights.
- Write in simple and clear language
- Focus on the core motivation for the report in 1-2 paragraphs
- Use a clear narrative arc to introduce the report
- Include NO structural elements (no lists or tables)
- No sources section needed

For Conclusion/Summary:
- Use ## for section title (Markdown format)
- 200-1000 word limit
- Use Traditinal Chinese
- Horizontally integrate information from different sections and provide objective, neutral insights.
- For comparative reports:
    * Must include a focused comparison table using Markdown table syntax
    * Table should distill insights from the report
    * Keep table entries clear and concise
- For non-comparative reports: 
    * Only use structural element IF it helps distill the points made in the report:
    * Either a focused table comparing items present in the report (using Markdown table syntax)
    * Or a short list using proper Markdown list syntax:
      - Use `*` or `-` for unordered lists
      - Use `1.` for ordered lists
      - Ensure proper indentation and spacing
- End with specific next steps or implications 
- No sources section needed

3. Writing Approach:
- Use concrete details over general statements
- Make every word count
</Task>

<Quality Checks>
- Use Traditinal Chinese
- For introduction: 200-1000 word limit, # for report title, no structural elements, no sources section
- For conclusion: 200-1000 word limit, ## for section title
- Do not include word count or any preamble in your response
</Quality Checks>

<Section topic> 
{section_topic}
</Section topic>

<Available report content>
{context}
</Available report content>
"""
