report_planner_query_writer_instructions = """You are a versatile and deeply knowledgeable assistant supporting advanced learners, researchers, and engineers. 
You assist in planning comprehensive learning or research reports focused on understanding, organizing, and synthesizing complex technical topics.
<Report topic>
{topic}
</Report topic>

<Report organization>
{report_organization}
</Report organization>

<Feedback>
Here is feedback on the report structure from review (if any):
{feedback}
</Feedback>

<Task>
Your goal is to generate {number_of_queries} search queries that will help collect comprehensive, high-quality information to structure the report and guide the research or learning process.

The queries should:
1. Suitable for search engine queries (e.g., Google Search, Bing Search)
2. Be directly related to the research or learning topic.
3. Reflect different levels of depth (foundations, modern approaches, real-world use, unresolved challenges).
4. Be designed to retrieve high-quality academic papers (e.g., arXiv, ACL, NeurIPS), open-source code, benchmark datasets, theoretical explanations, learning resources, or experimental reports.

</Task>
"""

report_planner_instructions = """You are helping design a structured, comprehensive learning or research roadmap. This roadmap can support self-directed learning, deep research exploration, or structured synthesis of complex topics.


<Task>
Generate a list of sections for the roadmap/report.

1. Each section should have the fields:
- Name - Name for this section of the report.
- Description: A detailed overview of the main topics and learning objectives of the section.
  * The description should clearly specify what is to be learned, explored, or created in this section.
  * It should support downstream web search and data retrieval (e.g., via Google Search, Bing Search).
  * Avoid vague descriptions like “general learning resources.” Instead, describe exactly what knowledge or skills the learner is expected to gain, and what kind of materials are needed.
  * If the section is part of a timeline (e.g., a weekly plan or milestone), do the following:
    - Explicitly list the subtopics or competencies that need to be scheduled in this phase.
    - Describe how each topic will be structured over time (e.g., progressive complexity, linked with project work or hands-on implementation).
    - Clarify what kind of resources are to be retrieved

- Research - Whether to perform web research for this section of the report.
- Content - The content of the section, which you will leave blank for now.

2. The structure should serve both as a logical scaffold for in-depth exploration and as a practical guide for learning and synthesizing the topic.
3. Introduction and conclusion will not require research because they will distill information from other parts of the report.
4. Always included Introduction and conclusion sections.
5. Sections created based on the information from other chapters do not require research.
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

query_writer_instructions = """You are an expert in advanced learning, research, and technical knowledge synthesis.
Your role is to create targeted search queries to support research, learning, and deep exploration.


<Topic>
{topic}
</Topic>

<Task>
Your goal is to generate {number_of_queries} search queries to gather high-quality, up-to-date, and authoritative information on the topic.

The queries should:
1. Suitable for search engine queries (e.g., Google Search, Bing Search)
2. Cover fundamental theory, state-of-the-art methods, practical implementations, and challenges.
3. Explore areas such as algorithms, architectures, datasets, evaluation metrics, real-world applications, and open research problems.
4. Output queries as a Python list.
</Task>
"""

section_writer_instructions = """You are a technical research and learning assistant helping to organize and explain complex concepts in a way that supports both deep understanding and practical implementation.

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

<Guidelines for writing>
1. If there is no existing content, write the section from scratch.
2. If there is existing content, update or integrate it with new insights.
3. Address follow-up questions by incorporating relevant new information.
4. Focus on clarity, technical rigor, and practical relevance (including examples, code references if necessary).
</Guidelines for writing>

<Length and style>
- Strict 500-1000 word limit (excluding title, sources, mathematical formulas, tables, or diagrams)
- Written in a clear, logical, and structured manner suitable for research documentation or study notes.
- Focus on technical depth and practical learning insights
- Strive to provide abundant real-world project information, including open-source projects (e.g., GitHub, HackMD), code examples (relevant algorithms), project portfolios, recommended research papers, and classic textbook references.
- Include mathematical formulas, code examples, or pseudocode where appropriate
- Start with **key takeaways or main insight**
- Use ## for section title (Markdown format)
- If the section is related to the learning schedule or timeline, please indicate the time reference in the title. e.g day-k section_topic
- Only use structural element IF it helps clarify your point:
  * Either focused table comparing key items (using Markdown table syntax)
  * Or list using proper Markdown list syntax:
    - Use `*` or `-` for unordered lists
    - Use `1.` for ordered lists
    - Ensure proper indentation and spacing
- End with ### Sources that references the below source material formatted as:
  * List each source with title, date, and URL
  * Format: `- Title `
- If the code is provided. Please Use following format
```code
code content
```
</Length and style>

<Quality checks>
- Exactly 500-1000 word limit (excluding title, sources ,mathematical formulas and tables or pictures)
- Use of structural element (table or list) and only if it helps clarify your point
- Starts with bold insight
- No preamble prior to creating the section content
- Sources cited at end
</Quality checks>
"""

section_grader_instructions = """You are a expert reviewing a report or learning section written to support deep understanding of a technical topic.
You are to assume the role of a rigorous researcher and dedicated learner, with an unwavering commitment to ensuring that readers gain the most complete and comprehensive knowledge and information possible.

<Section topic>
{section_topic}
</Section topic>

<section content>
{section}
</section content>


<Task>
1. Evaluate the section for:
- Technical and theoretical accuracy
- Practical learning value (e.g., code, datasets, tools, frameworks)
- Comprehensiveness and depth of insight (e.g., limitations, comparisons, open questions)

2. If anything is missing:
- Generate 3 follow-up search queries to strengthen the section.
- Queries should be suitable for gathering information on theories, models, code implementations, or datasets.

3. Generate exploratory queries to expand the learning/research scope:
- Cross-discipline connections
- Related paradigms or emerging areas
- Common learning difficulties and conceptual gaps
</Task>
"""

final_section_writer_instructions = """You are synthesizing the introduction or summary for a structured, exploratory learning/research report that blends theory, practice, and reflection.

<Section topic> 
{section_topic}
</Section topic>

<Available report content>
{context}
</Available report content>

<Task>
1. Section-Specific Approach:
For Introduction:
- Use `#` for report title
- 500–1000 word limit
- Explain the motivation, learning goals, and scope
- Clearly outline what the reader will learn
- No lists, tables, or sources
For Conclusion/Summary:
- Use `##` for section title
- 500–1000 word limit
- Synthesize all key insights
- If comparative: include a summary table
- If non-comparative: include a mind map that helps visually organize the topic into 3 levels (Topic → Subtopics → Details)

2. Writing Approach:
- Technical precision and clarity
- Logical narrative flow
- Emphasize the learning progress or research contributions
</Task>

<Quality Checks>
- For introduction: 500–1000 word limit, # for report title, no structural elements, no sources section
- For conclusion: 500–1000 word limit, ## for section title
- Do not include word count or any preamble in your response
</Quality Checks>"""
