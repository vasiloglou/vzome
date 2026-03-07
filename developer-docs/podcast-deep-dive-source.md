# From a Geometric Toy to Materials Discovery: The vZome Story

## A Construction Toy and Three Nobel Prizes Share the Same Math

Here is a fact that sounds made up: a construction toy designed in the 1990s, a class of materials that won the Nobel Prize in Chemistry in 2011, the molecular structure of buckminsterfullerene (Nobel 1996), and the protein shells of nearly every virus on Earth all share the exact same mathematical foundation. That foundation is the golden ratio — the number phi, approximately 1.618 — and the algebraic field it generates.

The story of how this connection goes from recreational geometry to cutting-edge materials science is the story of vZome.

In 1984, Dan Shechtman was working at the National Bureau of Standards in Washington, D.C., studying rapidly cooled aluminum-manganese alloys. He put a sample under an electron microscope and saw something that should not exist: a diffraction pattern with perfect ten-fold symmetry. Five-fold and ten-fold rotational symmetry are forbidden by the fundamental theorem of crystallography. Periodic crystals — the only kind anyone believed existed — can only have 2-fold, 3-fold, 4-fold, or 6-fold rotational symmetry. Shechtman's colleagues told him he was wrong. He was asked to leave his research group. Linus Pauling, who had won two Nobel Prizes, publicly declared: "There are no quasicrystals, only quasi-scientists."

Shechtman was right. He won the Nobel Prize in Chemistry in 2011 — alone.

What makes quasicrystals work is the golden ratio. Their atomic positions live in a mathematical structure called Q(phi) — the field of numbers that can be written as a + b*phi, where a and b are rational numbers. In practice, the positions land on an even more specific structure: Z[phi], where a and b are integers. This is the same number system that governs a physical construction toy called Zometool, and its virtual counterpart, an open-source application called vZome.

The question this document explores is: what if the same geometry that makes a toy work could help discover materials that do not exist yet?

---

## The Connector Ball: 62 Holes of Pure Mathematics

### What Is Zometool?

Zometool is a physical construction kit consisting of two types of pieces: connector balls and colored struts. The connector ball is approximately spherical, with 62 precisely positioned holes in three distinct shapes. The struts are thin rods with matching cross-sections — each shape of hole accepts exactly one family of struts. By connecting struts through balls, you can build an extraordinary range of three-dimensional geometric structures.

What most people do not realize is that those 62 holes are not arbitrary. They are a mathematically exact encoding of icosahedral symmetry — the same symmetry group that governs quasicrystals, viral capsids, and buckminsterfullerene.

### Where Do 62 Holes Come From?

The derivation follows a beautiful four-step geometric progression:

**Step 1: Start with the icosahedron.** The icosahedron has 20 triangular faces, 12 vertices, and 30 edges. Its rotational symmetry group contains exactly 60 rotations. These rotations come in three families: rotations around axes through pairs of opposite vertices (5-fold, 6 axes), rotations around axes through pairs of opposite face centers (3-fold, 10 axes), and rotations around axes through pairs of opposite edge midpoints (2-fold, 15 axes). That gives 6 + 10 + 15 = 31 axes, or 62 directed half-axes.

**Step 2: Rectification.** Cut each vertex of the icosahedron at the midpoint of its edges. The result is the icosidodecahedron: 30 vertices (one per original edge), 32 faces (12 pentagons from the original vertices, 20 triangles from the original faces), and 60 edges. The 30 vertices sit at the 2-fold axis positions. Combined with the 20 face centers (3-fold) and 12 original vertex positions (5-fold), you get 62 special positions on the surface — one per symmetry half-axis.

**Step 3: Expansion.** Push apart the faces of the icosidodecahedron until the edges separate, inserting squares between them. The result is the rhombicosidodecahedron: 62 faces consisting of 12 pentagons, 20 triangles, and 30 squares. Each face corresponds to one symmetry axis.

**Step 4: Sphericalize.** Inflate the rhombicosidodecahedron onto a sphere. The squares become golden rectangles (aspect ratio phi:1, not 1:1), encoding the fact that the 2-fold axes have only 180-degree symmetry, not 90-degree. A square would incorrectly imply 4-fold symmetry.

