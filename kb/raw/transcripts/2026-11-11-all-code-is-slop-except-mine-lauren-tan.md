---
source_url: https://github.com/The-Focus-AI/ai-engineer-code-2026-nov/blob/main/talks/2026-11-11-all-code-is-slop-except-mine/transcript.md
video_url: https://youtu.be/O_zcc6Xl12g
speaker: Lauren "poteto" Tan (SpaceXSI / xAI, Grokbot)
event: AI Engineer Code Summit, 2026-11-11, mainstage
ingested: 2026-11-15
sha256: ee45e9701c2a6251113f9d4ddc7aac2c8909075b122c566f7da42dca36b92599
scope: verbatim third-party transcript (Qwen3-ASR-1.7B, kept as transcribed — product name renders inconsistently); primary source for the potato-pyramid guardrail work
---

---
title: "All Code Is Slop (Except Mine)"
speakers:
  - name: Lauren Tan
    affiliation: "SpaceXSI (xAI)"
room: "Continental 4–6 (Mainstage)"
starts_at: 2026-11-11T10:10:00-08:00
ends_at: 2026-11-11T10:30:00-08:00
format: talk
recording: 2026-11-11_1000_lauren-tan
duration: 1107.5
source: qwen3-asr-1.7b
---

> The recording opens on the end of the MC's introduction. The program ran about ten minutes
> early: the talk began around 10:00, not at its scheduled 10:10.
>
> Transcribed locally with Qwen3-ASR 1.7B (timings per ~5 s segment), prompted with the
> speaker names of overlapping sessions. "Duckbill" at 00:12:37 comes from that prompt, not
> the audio: it is the MC's company, and the Voice Memos transcript has "bombadil" there.
> The product name is kept as transcribed ("GAPA", "Grokbot", "Grovbot", "Groppo", "Gau"); the
> abstract calls it Grok Bot, and the Voice Memos transcript never says "Grok". The Voice
> Memos transcript is kept beside it as `transcript.txt`.

### 00:00:00 — Introduction

Engineer at SpaceX Superintelligence. Skateboarder, whatever. Please. Hello everyone. I'm going to be giving you my slides, but my name is Potato. Also known as Lauren, and I'm very excited to chat with all of you today. Maybe we can get a big round of applause for our tech. Or not. Oh, there you go! Woo! All right. So. Again, I'm. My name is Potato. I work on GAPA at SpaceXSI.

And can I just do a quick show of hands? How many of you have ever looked at code that somebody else wrote and you thought? That's all slop. Well, I have two. But today, I'm going to convince you that you can turn that slope into gold.

### 00:01:40 — Coding machines and trust

And so I did something crazy last month, and I shipped three thousand requests to production. Now, before agents, we never really cared about volume, except for the outliers. At my previous company, we called these people coding machines. People like Brett Taylor, who famously rewrote all of Google Apps. In a weekend, just an insanely productive engineer. And well, with agents, anyone can now be a coding machine, and my thesis is that.

The job of a software engineer. The meta of being a software engineer. Is figuring out how to maintain or even improve the quality of the code. While massively increasing your productivity, to get there, some people like to call this a software factory. But I like to keep it simple, and I think of it as. All about trust—not blind trust, but investing in your agent's environment. So you can trust that your agents are going to do the right thing. Now it takes quite a lot of effort to get there.

And it took me six months to get to a point where. I could ship thousands of polar bears. A lot of them can't speak, but it's certainly possible. And it will take you much less time than I did.

### 00:02:55 — From low trust to high trust

So let's start by talking about how we move from a low trust environment to a high trust one. So this inverse pyramid is how I think about where to spend time on reagents environment. The first two layers are deterministic, so using your code itself. So things like good API design, architecture, refactoring. Or using lintools type systems, compilers, or different kinds of testing. And you can use both of these layers together to constrain what agents can do, and force them to do the right thing by default.

Verification, both runtime and formal, are great tools to layer on to find bugs. And check properties and the invariance in your system that you want to hold true. And also help you check whether or not the agent understood your goals and your intent. And then finally, you want to layer with a little bit of prose. So things like rules, skills, agents. Dot. Nd things that require judgment.

Well, let's start with the Coinbase. Agents generate their outputs based on their inputs. And so the quality of the input really matters, and it just so happens that your codebase is one of the largest inputs. So, whenever you're crafting your agent, think about how you can make that a deterministic check. Instead of adding another line to your rules or your agent's dot md, because it's far more reproducible, it's in code.

And it meant you trusted more.

### 00:04:26 — The codebase as a garden

