---
title: What are Connectors?
description: Connect your Agents to the tools your team already uses
sidebar:
  order: 0
intercom:
  id: '16413985'
  state: published
  url: https://help.cluing.io/en/articles/16413985-what-are-connectors
  collection: Agents and Skills
  updated: '2026-08-18'
url: https://help.cluing.io/en/articles/16413985-what-are-connectors
tags:
- agents-and-skills
- article
---
> [!note] In this collection
> [[collections/19716916-agents-and-skills|Agents and Skills]]

**Connectors** tell your Agents how to reach the tools your team already uses — GitHub, Google Analytics, Ghost, Linear, and anything else that speaks **MCP**. Set one up once, and any Agent in your workspace can use it.

## How a Connector works

Every Connector holds two things:

-   **A how-to** - the endpoint, the auth flow, and examples of how the tool should be used

-   **Its secrets** - the API keys, tokens, or credentials the tool needs to accept the request, stored encrypted

That combination is what lets your Agent do more than _know about_ a tool. It can actually call it.

## Shared across the workspace

Add a Connector once, and it's available to everyone in the workspace. When you're briefing an Autonomous Agent, just tell it to use the Connector by name.

Agents inherit access automatically. You don't wire each Agent to each Connector separately.
