// Year 9 deck v2: real radar imagery, to-scale diagram, "spot the real one", bigger classroom text.
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fs = require("fs");
const path = require("path");
const fa = require("react-icons/fa");
const { applyTheme } = require("/root/.claude/skills/synced/26823aa1-46f9-4ea3-9539-6420255be544_a3e46f98-5d1e-428d-a4cf-f58ed503d280/pptx/scripts/apply_theme.js");

const THEME = {
  name: "Desert Night Radar", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "1B2A41", lt1: "FFFFFF", dk2: "33415C", lt2: "EEF2F7", accent1: "D99A2B", accent2: "1F9E95",
    accent3: "C2553F", accent4: "6B7A99", accent5: "F2D492", accent6: "9FD8D2", hlink: "1F9E95", folHlink: "6B7A99" },
};
const H = THEME.colors;
const C = { ink: H.dk1, ink2: H.dk2, white: H.lt1, mist: H.lt2, gold: H.accent1, teal: H.accent2, red: H.accent3,
  slate: H.accent4, sand: H.accent5, aqua: H.accent6, rock: "E6D3AE", rockDark: "CDB68A" };
const OUT = process.argv[2] || "Radar_and_the_Pyramids_Year9.pptx";
const IMG = (f) => path.join(__dirname, "img", f);
const CREDIT = "Real radar image of Giza, 7 Feb 2023 · Umbra Space Open Data (CC BY 4.0)";

