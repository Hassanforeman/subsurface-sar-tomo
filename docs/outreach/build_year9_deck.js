const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require("/root/.claude/skills/synced/26823aa1-46f9-4ea3-9539-6420255be544_a3e46f98-5d1e-428d-a4cf-f58ed503d280/pptx/scripts/apply_theme.js");

const THEME = {
  name: "Desert Night Radar",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2A41", lt1: "FFFFFF", dk2: "33415C", lt2: "EEF2F7",
    accent1: "D99A2B", accent2: "1F9E95", accent3: "C2553F", accent4: "6B7A99",
    accent5: "F2D492", accent6: "9FD8D2", hlink: "1F9E95", folHlink: "6B7A99",
  },
};
const HEX = THEME.colors;
const OUT = "Radar_and_the_Pyramids_Year9.pptx";

async function icon(name, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(fa[name], { color: "#" + color, size: String(size) })
  );
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // 10 x 5.625
  pres.author = "Hassan Foreman";
  pres.title = "Can a Satellite See Under the Pyramids?";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = { text1: HEX.dk1, text2: HEX.dk2, background1: HEX.lt1, background2: HEX.lt2, accent1: HEX.accent1, accent2: HEX.accent2, accent3: HEX.accent3, accent4: HEX.accent4, accent5: HEX.accent5, accent6: HEX.accent6 }; // literal hex: renders the same in PowerPoint, Keynote, Google Slides and phone previews

  // ---------- layouts ----------
  pres.defineSlideMaster({
    title: "TITLE_DARK",
    background: { color: C.text1 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.1, w: 5.3, h: 2.1, fontSize: 40, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 3.35, w: 5.3, h: 1.2, fontSize: 18, color: C.accent5, valign: "top", align: "left", margin: 0 }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "CONTENT",
    background: { color: C.background1 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.8, fontSize: 30, bold: true, color: C.text1, valign: "middle", align: "left", margin: 0 }, text: "" } },
      { text: { text: "Hassan Foreman  ·  Testing a radar claim", options: { x: 0.5, y: 5.2, w: 6, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 } } },
    ],
    slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.3, fontSize: 10, color: C.accent4, align: "right" },
  });

  const circleIcon = async (slide, name, x, y, d, fill, fg, objName) => {
    slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: objName + " circle" });
    const pad = d * 0.25;
    slide.addImage({ data: await icon(name, fg), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad, objectName: objName + " icon" });
  };
  const T = (opts) => Object.assign({ isTextBox: true, margin: 0, color: C.text1, fontSize: 14 }, opts);

  // ---------- 1. Title ----------
  pres.addSection({ title: "Introduction" });
  let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Introduction" });
  s.addText("Can a Satellite See Under the Pyramids?", { placeholder: "title" });
  s.addText("Radar, big claims, and how scientists check them", { placeholder: "body" });
  s.addText("Hassan Foreman  ·  for Year 9 STEM, Islamic College of Brisbane", T({ x: 0.6, y: 4.75, w: 6.4, h: 0.35, fontSize: 12, color: C.accent6 }));
  s.addShape(pres.shapes.OVAL, { x: 7.05, y: 1.35, w: 2.5, h: 2.5, fill: { color: C.text2 }, line: { color: C.accent2, width: 2 }, objectName: "radar ring outer" });
  s.addShape(pres.shapes.OVAL, { x: 7.55, y: 1.85, w: 1.5, h: 1.5, fill: { color: C.text1 }, line: { color: C.accent2, width: 1.5 }, objectName: "radar ring inner" });
  s.addImage({ data: await icon("FaSatellite", HEX.accent1), x: 7.85, y: 2.15, w: 0.9, h: 0.9, objectName: "satellite icon" });
  s.addNotes("This deck explains, in plain language, a real scientific argument about satellite radar and the Giza pyramids, and uses it to show how scientists test a surprising claim. It is written so a teacher can present it without the author in the room: each slide has notes like these.");

  // ---------- 2. Radar = echo ----------
  pres.addSection({ title: "How radar works" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How radar works" });
  s.addText("Radar works like an echo", { placeholder: "title" });
  const steps2 = [
    ["FaVolumeUp", "1. Send", "The radar sends out a pulse of radio waves, like a shout."],
    ["FaMountain", "2. Bounce", "The pulse hits the ground, buildings or rocks and bounces back."],
    ["FaUndo", "3. Listen", "The radar times the echo. A longer wait means something further away."],
  ];
  for (let i = 0; i < 3; i++) {
    const x = 0.5 + i * 3.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.4, w: 2.8, h: 2.9, rectRadius: 0.1, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: `step card ${i + 1}` });
    await circleIcon(s, steps2[i][0], x + 0.25, 1.65, 0.8, C.accent2, HEX.lt1, `step ${i + 1}`);
    s.addText(steps2[i][1], T({ x: x + 0.25, y: 2.6, w: 2.3, h: 0.45, fontSize: 20, bold: true }));
    s.addText(steps2[i][2], T({ x: x + 0.25, y: 3.1, w: 2.3, h: 1.1, fontSize: 14, valign: "top" }));
  }
  s.addText("Bats and dolphins do the same thing with sound. Radar uses radio waves instead.", T({ x: 0.5, y: 4.55, w: 9, h: 0.4, fontSize: 14, italic: true, color: C.text2 }));
  s.addNotes("Ask students: how does a bat find a moth in the dark? It clicks and listens for the echo. Radar is the same idea using radio waves, which travel at the speed of light. Measuring how long the echo takes tells you how far away the thing is.");

  // ---------- 3. SAR ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How radar works" });
  s.addText("SAR: a satellite that takes photos with radar", { placeholder: "title" });
  s.addText([
    { text: "SAR stands for Synthetic Aperture Radar.", options: { bold: true, breakLine: true } },
    { text: "As the satellite flies, it collects thousands of echoes from the same spot.", options: { bullet: true, breakLine: true } },
    { text: "A computer combines them, as if the satellite had a giant antenna kilometres long. That gives a sharp picture.", options: { bullet: true, breakLine: true } },
    { text: "It works at night and through clouds, because it brings its own \"light\".", options: { bullet: true } },
  ], T({ x: 0.5, y: 1.35, w: 5.2, h: 3.0, fontSize: 16, valign: "top", paraSpaceAfter: 8 }));
  const stats3 = [["~500 km", "how high these satellites fly"], ["7 km/s", "how fast they travel"], ["~30 cm", "smallest detail they can show"]];
  for (let i = 0; i < 3; i++) {
    const y = 1.35 + i * 1.2;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.1, y, w: 3.4, h: 1.0, rectRadius: 0.08, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: `stat card ${i + 1}` });
    s.addText(stats3[i][0], T({ x: 6.3, y: y + 0.08, w: 3.0, h: 0.5, fontSize: 26, bold: true, color: C.accent1, fontFace: "Cambria" }));
    s.addText(stats3[i][1], T({ x: 6.3, y: y + 0.6, w: 3.0, h: 0.3, fontSize: 12, color: C.background1 }));
  }
  s.addNotes("SAR satellites from companies such as Umbra and Capella share some images free for research. That is what made this project possible for someone working from home. The figures here are approximate. Resolution varies by satellite and mode.");

  // ---------- 4. Can't see deep ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How radar works" });
  s.addText("But radar can't see deep underground", { placeholder: "title" });
  s.addText("Radio waves soak into rock the way torchlight fades in muddy water.", T({ x: 0.5, y: 1.25, w: 9, h: 0.4, fontSize: 16, color: C.text2 }));
  const cmp = [
    ["A few centimetres", "How far these satellites' radar gets into solid rock", C.accent2],
    ["Hundreds of metres", "How deep the structures in the claim were said to be", C.accent3],
  ];
  for (let i = 0; i < 2; i++) {
    const x = 0.5 + i * 4.65;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.9, w: 4.35, h: 2.2, rectRadius: 0.1, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: `compare card ${i + 1}` });
    s.addText(cmp[i][0], T({ x: x + 0.3, y: 2.15, w: 3.8, h: 0.8, fontSize: 30, bold: true, color: cmp[i][2], fontFace: "Cambria" }));
    s.addText(cmp[i][1], T({ x: x + 0.3, y: 3.0, w: 3.8, h: 0.9, fontSize: 15, valign: "top" }));
  }
  s.addText("So the claim needed a different trick: reading tiny vibrations at the surface and turning them into depth.", T({ x: 0.5, y: 4.35, w: 9, h: 0.6, fontSize: 15, bold: true }));
  s.addNotes("The satellites used here work at X-band (wavelength about 3 cm). In dry sand, longer-wavelength radar can reach a few metres, but nothing gets hundreds of metres into limestone. The researchers agreed that radar does not simply 'see through' the ground. Their idea was different: that the ground vibrates very slightly, and that those vibrations can be decoded to reveal what is below.");

  // ---------- 5. The claim ----------
  pres.addSection({ title: "The claim" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "The claim" });
  s.addText("The big claim", { placeholder: "title" });
  const tl = [
    ["2022", "Researchers Filippo Biondi and Corrado Malanga publish a paper saying satellite radar reveals hidden corridors inside the Great Pyramid."],
    ["2025", "They announce huge shafts going hundreds of metres down beneath the Khafre pyramid, plus chambers and spiral ramps."],
    ["2026", "They announce a buried \"second Sphinx\". The story goes viral around the world."],
  ];
  s.addShape(pres.shapes.LINE, { x: 1.2, y: 1.55, w: 0, h: 2.85, line: { color: C.accent4, width: 1.5 }, objectName: "timeline line" });
  for (let i = 0; i < 3; i++) {
    const y = 1.35 + i * 1.05;
    s.addShape(pres.shapes.OVAL, { x: 0.65, y, w: 1.1, h: 0.55, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: `year pill ${i + 1}` });
    s.addText(tl[i][0], T({ x: 0.65, y, w: 1.1, h: 0.55, fontSize: 16, bold: true, align: "center", valign: "middle", color: C.text1 }));
    s.addText(tl[i][1], T({ x: 2.0, y: y - 0.05, w: 7.5, h: 0.75, fontSize: 15, valign: "middle" }));
  }
  s.addText("If it were true, it would change archaeology. That is exactly why it needed careful checking.", T({ x: 0.5, y: 4.55, w: 9, h: 0.45, fontSize: 15, italic: true, color: C.text2 }));
  s.addNotes("Be fair to the researchers. They are qualified people with a real, interesting idea, and they still stand by their work. The question for any scientist is not 'do I like this idea?' but 'does the evidence hold up when someone else tests it?'");

  // ---------- 6. Toolkit ----------
  pres.addSection({ title: "How scientists check" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How scientists check" });
  s.addText("A scientist's toolkit for checking a claim", { placeholder: "title" });
  const kit = [
    ["FaRedoAlt", "Repeat it", "Follow the same recipe yourself. Do you get the same thing?"],
    ["FaDice", "Feed it nothing", "Give the method pure random noise. A real detector should find nothing."],
    ["FaBullseye", "Plant a fake", "Hide a signal you made yourself. Can the method find it?"],
    ["FaClipboardCheck", "Set the rules first", "Write down what counts as success before you look at the results."],
  ];
  for (let i = 0; i < 4; i++) {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.6, y = 1.35 + row * 1.85;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 4.4, h: 1.65, rectRadius: 0.1, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: `kit card ${i + 1}` });
    await circleIcon(s, kit[i][0], x + 0.25, y + 0.4, 0.85, C.accent2, HEX.lt1, `kit ${i + 1}`);
    s.addText(kit[i][1], T({ x: x + 1.3, y: y + 0.2, w: 2.95, h: 0.45, fontSize: 18, bold: true }));
    s.addText(kit[i][2], T({ x: x + 1.3, y: y + 0.65, w: 2.95, h: 0.85, fontSize: 14, valign: "top" }));
  }
  s.addNotes("These four checks are used in every field, from medicine to physics. 'Feed it nothing' is called a null test or control. 'Plant a fake' is a positive control. 'Set the rules first' is called pre-registration: it stops you from moving the goalposts after you see the answer you hoped for.");

  // ---------- 7. What I did ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "How scientists check" });
  s.addText("What I did", { placeholder: "title" });
  const did = [
    ["FaDatabase", "Got free satellite images of Giza and other places"],
    ["FaCode", "Rebuilt their method from their paper and patent"],
    ["FaGlobeAfrica", "Ran it on Giza, a volcano, a mine and a city"],
    ["FaDice", "Ran it on pure random noise"],
    ["FaShareAlt", "Published all my code so anyone can check me"],
  ];
  for (let i = 0; i < 5; i++) {
    const x = 0.5 + i * 1.85;
    await circleIcon(s, did[i][0], x + 0.35, 1.5, 1.0, i === 3 ? C.accent1 : C.accent2, HEX.lt1, `did ${i + 1}`);
    s.addText(String(i + 1), T({ x: x + 0.35, y: 2.65, w: 1.0, h: 0.4, fontSize: 18, bold: true, align: "center", color: C.accent4 }));
    s.addText(did[i][1], T({ x, y: 3.1, w: 1.7, h: 1.3, fontSize: 14, align: "center", valign: "top" }));
  }
  s.addText("Step 4 is the key one: if random noise gives the same \"discovery\", the discovery is coming from the maths.", T({ x: 0.5, y: 4.5, w: 9, h: 0.5, fontSize: 15, bold: true }));
  s.addNotes("Places tested: three free radar scenes of Giza, Mount Vesuvius in Italy, the mining town of Butte in the USA, and a scene of Cairo. Every step was also checked with a planted test signal, and the method could find those, so the computer code was working.");

  // ---------- 8. Chart ----------
  pres.addSection({ title: "What I found" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "What I found" });
  s.addText("The \"discovery\" appears even in random noise", { placeholder: "title" });
  s.addChart(pres.charts.BAR, [{
    name: "Depth of brightest spot",
    labels: ["Giza (Feb 7)", "Giza (Feb 8)", "Giza (Mar 8)", "Vesuvius volcano", "Butte mine, USA", "Cairo city", "Random noise (no satellite)"],
    values: [1.69, 1.84, 1.71, 1.67, 1.78, 1.73, 1.66],
  }], {
    x: 0.5, y: 1.25, w: 5.9, h: 3.8, barDir: "bar",
    showTitle: true, title: "Where the brightest spot appears (steps below the surface)",
    titleFontSize: 12, titleColor: HEX.dk2, titleFontFace: "+mn-lt",
    chartColors: [HEX.accent2], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0",
    dataLabelFontSize: 11, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt",
    catAxisLabelColor: HEX.dk1, catAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt", catAxisOrientation: "maxMin",
    valAxisLabelColor: HEX.accent4, valAxisLabelFontSize: 10, valAxisLabelFontFace: "+mn-lt",
    valAxisMinVal: 0, valAxisMaxVal: 4, valAxisMajorUnit: 1,
    valGridLine: { color: "DDE3EC", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false,
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.7, y: 1.35, w: 2.8, h: 3.6, rectRadius: 0.1, fill: { color: C.text1 }, line: { color: C.text1 }, objectName: "takeaway card" });
  s.addText([
    { text: "Same spot, every time", options: { bold: true, fontSize: 18, color: C.accent1, breakLine: true } },
    { text: " ", options: { fontSize: 8, breakLine: true } },
    { text: "A pyramid, a volcano, a mine, a city and pure noise all give a bright spot just under the surface.", options: { fontSize: 14, color: C.background1, breakLine: true } },
    { text: " ", options: { fontSize: 8, breakLine: true } },
    { text: "Random noise has nothing underground, so the spot must come from the method itself.", options: { fontSize: 14, color: C.accent6 } },
  ], T({ x: 6.95, y: 1.6, w: 2.35, h: 3.2, valign: "top" }));
  s.addNotes("Each bar shows where the method's brightest 'echo' lands, measured in steps of its depth grid. All the real places land in the same spot, and so does a run with no satellite data at all, just computer-generated random numbers. That is the signature of an artifact: a pattern made by the processing rather than by the thing being measured. Data: the author's public repository, Test J run files (runs/test_j_*.json), 11 sub-apertures, half-bandwidth settings.");

  // ---------- 9. Who picks the depth ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "What I found" });
  s.addText("Who chooses how deep \"deep\" is?", { placeholder: "title" });
  s.addText("To turn \"steps\" into metres, the method uses a number that the person running it picks.", T({ x: 0.5, y: 1.25, w: 9, h: 0.5, fontSize: 16, color: C.text2 }));
  const pick = [["200", "the number chosen in the researchers' volcano study"], ["22,000", "the number used for the Giza pyramids"]];
  for (let i = 0; i < 2; i++) {
    const x = 0.5 + i * 3.3;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.95, w: 3.0, h: 2.0, rectRadius: 0.1, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: `pick card ${i + 1}` });
    s.addText(pick[i][0], T({ x: x + 0.25, y: 2.1, w: 2.5, h: 0.9, fontSize: 44, bold: true, color: C.accent2, fontFace: "Cambria" }));
    s.addText(pick[i][1], T({ x: x + 0.25, y: 3.0, w: 2.5, h: 0.8, fontSize: 13, valign: "top" }));
  }
  await circleIcon(s, "FaRuler", 7.35, 1.95, 0.9, C.accent1, HEX.dk1, "ruler");
  s.addText("Like a ruler where you decide how long a centimetre is.", T({ x: 7.0, y: 2.95, w: 2.5, h: 1.0, fontSize: 15, bold: true, valign: "top" }));
  s.addText("Same method, a number about 110 times different. A real measurement doesn't depend on a dial you set.", T({ x: 0.5, y: 4.3, w: 9, h: 0.6, fontSize: 15, bold: true }));
  s.addNotes("In the researchers' Mount Vesuvius paper, the frequency used to set the depth scale is 200 hertz, which they describe as set by themselves. For Giza the recipe uses about 22,000 hertz. Change that number and the same picture is relabelled as shallower or deeper. The researchers themselves have said the maximum depth depends on the settings chosen.");

  // ---------- 10. What happened ----------
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "What I found" });
  s.addText("What happened next", { placeholder: "title" });
  const next = [
    ["FaGavel", "August 2026", "The journal retracted (withdrew) the 2022 paper, citing serious problems with its methods and statistics."],
    ["FaFileAlt", "Now", "My paper is being peer reviewed: other scientists are checking my work, the way I checked theirs."],
    ["FaBalanceScale", "Being honest", "The original researchers disagree with the retraction. And a few of my own results I can't fully explain yet, so I say that openly in my paper."],
  ];
  for (let i = 0; i < 3; i++) {
    const y = 1.3 + i * 1.25;
    await circleIcon(s, next[i][0], 0.5, y, 0.85, i === 2 ? C.accent1 : C.accent2, HEX.lt1, `next ${i + 1}`);
    s.addText(next[i][1], T({ x: 1.6, y: y - 0.02, w: 7.9, h: 0.4, fontSize: 18, bold: true }));
    s.addText(next[i][2], T({ x: 1.6, y: y + 0.38, w: 7.9, h: 0.7, fontSize: 14, valign: "top" }));
  }
  s.addNotes("A retraction means a journal withdraws a paper it published because it no longer stands behind the findings. The author's paper was not the cause of the retraction and does not claim to be. It is being reviewed by PCI Archaeology. Admitting what you cannot yet explain is a strength in science, not a weakness.");

  // ---------- 11. Lessons ----------
  pres.addSection({ title: "Lessons" });
  s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Lessons" });
  s.addText("Lessons for young scientists", { placeholder: "title" });
  s.addText("Questions?", { placeholder: "body" });
  const les = [
    ["FaSearch", "Test your favourite idea the hardest"],
    ["FaQuestion", "Say what would prove you wrong"],
    ["FaShareAlt", "Share your data so others can check"],
    ["FaLightbulb", "Changing your mind is a win"],
  ];
  for (let i = 0; i < 4; i++) {
    const y = 0.75 + i * 1.05;
    await circleIcon(s, les[i][0], 6.3, y, 0.7, C.text2, HEX.accent1, `lesson ${i + 1}`);
    s.addText(les[i][1], T({ x: 7.15, y, w: 2.5, h: 0.7, fontSize: 14, color: C.background1, valign: "middle" }));
  }
  s.addNotes("Modern technology like satellite radar may well help us learn genuine things about the past, as long as we test the evidence carefully and honestly. Possible discussion questions: What would convince you that a hidden chamber was real? Why is testing a method on random noise so useful? Why do scientists share their code and data?");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
