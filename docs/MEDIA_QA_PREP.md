# Media Q&A Prep — Refutation Paper

*Plain-speak answers for interviews/podcasts. Golden rules first, then the questions.
Stay measured: the rigour is the weapon. The moment you sound like you're on a crusade,
you hand defenders an excuse to dismiss you.*

*Last updated 29 July 2026 — after Biondi responded publicly, after we found and corrected an
error in our own table, and after preprint v3. New material is marked **[NEW]**.*

---

## Where things actually stand (facts, so you don't misstate them)

- The paper is a **preprint under evaluation at PCI Archaeology**, submission #1130. It is **not
  peer-reviewed yet**. Never imply otherwise.
- A recommender — the PCI equivalent of a journal editor — **took charge on 8 July 2026**. As of
  29 July, **no reviewer had yet agreed** to review it. Nine were invited and six declined. That is
  ordinary for a contested, technical, cross-disciplinary submission; don't read drama into it, and
  don't volunteer the numbers unless asked.
- **Dr Biondi responded publicly** to the paper. A reply has been posted.
- The current version is **v3**, `doi.org/10.5281/zenodo.21668674`. Everything — code, data
  identifiers, figures — is open.

---

## Six golden rules

1. **Attack the method, never the man.** "I'm critiquing the math and the result, not Biondi's
   character." Repeat it whenever a question tries to bait you into "is he a fraud."
2. **Concede what's real.** His ship/bridge/dam (surface) work is legitimate. Saying so makes you
   credible and makes the deep claim stand out as the one weak link.
3. **"His method doesn't show it" ≠ "there's nothing there."** You haven't disproven underground
   Giza structures; you've shown his technique can't see them and invents them on empty ground.
4. **You invite the test.** You're not slamming a door — you're asking for the one experiment that
   would settle it (run with controls on a site of known structure). That's the high ground.
5. **Plain words win.** "It's a Fourier transform that draws a picture out of noise." Don't
   out-jargon them; out-clarity them.
6. **[NEW] Own your own errors first and fast.** You found a mistake in your own table and
   corrected it publicly before any reviewer saw it. Lead with that when it comes up. It is the
   single strongest credibility card you hold, and it only works if you never sound reluctant.

---

## The core questions

**Q: In one sentence, what did you find?**
A: I rebuilt Biondi's own method from his published papers and patent, added the basic quality-checks
he left out, and it turned a pile of surface noise into a confident-looking "underground structure"
on a site where we know exactly what's below — so the method invents structures, it doesn't find them.

**Q: Are you saying there's nothing under the Giza pyramids?**
A: No — and I'm careful about this. I'm saying his *method* can't reliably see what's down there, and
when you test it honestly it produces fake structures. Whether something real exists under Giza is a
separate question that this technique simply can't answer.

**Q: How can a satellite "see" underground at all? Isn't that the whole magic?**
A: It can't, and Biondi agrees — his own paper says radar doesn't penetrate solid rock. The idea is
indirect: the ground is always faintly vibrating, and the satellite measures that surface wobble.
Then he tries to work backwards from the wobble to what's underground. Measuring the wobble is real.
Working backwards to deep 3-D structure is where it falls apart.

**Q: So what exactly is wrong with his method?**
A: Three things, plainly. One: the core step is a Fourier transform — a standard piece of math that
will draw a structured picture out of *any* data, including pure noise. Two: to turn that picture into
"depth," he plugs in a frequency of 22,000 Hz, which is ultrasonic — physically impossible for the
ground vibrations he's describing. Three: he runs no control tests. When I add the controls, the
"structures" are exposed as surface noise.

**Q: What's the "22,000 Hz" thing in plain terms?**
A: Depth in his method is just the picture multiplied by a number, and that number comes from a chosen
frequency. He picks 22 kHz. I showed that the *same* picture, with a realistic frequency instead,
puts the feature at a few metres down instead of two kilometres. The "depth" isn't measured — it's
dialled in. Same data, any depth you like, depending on the knob.

**Q: What's a "null test" and why does it matter so much?**
A: It's the simplest honesty check in science. You scramble your own data — destroy any real signal —
and re-run. If you still get a "structure," then your method makes structures out of nothing. He never
did this. I did, and the scrambled data looked just like his "discoveries."

**Q: Tell me about the Butte experiment — the smoking gun.**
A: Butte, Montana is the most thoroughly mapped underground mining area on Earth — we know every tunnel
level and the water table depth. I ran his exact recipe there. It produced a dramatic, confident
"detection," 1,720 times above the noise — and it sat right at the surface, matching *none* of the
real tunnels or the water table. A textbook false alarm, on ground we know cold. That's how his
"shafts" are made.

