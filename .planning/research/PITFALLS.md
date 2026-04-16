# Domain Pitfalls: v1.82 Illustrated Tutorial and Publication-Quality Visualization

**Milestone:** `v1.82`
**Researched:** 2026-04-15
**Confidence:** HIGH for notebook rendering and tutorial narrative risks,
MEDIUM for quasicrystal-specific visualization edge cases.

## Critical Pitfalls

### Pitfall 1: Plotly 3D HTML blob size crashes notebooks

**What goes wrong:**
Each plotly 3D figure embeds the full plotly.js bundle (~3.5 MB) in the
notebook cell output. Multiple 3D figures in one notebook can balloon the
`.ipynb` file to 30+ MB, making it slow to open, version, and render on
GitHub.

**Why it happens here:**
The milestone adds multiple interactive 3D figures (orbit view, shell
decomposition, cage view, expansion view) to one notebook.

**Prevention:**
- Use `fig.show(renderer="notebook_connected")` which loads plotly.js from CDN
  once instead of embedding per-cell.
- Limit the number of inline 3D figures to 3-4 per notebook.
- For the markdown tutorial, export static PNG/SVG via kaleido instead of
  embedding interactive HTML.
- Strip large cell outputs before committing with `nbstripout` or equivalent.

**Address in phase:** Phase 2 (plotly integration).

### Pitfall 2: Misleading periodic approximant shown as true quasicrystal

**What goes wrong:**
The Sc-Zn Tsai bridge is a cubic approximant (a=b=c=13.79 Å, all angles 90°),
not a true icosahedral quasicrystal. The expansion view could mislead readers
into thinking they are seeing aperiodic tiling when the structure is actually
periodic.

**Why it happens here:**
The Features research flagged that a 2D Penrose tiling overlay would be
incorrect for this 3D approximant. The same risk applies to any expansion view
that does not clearly label the periodicity.

**Prevention:**
- Label expansion views as "periodic approximant tiling" not "quasicrystal
  expansion."
- Add a prose note explaining the relationship between the Tsai cluster motif
  and the periodic unit cell.
- Do NOT overlay Penrose tilings on the 3D structure.
- If showing diffraction, note that the approximant has Bragg peaks at rational
  positions, not the irrational positions of a true QC.

**Address in phase:** Phase 1 (narrative) and Phase 3 (expansion view).

### Pitfall 3: Label overcrowding in 3D views

**What goes wrong:**
The current viewer shows all 52 labeled points simultaneously. With
human-readable labels (longer than `pent.top.center`), the 3D view becomes an
unreadable wall of overlapping text.

**Why it happens here:**
The milestone specifically asks for more intuitive labels. Longer, clearer
labels take more screen space.

**Prevention:**
- Default to labels OFF in 3D plotly views; show on hover instead.
- Provide a toggle or separate "labeled view" figure with only representative
  sites labeled (one per orbit, not all 52).
- Use color legend + hover text as the primary identification method.
- Keep the full labeled view available as an explicit option, not the default.

**Address in phase:** Phase 2 (plotly 3D + label design).

### Pitfall 4: Shell assignment hardcoded instead of computed

**What goes wrong:**
The orbit-to-shell mapping is entered manually from a paper reference and
becomes wrong when the design changes or a different system is used.

**Why it happens here:**
The IUCrJ 2016 Sc-Zn paper shows specific shell assignments for the Tsai
cluster. It is tempting to copy those directly.

**Prevention:**
- Compute shell assignment from mean radial distance of each orbit's sites
  relative to `motif_center` in the design YAML.
- Validate against the known Tsai shell sequence as a sanity check, but do not
  hardcode it.
- Log the computed shell ordering so users can verify it.

**Address in phase:** Phase 2 (orbit visualization).

### Pitfall 5: Narrative drifts from checked artifacts

**What goes wrong:**
The prose explains a workflow or result that does not match the actual checked
artifacts in the repo. For example, claiming 4 shortlisted candidates when the
checked snapshot has a different count, or describing validation results that
do not match the committed data.

**Why it happens here:**
The milestone adds substantial narrative text. The more prose, the more surface
area for claims that age badly when artifacts are refreshed.

**Prevention:**
- Every quantitative claim in the narrative must reference a specific checked
  artifact file and field.
- Use notebook cells to pull values programmatically rather than hardcoding
  numbers in prose.
- In the markdown tutorial, use phrasing like "the current checked snapshot
  shows..." rather than absolute claims.
- Verify all narrative claims against actual artifact values before marking
  phases complete.

**Address in phase:** Phase 1 (narrative) — set the convention early.

### Pitfall 6: Matplotlib figure sizing inconsistent between notebook and export

**What goes wrong:**
Figures look good inline in the notebook but are too small, too large, or have
unreadable labels when exported as PNG/SVG for the markdown tutorial or PDF.

**Why it happens here:**
Notebooks render at screen DPI (~72-96), but publication figures need 300 DPI.
Font sizes that look right at screen DPI become tiny at publication DPI unless
explicitly scaled.

**Prevention:**
- Define a shared figure style context in `matplotlib_pub.py` with explicit
  `figsize`, `dpi`, and font size settings.
- Use `matplotlib.style.context()` to isolate tutorial figure style from user's
  global matplotlib config.
- Test figure export at 300 DPI as part of verification.
- Keep figure width at 6-8 inches max for readability.

**Address in phase:** Phase 3 (matplotlib panels).

### Pitfall 7: Crystal expansion performance with large supercells

**What goes wrong:**
Expanding a 100-site motif into a 3x3x3 supercell produces 2,700 sites. With
polyhedral cages and bonds, the plotly figure can have thousands of traces and
become sluggish or crash the browser.

**Why it happens here:**
The user wants to "show how the crystal would look by expanding it." The
natural instinct is to expand further than necessary.

**Prevention:**
- Default to 2x2x2 expansion (800 sites) which is visually clear and
  performant.
- Use `Scatter3d` with `mode='markers'` (no lines) for the expansion view.
- Offer the full cage/bond view only for the central unit cell.
- Add a performance note in the notebook if expanding beyond 2x2x2.

**Address in phase:** Phase 3 (expansion view).

### Pitfall 8: Color scheme not accessible

**What goes wrong:**
Orbit colors that look distinct on a standard display are indistinguishable for
colorblind users (~8% of male readers).

**Prevention:**
- Use a colorblind-safe palette: Wong (2011) 7-color or Tol's qualitative
  scheme (both have 5+ distinguishable colors, matching the 5 orbits).
- Add marker shape variation as a secondary channel (circle, square, diamond,
  triangle, cross) so orbits are distinguishable even in grayscale.
- Test with a CVD simulator before finalizing.

**Address in phase:** Phase 2 (color scheme definition).

## Cross-Cutting Warning

Keep the markdown tutorial and notebook in sync. When narrative or figures
change in one, update the other. The v1.81 convention — markdown is the short
operator story, notebook is the rich runnable companion — should carry forward.
Do not let the notebook grow new sections that have no markdown counterpart or
vice versa.