And the analogy that I like to use is that your codebase is kind of like a garden. You know, code used to arrive a few pull requests at a time. And I remember going into work in twenty four. And reviewing the three pull requests that my colleagues wrote, colleagues wrote, and today that number is more like. Three hundred. So you know every engineer is now a team of.

Hundreds, even thousands of agents, and code is arriving so rapidly that it almost feels like. A continuous stream, and it almost feels organic. Like a living thing, and in this analogy, the codebase. The constraints that you impose, the guardrails that you put up, are the concrete foundations that. The new code that your agents write grow around, just like the building in this picture. And so, in many ways, the job of being a software engineer is.

Kind of becoming like garbage because code is the biggest input for agents. It means that any workarounds, anti-patterns, deprecated code, tech debt. It's now likely to be just copied by the next agent, since it looks like the established pattern in the codebase. And it's like you have some weeds or pests growing in your garden. And then they spread everywhere before you know it. So you want to make your codebase as pristine as possible, so that agents are always copying the right stuff.

### 00:05:56 — Dune and organic architecture

All right. Let's look at some real examples. So Dune is a client framework that we created for Grokbot. To implement this idea for organic architecture. It's not really that interesting technically. You can kind of think of Dune as kind of like Next.js for Electron apps. But the interesting part of D is that it has a lot of constraints. And rules that we've encoded a lot of the lessons that we've learned building desktop applications.

And one such lesson is that anything that requires nuance to resolve often needs to solve. You know, your classic example is use effect and react. Right, it has its use cases. It's often misused. Some people just think that to ensure. In other words, it really requires a lot of nuance to move on. And agents are not bad. So our solution has been to just ban it in part two.

And it's really only allowed in some places inside of Doom APIs. And effectively, this problem has now been categorically eliminated, and we never need to catch that during a court review again. Another interesting pattern that we use is context through directory structure. So one anti-pattern that we saw with Cursor, which is an electrona. Is that users would often import main thread code into a renderer thread, which would cause long tasks and jank.

So in Groppo and in new apps, we make this very conventional. We have these two top-level directories, literally called Electron Vendor and Electron Main. And imports between them are forbidden or banned by our dependency graph analyzer. And some of the goals, and again, you know, these are simple rules to set up, but. It means one less thing that we need to review and think about, you know, during COVID.

### 00:07:54 — Agents and markdown

And then, one more surprising thing that I've seen is Asians using markdown. So things like documentation, code comments, rules, or skills. And you use this as a place to write down your justifications for not doing something. Or I don't remember seeing this, but to over rotate on some small correction that you made. And you treat it like a hard rule that can never be broken ever again.

And here's another example from Cursor. So agents really loved using imperative timers. So things like set timeout, request animation frame, request idle callback, and they were using these as quick fixes because. They were really patching over an architecture clash between. VS Code's imperative style and React's declarative style. So our choice of architecture actually made both. The client and the user performance is much worse. And if you've ever done any performance work in JavaScript, you'll know that when you have tons of timers being rapidly created and destroyed.

Causes a lot of major garbage collection, which causes a lot of lag and jam. But the worst part is that agents wrote a lot of code comments, like you can see in red here. Explaining why this quick fix was justified. Before you know it, we have pingers spreading everywhere, and the you know the performance of the app really suffered. Now in Grovbot, we learned our lesson there, and we decided to just.

Ban 99% of comments because. They go stale easily. Humans just really don't bother reading the comments a lot anyway. And again, it gives an agent the escape hatch to justify not doing the right thing because it's. Hard, and the worst part about condoms, though, is that they're not enforceable. So what seems well intentioned, you know, like. I'm gonna tell the next agent not to do something. Never ends up actually being anything that you can trust.

So in Gau and in Dune, we now have mid rules that give. Good and very helpful error messages telling the agent to fix the root. On a new problem, rather than just patching on. And so our general principle is that every time we correct our agents, it turns into one of these deterministic checks. Or we think about how to categorically eliminate that problem in the code through better API design, through better architecture.

And if you do this enough times, you find that you have just less things to look out for in code review. And at some point, you realize there's there's nothing left to review, and you can just let agents. Merge most of their full requests.

### 00:10:40 — Verification

All right. Moving on, verification is also a really big part of how we make our agents more autonomous. And also increase our confidence and trust in their work. And our code review process has now really shrunk into looking at verification artifacts. Instead, so things like videos, screenshots. Dimensions. And the most basic example of this is runtime verification, which is just a fancy way of saying. Giving your agent a way to run the code for itself.

And use debugging tools that you know human developers use as well, like the Chrome Dev Tools Protocol. In our runtime verification skills, we have this thing that we call a feature map, and that's basically kind of like. A snapshot of all of the features that are available in the application from the user's point of view. And so, with this, agents don't need to guess when you say, you know, the thingy in the left sidebar. It gives you some.