**[NEW] Q: Has it happened on more than one site?**
A: Yes. The clearest second case is Bingham Canyon in Utah — an open-pit copper mine, so we know
what's there. Run properly, the method puts its "structure" three and a half metres down, which is
essentially the surface. It's the same false alarm as Butte, on different ground, from a different
satellite pass. One artifact is an anecdote. Two, on known ground, is a pattern.

---

## [NEW] The correction — rehearse this one hardest

*This will come up, because it's now public in three places: the reply to Biondi, the release notes,
and the letter to the journal. Treat it as an asset, not a wound.*

**Q: You found a mistake in your own paper. Doesn't that undermine everything?**
A: It's a fair thing to ask, so let me be exact about what it was. One row of one table — a South
African power station site — had been run at a different setting from the other rows, and I hadn't
noticed. I found it myself, while stress-testing my own work against Biondi's criticism. I corrected
it, posted a new version, told the journal's editor before any reviewer had even been assigned, and
put the whole thing in the open. That's the process working. What would undermine everything is if
someone else had found it and I'd argued about it.

**Q: What did the correction change?**
A: It made the result stronger, which is the awkwardly convenient truth. The old number sat exactly
on my own cut-off for "is this a real detection" — right on the line, the weakest row in the table.
The corrected number is well below the line. Nothing in the paper's conclusions changed. If I'd been
massaging results, that's not the direction I'd have massaged.

**Q: How do we know there aren't more errors?**
A: You don't, and neither do I — that's precisely why everything is public. The code, the settings,
the satellite scene IDs, the figures, all of it. Anyone can re-run it. I also found two further
weaknesses in my own quality-checks during the same exercise and published those too, before anyone
asked. I'd rather be the person who keeps finding his own problems than the person who never finds any.

**Q: What were those two other weaknesses?**
A: Both were in my safety checks, and both made my checks too *lenient* — so fixing them makes my
negative result more solid, not less. First, my "is this just a surface effect?" test used a
percentage of the depth scale, and the depth scale stretches depending on a setting, so the test
quietly meant different things in different runs. Now it's a fixed distance in metres. Second, my
scramble test wasn't scrambling hard enough — the way the data overlaps means some smoothness
survives scrambling even in pure noise. I built a stricter one. Both are published.

**Q: Why haven't you put those fixes in the paper yet?**
A: Because the paper is with an editor right now. Changing every number in the results table
mid-review would mean reviewers are reading one thing and being asked to evaluate another. The fixes
are written, tested and public — anyone can look at them today. They go into the paper at revision,
where they belong.

---

## The hostile / credibility questions (rehearse these most)

**Q: Are you calling Filippo Biondi a fraud?**
A: No. I want to be clear about that. I can prove things about the mathematics — I can't read his mind.
The most likely story isn't fraud, it's self-deception: he has a real tool, he skipped the safety
checks, and the math handed him confident pictures he believed. That happens to honest people.

**[NEW] Q: Biondi responded to you. What did he say, and did he have a point?**
A: He raised specific technical objections — essentially, that I might have got a different answer if
I'd made different processing choices at three points in the pipeline. That's a legitimate challenge
and I took it seriously: I ran ninety-six versions of the analysis, crossing every combination of
those choices, and published all of them. The answer didn't change. What the exercise did do was find
that error in my own table, which is a good argument for engaging with your critics rather than
dismissing them.

**[NEW] Q: So his criticism was wrong?**
A: His criticism was reasonable and worth testing — the outcome was that the result held. But there's
a deeper point buried in it. None of those three settings is written down anywhere in his published
paper, his patent, or his presentations. If a method's answer depends on four knobs and none of them
are disclosed, nobody can independently check it. That's not a small thing; it's most of the problem.

**Q: Who are you to challenge a published scientist? What are your credentials?**
A: Fair question. I'm an independent researcher, and you shouldn't take my word for it — that's the
whole point. Everything I did is open: the code, the data, the steps. Anyone with a laptop can run it
and check. Science isn't about credentials, it's about whether the result reproduces. Mine does;
his doesn't.

**Q: His paper was peer-reviewed. Yours isn't. Why should we believe you?**
A: Two things. First, his 2022 paper was about the *pyramid's interior* — the dramatic deep-city Giza
claims were announced at a press conference, never peer-reviewed. Second, peer review isn't magic; it's
a few people reading a paper. Reproduction is stronger than review, and I reproduced his method and it
failed its own tests. Mine is in review right now, openly, at a platform that publishes the reviews
alongside the paper.

