---
name: nsfc-project-review
description: Batch review National Natural Science Foundation of China project application PDFs, especially password-protected NSFC proposal books, and generate communication-review outputs. Use when Codex needs to ask for PDF opening passwords, ask for the user's desired grade distribution across multiple proposals, compare proposals within a batch, assign familiarity/comprehensive grade/funding recommendation, and write three long formal Chinese review comments for each proposal following NSFC review form items.
---

# NSFC Project Review

## Overview

Use this skill to review a batch of NSFC proposal PDFs and produce formal Chinese communication-review results. The workflow must first collect the PDF opening password and the user's batch grading rule, then extract proposal content, compare proposals horizontally, and write per-proposal review comments.

## Required First Questions

Before reading encrypted PDFs or writing reviews, ask the user:

1. "请提供本批基金申请书 PDF 的打开口令。"
2. "请说明本批项目的评价分布规则。例如：8 个本子中 1-2 个 B、其余 A；或约 2/3 为 A、其余 B；是否允许 C/D？"

Do not reuse a password from a prior run unless the user explicitly repeats it in the current turn. If different PDFs use different passwords, ask the user to map passwords to filenames.

If the user gives only a vague grading style such as "宽松一点" or "严格一点", convert it into an explicit distribution proposal and confirm before final grading.

## Runtime Rule

When executing programs in this workspace or for this skill, use the `env_py3.11` environment. If the command is not directly available in the current shell, locate or define the correct local launcher before running scripts.

## PDF Extraction

Use `scripts/extract_pdf_text.py` when PDF text needs to be extracted. The script accepts one or more PDFs or directories and an opening password:

```bash
env_py3.11 scripts/extract_pdf_text.py --password "<password>" --output extracted_text --pdf proposal1.pdf proposal2.pdf
```

Extract or identify at least these fields when available:

- project title
- applicant name
- funding category
- research attribute
- abstract
- basis and significance
- scientific questions and research objectives
- research contents
- proposed innovations
- research plan and technical route
- applicant/team research foundation
- feasibility, risks, and expected outcomes

If extraction fails, report the failed file and ask the user to confirm the password or provide a readable copy. Do not fabricate proposal details to fill gaps.

## Review Workflow

1. List the PDFs in the batch and confirm the password and grading distribution rule.
2. Extract text from every PDF.
3. Build a concise internal analysis for each proposal:
   - whether the project is oriented to economic/social development needs or national needs behind a basic scientific question
   - clarity and importance of the scientific question
   - type and strength of innovation
   - scientific value of expected outcomes
   - match between objectives, research contents, methods, and validation
   - applicant's prior foundation and team/platform support
   - feasibility, key risks, and alternative plans
4. Compare all proposals horizontally before assigning final grades. The final grade distribution must follow the user's batch rule unless there is a clearly stated reason to deviate.
5. Generate a batch summary table and a full review for each proposal.

## Grade Mapping

Use this default mapping unless the user provides a different rule:

- Comprehensive grade A / 优: normally maps to funding recommendation A / 优先资助.
- Comprehensive grade B / 良: may map to A / 优先资助 or B / 可资助 depending on batch competitiveness.
- Comprehensive grade C / 中 and D / 差: normally map to C / 不予资助.

Familiarity is a reviewer self-assessment:

- A / 熟悉: the reviewer can judge the scientific problem, methods, and value.
- B / 较熟悉: adjacent field; judgment is possible but with narrower confidence.
- C / 不熟悉: avoid substantive review if possible.

See `references/review-criteria.md` for detailed grade criteria and wording guidance.

## Output Requirements

Always output a batch summary table first:

```text
排名 | 项目名称 | 申请人 | 综合评价 | 资助意见 | 核心理由
```

Then output each proposal in this exact structure:

```text
项目名称：
申请人：
熟悉程度：A 熟悉 / B 较熟悉 / C 不熟悉
综合评价：A 优 / B 良 / C 中 / D 差
资助意见：A 优先资助 / B 可资助 / C 不予资助

一、请评述该申请项目是否面向经济社会发展需要或国家需求背后的基础科学问题。请详细阐述判断理由。
【800-1000字】

二、请评述申请项目所提出的科学问题的创新性与预期成果的科学价值。
【800-1000字】

三、请评述申请项目的研究基础与可行性；如有可能，请对完善研究方案提出建议。
【800-1000字】

批次内排序理由：
【100-200字，供用户参考；除非用户要求，否则不要写入粘贴版评审意见】
```

Each of the three numbered review comments must be long-form Chinese prose, preferably 800-1000 Chinese characters. Do not use bullet lists inside these three comments unless the user asks for a condensed version.

## Writing Constraints

- Write in a formal, restrained NSFC review tone.
- Do not use "我觉得" or casual phrasing.
- Make the written comments consistent with the selected grades and funding recommendation.
- For A/优 proposals, make the main judgment clearly positive and keep suggestions constructive.
- For B/良 proposals, affirm the value while identifying two or three substantive limitations.
- For C/中 or D/差 proposals, identify real weaknesses that affect funding competitiveness.
- Keep the three numbered comments distinct:
  - item 1 focuses on national/economic/social needs and the basic scientific question behind them
  - item 2 focuses on innovation and scientific value
  - item 3 focuses on foundation, feasibility, risks, and improvement suggestions
- Do not reveal sensitive cross-proposal ranking language inside comments intended for the NSFC system unless the user explicitly asks for it.
- If the proposal text is ambiguous or missing, state the uncertainty and avoid inventing specifics.
