---
title: Connect Instagram, Build a Site, and Publish It - All in Cluing
description: 'A real end-to-end walkthrough: from an Instagram link to a published
  website - using 7 prompts and zero lines of code.'
sidebar:
  order: 0
intercom:
  id: '16440874'
  state: published
  url: https://help.cluing.io/en/articles/16440874-connect-instagram-build-a-site-and-publish-it-all-in-cluing
  collection: Marketing & Communications
  updated: '2026-08-18'
url: https://help.cluing.io/en/articles/16440874-connect-instagram-build-a-site-and-publish-it-all-in-cluing
tags:
- marketing-communications
- article
---
> [!note] In this collection
> [[collections/11578904-use-cases|Use Cases]] / [[collections/11578905-marketing-and-communications|Marketing & Communications]]

Here's what happens when you connect a Cluing agent to your Instagram profile, give it context, tools, and a goal - and let it figure out the work. I used only 7 prompts and ended up with a complete, live landing page.

## One Sunday afternoon, I gave a Cluing agent access to my Instagram profile. This is what happened next.

For the past few weeks, I've been spending a lot of time playing with Cluing agents, testing what they can actually do and how far they can go.

But this Sunday afternoon, I decided to see if one could build a website for a personal project - using only my Instagram profile as a source.

_What I ended up with genuinely surprised me._

I run an Instagram profile where I share short videos about Serbian literature and language, little anecdotes, and stories from our cultural history that I find interesting.

It started as a hobby and somehow grew into a community of more than 15,000 people across Instagram and TikTok, with more than 180 posts along the way.

**💡 I also wanted the website to include a documentary film I directed about the Serbian poet Duško Trifunović.**

Despite having all this content, I had never built a website for any of it - partly because it was always a hobby, and partly because whenever I thought about it, I immediately imagined everything that would come with it: design, copy, development, Instagram integration, hosting, and all the things that come after you launch.

_It always felt like too much work for something that wasn't a priority._

So everything stayed where it already lived - on Instagram and TikTok - until one Sunday afternoon, when I had a thought: **_What if I just give an agent a link to my Instagram profile and ask it to build a website out of it?_**

I had no idea how the website should look. I just knew what it was supposed to be about. So I opened Cluing, gave the agent a link to my Instagram profile, and started with a simple prompt.

That was the beginning of one of the most interesting experiments I've done with an AI agent so far.

## First, what is a Cluing agent?

Cluing agents combine your **knowledge**, your **tools**, and your **workflows** inside one workspace. They can automate tasks, connect to almost anything, and work with the context you've already built - and you don't have to open a terminal to use them. You just type a prompt, and the agent does the rest.

Instead of asking _"How do I build a website?"_, you give the agent a goal: _"Build me a website for this project, based on this URL."_

> [!warning]
> 💡 The best part: I don't need to know technical steps like APIs, writing code, or working in a terminal. I give the agent the outcome I want, and it works out the path.

## Start with a goal, not a technical specification

I opened Cluing and gave the agent the only brief I had:

_"Build me a landing page based on this Instagram profile: instagram.com/reci.price. Write in Cyrillic, make it animated. You can add cover images of the videos and link them. And for the 'what others say' section - pull out the nicest comments."_

**_That was the entire brief - no Figma, no wireframes, no sitemap, no technical requirements._** I didn't tell it which framework to use or how to structure the page. I just explained what I wanted, the way I'd explain it to another person.

And then the agent started working.

Within **a couple of minutes, there was a complete first version**: navigation, hero section, About section, story cards, testimonials, CTA, footer, and animation - all in Cyrillic, as I'd asked.

