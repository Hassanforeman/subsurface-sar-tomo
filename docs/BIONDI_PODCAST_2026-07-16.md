# Biondi — Symposium Podcast, 16 July 2026: quotable statements

**Source:** "What Is Hidden Under the Pyramids of Giza? — Filippo Biondi on the Symposium Podcast"
**Channel:** Symposium Podcast (129K subscribers) · **Uploaded:** 16 July 2026 · **Length:** 34:30
**URL:** https://www.youtube.com/watch?v=4E0q4deWshY
**Language:** recorded in Italian; YouTube auto-dubs to English. Quotes below are from the
Italian auto-generated transcript.

---

## ⚠️ READ THIS BEFORE QUOTING ANY OF IT

Every quote below came from a **machine transcript of Italian speech**. It demonstrably garbles
words — it renders "7 km/s" as "7 km/pler" and mangles a conference name beyond recognition. The
substance of each passage is unambiguous, but the exact wording is not yet confirmed.

**Do not put any of these in front of a journalist until you have listened to the timestamp and
confirmed the words.** A mistranslated quote becomes the story instead of the physics, and it hands
the other side a free win. Mark each one VERIFIED below once you've checked the audio.

There is no substitute for this step. Ten minutes of listening protects the whole argument.

| # | Timestamp | Verified? |
|---|---|---|
| 1 | ~12:04–12:43 | ☐ |
| 2 | ~19:51–20:30 | ☐ |
| 3 | ~20:52–21:20 | ☐ |
| 4 | ~24:09–24:39 | ☐ |

---

## Ranked by how safely you can use them

**Use freely (once verified):** #1, #2 — statements about physics and method. You are disagreeing
with a technical claim, which is exactly the ground you want to fight on.

**Use as an invitation, never an accusation:** #4.

**Handle with care, and never lead with it:** #3. It is the most striking and the most easily
turned against you. See the counter-reading.

---

## 1. Where the ~22 kHz actually comes from — ≈12:04–12:43

**Italian (as transcribed):**
> Siccome il satellite vola nello spazio a una velocità enorme, circa 7 km/s... e questo effetto
> doppler ricade nella banda dei suoni, quindi da 0 Hz a 20-30 kHz, ok? che sono i suoni. E i suoni
> dove si propagano? Nella materia, non nel vuoto. La luce si propaga solo nel vuoto. Il suono si
> propaga solo nella materia e allora è fatto. E quindi, siccome il suono si propaga solo nella
> materia, bastava solo trovare il metodo per organizzare questi suoni, studiare questi suoni in
> modo da ottenere una fotografia dell'interno.

**English:**
> Since the satellite flies through space at an enormous velocity, about 7 km/s... this Doppler
> effect falls in the band of sounds, so from 0 Hz to 20–30 kHz — which are sounds. And sounds,
> where do they propagate? In matter, not in vacuum. Light propagates only in vacuum. Sound
> propagates only in matter, and so it's done. And therefore, since sound propagates only in
> matter, it was enough to find the method to organise these sounds, to study these sounds, so as
> to obtain a photograph of the interior.

**Why this matters.** The 22 kHz investigation frequency is the number that converts his tomogram
into *depth*, and neither the 2022 paper nor patent WO2024008365A1 justifies it. This is the first
public account of where it came from.

The reasoning is a category error. The **SAR Doppler bandwidth** is a signal-processing quantity —
a beat frequency inside the radar receiver, set by platform velocity and antenna geometry. It
happens to land numerically in the same range as audible sound. He treats that numerical
coincidence as physical identity: *it's in the kHz range, therefore it is sound, therefore it
travels through rock.*

Nothing is vibrating at 22 kHz in the ground. Rock does not carry a coherent 22 kHz seismic wave
over kilometres — attenuation scales steeply with frequency, which is why reflection seismics works
in the **single-digit-to-tens-of-hertz** range, three orders of magnitude lower.