The result is the Zometool connector ball: a sphere with 12 pentagonal holes (5-fold axes), 20 triangular holes (3-fold axes), and 30 rectangular holes (2-fold axes).

### Three Colors, Three Symmetries

The struts come in three primary colors, one for each hole shape:

- **Blue struts** (rectangular cross-section): 30 holes, 15 axes. These directions are parallel to the edges of both the icosahedron and the dodecahedron. Blue struts are the workhorses — most Zometool models are primarily blue.

- **Yellow struts** (triangular cross-section): 20 holes, 10 axes. These connect the centers of opposite triangular faces of the icosahedron. In a dodecahedron model, yellow directions connect pairs of opposite face diagonals.

- **Red struts** (pentagonal cross-section): 12 holes, 6 axes. These connect opposite vertices of the icosahedron (equivalently, opposite face centers of the dodecahedron). Red struts point along the 5-fold symmetry axes.

Each color comes in multiple lengths. The critical fact: each successive length is exactly phi times the previous one. A "medium" blue strut is phi times longer than a "short" blue strut. This phi-scaling is not an approximation — it is algebraically exact.

### The Golden Ratio: Why Phi Rules Everything

The golden ratio phi = (1 + sqrt(5)) / 2 ≈ 1.618 has a defining algebraic property: phi squared equals phi plus one. Written as an equation: phi^2 = phi + 1. This single identity makes the entire Zometool system work.

Because phi^2 = phi + 1, any power of phi can be written as a + b*phi where a and b are integers. The powers follow the Fibonacci sequence:

- phi^0 = 1 + 0*phi (Fibonacci: 1, 0)
- phi^1 = 0 + 1*phi (Fibonacci: 0, 1)
- phi^2 = 1 + 1*phi (Fibonacci: 1, 1)
- phi^3 = 1 + 2*phi (Fibonacci: 1, 2)
- phi^4 = 2 + 3*phi (Fibonacci: 2, 3)
- phi^5 = 3 + 5*phi (Fibonacci: 3, 5)

In general, phi^n = F(n) + F(n+1)*phi, where F(n) is the nth Fibonacci number. Multiplying any number in the golden field by phi is equivalent to applying the Fibonacci recurrence: the pair (a, b) maps to (b, a+b). This will become important when we discuss the materials discovery pipeline.

The deeper reason phi matters: the rotational symmetry group of the icosahedron (60 rotations) can be represented as 3x3 matrices whose entries are all elements of Q(phi). When you rotate a point with Q(phi) coordinates by any icosahedral rotation, you get another point with Q(phi) coordinates. Zero rounding error. Zero drift. Exact, forever.

Think of the connector ball as a three-dimensional compass that only points in 62 specific directions. Every direction it allows is dictated by the mathematics of the icosahedron, and every measurement it makes is exact.

---

## vZome: The Virtual Zometool (And Why It Goes Further)

### Twenty Years of Exact Geometry

vZome is an open-source application for creating virtual Zometool models and exploring constrained geometric realms. Started around 2001 by Scott Vorthmann, with significant contributions from David Hall, it has accumulated over 4,238 commits across more than two decades of continuous development.

vZome runs in two forms: a web application at vzome.com/app (built with SolidJS and Three.js) and a desktop Java application. The web version is the active focus of development and provides interactive 3D construction with trackball controls, multiple rendering modes, and real-time manipulation.

### Zero Floating-Point Errors

The most important technical feature of vZome is exact arithmetic. Every coordinate in a vZome model is stored as a linear combination of algebraic basis values with integer coefficients — never as floating-point numbers. For the standard Zometool system, every coordinate is a number of the form a + b*phi, stored as the integer pair (a, b).

The difference matters. Think of it as the difference between storing "one-third" and storing "0.33333333." The first is exact. The second is an approximation that introduces error every time you compute with it. Over hundreds of operations, floating-point errors accumulate. In vZome, they do not. A closed polygon that returns to its starting point returns exactly, verified algebraically. A symmetry operation applied 60 times returns to exactly the original position, not "close enough."

### Beyond Three Colors

