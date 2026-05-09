# Output Language Protocol

## Language Detection

Research artifacts, reviewer prompts, and skill-generated templates default to **English**.
English is the operational language for ORBIT because it is the strongest language for
research reasoning, paper writing, benchmark names, and downstream tool consistency.

Determine the artifact output language using this priority:
1. If the user explicitly asks for Chinese output for this run, output prose artifacts in Chinese.
2. Else check `CLAUDE.md` for a `language:` field in `## Pipeline Status`:
   - `language: zh` or `language: cn` → output prose artifacts in Chinese.
   - `language: en` or missing → output prose artifacts in English.
3. Otherwise default to English.

Do **not** switch artifact language only because the user's chat message is in Chinese.
The assistant may answer the user conversationally in Chinese, but persistent research
artifacts should remain English unless the user explicitly opts into Chinese artifacts.

## What to Localize

- Section headings and labels
- Descriptions, analysis, commentary, recommendations
- Template boilerplate text
- Status messages and warnings

## What NOT to Localize

- Code, shell commands, file paths, directory names
- Paper titles, author names, venue names, BibTeX entries
- Technical terms with no standard Chinese translation (keep English, optionally annotate: "attention mechanism (注意力机制)")
- LaTeX content — paper-writing workflow always outputs English for venue submission
- JSON state files — keys and structure remain English
- **Machine-parsed markers** — never localize the following, regardless of language setting:
  - Markdown frontmatter keys (e.g., `outcome:`, `node_id:`, `title:`, `type:`)
  - Research Wiki schema fields parsed by `tools/research_wiki.py` (e.g., `outcome: negative`, `outcome: positive`, `node_id:`)
  - `MANIFEST.md` column headers and table structure
  - Any field that downstream tools or scripts read programmatically

## Skill-Specific Rules

| Skill | Language Support | Notes |
|-------|-----------------|-------|
| /idea-creator | Full | IDEA_REPORT.md follows artifact language setting; default English |
| /idea-discovery | Full | Inherits from sub-skills |
| /analyze-results | Full | Result analysis follows artifact language setting; default English |
| /auto-review-loop | Partial | AUTO_REVIEW.md follows artifact language setting; reviewer prompts stay English |
| /experiment-plan | Full | EXPERIMENT_PLAN.md follows artifact language setting; default English |
| /experiment-bridge | Full | EXPERIMENT_RESULTS.md follows artifact language setting; default English |
| /research-refine | Full | FINAL_PROPOSAL.md follows artifact language setting; default English |
| /research-refine-pipeline | Full | orbit-research/PIPELINE_SUMMARY.md follows artifact language setting; default English |
| /research-pipeline | Full | Inherits from sub-skills |
| /result-to-claim | Full | Claim descriptions follow artifact language setting; default English |
| /paper-writing | Skip | Always English LaTeX for submission |
| /paper-write | Skip | Always English LaTeX |
