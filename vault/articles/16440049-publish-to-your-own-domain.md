---
title: Publish to your own domain
description: Take a Task result live on your URL
sidebar:
  order: 0
intercom:
  id: '16440049'
  state: published
  url: https://help.cluing.io/en/articles/16440049-publish-to-your-own-domain
  collection: Agents and Skills
  updated: '2026-08-18'
url: https://help.cluing.io/en/articles/16440049-publish-to-your-own-domain
tags:
- agents-and-skills
- article
---
> [!note] In this collection
> [[collections/19716916-agents-and-skills|Agents and Skills]]

You've briefed an Agent, it built you something worth showing off - a landing page, a dashboard, a report you're proud of. Sooner or later you'll want the result to live somewhere that looks like you - to **_share it with your own URL._**

## Where to find it

To Publish your work:

1.  Open the Task you want to publish

2.  Scroll down to the bottom of the Task overview

3.  In the **Attachments** section at the top, click **Publish**

The panel that opens is the same one you'll use for both flows below - the quick web link, and your own domain

## Quick publish to the web

Inside the Task, open the Publish panel and check **Publish to the web**.

That's it. Cluing gives you a permanent link - anyone with it can open the result, no Cluing account needed. It stays live until you uncheck the box.

> [!note]
> **The difference from a preview link.** Preview links are for a 15-minute window. _Publish to the web_ is permanent. Same idea (a link anyone can open), different lifespan.

## Step 1 - Publishing to your own domain

If you'd rather serve the result from a URL you control - `reports.yourcompany.com`, `dashboard.yourcompany.com` - you can do that from the same panel.
Two things need to happen:

-   enter your domain in Cluing

-   add two records at your DNS registrar

Enter your Domain

1.  Open the Task and click **Publish**.

2.  Under **Your own domain**, type the domain or subdomain you want to use

3.  Click **Connect**. Cluing shows you two DNS records - leave that tab open

![](/media/2612736006/image.webp)

## Step 2 - Add the two DNS records at your registrar

Open your DNS provider (Cloudflare, Namecheap, GoDaddy, Google Domains - wherever you bought the domain) and add the two records Cluing showed you. Copy each value exactly.

> [!note]
> **🔐 We handle the HTTPS certificate.** No SSL to buy, no renewals to track. Once your DNS is in place, Cluing issues and renews the certificate for you. Your site is served over HTTPS from the moment it goes live.

## Come back and confirm

Once Cluing sees your DNS records, your domain lights up as verified and the Task result goes live at your URL.

> [!note]
> **📌 DNS takes a minute.** Records usually propagate in a few minutes - some providers take up to an hour. If it isn't live yet, give it time before troubleshooting.

## Unpublishing

Uncheck "**Publish to the web"** and it's gone - same for a custom domain if you've connected one. No confirmation dialog, no delay. Change your mind and switch it back on whenever.
​