While the physical Zometool kit has three strut colors, vZome supports over fifteen in icosahedral symmetry alone: blue, yellow, red, green, orange, purple, black, lavender, olive, maroon, rose, navy, turquoise, coral, sulfur, and more. Each represents a geometrically distinct direction family — an "orbit" under the icosahedral group. Green struts, for instance, follow directions halfway between blue and yellow.

Even more remarkably, vZome supports eleven different algebraic number fields beyond the golden ratio. You can work in the sqrt(2) field for octahedral symmetry (cubes, octahedra), the sqrt(3) field for hexagonal and tetrahedral geometry, the heptagonal field for 7-fold symmetry, and PolygonField(N) for arbitrary N-fold symmetry. Each field provides its own exact arithmetic, its own symmetry group, and its own construction possibilities.

### What You Can Visualize

The range of geometric objects constructible in vZome is vast:

- **Classic polyhedra:** Icosahedra, dodecahedra, tetrahedra, octahedra, cubes, and all thirteen Archimedean solids
- **Stellations:** All 59 stellations of the icosahedron, explorable through a dedicated web application
- **Truncations and expansions:** Truncated icosahedra (the shape of C60 buckminsterfullerene and a soccer ball), rhombicosidodecahedra, snub dodecahedra
- **Tilings:** Penrose tilings (2D quasicrystal patterns), rhombic tilings, geodesic subdivisions
- **4D polytopes:** Projections of the 120-cell (120 dodecahedral cells, 600 vertices, symmetry group H4 with 14,400 elements), the 600-cell, the 24-cell, and the tesseract
- **Molecular structures:** C60 fullerene, viral capsid models, Mackay icosahedra, quasicrystal approximant cells
- **E8 root system projections:** The 240 roots of the densest 8D lattice, projected to 3D, forming concentric icosahedral shells

The Zomic scripting language adds programmatic construction: a turtle-graphics system in 3D with commands like `move`, `rotate`, `symmetry`, and `repeat`. You can script a logarithmic spiral, a fractal tree, or a complete polytope in a few lines of code.

Models can be exported to STL for 3D printing, PDB for molecular visualization software, glTF for web rendering, POV-Ray for photorealistic rendering, SVG and PDF for publication, and OpenSCAD and STEP for engineering applications.

### The File Format Is the Physics

Here is the detail that bridges the toy to the science. The vZome file format (.vZome, XML) stores each 3D point as six integers: "a0 a1 b0 b1 c0 c1". These represent three coordinates in the golden field:

- x = a0 + a1*phi
- y = b0 + b1*phi
- z = c0 + c1*phi

Six integers for one 3D point. But six integers can also be read as the coordinates of a point in a six-dimensional lattice. And the standard method for generating quasicrystal structures — the cut-and-project method — starts with exactly a six-dimensional periodic lattice, slices it at an irrational angle involving phi, and projects down to 3D.

The six integers in a vZome file ARE the six-dimensional lattice coordinates used in quasicrystal theory. The file format is the quasicrystal math. This is not a metaphor.

---

## Three Nobel Prizes, One Symmetry Group

The mathematical framework underlying vZome — icosahedral symmetry in the golden field Q(phi) — appears across an astonishing range of physical science. Every one of these connections is the same math.

### Quasicrystals: The "Impossible" Materials

Classical crystallography proved that periodic structures in 3D can only have 2-fold, 3-fold, 4-fold, or 6-fold rotational symmetry. This was considered a theorem, not a conjecture. When Shechtman observed 10-fold symmetry in 1984, it meant one of two things: the fundamental theorem was wrong, or the structure was not periodic.

The resolution: quasicrystals are ordered but not periodic. They have long-range orientational order (sharp diffraction peaks) but no translational periodicity. Their structure can be generated by the cut-and-project method: start with a periodic lattice in 6D, select points near a particular 3D hyperplane, and project down. The resulting 3D arrangement has sharp diffraction and icosahedral symmetry — but never repeats.

The coordinates of every atom in an icosahedral quasicrystal lie in Q(phi)^3. The symmetry group is the same 60 rotations. The Z[phi] lattice that organizes the atoms is the same lattice that organizes Zometool connector positions. Many Zometool models are, quite literally, finite patches of quasicrystal-compatible point sets.