async function icon(name, color) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(fa[name], { color: "#" + color, size: "256" }));
  return "image/png;base64," + (await sharp(Buffer.from(svg)).png().toBuffer()).toString("base64");
}
const imgData = (f) => "image/png;base64," + fs.readFileSync(IMG(f)).toString("base64");

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "Hassan Foreman";
  pres.title = "Can a Satellite See Under the Pyramids?";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };

  pres.defineSlideMaster({ title: "DARK", background: { color: C.ink }, objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.0, w: 4.1, h: 2.3, fontSize: 38, bold: true, color: C.white, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 3.45, w: 4.1, h: 1.0, fontSize: 18, color: C.sand, valign: "top", align: "left", margin: 0 }, text: "" } },
  ] });
  pres.defineSlideMaster({ title: "CONTENT", background: { color: C.white }, objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.75, fontSize: 30, bold: true, color: C.ink, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: "Hassan Foreman  ·  Testing a radar claim", options: { x: 0.5, y: 5.25, w: 6, h: 0.25, fontSize: 10, color: C.slate, margin: 0 } } },
  ], slideNumber: { x: 9.0, y: 5.25, w: 0.5, h: 0.25, fontSize: 10, color: C.slate, align: "right" } });

  const T = (o) => Object.assign({ isTextBox: true, margin: 0, color: C.ink, fontSize: 18 }, o);
  const circleIcon = async (s, name, x, y, d, fill, fg, tag) => {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: tag + " circle" });
    const p = d * 0.25;
    s.addImage({ data: await icon(name, fg), x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p, objectName: tag + " icon" });
  };
  const card = (s, x, y, w, h, fill, tag) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: fill }, line: { color: fill }, objectName: tag });

  // 1. Title — real radar image of Giza
  pres.addSection({ title: "Introduction" });
  let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Introduction" });
  s.addImage({ data: imgData("giza_title.png"), x: 4.95, y: 0, w: 5.05, h: 5.625, objectName: "Giza radar image" });
  s.addText("Can a Satellite See Under the Pyramids?", { placeholder: "title" });
  s.addText("Radar, big claims, and how scientists check them", { placeholder: "body" });
  s.addText("Hassan Foreman  ·  Year 9 STEM, Islamic College of Brisbane", T({ x: 0.6, y: 4.9, w: 4.2, h: 0.3, fontSize: 12, color: C.aqua }));
  s.addShape(pres.shapes.RECTANGLE, { x: 4.95, y: 5.25, w: 5.05, h: 0.375, fill: { color: C.ink, transparency: 30 }, line: { color: C.ink, transparency: 100 }, objectName: "credit backing" });
  s.addText(CREDIT, T({ x: 5.1, y: 5.3, w: 4.8, h: 0.28, fontSize: 9, color: C.white }));
  s.addNotes("The picture on the right is a real radar image of the Giza pyramids, taken from space by an Umbra satellite. Radar images look grainy and black-and-white: bright means a strong echo came back, dark means a weak one. This deck tells the story of a big claim about what lies under these pyramids and how scientists test claims like it. Every slide has notes like these so a teacher can present it.");

  // 2. Radar is an echo — diagram
  pres.addSection({ title: "How radar works" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How radar works" });
  s.addText("Radar works like an echo", { placeholder: "title" });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.3, w: 4.6, h: 0.75, fill: { color: C.rock }, line: { color: C.rock }, objectName: "ground" });
  s.addShape(pres.shapes.ISOSCELES_TRIANGLE, { x: 2.85, y: 3.45, w: 1.5, h: 0.85, fill: { color: C.rockDark }, line: { color: C.rockDark }, objectName: "pyramid" });
  await circleIcon(s, "FaSatellite", 0.6, 1.3, 0.95, C.ink, C.gold, "satellite");
  s.addShape(pres.shapes.LINE, { x: 1.55, y: 1.85, w: 1.95, h: 1.65, line: { color: C.teal, width: 3, dashType: "dash", endArrowType: "triangle" }, objectName: "pulse arrow" });
  s.addShape(pres.shapes.LINE, { x: 1.3, y: 2.3, w: 1.95, h: 1.35, line: { color: C.gold, width: 3, dashType: "dash", beginArrowType: "triangle" }, objectName: "echo arrow" });
  s.addText("pulse", T({ x: 2.7, y: 2.1, w: 1.2, h: 0.35, fontSize: 16, bold: true, color: C.teal }));
  s.addText("echo", T({ x: 1.25, y: 3.05, w: 1.0, h: 0.35, fontSize: 16, bold: true, color: C.gold }));
  const steps = [["1", "Send", "The radar fires a pulse of radio waves, like a shout."], ["2", "Bounce", "The pulse hits the ground and bounces back."], ["3", "Listen", "A longer wait for the echo means something further away."]];
  for (let i = 0; i < 3; i++) {
    const y = 1.3 + i * 1.2;
    s.addShape(pres.shapes.OVAL, { x: 5.6, y, w: 0.6, h: 0.6, fill: { color: C.teal }, line: { color: C.teal }, objectName: `step ${i + 1} badge` });
    s.addText(steps[i][0], T({ x: 5.6, y, w: 0.6, h: 0.6, fontSize: 20, bold: true, color: C.white, align: "center", valign: "middle" }));
    s.addText(steps[i][1], T({ x: 6.4, y: y - 0.05, w: 3.1, h: 0.35, fontSize: 20, bold: true }));
    s.addText(steps[i][2], T({ x: 6.4, y: y + 0.32, w: 3.1, h: 0.65, fontSize: 15, color: C.ink2, valign: "top" }));
  }
  s.addText("Bats and dolphins do this with sound. Radar uses radio waves.", T({ x: 5.6, y: 4.75, w: 3.9, h: 0.35, fontSize: 14, italic: true, color: C.slate }));
  s.addNotes("Ask the class how a bat finds a moth in the dark: it clicks and listens for the echo. Radar does the same with radio waves, which travel at the speed of light. Timing the echo tells you how far away something is.");

  // 3. What the satellite actually saw
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How radar works" });
  s.addText("What the satellite actually saw", { placeholder: "title" });
  s.addImage({ data: imgData("giza_wide.png"), x: 0.5, y: 1.2, w: 5.4, h: 3.8, objectName: "Giza radar image wide" });
  s.addText("Umbra Space Open Data (CC BY 4.0)", T({ x: 0.5, y: 5.02, w: 5.4, h: 0.2, fontSize: 9, color: C.slate }));
  const facts = [["~500 km", "how high up the satellite was"], ["Day or night", "radar brings its own \"light\", and sees through cloud"], ["Bright vs dark", "bright = strong echo. The dark triangles are the pyramids' radar shadows"]];
  for (let i = 0; i < 3; i++) {
    const y = 1.2 + i * 1.3;
    s.addText(facts[i][0], T({ x: 6.25, y, w: 3.3, h: 0.45, fontSize: 24, bold: true, color: C.teal, fontFace: "Cambria" }));
    s.addText(facts[i][1], T({ x: 6.25, y: y + 0.47, w: 3.3, h: 0.7, fontSize: 15, color: C.ink2, valign: "top" }));
  }
  s.addNotes("This is a Synthetic Aperture Radar (SAR) image. As the satellite flies past, it records thousands of echoes and a computer combines them into a sharp picture, as if the satellite had an antenna kilometres long. You can see the three Giza pyramids and the city of Giza around them. Each pyramid has a bright side facing the radar and a dark 'radar shadow' behind it. Ask: what do you notice? Can you find the pyramids, roads and buildings?");

  // 4. To-scale cross-section
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How radar works" });
  s.addText("Radar can't see deep underground", { placeholder: "title" });
  const g = 1.95, k = 2.9 / 648; // ground line y; inches per metre
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: g, w: 5.0, h: 648 * k + 0.1, fill: { color: C.rock }, line: { color: C.rock }, objectName: "rock" });
  s.addShape(pres.shapes.ISOSCELES_TRIANGLE, { x: 1.0, y: g - 136 * k, w: 215 * k, h: 136 * k, fill: { color: C.rockDark }, line: { color: C.rockDark }, objectName: "Khafre to scale" });
  for (const dx of [1.32, 1.52]) s.addShape(pres.shapes.RECTANGLE, { x: dx, y: g, w: 0.06, h: 648 * k, fill: { color: C.red }, line: { color: C.red }, objectName: "claimed shaft" });
  s.addShape(pres.shapes.LINE, { x: 0.5, y: g, w: 5.0, h: 0, line: { color: C.teal, width: 2.5 }, objectName: "radar reach line" });
  s.addText("Pyramid: 136 m tall", T({ x: 2.2, y: g - 0.5, w: 2.6, h: 0.3, fontSize: 14, bold: true }));
  s.addText("Radar's reach: a few centimetres (it would be thinner than this teal line)", T({ x: 2.2, y: g + 0.12, w: 3.2, h: 0.6, fontSize: 13, bold: true, color: C.teal }));
  s.addText("Claimed shafts: about 650 m deep", T({ x: 1.75, y: g + 2.35, w: 3.5, h: 0.3, fontSize: 14, bold: true, color: C.red }));
  card(s, 6.0, 1.3, 3.5, 3.55, C.ink, "scale card");
  s.addText([
    { text: "Drawn to scale", options: { fontSize: 22, bold: true, color: C.gold, fontFace: "Cambria", breakLine: true } },
    { text: " ", options: { fontSize: 8, breakLine: true } },
    { text: "Radio waves fade fast in rock, like torchlight in muddy water.", options: { fontSize: 15, color: C.white, breakLine: true } },
    { text: " ", options: { fontSize: 8, breakLine: true } },
    { text: "So the claim used a different idea: reading tiny vibrations at the surface and turning them into depth.", options: { fontSize: 15, color: C.aqua } },
  ], T({ x: 6.25, y: 1.5, w: 3.05, h: 3.2, valign: "top" }));
  s.addNotes("This drawing is to scale. Khafre's pyramid is about 136 metres tall. The claimed shafts went down about 648 metres. The radar on these satellites (X-band, wavelength about 3 cm) only gets a few centimetres into solid rock, so on this drawing its reach would be far thinner than the teal line. The researchers agreed radar does not simply see through the ground. Their idea was that the ground vibrates very slightly and those vibrations can be decoded into depth.");

  // 5. The claim
  pres.addSection({ title: "The claim" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "The claim" });
  s.addText("The big claim", { placeholder: "title" });
  const tl = [["2022", "Filippo Biondi and Corrado Malanga publish a paper: satellite radar reveals hidden corridors inside the Great Pyramid."],
    ["2025", "They announce huge shafts going hundreds of metres down beneath the Khafre pyramid, plus chambers and spiral ramps."],
    ["2026", "They announce a buried \"second Sphinx\". The story goes viral around the world."]];
  s.addShape(pres.shapes.LINE, { x: 1.05, y: 1.6, w: 0, h: 2.7, line: { color: C.slate, width: 1.5 }, objectName: "timeline" });
  for (let i = 0; i < 3; i++) {
    const y = 1.3 + i * 1.25;
    s.addShape(pres.shapes.OVAL, { x: 0.5, y, w: 1.1, h: 0.55, fill: { color: C.gold }, line: { color: C.gold }, objectName: `year ${tl[i][0]}` });
    s.addText(tl[i][0], T({ x: 0.5, y, w: 1.1, h: 0.55, fontSize: 17, bold: true, align: "center", valign: "middle" }));
    s.addText(tl[i][1], T({ x: 1.85, y: y - 0.2, w: 4.4, h: 0.95, fontSize: 15, valign: "middle" }));
  }
  card(s, 6.6, 1.3, 2.9, 3.55, C.mist, "big idea card");
  await circleIcon(s, "FaLightbulb", 6.85, 1.55, 0.75, C.gold, C.ink, "idea");
  s.addText("If it were true, it would change archaeology.", T({ x: 6.85, y: 2.5, w: 2.45, h: 1.0, fontSize: 18, bold: true, valign: "top" }));
  s.addText("That is exactly why it needed careful checking.", T({ x: 6.85, y: 3.55, w: 2.45, h: 1.0, fontSize: 15, color: C.ink2, valign: "top" }));
  s.addNotes("Be fair to the researchers: they are qualified people with an interesting idea, and they still stand by their work. The question for any scientist is not 'do I like this idea?' but 'does the evidence hold up when someone else tests it?'");

  // 6. Toolkit
  pres.addSection({ title: "How scientists check" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How scientists check" });
  s.addText("A scientist's toolkit for checking a claim", { placeholder: "title" });
  const kit = [["FaRedoAlt", "Repeat it", "Follow the same recipe yourself. Do you get the same thing?"], ["FaDice", "Feed it nothing", "Give the method random noise. A real detector should find nothing."],
    ["FaBullseye", "Plant a fake", "Hide a signal you made yourself. Can the method find it?"], ["FaClipboardCheck", "Set the rules first", "Write down what counts as success before you look."]];
  for (let i = 0; i < 4; i++) {
    const x = 0.5 + (i % 2) * 4.6, y = 1.25 + Math.floor(i / 2) * 1.95;
    card(s, x, y, 4.4, 1.75, C.mist, `kit card ${i + 1}`);
    await circleIcon(s, kit[i][0], x + 0.25, y + 0.42, 0.9, C.teal, C.white, `kit ${i + 1}`);
    s.addText(kit[i][1], T({ x: x + 1.35, y: y + 0.2, w: 2.85, h: 0.42, fontSize: 20, bold: true }));
    s.addText(kit[i][2], T({ x: x + 1.35, y: y + 0.68, w: 2.85, h: 0.95, fontSize: 15, valign: "top" }));
  }
  s.addNotes("These four checks are used in every field, from medicine to physics. 'Feed it nothing' is a null test or control. 'Plant a fake' is a positive control. 'Set the rules first' is pre-registration: it stops you moving the goalposts after you see the answer you hoped for.");

  // 7. What I did
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How scientists check" });
  s.addText("What I did", { placeholder: "title" });
  const did = [["FaDatabase", "Got free satellite images of Giza"], ["FaCode", "Rebuilt their method step by step"], ["FaGlobeAfrica", "Ran it on Giza, a volcano, a mine and a city"], ["FaDice", "Ran it on pure random noise"], ["FaShareAlt", "Published my code so anyone can check me"]];
  for (let i = 0; i < 5; i++) {
    const x = 0.5 + i * 1.85;
    await circleIcon(s, did[i][0], x + 0.3, 1.35, 1.1, i === 3 ? C.gold : C.teal, C.white, `did ${i + 1}`);
    s.addText(String(i + 1), T({ x: x + 0.3, y: 2.6, w: 1.1, h: 0.4, fontSize: 20, bold: true, align: "center", color: C.slate }));
    s.addText(did[i][1], T({ x, y: 3.05, w: 1.7, h: 1.2, fontSize: 15, align: "center", valign: "top" }));
  }
  card(s, 0.5, 4.3, 9.0, 0.75, C.mist, "key step card");
  s.addText("Step 4 is the key one: if random noise gives the same \"discovery\", it is coming from the maths.", T({ x: 0.75, y: 4.3, w: 8.5, h: 0.75, fontSize: 16, bold: true, valign: "middle" }));
  s.addNotes("Places tested: three free radar images of Giza, Mount Vesuvius in Italy, the mining town of Butte in the USA, and Cairo. The method was also checked with planted test signals, and it could find those, so the code was working properly.");

  // 8. Spot the real one
  pres.addSection({ title: "What I found" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "What I found" });
  s.addText("Spot the real one", { placeholder: "title" });
  s.addText("Both pictures came out of the method. One used real Giza radar data. The other used the same data scrambled into nonsense.", T({ x: 0.5, y: 1.1, w: 9.0, h: 0.6, fontSize: 16, color: C.ink2 }));
  const pw = 4.3, ph = pw * 433 / 688;
  for (const [i, f, lab] of [[0, "tomo_scrambled.png", "A"], [1, "tomo_real.png", "B"]]) {
    const x = 0.5 + i * 4.7;
    s.addImage({ data: imgData(f), x, y: 1.85, w: pw, h: ph, objectName: `panel ${lab}` });
    s.addShape(pres.shapes.OVAL, { x: x + 0.12, y: 1.97, w: 0.55, h: 0.55, fill: { color: C.gold }, line: { color: C.white, width: 1.5 }, objectName: `label ${lab}` });
    s.addText(lab, T({ x: x + 0.12, y: 1.97, w: 0.55, h: 0.55, fontSize: 20, bold: true, align: "center", valign: "middle" }));
  }
  s.addText("Bright blobs are what get read as \"chambers\". Which one is real? Answer on the next slide.", T({ x: 0.5, y: 4.7, w: 9.0, h: 0.4, fontSize: 15, bold: true }));
  s.addNotes("Give the class a minute to vote. Answer: B is from the real Giza data; A is the same data scrambled (shuffled) so it cannot contain any real underground structure. Both show bright 'chamber-like' blobs. If scrambled nonsense makes chambers too, bright blobs on their own cannot prove anything is down there. Images are cross-sections from the author's Giza run on the 7 Feb 2023 scene: horizontal = position along a line, vertical = depth label.");

  // 9. Chart
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "What I found" });
  s.addText("The same bright spot shows up everywhere", { placeholder: "title" });
  s.addChart(pres.charts.BAR, [{ name: "Depth of brightest spot",
    labels: ["Giza (7 Feb)", "Giza (8 Feb)", "Giza (8 Mar)", "Vesuvius volcano", "Butte mine, USA", "Cairo city", "Random noise"],
    values: [1.69, 1.84, 1.71, 1.67, 1.78, 1.73, 1.66] }], {
    x: 0.5, y: 1.15, w: 5.9, h: 3.95, barDir: "bar", showTitle: true, title: "Where the brightest spot lands (steps below the surface)",
    titleFontSize: 13, titleColor: C.ink2, titleFontFace: "+mn-lt", chartColors: [C.teal], showValue: true, dataLabelPosition: "outEnd",
    dataLabelFormatCode: "0.0", dataLabelFontSize: 13, dataLabelColor: C.ink, dataLabelFontFace: "+mn-lt",
    catAxisLabelColor: C.ink, catAxisLabelFontSize: 13, catAxisLabelFontFace: "+mn-lt", catAxisOrientation: "maxMin",
    valAxisLabelColor: C.slate, valAxisLabelFontSize: 11, valAxisLabelFontFace: "+mn-lt", valAxisMinVal: 0, valAxisMaxVal: 4, valAxisMajorUnit: 1,
    valGridLine: { color: "DDE3EC", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false });
  card(s, 6.7, 1.25, 2.8, 3.8, C.ink, "takeaway card");
  s.addText([
    { text: "Answer: B was real", options: { bold: true, fontSize: 17, color: C.gold, breakLine: true } },
    { text: "...but A made \"chambers\" too.", options: { fontSize: 15, color: C.white, breakLine: true } },
    { text: " ", options: { fontSize: 8, breakLine: true } },
    { text: "A pyramid, a volcano, a mine, a city and pure noise all put the bright spot in the same place.", options: { fontSize: 15, color: C.white, breakLine: true } },
    { text: " ", options: { fontSize: 8, breakLine: true } },
    { text: "Noise has nothing underground, so the spot comes from the method.", options: { fontSize: 15, bold: true, color: C.aqua } },
  ], T({ x: 6.95, y: 1.45, w: 2.35, h: 3.5, valign: "top" }));
  s.addNotes("Each bar shows where the method's brightest 'echo' lands, in steps of its depth grid. All the real places land in the same spot, and so does a run on computer-generated random numbers with no satellite data at all. That is the signature of an artifact: a pattern made by the processing, not by the thing being measured. Data: the author's public repository, Test J run files (runs/test_j_*.json), 11 looks, half-bandwidth settings.");

  // 10. Who sets the depth
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "What I found" });
  s.addText("Who decides how deep \"deep\" is?", { placeholder: "title" });
  s.addText("To turn steps into metres, the method uses a number the person running it picks.", T({ x: 0.5, y: 1.1, w: 9.0, h: 0.45, fontSize: 16, color: C.ink2 }));
  const pick = [["200", "chosen in the researchers' volcano study"], ["22,000", "used for the Giza pyramids"]];
  for (let i = 0; i < 2; i++) {
    const y = 1.75 + i * 1.45;
    card(s, 0.5, y, 3.6, 1.25, C.mist, `pick card ${i + 1}`);
    s.addText(pick[i][0], T({ x: 0.75, y: y + 0.1, w: 3.1, h: 0.65, fontSize: 36, bold: true, color: C.teal, fontFace: "Cambria" }));
    s.addText(pick[i][1], T({ x: 0.75, y: y + 0.75, w: 3.1, h: 0.4, fontSize: 14 }));
  }
  // illustration: one picture, two rulers
  s.addText("Same picture, two dials", T({ x: 4.6, y: 1.75, w: 4.9, h: 0.35, fontSize: 16, bold: true }));
  s.addImage({ data: imgData("tomo_real.png"), x: 5.67, y: 2.2, w: 2.7, h: 2.7 * 433 / 688, objectName: "same picture" });
  const ry0 = 2.2, rh = 2.7 * 433 / 688;
  for (const [x, labels, col] of [[5.35, ["0 m", "10 m", "20 m"], C.gold], [8.6, ["0 m", "1,000 m", "2,000 m"], C.red]]) {
    s.addShape(pres.shapes.RECTANGLE, { x, y: ry0, w: 0.12, h: rh, fill: { color: col }, line: { color: col }, objectName: "ruler" });
    labels.forEach((t, j) => s.addText(t, T({ x: x === 5.35 ? 4.55 : x + 0.2, y: ry0 + j * (rh / 2) - 0.12, w: 0.72, h: 0.25, fontSize: 11, bold: true, color: col, align: x === 5.35 ? "right" : "left" })));
  }
  s.addText("Change the dial and the same blob becomes shallow or deep. A real measurement doesn't depend on a dial you set.", T({ x: 4.6, y: 4.1, w: 4.9, h: 0.9, fontSize: 15, bold: true, valign: "top" }));
  s.addNotes("In the researchers' Mount Vesuvius paper, the frequency that sets the depth scale is 200 hertz, which they say they set themselves. For Giza the recipe uses about 22,000 hertz: same method, a number about 110 times different. The two rulers are an illustration only: the point is that the same picture can be labelled as shallow or deep depending on a setting. The researchers have said the maximum depth depends on the settings chosen.");

  // 11. What happened next
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "What I found" });
  s.addText("What happened next", { placeholder: "title" });
  const nx = [["FaGavel", "August 2026", "The journal retracted (withdrew) the 2022 paper, citing serious problems with its methods and statistics."],
    ["FaFileAlt", "Now", "My paper is being peer reviewed: other scientists are checking my work, the way I checked theirs."],
    ["FaBalanceScale", "Being honest", "The original researchers disagree. And a few of my own results I can't fully explain yet, so I say that openly."]];
  for (let i = 0; i < 3; i++) {
    const y = 1.25 + i * 1.3;
    await circleIcon(s, nx[i][0], 0.5, y, 0.9, i === 2 ? C.gold : C.teal, C.white, `next ${i + 1}`);
    s.addText(nx[i][1], T({ x: 1.65, y: y - 0.03, w: 7.85, h: 0.4, fontSize: 20, bold: true }));
    s.addText(nx[i][2], T({ x: 1.65, y: y + 0.4, w: 7.85, h: 0.7, fontSize: 16, color: C.ink2, valign: "top" }));
  }
  s.addNotes("A retraction means a journal withdraws a paper because it no longer stands behind the findings. The author's paper was not the cause of the retraction and does not claim to be. It is being reviewed by PCI Archaeology. Admitting what you cannot yet explain is a strength in science, not a weakness.");

  // 12. Lessons
  pres.addSection({ title: "Lessons" });
  s = pres.addSlide({ masterName: "DARK", sectionTitle: "Lessons" });
  s.addText("Lessons for young scientists", { placeholder: "title" });
  s.addText("Questions?", { placeholder: "body" });
  const les = [["FaSearch", "Test your favourite idea the hardest"], ["FaQuestion", "Say what would prove you wrong"], ["FaShareAlt", "Share your data so others can check"], ["FaLightbulb", "Changing your mind is a win"]];
  for (let i = 0; i < 4; i++) {
    const y = 0.7 + i * 1.1;
    await circleIcon(s, les[i][0], 5.6, y, 0.8, C.ink2, C.gold, `lesson ${i + 1}`);
    s.addText(les[i][1], T({ x: 6.6, y, w: 3.0, h: 0.8, fontSize: 17, color: C.white, valign: "middle" }));
  }
  s.addNotes("Satellite radar may well help us learn genuine things about the past, as long as we test the evidence carefully and honestly. Discussion questions: What would convince you a hidden chamber was real? Why is testing a method on random noise so useful? Why do scientists share their code and data?");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
