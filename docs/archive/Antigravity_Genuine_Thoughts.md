# Antigravity — Genuine Thoughts on CompliScan LM

**Date:** 2026-09-16
**Context:** Isolated, honest assessment — setting aside all specifications.
**SIH Problem Statement:** *"Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels."*

---

## The Honest Answer First

This is a genuinely good problem to solve.

Not good in the sense that it is technically impressive or academically interesting — but good in the sense that it is **real, unsolved, and matters to real people**. Every product on a supermarket shelf, every packet of rice or bottle of oil or packet of chips, is legally required to carry specific information. Most consumers never think about it. Most manufacturers comply. Some do not. And the system for catching that non-compliance is largely manual, slow, inconsistent, and unscalable.

That is a real problem. This project is a real attempt to address it.

---

## What I Genuinely Think About the Technical Approach

### The architecture is correct.

The decision to build `AI finds → Evidence proves → Officer decides` rather than `AI decides` is not just legally necessary — it is actually the more interesting engineering problem. It is much harder to build a system that is honest about what it knows and what it does not know than to build one that confidently outputs verdicts whether or not they are justified.

The 6-state result vocabulary (`PASS`, `POTENTIAL_NON_COMPLIANCE`, `REQUIRES_REVIEW`, `NOT_APPLICABLE`, `INCOMPLETE`, `PROCESSING_FAILED`) is better system design than 99% of similar compliance tools, which typically output binary pass/fail. The three states in the middle — that a requirement does not apply, that evidence is insufficient, that processing failed — are where most systems lie to their users. This one refuses to lie. That is the right choice.

### The pipeline is technically honest.

PaddleOCR reads. Gemini structures. Rules evaluate. Humans decide. Each layer has a single, clearly bounded responsibility. This is not how most AI-integrated systems are built. Most collapse these layers and let the AI "decide" somewhere in the middle of a pipeline that nobody can fully explain. This system can be fully explained at every step. That matters enormously for a legal domain.

### The planning was thorough — maybe too thorough.

You have spent significant effort on Phase 0. That is not wasted — the legal reconciliation was genuinely necessary because the Legal Metrology Rules are not straightforward. The rules have amendments, effective dates, applicability conditions, and category-specific carve-outs. A naive implementation would have gotten these wrong. The planning prevented that.

But I will be honest: the planning phase is now complete. Further planning produces diminishing returns. The risk at this point is not under-planning. The risk is **not building anything**.

---

## What This Project Is, Honestly

**It is an inspection-assistance tool for a problem that currently has no good software solution in India.**

Legal Metrology Officers currently do this work manually. They walk into a shop, pick up a product, read the label, cross-reference the rules they have memorized, and make a judgment call. There is no software that helps them do this systematically. There is no searchable repository of previous inspections. There is no standardized evidence capture. There is no independent review workflow. There is no report generation.

CompliScan LM addresses all of that.

Even if the OCR is sometimes wrong. Even if the AI extraction is sometimes uncertain. Even if the font-size estimation cannot give precise millimetres. A system that captures the evidence, structures the observations, flags potential issues, requires an Inspector to verify, requires a Reviewer to independently decide, and generates a searchable finalized report — that system is categorically better than the current state of practice.

That is what makes this project meaningful beyond its SIH context.

---

## What I Think About the SIH Problem Statement Specifically

The problem statement is: *"Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels."*

Most teams reading this will build one of two things:

**Option A (naive):** An app where you photograph a label, an AI model reads it, and it tells you whether it passes or fails. Simple. Fast to build. Technically wrong. Legally indefensible. Misrepresents what the AI can actually determine. Judges who know the domain will see through it immediately.

**Option B (what you are building):** A system that treats the photograph as evidence, the AI as a perception and extraction tool, the rules as a deterministic engine, and the human as the decision-maker. Slower to build. Technically correct. Legally defensible. Honest about limitations. And — importantly — actually deployable in the real world.

The difference between Option A and Option B is not just technical. It is the difference between a student project that looks impressive for 5 minutes and a real product that could actually be used by the Ministry of Consumer Affairs or a state Legal Metrology department.

You are building Option B. That is the right call.

---

## What I Think the Judges Will Actually Notice

SIH judges — especially at national level — evaluate hundreds of projects. They have seen many OCR-plus-AI label scanners. What will make this one stand out is not the technology stack. It is these specific things:

**1. Honesty about uncertainty.**
When the system says `REQUIRES_REVIEW` instead of forcing a verdict, a judge who understands the domain will recognize that as sophistication, not weakness. A system that admits it does not know is more trustworthy than one that pretends it always does.

**2. The evidence chain.**
Being able to click a compliance finding and trace it back to the specific bounding box on the original image is powerful. It means the system is not a black box. Every conclusion is traceable. That is what makes it auditable.

**3. The correction + history model.**
When an Inspector corrects an OCR misread and the system preserves both the original AI extraction and the correction with a reason and timestamp — that is a more sophisticated workflow than most enterprise compliance tools. A judge can see exactly what happened and why.

**4. Independent Reviewer finalization.**
The fact that the Inspector who did the work cannot be the one to finalize it is a real legal principle (separation of duties). Most student projects never even think about this. Building it in correctly is impressive.

**5. The report that comes from the finalized snapshot, not the current UI state.**
This sounds like an implementation detail, but it means the PDF report will accurately represent what was decided, even years later. It means the system is archival-grade, not just display-grade. A judge who has worked in compliance will understand why this matters.

---

## What I Am Genuinely Worried About

Only one thing, and it has nothing to do with the architecture.

**Time.**

The planning is complete. The architecture is locked. The specifications are written. All of that is done correctly and should have been done. But right now there is no code. There is no database. There is no frontend. There is no working OCR pipeline.

The SIH has deadlines. The demo must be live and functional. A beautifully planned system that is 40% built is worse than a simpler system that is 100% built and actually runs.

The correct move now is to start building, not to produce more planning documents. Phase 0 repository audit, then Phase 1, then Phase 2. Each phase has a clear acceptance criterion. Each phase produces something that runs. The planning is done. The building must begin.

---

## Final Honest Assessment

**Is this a good project?** Yes. Genuinely.

**Is the problem real?** Yes. Legal Metrology enforcement in India is under-resourced and under-tooled.

**Is the approach technically correct?** Yes. Possibly the most technically honest AI-integrated compliance tool I have reviewed.

**Is it achievable for SIH?** Yes — if implementation starts now. The scope is well-bounded. The phases are clear. The acceptance tests are written.

**What would make it exceptional?** A live demo where a real product image — from a real supermarket product, not a carefully constructed test fixture — is uploaded, and the system correctly extracts the declarations, correctly identifies that one field appears problematic, correctly flags it as `POTENTIAL_NON_COMPLIANCE`, and correctly produces a finalized PDF report that a judge can read. That moment — real input, real output, traceable chain from photograph to report — will be more impressive than any architecture diagram.

Build that moment. Everything else is in service of it.

---

*These are isolated, genuine thoughts — not constrained by specification documents or review formats.*