**Q: He used 200+ scans from four different satellites and they all agree. Doesn't that prove it's real?**
A: It feels convincing, but it's backwards. If your method has a built-in flaw, it produces the *same*
flaw on every scan and every satellite — because it's the same math each time. Consistency proves the
method is consistent, not that the structures are real. I can make the identical fake "appear" on a
hundred scans of an empty site. Agreement isn't evidence; ground truth is.

**Q: Isn't this just mainstream science gatekeeping a maverick who found something inconvenient?**
A: I get why it looks that way, and honestly I went in wanting it to be real — it'd be amazing. But I
followed the method, not the politics. I even gave it every advantage: his exact recipe, the same kind
of satellite data, his own best-case site. It still failed. I'm not defending an institution; I'm
showing my work and asking him to show his.

**[NEW] Q: Did you use AI to write this paper?**
A: Yes, and it's disclosed in the paper itself — I declared it when I submitted. I directed the work,
chose the experiments, and reviewed every result; AI assisted with the coding and the mathematics.
It's a tool, like the statistics packages every scientist uses. What matters is whether the output is
checkable, and it is: run the code yourself. No AI is listed as an author, because authorship means
taking responsibility, and the responsibility is mine.

**Q: Have you contacted Biondi? Would you debate him?**
A: We've exchanged views publicly, and I'd welcome more. My paper literally invites the deciding
experiment — run the method with controls on a site where we independently know what's underground.
If it works there, I'll say so publicly. That's the offer.

**Q: What would change your mind?**
A: One clean result: the method, with controls, producing a real above-noise detection that matches
known underground structure in the right place and depth — using honest physics, not the 22 kHz dial.
Show me that and I'll change my conclusion the same day.

---

## The "so what" questions

**Q: Does this mean his bridge and dam monitoring work is also wrong?**
A: No — and this is important. That work measures movement of things *on the surface*, and it's solid,
peer-reviewed, genuinely useful. He's a capable engineer. The problem is only the leap from "I can
measure the surface" to "I can therefore map cities kilometres underground." One is real; the other
isn't.

**Q: Why does this matter? It's just pyramids.**
A: Because real money, real archaeology, and public trust are riding on it, and because the same method
gets pointed at other sites. If a technique can manufacture confident "discoveries" from noise, people
should know before they dig, fund, or believe. That's worth getting right.

**Q: What happens next?**
A: It's with an editor at PCI Archaeology, an open peer-review platform where the reviews get published
alongside the paper. Reviewers are being sought. Whatever they say will be public. And the honest next
step scientifically is still the ground-truth test I keep offering.

**[NEW] Q: Would you run this on Giza itself?**
A: I'd like to. The obstacle is mundane: there's no suitable free satellite data over Giza in the open
archives, and commissioning a new tasking costs real money I don't currently have. But it's worth
saying this doesn't weaken the finding. The argument is about whether the *method* works at all, and
you test that on ground where you already know the answer. Giza is the one place you *can't* check the
method, because nobody knows what's down there. That's rather the point.

---

## Traps to avoid (say these wrong and it backfires)

- Don't say "there's nothing under Giza." (You didn't show that.)
- Don't say "he's a fraud / grifter." (You can't prove intent; it makes you the aggressor.)
- Don't say "satellites can't measure the ground." (They can — that's his real, valid part.)
- Don't get pulled into Atlantis / ancient-aliens / energy-grid lore. ("That's outside what I tested —
  I can only speak to whether the radar method works.")
- Don't overclaim certainty. "Reproducible as an artifact" and "doesn't survive controls" — not
  "definitely fake."
- **[NEW]** Don't say the paper is peer-reviewed. It's a preprint under evaluation.
- **[NEW]** Don't say Biondi "admitted" or "conceded" anything. He raised objections; the analysis
  held. Overstating his response is the fastest way to lose the high ground you currently hold.
- **[NEW]** Don't say the YouTube account was definitely him. It's very likely genuine but was never
  verified, and the blue mark on it is a channel-membership badge, not a verification tick.
- **[NEW]** Don't quote the "z = 12" figure from the Bingham analysis without its context. It comes
  from the *weaker* of two statistical tests — the one being replaced precisely because it's too easy
  to beat. On the proper test the site is nowhere near a detection. Said alone, "z = 12" hands someone
  a headline claiming your own data found something.
- **[NEW]** Don't get defensive about the correction. One row, found by you, fixed by you, disclosed
  before review. Say it flatly and move on.