### Viral Capsids: Biology's Icosahedra

Most viruses package their genetic material inside an icosahedral protein shell called a capsid. The capsid is built from protein subunits arranged with the same 60-fold symmetry as the icosahedron.

The Caspar-Klug classification (part of the work that contributed to Aaron Klug's Nobel Prize in 1982) organizes capsids by a triangulation number T = h^2 + hk + k^2. A T=1 capsid has 60 protein subunits — one per rotation — as seen in satellite tobacco necrosis virus. Poliovirus and rhinovirus (the common cold) are T=3 with 180 subunits. Human papillomavirus (HPV) is T=7 with 420 subunits. Adenovirus is T=25 with 1,500 subunits.

Every icosahedral capsid, regardless of T-number, has exactly 12 pentamers — clusters of five protein subunits arranged around the twelve 5-fold symmetry axes. These are the same twelve positions as the twelve pentagonal holes on the Zometool connector ball. The same twelve vertices of the icosahedron.

### C60 Fullerene: The Nobel Prize Soccer Ball

In 1985, Harold Kroto, Robert Curl, and Richard Smalley discovered a stable molecule of sixty carbon atoms: C60, buckminsterfullerene. Its structure is the truncated icosahedron — the same shape as a soccer ball: 12 pentagonal faces, 20 hexagonal faces, 90 edges, 60 vertices. They shared the Nobel Prize in Chemistry in 1996.

Every vertex of the truncated icosahedron has coordinates in Q(phi)^3 and is directly constructible in vZome. C60 has full icosahedral symmetry (I_h, order 120 including reflections). Electronic structure calculations for C60 exploit this symmetry to block-diagonalize the quantum mechanical Hamiltonian.

### Penrose Tilings: 2D Quasicrystals

Roger Penrose discovered in 1974 that two rhombus shapes — a "fat" rhombus with angles 72/108 degrees and a "thin" rhombus with angles 36/144 degrees — can tile the entire plane without ever repeating. The resulting patterns have five-fold orientational order. The ratio of fat to thin rhombi approaches phi.

Penrose tilings are self-similar: you can group tiles into larger tiles of the same two types, and the larger tiles form another Penrose tiling at a larger scale. The scaling factor between levels is phi — the same scaling as Zometool strut lengths.

In 3D, the generalization uses two rhombohedra (prolate and oblate) to fill space aperiodically with icosahedral symmetry. This is the Ammann-Kramer-Neri tiling, and its vertices form exactly the Z[phi] lattice — the same lattice as Zometool.

### E8 and the Deepest Connections

The E8 lattice is the densest lattice packing in eight dimensions. Its 240 minimal vectors (root vectors) can be projected from 8D to 3D along icosahedral directions. The resulting points land on concentric shells with exact icosahedral symmetry:

| Shell | Polyhedron | Vertices | Radius |
|-------|-----------|----------|--------|
| 1 | Icosahedron | 12 | 1 |
| 2 | Dodecahedron | 20 | phi |
| 3 | Icosidodecahedron | 30 | phi^2 |

The shell radii are powers of phi — the same scaling as Zometool strut lengths. Every vertex has Q(phi)^3 coordinates. The E8 x E8 gauge group appears in heterotic string theory as the symmetry of one of the consistent ten-dimensional theories. Garrett Lisi's controversial 2007 "Exceptionally Simple Theory of Everything" attempted to embed all particles and forces in E8.

### The Unifying Pattern

| Property | Quasicrystals | Viral Capsids | C60 | Zometool/vZome |
|----------|--------------|---------------|-----|----------------|
| Symmetry group | Icosahedral (60 rotations) | Icosahedral (60 rotations) | Icosahedral (60+60 reflections) | Icosahedral (60 rotations) |
| Coordinate field | Q(phi) | Q(phi) | Q(phi) | Q(phi) |
| Special 12 positions | 12 vertex clusters | 12 pentamers | 12 pentagons | 12 pentagonal holes |
| Scaling principle | phi^n between shells | T-number classification | Bond length ratios | phi^n between strut lengths |
| Aperiodicity | No translational symmetry | N/A (finite) | N/A (finite) | Same (finite constructions) |

Three Nobel Prizes — quasicrystals (2011), fullerenes (1996), and viral capsid theory (1982) — all describe structures whose mathematics is the same as a construction toy.

### Metallic Clusters: The Mackay Icosahedron

In metallic clusters and metallic glasses, the Mackay icosahedron is the most stable small cluster for many elements: 13 atoms (1 central atom plus 12 at the vertices of an icosahedron). Larger Mackay icosahedra have 55, 147, 309 atoms — following the magic number formula 10n^2 + 2. These clusters appear in Frank-Kasper phases, noble gas clusters, and are the local building blocks of many metallic glasses. The same icosahedral geometry. The same golden ratio. The same math.

---

## The Materials Discovery Pipeline: From Geometry to New Materials

### The Core Insight

Here is where the story turns from recreational mathematics to practical science. If quasicrystal-compatible structures have atomic positions in Z[phi]^3, then searching for new quasicrystal materials is equivalent to searching over integer pairs.

Instead of optimizing over all of continuous 3D space — an infinite, uncountable search space — you constrain candidates to the Z[phi] lattice. Each atomic coordinate becomes (a + b*phi), stored as the integer pair (a, b). One 3D atom position is six integers. A structure with 12 atoms is 72 integers plus a species assignment.

This dramatically shrinks the search space while keeping all quasicrystal-compatible structures. You cannot miss a valid quasicrystal this way — every one has Z[phi] coordinates. But you have turned a continuous optimization problem into a discrete one over bounded integers.

### Phi-Scaling Is Fibonacci

The pipeline implements phi-scaling through a function called `phi_scale_pair`. It takes an integer pair (a, b) representing the number a + b*phi, and multiplies it by phi. The result: (a, b) maps to (b, a+b).

This is the Fibonacci recurrence. Scaling a quasicrystal structure by the golden ratio is literally computing the next Fibonacci number for every coordinate. The reverse operation — dividing by phi — maps (a, b) to (b-a, a). It is exact and perfectly invertible. No rounding, no information loss.

This means the pipeline can inflate and deflate candidate structures through Fibonacci arithmetic on their integer coordinate pairs. It is algebraically exact at every step.

### Template Families: Cookie Cutters for Atoms

The pipeline does not search blindly over all possible Z[phi] positions. Instead, it uses template families — known approximant motif cells that define where atoms can sit. Three families are built in:

**Icosahedral approximant 1/1:** 12 atomic sites positioned at the vertices of an icosahedron, within a cubic unit cell of approximately 14.2 angstroms. This template targets the Al-Cu-Fe system — the alloy family that includes Shechtman's Nobel Prize-winning quasicrystal. The pipeline loads a system-anchored Mackay-type orbit library for this system.

**Decagonal proxy 2/1:** 10 atomic sites arranged in two pentagonal rings (one rotated by 36 degrees relative to the other), with a non-cubic cell of approximately 11.8 x 11.8 x 16.0 angstroms. This targets the Al-Pd-Mn decagonal quasicrystal system, using a xi-prime pseudo-Mackay orbit library.

**Cubic proxy 1/0:** 8 atomic sites at cube corner positions, in a 10.0 angstrom cubic cell. This targets the Sc-Zn system, specifically the Tsai-type ScZn6 cluster, with an orbit library exported from crystallographic data (COD CIF entry 4344182).

Each template can be generic (built-in mathematical positions) or anchored to real experimental structures through orbit library JSON files. The system tries the anchored version first and falls back to generic if none exists.

### Seven Pipeline Stages

The pipeline is implemented as a Python CLI tool called `mdisc` with seven commands, comprising approximately 60 modules and 7,200 lines of code.

**1. Ingest** (`mdisc ingest`): Load known reference phases — materials that already exist. These form the baseline for computing how far above the convex hull (the thermodynamic stability boundary) each candidate sits.

**2. Generate** (`mdisc generate`): Create candidate structures from Z[phi] templates. Generation is fully deterministic from a seed — the same seed and index always produce the same candidate. The pipeline applies coordinate permutation (6 variants), phi-scaling (inflate/deflate), translation, and coefficient bounding to create diverse structures from each template. Each candidate's unit cell can also scale by 1/phi, 1, or phi — the golden ratio is built into the search grid.

**3. Screen** (`mdisc screen`): Fast filtering with a single ML interatomic potential. Relax the structure, check if the energy per atom is reasonable, verify minimum interatomic distances, and shortlist the top candidates. In real mode, screening thresholds adapt to the actual distribution (30th percentile for distance, 65th for energy) rather than using fixed cutoffs.

**4. High-Fidelity Validate** (`mdisc hifi-validate`): This is where the committee of three ML models comes in. MACE, CHGNet, and MatterSim each independently evaluate every surviving candidate. The pipeline computes committee disagreement (uncertainty), checks the energy against competing phases (distance to convex hull), runs phonon stability analysis (are there imaginary phonon modes?), performs short molecular dynamics simulations (does the structure remain stable at 600 K?), and checks XRD pattern confidence.

A candidate passes validation only if ALL of the following hold: uncertainty per atom is at most 0.04 eV, energy above the convex hull is at most 0.08 eV/atom, the phonon check passes, the MD check passes, and the XRD check passes. Five gates, all must clear.

Think of the committee of three ML models as three independent peer reviewers. If all three agree a candidate is stable, confidence is high. If they disagree wildly, that candidate gets flagged as uncertain and probably rejected. Built-in peer review for materials.

**5. Rank** (`mdisc hifi-rank`): Uncertainty-aware ranking of validated candidates, producing calibrated stability probability, out-of-distribution score, novelty score, and overall decision score.

**6. Active Learn** (`mdisc active-learn`): Train a surrogate model on the validated candidates — what structural and chemical features predict stability? Then use uncertainty-aware acquisition to propose the best next batch to validate. The system improves each cycle. Self-improving materials discovery.

**7. Report** (`mdisc report`): Generate experiment-ready output with simulated powder X-ray diffraction patterns, recommendation tiers, risk flags, and release-gate calibration. This is what a materials scientist would use to decide what to synthesize in the lab.

### No DFT: The Speed Advantage

The standard approach to computational materials discovery uses Density Functional Theory — a quantum mechanical calculation that solves the Schrodinger equation approximately for a periodic structure. DFT is accurate but slow: a single structure can take hours to days on a supercomputer, depending on system size and desired accuracy.

The vZome materials pipeline bypasses DFT entirely. Instead, it uses machine-learned interatomic potentials — neural networks trained on millions of DFT calculations — that can evaluate a structure in seconds rather than hours. The three models in the committee (MACE, CHGNet, MatterSim) were each trained on large databases of quantum mechanical calculations. They have learned the patterns. They are not as accurate as DFT for any individual structure, but they are 100 to 1,000 times faster, and by using three models instead of one, you get built-in uncertainty quantification.

This is the difference between calculating every raindrop in a thunderstorm from first principles versus using a weather forecast model trained on decades of meteorological data. The forecast is not as precise for any single raindrop, but it tells you whether it will rain — and it does so in minutes, not years.

### Four Layers of Execution

The pipeline has an elegant backend architecture with four execution layers:

- **Mock mode:** Deterministic fixture data for fast testing and CI. Run the entire pipeline in seconds with reproducible results.
- **Fixture mode:** Pinned snapshots from real calculations for reproducible benchmarking without external dependencies.
- **Exec mode:** External command execution with on-disk caching. Run real ML models as subprocesses and cache results.
- **Native mode:** Direct Python calls to MACE, CHGNet, pymatgen, and ASE. Full production execution.

All four layers use the same code, the same data schemas, the same CLI commands. You switch between them by changing a single field in a YAML configuration file. This means a researcher can develop and test with mock data in minutes, validate with pinned benchmarks, and then run production calculations — all with the same pipeline.

---

## Why This Matters

### The Full Arc

The journey from a geometric toy to a materials discovery pipeline spans over two decades and multiple scientific domains:

**Physical toy** (Zometool, 1990s): A construction kit whose connector ball encodes icosahedral symmetry in 62 precisely placed holes.

**Virtual modeler** (vZome, 2001-present): An open-source application with exact arithmetic in the golden field, supporting 15+ strut colors, 11+ algebraic fields, 4D polytope projections, scripting, and export to dozens of formats. Over 20 years and 4,238 commits of continuous development.

**Materials discovery engine** (2025-2026): A 60-module Python pipeline that uses Z[phi] geometry to generate, screen, validate, rank, and iteratively improve candidate quasicrystal-compatible materials — all without DFT.

This is a line from recreational mathematics to cutting-edge materials science. The same algebraic identity — phi^2 = phi + 1 — that makes a toy work is now being used to search for materials that do not exist yet.

### What Quasicrystal Materials Could Enable

Quasicrystalline materials have unusual and potentially useful properties:

- **Low thermal conductivity** despite metallic bonding — making them candidates for thermoelectric energy conversion
- **Non-stick and anti-corrosion surfaces** — quasicrystalline coatings are already used on some cookware
- **Extreme hardness** combined with low friction coefficients
- **Unusual electronic properties** — pseudogaps at the Fermi level that could enable photonic applications
- **Hydrogen storage** — some quasicrystal alloys show promising hydrogen absorption characteristics

The pipeline currently targets three real alloy systems: Al-Cu-Fe (the classic icosahedral quasicrystal family), Al-Pd-Mn (a well-studied decagonal system), and Sc-Zn (the Tsai cluster family, a more recent discovery). New systems can be added by creating a YAML configuration file and, optionally, registering element properties and orbit libraries.

### Open Source, Reproducible, Production-Ready

The entire codebase lives in a single Git repository. It is written in Python 3.11+ with strict type checking (mypy in strict mode), linting (ruff), and 21 test files covering unit, integration, and end-to-end scenarios. Dependencies are managed with uv. Every candidate is deterministically generated from a seed. Every pipeline stage emits a manifest with content hashes for reproducibility. Every intermediate artifact is stored as JSONL.

A researcher can install the pipeline, run `uv sync --extra dev`, execute `uv run pytest` to verify everything works, and then run the full seven-stage pipeline on mock data in under a minute. Switching to real ML models requires installing the optional MLIP dependencies and changing one YAML field.

### The Deeper Point

Deep mathematics has a way of finding applications that nobody predicted. The golden ratio was studied by Euclid. Fibonacci numbers appeared in a 13th-century book about rabbit populations. Icosahedral symmetry was classified in the 19th century. For most of the 20th century, these were considered beautiful but impractical — mathematical curiosities with no bearing on the real world.

Then Shechtman looked through a microscope in 1984 and discovered that atoms arrange themselves using this exact same math. Now, four decades later, a geometric construction toy built on the same principles is being extended into a computational tool for discovering materials that have never been synthesized.

The connector ball has 62 holes. Each one encodes a symmetry axis. Each axis connects to the golden ratio. And the golden ratio connects to quasicrystals, to viral shells, to carbon molecules, to the densest lattice in eight dimensions, and now — to a pipeline for discovering new materials.

---

## Further Reading

- **Try vZome online:** https://vzome.com/app
- **vZome website:** https://vzome.com
- **Source code:** https://github.com/david-hall/vzome (vZome) and the `materials-discovery/` workspace within the repository
- **vZome Geometry Tutorial:** `developer-docs/vzome-geometry-tutorial.md` — comprehensive mathematical reference (Section 10.8 covers the materials optimization framework)
- **Materials Discovery Documentation:** `developer-docs/materials_discovery/index.md` — full pipeline reference including architecture, backend system, configuration, and data schemas
- **HYPOD-X datasets:** https://www.nature.com/articles/s41597-024-04043-z
- **Matbench Discovery benchmark:** https://www.nature.com/articles/s42256-025-01055-1
- **Quasicrystal ML discovery:** https://doi.org/10.1103/PhysRevMaterials.7.093805
- **CHGNet:** https://github.com/CederGroupHub/chgnet | **MACE:** https://github.com/ACEsuit/mace | **MatterSim:** https://github.com/microsoft/mattersim
- **"Zome Geometry"** by George Hart and Henri Picciotto — the definitive book on Zometool mathematics
