---
title: How to create a Connector
sidebar:
  order: 0
intercom:
  id: '16414423'
  state: published
  url: https://help.cluing.io/en/articles/16414423-how-to-create-a-connector
  collection: Agents and Skills
  updated: '2026-08-18'
url: https://help.cluing.io/en/articles/16414423-how-to-create-a-connector
tags:
- agents-and-skills
- article
---
> [!note] In this collection
> [[collections/19716916-agents-and-skills|Agents and Skills]]

There are two ways to add a Connector to your workspace. Pick the one that fits how you're working right now.

## Create it from the Connectors page

The direct route. Best when you already know which tool you're connecting to and have the credentials ready.

1.  In the left sidebar, click **Connectors**.

2.  Start your Connector one of two ways:

    -   **From the library**

    -   **From scratch** - click **Create your first connector** to open a blank panel and write your own how-to.

### From the Library

Pick a pre-made template(GitHub, Google Analytics...). Most fields are pre-filled you only add your own access token.

![](/media/2609168198/image.webp)

### From the scratch

To c**reate your first connector from scratch, click the "Create your first con** to open a blank panel and write your own how-to.

1.  Fill in the fields:

    -   **Name**

    -   **Description** - one line about what the Connector reaches.

    -   **How to use it** - the endpoint, the auth flow, and short examples of how Agents should call it.

2.  Reference your keys and tokens **by name**, never by value. The Connector stores the raw secrets separately, encrypted.

3.  Click **Create Connector**.

![](/media/2609184270/image.webp)

## Ask an Agent to set it up with you

If you're not sure which fields to fill in, or you'd rather have the Agent walk you through it.

1.  Open any **Autonomous Agent**.

2.  In a Task, ask it something like _"Connect me to Linear so you can read our issues"_

3.  The Agent asks for what it needs - the endpoint, the type of auth, the credentials it should use

4.  The Agent creates the Connector from your answers and confirms when it's ready to use

You end up with the same Connector either way.

> [!note]
> 📌 Use this option when the tool is unfamiliar and you'd rather describe what you want to do than fill in fields you don't recognize.

## What "How to use it" should contain?

Think of this field as the manual you'd hand a new teammate. A useful one covers four things:

-   **The endpoint** - where the tool lives (URL, MCP server name, connection string).

-   **The auth** - what kind of secret is needed and the name it's referenced by.

-   **What to use it for** - 3–5 concrete things Agents should do with this Connector.

-   **What not to do** _(optional)_ - read-only limits, PII rules, anything the Agent should stay away from.