**Plain-language version for an interview:**
> His depth numbers come from treating the radar's own internal frequency as if it were a sound
> travelling through rock. They're both measured in hertz and they land on similar numbers, so
> they look like the same thing. They aren't. One is a number inside the satellite's electronics;
> the other is a physical vibration in the ground. Real seismics works at a few tens of hertz,
> because high frequencies die out in rock almost immediately. Twenty-two thousand hertz doesn't
> travel two kilometres through limestone — it doesn't travel two metres.

**Counter-reading to expect:** that he's speaking loosely for a lay audience and the papers are
more rigorous. Fair — so the response is not "he's wrong on a podcast," it's: *the papers never
state where 22 kHz comes from at all, and this is the only account anyone has been given.*

---

## 2. "Mine is reflection seismics, done with the satellite" — ≈19:51–20:30

**Italian:**
> ...c'è la sismica a riflessione, che alla fine la mia è una sismica a riflessione, ma fatta col
> satellite, perché vado a vedere istante per istante la sismica che c'è pixel su pixel
> dell'immagine. La sismica a riflessione classica inseriscono dei geofoni sulla Terra, dei
> microfoni... e il microfono ascolta la Terra... e quindi si fa l'inversione tomografica. È la
> stessa cosa.

**English:**
> ...there's reflection seismics — in the end mine is a reflection seismics, but done with the
> satellite, because I look instant by instant at the seismics present, pixel by pixel of the
> image. In classical reflection seismics they put geophones in the Earth, microphones... and the
> microphone listens to the Earth... and then you do the tomographic inversion. **It's the same
> thing.**

**Why this matters.** It is a falsifiable claim of equivalence, and the equivalence fails on
requirements, not on opinion. Reflection seismics needs three things he does not have:

1. **A controlled source** — a shot, a vibroseis truck, a known bang at a known time and place. He
   has none. Without a source there is no travel time to measure.
2. **An array of receivers at known positions.** Geophone spreads are surveyed to centimetres. He
   has one satellite.
3. **Travel-time picking against that known geometry.** This is what makes the inversion
   well-posed. Without it, "tomographic inversion" has no constraint to invert against.

He is claiming the output of an inversion without the inputs that make an inversion meaningful.

**Plain-language version:**
> Reflection seismics works because you set off a known bang at a known spot, and dozens of
> microphones at surveyed positions time how long the echo takes. All three of those are what make
> the maths solvable. He has no bang, one sensor, and no timings. Calling it the same thing is like
> saying you've done a CT scan because you took one photograph.

---

## 3. "Very often one was inverting noise" — ≈20:52–21:20 ⚠️ CARE

**Italian:**
> ...mi ci sono dedicato parecchio, 4-5 anni almeno, perché molte cose le abbiamo buttate via
> perché non avevano senso... perché molto spesso si invertiva rumore, perché magari c'era troppo
> rumore... però molti, molti esperimenti sono andati bene e li abbiamo tenuti. 2-300 esperimenti
> sono andati bene su altre cose.

**English:**
> I've dedicated a great deal to it, four or five years at least, because **many things we threw
> away because they made no sense**... because **very often one was inverting noise**, because
> there was maybe too much noise... but many, many experiments went well and **we kept them**.
> Two or three hundred experiments went well on other things.

**Why it's striking.** Two things sit in one sentence. He concedes the process can **invert
noise** — the exact failure your paper demonstrates. And he describes **retaining runs that "went
well" and discarding runs that "made no sense."**

For a method whose core step is a DFT — which returns structured output from *any* input,
including noise — selecting on whether the output looks sensible does not filter out the false
positives. It selects *for* them. It also explains the "200+ consistent results": consistency
measured only across the runs that were kept is not evidence of anything.

### ⚠️ The counter-reading you must be ready for

He can reasonably say: *"I meant we discarded scenes with poor signal-to-noise. That is ordinary
quality control, which every remote-sensing scientist does."* **That defence is legitimate and
partly correct** — discarding bad-SNR scenes genuinely is standard practice.

