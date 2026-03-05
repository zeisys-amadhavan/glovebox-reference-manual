/*
Glovebox_Trace_ClosedWhiteFill.jsx

Goal:
- Place raster
- Image Trace (B/W)
- Expand
- Normalize to: 1px black stroke + white fill
- Attempt to close paths if endpoints are near
- Flag any still-open paths in magenta for quick manual fixing

Notes:
- “Perfect closure” can’t be guaranteed by tracing alone for every raster.
- This script gets you very close; remaining open paths are highlighted.

*/

#target illustrator

(function () {
  if (app.documents.length === 0) app.documents.add(DocumentColorSpace.RGB);
  var doc = app.activeDocument;

  // ---------- CONFIG ----------
  var STROKE_PX = 1;                 // 1pt ≈ 1px at 72ppi (Illustrator units)
  var CLOSE_TOLERANCE_PX = 2.0;      // max endpoint distance to force-close
  var TRACE_THRESHOLD = 145;         // 0–255: higher => more black
  var TRACE_PATHS = 85;              // 0–100
  var TRACE_CORNERS = 75;            // 0–100
  var TRACE_NOISE = 1;               // 1–100 (lower keeps tiny details)
  var IGNORE_WHITE = true;           // remove background
  // Important: We want boundary loops.
  // Tracing as STROKES tends to produce open paths; tracing as FILLS tends to produce closed shapes.
  // We'll trace as FILLS, then normalize style to white-fill + black-stroke.
  var TRACE_FILLS = true;
  var TRACE_STROKES = false;
  // ---------------------------

  function dist(a, b) {
    var dx = a[0] - b[0], dy = a[1] - b[1];
    return Math.sqrt(dx*dx + dy*dy);
  }

  function rgb(r, g, b) {
    var c = new RGBColor();
    c.red = r; c.green = g; c.blue = b;
    return c;
  }

  var BLACK = rgb(0,0,0);
  var WHITE = rgb(255,255,255);
  var MAGENTA = rgb(255,0,255);

  var f = File.openDialog("Select raster to trace (PNG/JPG)", "*.png;*.jpg;*.jpeg;*.tif;*.tiff;*.bmp");
  if (!f) return;

  // Place & embed
  var placed = doc.placedItems.add();
  placed.file = f;
  placed.embed();

  doc.selection = null;
  placed.selected = true;

  if (!placed.trace) {
    alert("This Illustrator version does not expose placed.trace() to scripting. Run Image Trace manually once, then re-run script, or update Illustrator.");
    return;
  }

  // Trace
  var t = placed.trace();
  var opt = t.tracingOptions;

  opt.tracingMode = TracingModeType.TRACINGMODEBLACKANDWHITE;
  opt.threshold = TRACE_THRESHOLD;
  opt.pathFitting = TRACE_PATHS;
  opt.cornerFitting = TRACE_CORNERS;
  opt.noiseFitting = TRACE_NOISE;

  opt.ignoreWhite = IGNORE_WHITE;
  opt.fills = TRACE_FILLS;
  opt.strokes = TRACE_STROKES;

  t.tracing = true;

  // Expand
  doc.selection = null;
  t.selected = true;
  app.executeMenuCommand("expandStyle");
  app.executeMenuCommand("expand");

  // Remove embedded/placed originals (optional but usually desired)
  for (var r = doc.rasterItems.length - 1; r >= 0; r--) {
    try { doc.rasterItems[r].remove(); } catch (e) {}
  }
  for (var p = doc.placedItems.length - 1; p >= 0; p--) {
    try { doc.placedItems[p].remove(); } catch (e) {}
  }

  // Normalize styles + attempt closure
  var closedAuto = 0, stillOpen = 0;

  for (var i = 0; i < doc.pathItems.length; i++) {
    var it = doc.pathItems[i];

    if (it.guides || it.clipping) continue;

    // Enforce coloring-book spec
    it.stroked = true;
    it.strokeColor = BLACK;
    it.strokeWidth = STROKE_PX;

    it.filled = true;
    it.fillColor = WHITE;

    // Best-effort close
    if (!it.closed && it.pathPoints.length >= 2) {
      var first = it.pathPoints[0].anchor;
      var last = it.pathPoints[it.pathPoints.length - 1].anchor;

      if (dist(first, last) <= CLOSE_TOLERANCE_PX) {
        it.closed = true;
        closedAuto++;
      } else {
        // Flag for manual fix
        it.strokeColor = MAGENTA;
        stillOpen++;
      }
    }
  }

  alert("Done.\nAuto-closed: " + closedAuto + "\nStill open (magenta): " + stillOpen +
        "\nTip: If many magenta paths appear, run Prompt 2 to get a cleaner binary raster before tracing.");

})();