Shared vocabulary. We also make use of custom CLI that I do so that agents can reuse the CLI and the driver. Every time, which cuts down on token usage, and is also testable. And then recently, we've also started looking at formal verification. So we now use TLA+ to do some model checking. Major user flows such as notifications across multiple devices and platforms. We use a leaning as ball for pruning certain algorithms. For example, we have our own.

We wrote our own custom virtualization library, and we use the there to check that we don't have. You know, flickering or jittering problems, and we're still experimenting with this approach overall. It seems very promising. We've already found quite a few bugs with formal verification, but it's certainly not a silver bullet. And we're treating it as another tool, another layer. In our agents' environment. And then this is a very fast video, but.

Another thing that we just started looking at is property-based testing as well for UIs. So we use this library called Duckbill. And this has also caught a few UI bugs for us already.

### 00:12:50 — Where the tokens go

Okay, so Zunia, I saw this tweet from Cindy, and six months ago, she said that she was. She's talking about not being able to trust her agents because of subtle bugs that were getting merged. And really, what was missing for her in being able to trust her agents was the verification process. And now, six months later, she says that seventy percent of her daily tokens go into verification.

And I say that tracks with what I see as well. That most of my token usage goes to documentation. And if you really look closely at the process, none of these things here. Are new or novel techniques that we've never had before. These are just good software engineering tools. But ones that might have been prohibitively expensive to use before, as they were hard to understand, or by or maintain.

But agents drastically cut this cost down. And really, we are entering a golden age of software testing and application with agents. Let us test everything to a much better degree than used to be economical. And then formal verification can also help you better reason about how your models work and whether your agents really understand intent and goals. I made this new skill called State Chart in my plugin P Stack.

Potato stack, which helps you visualize state machines from the user's point of view. And I find this much easier to review alongside the videos and screenshots that we provide. So that's been great. Sorry about the flashback.

### 00:14:22 — The promised land

Okay, now let's look at what the promised land looks like. What do you get in return for all of this? Investment. So on the Grokbot team, our velocity is. Taking off and traveling, and then our team shipped. A ridiculous eleven thousand pull requests to production, which is a wild number. The amount of releasing of the clients has also increased, and we cut a new stable version about once a day.

And then the core team is also shipping much more. And we also have a lot more casual or drive-by. Contributors who don't always have a lot of context, but they're also contributing. And in October, we had about 227 people who contributed at least one request. So, despite this velocity accelerating, you might be thinking to yourself, like, isn't this going to be chaos? Isn't this going to be a bunch of slop?

And actually, the number of PRs that get diverted has actually gotten lower on a relative basis, and is steady at. About half a percent. But I think the really interesting thing about this shipping pace and this volume of pull requests. Is that the performance of Grovbot has stayed not just stable? But has improved on multiple dimensions compared to when we launched. So startup. Typing, opening chats, switching chats—all of this has gotten faster.

And keep in mind, GraphR is still an electron app. So there is a ceiling, right? But it's already much faster than many other Asian AI startups. And for an election with this high velocity and this many people contributing. I'd say that's pretty good.

### 00:16:10 — Before you build a software factory

So before you jump into building out a software factory and you know automating everything that you can, whenever you correct your agent. Trying to do it by improving your codebase first, if possible, to prevent new occurrences of anti-patterns. And then clean up those old patterns as well, and then make sure that your verification story is really strong. A lot of this work is a prerequisite to automation anyway, and if your inner coding loop produces.

Slop. Then automating that loop just produces more slop. And you need to throw more and more and more tokens at the problem, which we all know is very expensive. And once you make these investments into you know code into your codebase, static analysis. Runtime informal verification. You start to find that many things become. Possible with these foundations, and that you can really easily build your own factory on top of these foundations.

And when you're ready, Grokbot is a great way to build that outer loop. We have tons of connectors, routines that can kick off Cursor. Cloud agents and projects, which let you orchestrate thousands of, hundreds or even thousands of agents. And as a quick example, you know whenever we cut a new release now, Grokbot will automatically spin up a new Cursor project for us. That will fuzz the entire application. The entire build.

And we'll find bugs by running the app and using it like a real user. And then it's going to open fixed PRs for each of those bugs that it finds, and it's going to auto merge it. As crazy as that sounds, and that's because our codebase is good enough that. Pull requests tend to just be good by default, and most product code that we land no longer really requires deep human review.

So. When you have solid foundations and good organic architecture, you can turn slop into gold. And you can ship with high quality, high velocity without compromising on quality. My name is Potato. Also known as Lauren. Thanks again for listening to my talk.
