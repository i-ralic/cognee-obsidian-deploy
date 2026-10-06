---
title: How Agents, Skills and Connectors work together
description: Three layers and how to work with them
sidebar:
  order: 0
intercom:
  id: '16441235'
  state: published
  url: https://help.cluing.io/en/articles/16441235-how-agents-skills-and-connectors-work-together
  collection: Agents and Skills
  updated: '2026-08-18'
url: https://help.cluing.io/en/articles/16441235-how-agents-skills-and-connectors-work-together
tags:
- agents-and-skills
- article
---
> [!note] In this collection
> [[collections/19716916-agents-and-skills|Agents and Skills]]

Individually, Agents, Skills and Connectors are simple. The trick is how they stack. Once you see the three layers in one picture, every other article in this section clicks into place.

Think of each layer as answering a different question about the work you want done:

-   **Agent** - _who_ does the work. The role, the ground rules, the tone of voice.

-   **Skill** - _how_ the work gets done. The workflow, the checklist, the steps.

-   **Connector** - _where_ the work reaches. The tools the Agent can touch out in the world.

## One worked example

Imagine you run content for a small team. You want an Agent that writes SEO articles for your blog and publishes them to Ghost. Here's how the three layers stack up.

### The Agent - Content Assistant

You create an Autonomous Agent called **Content Assistant**. Its instructions are the ground rules that apply to every piece of work it does:

> [!note]
> **_Agent Instructions_**
>
> You are the content assistant for a small B2B team. Every article you write should match our published tone - friendly but professional, second-person, no jargon. Always link back to sources. Never fabricate statistics.

Those rules apply to _everything_ this Agent touches, forever.

## The Skill - how it writes SEO articles

Not every Task is an SEO article - the Agent might also draft newsletters, summarise research, or edit landing pages. So the specific workflow for writing an SEO article lives in a Skill:

> [!note]
> **_SEO Writing Skill instructions_**
> Follow our SEO writing process. Use our preferred article structure (H1, three H2s, one CTA). Include one relevant internal link. Follow our quality checklist. Pull examples and keyword research from the connected Topic.

The Skill's connected Topic holds your best-performing posts, SEO research, keyword lists, and content guidelines. That's the knowledge the Agent leans on when the Skill runs.

### The Connector - how it publishes to Ghost

Writing is one thing. Getting the article into your CMS is another. A **Ghost Blog Connector** lives at the workspace level and tells any Agent how to reach Ghost:

-   The endpoint (Ghost Admin API).

-   The auth (your admin API key, stored encrypted).

-   What to use it for - create drafts, list posts, upload images.

You wire this Connector up once. Every Agent in the workspace inherits access, so the Content Assistant can use it without any extra setup

### One Task - Put it together

Now you write a single Task under the Content Assistant Agent:

> [!note]
> **_Task description_**
>
> Use my SEO Writing skill to draft a 1,200-word article on "async onboarding for remote teams" targeting HR managers. Publish it as a draft to Ghost via the Ghost Connector when it's ready.

Look what each layer contributes:

-   **The Agent** gives it the tone, the linking rule, the "no fabricated stats" rule.

-   **The Skill** gives it the structure, the checklist, the research to pull from.

-   **The Connector** gives it the ability to actually reach Ghost and create the draft.

-   **The Task** is the one-off brief - the topic, the length, the audience, the destination.

## Why keeping them separate matters

The temptation, when you're setting things up, is to cram everything into the Agent's instructions. Don't! Keeping the layers separate is what makes each one easy to change without breaking the others:

-   **Tone drifted?**

    -   Edit the Agent's instructions... except you can't (they're permanent). Which is exactly why we keep the tone in the Agent and everything else out of it. Fresh Agent when the role really changes.

-   **Process needs updating?**

    -   Edit the Skill. New checklist item, new structure, tighter guidelines. The Agent doesn't care.

-   **Endpoint moved, API key rotated?**

    -   Edit the Connector. The Agent and the Skill don't need to know.

-   **New topic to write about?**

    -   Just a new Task. Same Agent, same Skill, same Connector.

> [!note]
> 📌 **Change one layer at a time.** If you find yourself editing all three to fix one thing, one of them is doing another's job.

## What goes where - a quick reference

-   **Tone, values, "always/never" rules** → Agent instructions.

-   **Step-by-step process, format, checklist** → Skill instructions.

-   **Research, examples, keyword lists, past work** → Topic (connected to the Skill).

-   **Endpoints, API keys, service-specific how-tos** → Connectors.

-   **The specific job — deliverable, inputs, deadline, destination** → Task description.