If you assert "Biondi admitted he inverts noise" and he gives that answer, you look like you
over-read a quote, and you lose the exchange in front of an audience that can't adjudicate the
physics.

**So don't make it an accusation. Make it a question about criteria:**

> He's describing keeping the experiments that went well and discarding the ones that didn't make
> sense. That's fine if the criterion is set in advance and stated — bad signal-to-noise, say,
> measured before you look at the answer. My question is simply what the criterion was, and whether
> it was applied before or after seeing the output. With a method that draws a structured picture
> out of any input, if you decide afterwards which pictures look sensible, you'll end up with a
> folder of confident results no matter what's underground. That's not a criticism of his honesty.
> It's the reason blind protocols exist.

That version is unanswerable, fair, and keeps you on method rather than motive.

---

## 4. Unpublished blind tests — ≈24:09–24:39

The interviewer proposes precisely the experiment your paper invites: *test repeatedly on
structures already known and check that it matches.*

**Italian:**
> ...questi sono i test a doppio cieco che vengono fatti, ne abbiamo fatti molti che sono andati
> quasi tutti a buon fine. Dove non va a buon fine? Quando le caratteristiche del terreno non sono
> buone, c'è vegetazione, troppa vegetazione, quindi non funziona... non è che la tecnica mia
> funziona ovunque, ha anche dei problemi, ma è giusto che sia così. Non è unica, ma deve essere
> compensata con altri metodi.

**English:**
> ...these are the double-blind tests that get done — we've done many, and almost all went well.
> Where does it not go well? When the terrain characteristics aren't good, there's vegetation, too
> much vegetation, so it doesn't work... it's not that my technique works everywhere, it has
> problems too, and that's how it should be. **It isn't unique — it has to be compensated with
> other methods.**

**Why this matters.** He asserts many, near-universally successful blind tests against known
structures. **None of these appear in any publication.** That changes your ask from something he
can decline as unreasonable into something much harder to refuse.

**Plain-language version:**
> He says he's already run many blind tests against known structures and that almost all succeeded.
> That's the exact test I've been asking for — so I'm not asking him to do new work. I'm asking him
> to publish the work he says he's already done. If those results exist and they hold up, they'd
> settle this in his favour, and I'd say so publicly.

Note also the concession in the last line: *it isn't unique, it must be compensated with other
methods.* That is meaningfully softer than the press-conference framing, and worth quoting when
someone insists the technique stands alone.

---

## Also on the record (lower value, context only)

- **≈25:08–25:26** — the second Sphinx on the Giza plateau: *"probably we've found it, and we have
  the photographs."*
- **≈26:29–26:43** — scope now extends to Göbekli Tepe and a Russian site (transcribed as
  "Caracora"), with "structures that descend for kilometres below." Asked what they are, he answers
  plainly: *"I don't know, don't ask me, I haven't the faintest idea."* Quote that fairly — it's an
  honest answer, and mocking it would cost you more than it gains.
- **≈19:01** — he states he has never charged anyone and has done all of it free of charge. If cost
  or motive comes up, say so. It's true, it's to his credit, and conceding it makes everything else
  you say more credible.

---

## How this changes your public position

It doesn't change the paper. Nothing here is a processing parameter, so **the four undisclosed
knobs — window, coregistrator, precision, sub-aperture count — remain undisclosed**, and your
sensitivity sweep is still the only public map of how much they matter.

What it changes is the *shape* of the argument. Before, you were inferring that the 22 kHz was
dialled in. Now there's an account of the reasoning that produced it, and the reasoning is a
confusion between a number inside a radar receiver and a wave in the ground. That's easier to
explain to a non-technical audience than anything in your paper, and it's the thing to lead with.

**Keep golden rule #1 in force.** Every one of these quotes is about method. None of them is about
character, and none should be used to imply bad faith. The self-deception reading — a real tool,
skipped safety checks, confident pictures believed — remains both the most probable explanation and
the most credible thing you can say.