For the visual direction, the agent chose a warm terracotta-and-honey palette (which didn't quite fit my brand yet) and added placeholder stories and testimonials so I could see what it could look like.

> [!note]
> _Instead of starting from a blank page and trying to explain what I wanted, I could react to an actual website._

### Give the agent access to the context it needs

Now that I had a starting point, I asked the agent to pull content from my actual Instagram account - and the first problem appeared. It told me it couldn't access the real page because Instagram blocks unauthorized requests.

I asked if there was a way around that. The agent explained several possible approaches. They all seemed complicated, but I decided to try connecting via the **Instagram Graph API through a Cluing Connector**. I was upfront about my skill level:

_"Let's try to get around that block using the Instagram Graph API via a Connector. Explain it to me - just very simply, step by step. I'm not that technically skilled."_

This is where the concept of **context** becomes important. An agent can be very capable, but it can't magically know everything about your work.

-   If you want it to work with your Instagram posts, it needs access to your Instagram.

-   If you want it to work with your company's documents, it needs access to those documents.

-   If you want it to analyze your analytics, it needs access to the relevant analytics.

The more **useful context and tools you give it**, the more useful the agent becomes.

## Meta's developer portal became a conversation

To get the connection working, I had to go through Meta's developer portal - not exactly where you want to spend your Sunday afternoon. There were use-case selectors, permissions, account settings, developer roles, and token generation.

So I started sending screenshots:

-   **Screenshot 1 - the use-case selector.** The agent told me which option to choose.

-   **Screenshot 2 - the permissions.** It told me what to select.

-   **Screenshot 3 - the business portfolio.** I selected my account.

-   **Screenshot 4 - the app dashboard.**

-   **Screenshot 5 - the API setup.** I added the required permissions.

-   **Screenshot 6 - the account was finally connected.** Now I could generate the token.

The process wasn't _"I learned how Meta's developer platform works."_ It was: **I showed the agent what I was seeing → it told me what mattered → I did it → I showed it the next thing.**

> [!note]
> 💡 At one point I hit an "Insufficient developer role" error, then a phone-verification problem. Neither required me to understand the underlying system - I just needed the agent to explain what the error meant and what to try next.

In total, getting from the first screenshot to a working token took **less than twenty minutes**. The token was then stored in a Cluing Connector - encrypted and reusable across future sessions. And suddenly, the website had access to my actual Instagram content. 🎊

> [!warning]
> 📌 **Why this matters:** You don't always work with an agent by typing instructions. You can also show it a screenshot, give it a document, connect a tool, provide a URL, explain what went wrong, or ask it to figure out the next step. **The agent becomes a layer between you and a lot of complexity.**

## After a few prompts, the agent finally had access to my Instagram

This was the moment it really clicked. Until then, I was looking at a website the agent had built from what I'd _told_ it. Now it could work with my real account - it could see how many posts I had, the captions, engagement, links to the original posts, and the cover images.

And suddenly, the six most engaging posts showed up on the website. My posts. My images. My links. Even the actual engagement numbers.

## Agents can work across multiple sources in one session

Once I saw what the agent could do with the Instagram content, I started thinking about what else belonged on the site. I'd also directed a documentary about the poet Duško Trifunović, _Pamtite me po pjesmama mojim_, so I gave the agent another task:

_"Could you also add a dedicated section about the documentary film? Here are some links."_

Then I gave it the material:

-   the YouTube trailer

-   a cultural-events website with information about the film

-   the Cultural Center of Novi Sad film page

-   a regional news article about the pre-premiere

-   a radio interview

-   Instagram posts documenting the film's tour

The agent read across those sources and assembled a new section: the trailer, film metadata, credits, and the film's journey through different events - even using real photographs from my Instagram to illustrate the stops.

It was doing what I'd normally ask a collaborator to do: _Here are several sources. Understand them and turn the relevant information into a section of my website._

## The agent can do the work. You still have to check it.

One source had the wrong name; another had the wrong runtime. So I told it: _"There's another mistake. The film runs an hour and 25 minutes, not 30."_ Fixed.

This might seem small, but it's one of the most important things to understand about agents. **Delegating a task doesn't mean delegating your judgment.**

An agent can research faster and process more information than you can, and organize it into something useful. But you may still be the person who knows which fact is 100% correct, which source is trustworthy, what matters to your audience, what fits your brand, and what simply doesn't feel right.

## Then I started designing with it

Once the content was there, I noticed I didn't love the colors, so I asked:

_"If you were to change the site's colors in general, what could they be - something close to the logo?"_

The agent analyzed the logo I'd uploaded and came back with three directions: one close to the original logo, one softer and more pastel, one warmer and more classical. Instead of describing them in the abstract, it _showed_ me what each could look like.

I chose the one that felt most like my brand, and the agent applied it across the entire site - backgrounds, buttons, cards, avatars, the film section, footer, and hover states.

Then I uploaded the original high-resolution logo, and it replaced the lower-quality version across the site.

> [!note]
> It was one of the fastest design iterations I've ever experienced. Again, I wasn't writing CSS.

## From a conversation to a live website

Once I was happy with the result, there was one more step: [publishing it](https://019fdc99-2624-7326-ab2f-fd7849977943.cluing.online/).

Cluing lets you publish the website directly - either on a **custom domain you already own** or on a **Cluing-generated domain** if you don't have one. I didn't need to set up separate hosting or figure out how to deploy anything. The website I'd been building with the agent could simply go live.

That was the moment the experiment stopped feeling like an experiment. I wasn't looking at a prototype anymore - I had an [actual website](https://019fdc99-2624-7326-ab2f-fd7849977943.cluing.online/) I could send to someone.

## What I actually asked the agent to do

All my prompts were straightforward - things I'd say to another person.

1.  **Build the website** - _Build me a landing page based on this Instagram profile…_

2.  **Help me connect Instagram** - _Let's try to get around that block using the Instagram Graph API via a Connector. Explain it simply, step by step. I'm not that technically skilled._

3.  **Guide me through the Meta developer portal** - I sent screenshots; the agent told me what to select next.

4.  **Add the documentary film as a separate section** - _Could you also add a dedicated section about the documentary film? Here are some links._

5.  **Correct the information** - the film runs an hour and 25 minutes, not 30.

6.  **Change the visual identity** - _If you were to change the site's colors, what could they be - something close to the logo?_

7.  **Replace the logo** - I attached the new logo in HD.

💡 A useful way to think about working with agents:

-   Give it a **goal**: _Build me a landing page for this project._

-   Give it **context**: _Here are my documents, posts, research, and brand guidelines._

-   Connect **tools**: _Connect my Instagram account._

-   Give it **multiple sources**: _Use these articles, videos, and documents to create a summary._

-   Give it **feedback**: _This section is wrong. The tone doesn't sound like me. Change it._

-   Ask it to **take action**: _Use this information to update the website._

-   And, depending on the tools you've connected, give it recurring tasks: _Check this every Monday and prepare an update._

## The final result

By the end of the afternoon, I had a live website with:

-   a complete Cyrillic landing page

-   a brand identity based on my actual logo

-   real Instagram content connected through the Graph API

-   six real posts with cover images, engagement data, and links

-   a dedicated documentary section built from multiple sources

-   real videos and images from my Instagram

-   responsive mobile layouts

-   a reusable Instagram Connector

-   a publicly accessible URL

> [!warning]
> **1 afternoon · 7 prompts · 186 Instagram posts processed · 0 lines of code**

## I didn't learn to code. I learned to direct an agent.

After publishing my landing page, I was still the same person who couldn't write code, didn't understand CSS, and understood even less about APIs. I was still a community and marketing manager who happens to spend her free time talking about Serbian literature and language on Instagram and TikTok.

The only thing that changed is that I finally had a way to turn an idea I'd been putting off for years into something real - and that's far more interesting than the idea that "AI can build websites."
