# vZome Geometry Tutorial

A comprehensive guide to the mathematical foundations, architecture, and geometric systems behind vZome — the virtual Zometool application for exploring constrained geometric realms.

---

## Table of Contents

1. [What is Zometool?](#1-what-is-zometool)
2. [The Golden Ratio: Why Zometool Works](#2-the-golden-ratio-why-zometool-works)
3. [Exact Arithmetic: Algebraic Number Fields](#3-exact-arithmetic-algebraic-number-fields)
4. [Symmetry Systems](#4-symmetry-systems)
5. [Geometric Construction](#5-geometric-construction)
6. [The Zomic Scripting Language](#6-the-zomic-scripting-language)
7. [4D Polytopes and Projections](#7-4d-polytopes-and-projections)
8. [File Formats](#8-file-formats)
9. [Connections to Quasicrystals](#9-connections-to-quasicrystals)
10. [Physics in Zome Geometry](#10-physics-in-zome-geometry)
11. [Further Resources](#11-further-resources)

---

## 1. What is Zometool?

Zometool is a precision mathematical construction toy designed to build 3D geometric structures using two components:

### Euclidean Bridge: Same Geometry, Different Allowed Coordinates

If you already know Euclidean geometry, the fastest way to understand zome geometry is:

- Same ambient space: all points, lines, planes, angles, and rigid motions are still in ordinary 3D Euclidean space.
- Different coordinate language: instead of arbitrary real coordinates, constructions are built from vectors whose components lie in `Q(phi)` (numbers of the form `a + b*phi`).
- Direction constraint: strut directions come from finite icosahedral orbits (blue/yellow/red plus additional vZome orbits).
- Length constraint: strut lengths are powers of `phi`, so reachable positions are integer combinations in a `Z[phi]` module.

So zome geometry is best viewed as **Euclidean geometry with a structured ruler and compass**: fewer allowed moves, but exact algebraic closure and strong symmetry.

### The Connector Ball

The Zometool connector ball is approximately spherical, with 62 precisely positioned holes in three shapes. These hole positions correspond to the symmetry axes of the icosahedron (see [From Icosahedron to Connector Ball](#from-icosahedron-to-connector-ball) below):

| Hole Shape | Count | Symmetry Axis | Rotational Order |
|------------|-------|---------------|------------------|
| **Rectangular** | 30 | 2-fold axes | Along icosidodecahedron edges |
| **Triangular** | 20 | 3-fold axes | Icosahedron face centers |
| **Pentagonal** | 12 | 5-fold axes | Dodecahedron face centers |

Each hole shape accepts only struts with a matching cross-section, physically enforcing geometric constraints.

![Hole Shapes and Strut Colors](images/hole-shapes.svg)

#### Why These Counts?

The hole counts are derived directly from the **symmetry axes of the icosahedron**. Each hole sits where a rotation axis pierces the surface of the ball. Since each axis passes through both sides, the number of holes is twice the number of axes:

| Hole | Rotation | Geometric Origin | Axes | Holes (2 ends per axis) |
|------|----------|-----------------|------|------------------------|
| Rectangular | 2-fold (180°) | One axis per **edge midpoint** (30 edges → 15 opposite pairs) | 15 | 15 × 2 = **30** |
| Triangular | 3-fold (120°) | One axis per **face center** (20 faces → 10 opposite pairs) | 10 | 10 × 2 = **20** |
| Pentagonal | 5-fold (72°) | One axis per **vertex** (12 vertices → 6 opposite pairs) | 6 | 6 × 2 = **12** |

The hole *shape* encodes the rotational order of its axis: a pentagonal hole has 5-fold symmetry because rotating 72° around that axis maps the icosahedron to itself, a triangular hole has 3-fold because 120° works, and a rectangular hole has 2-fold because only 180° works.

Total: 62 holes — matching the relevant faces of the truncated icosidodecahedron that the connector ball is based on.

The following diagrams show each axis type on the icosahedron. The colored dots mark the geometric features (vertices, face centers, or edge midpoints), and the dashed lines show how opposite features pair up to form rotation axes:

![5-Fold Axes: Through Vertices](images/5fold-axes.svg)

![3-Fold Axes: Through Face Centers](images/3fold-axes.svg)

![2-Fold Axes: Through Edge Midpoints](images/2fold-axes.svg)

Here is a combined summary of how all 62 holes are derived:

![Combined Axes Summary](images/axes-summary.svg)

And a visual explanation of what "rotation order" means for each axis type:

![Rotation Orders](images/rotation-orders.svg)

### From Icosahedron to Connector Ball

The connector ball's geometry is derived from the **icosahedron** through a sequence of geometric operations. Understanding this requires knowing three intermediate shapes.

![From Icosahedron to Connector Ball — 4 Steps](images/icosahedron-to-ball.svg)

#### Step 1: The Icosahedron — Defining the Symmetry

**Icosahedron** — The fundamental shape that defines all the symmetry. It is a *Platonic solid* (all faces identical) with 20 equilateral triangular faces, 12 vertices, and 30 edges. Its rotation group has 60 elements. These three types of features (vertices, faces, edges) correspond to the three types of symmetry axes (5-fold, 3-fold, 2-fold).

![Feature Mapping: How icosahedron features become holes](images/feature-mapping.svg)

#### Step 2: Rectification — The Icosidodecahedron

**Rectification** cuts the icosahedron at its edge midpoints. Imagine slicing each vertex so that the cut passes through the midpoints of all 5 edges meeting at that vertex. Each slice reveals a **pentagon**. Meanwhile, the original 20 triangular faces shrink as their corners are trimmed, becoming smaller triangles.

The result is the **icosidodecahedron** — an *Archimedean solid* with 32 faces: 12 pentagons (one per original vertex) + 20 triangles (one per original face). It has 30 vertices (one at each original edge midpoint) and 60 edges. Every vertex sits at the junction of 2 pentagons and 2 triangles, alternating.

![The Icosidodecahedron](images/icosidodecahedron.svg)

The icosidodecahedron has the right *topology* — its 32 face centers + 30 vertices = 62 positions, one for each symmetry axis. But the 30 vertices are *points*, not flat surfaces. You can't punch a hole through a point. This is where the next step comes in.

#### Step 3: Expansion — The Rhombicosidodecahedron

**Expansion** (also called **cantellation**) pushes all faces of the icosidodecahedron radially outward, keeping each face the same size and orientation. As the pentagons and triangles separate, gaps open up where edges used to be. Each gap is filled with a new rectangular face.

The result is the **rhombicosidodecahedron** — an *Archimedean solid* with **62 faces**:

| Face type | Count | Origin | Symmetry |
|-----------|-------|--------|----------|
| **Pentagons** | 12 | Original icosidodecahedron pentagons, pushed apart | 5-fold |
| **Triangles** | 20 | Original icosidodecahedron triangles, pushed apart | 3-fold |
| **Squares** | 30 | New faces filling the gaps at former vertices | 2-fold |

It also has 60 vertices and 120 edges. At every vertex, the faces cycle: triangle, square, pentagon, square (vertex configuration 3.4.5.4).

Now every one of the 62 symmetry positions has its own **flat face** — a surface through which a hole can be punched.

![Rectangles at Edge Midpoints](images/rectangles-at-midpoints.svg)

#### Step 4: Sphericalize — The Connector Ball

The final step transforms the rhombicosidodecahedron into the physical connector ball:

1. **Project onto a sphere**: Inflate the polyhedron so it's roughly spherical, making it comfortable to hold and allowing struts to insert from any angle.
2. **Stretch squares to golden rectangles**: The 30 square faces become **golden rectangles** (aspect ratio phi:1). This is essential because the local symmetry at edge midpoints is only 2-fold, not 4-fold — a square would incorrectly imply 90° rotational symmetry (see [Why Rectangles?](#why-rectangles-the-shape-of-each-hole-explained) below).
3. **Cut holes through each face**: Each of the 62 faces becomes a hole shaped to match its symmetry: pentagon, triangle, or rectangle.

The result is the Zometool connector ball — 62 precisely positioned holes, each shaped to accept only struts with a matching cross-section.

![The Connector Ball — All 62 Holes](images/connector-ball-3d.svg)

#### The Complete Chain

| Step | Operation | Shape | Faces | Key Property |
|------|-----------|-------|-------|-------------|
| 1 | — | Icosahedron | 20 triangles | Defines the symmetry group |
| 2 | Rectification | Icosidodecahedron | 12 pentagons + 20 triangles | 62 positions (32 faces + 30 vertices) |
| 3 | Expansion | Rhombicosidodecahedron | 12 pentagons + 20 triangles + 30 squares | All 62 positions are flat faces |
| 4 | Sphericalize | Connector ball | 12 pent + 20 tri + 30 rect holes | Physical ball with golden-ratio rectangles |

#### Why Rectangles? The Shape of Each Hole Explained

The shape of each hole on the connector ball isn't arbitrary — it's dictated by the **local rotational symmetry** at that axis. The hole must be a shape that maps to itself under exactly the rotations that leave that axis fixed:

- **Pentagonal holes (5-fold axes):** At each icosahedron vertex, rotating 72° (= 360°/5) around the axis through that vertex maps the icosahedron to itself. A regular pentagon has exactly this 5-fold symmetry — rotate it 72° and it looks the same. So a pentagonal hole is the natural fit.

- **Triangular holes (3-fold axes):** At each icosahedron face center, rotating 120° (= 360°/3) is a symmetry. An equilateral triangle has exactly 3-fold symmetry, so a triangular hole encodes this.

- **Rectangular holes (2-fold axes):** At each icosahedron edge midpoint, the *only* non-trivial rotation that works is 180° (= 360°/2). Now consider the geometry at an edge midpoint: there are two natural directions — one **along the edge**, and one **perpendicular to the edge** (lying in the plane that bisects the two adjacent faces). These two directions are *not equivalent* to each other (the edge direction connects two vertices, while the perpendicular direction points between two face centers). A 180° rotation swaps the two ends of each direction but doesn't interchange the directions themselves. This is exactly the symmetry of a **rectangle**: it looks the same after a 180° rotation, but *not* after 90° (which would require the two directions to be equivalent, as in a square). The rectangle's long side aligns with one direction and its short side with the other, physically encoding the fact that the two local directions at an edge midpoint are geometrically distinct.

This is why the connector ball uses rectangles rather than squares — a square hole would imply 4-fold symmetry (90° rotation), which doesn't exist at an icosahedral edge midpoint.

![How Rectangular Holes Appear at Edge Midpoints](images/rectangle-at-edge.svg)

> **Try the interactive visualization**: Open [symmetry-visualization.html](symmetry-visualization.html) in a browser and click **"Show Ball"** to see the connector ball's hole markers overlaid on the icosahedron, with the icosidodecahedron wireframe visible underneath.

### Strut Types

Struts are color-coded by their geometric direction family:

| Color | Cross-section | Directions | Geometric Role |
|-------|--------------|------------|----------------|
| **Blue** | Rectangular | 15 axes (30 holes) | Parallel to icosahedron and dodecahedron edges |
| **Yellow** | Triangular | 10 axes (20 holes) | Connect icosahedron face centers |
| **Red** | Pentagonal | 6 axes (12 holes) | Connect dodecahedron face centers (5-fold axes) |

Each color comes in multiple lengths. The ratio between successive sizes is always the **golden ratio** (phi ~ 1.618).

### Beyond Blue, Yellow, Red: vZome's Extra Strut Colors

Physical Zometool is limited to 3 direction families because the connector ball only has 3 hole shapes. But the golden field Q(phi) contains infinitely many other **geometrically distinct directions** — vectors pointing at entirely different angles through 3D space, not just different lengths of the existing 3. vZome, being virtual, can use any of them.

Each extra color represents a different **orbit** — a family of directions related by the 60 icosahedral rotations.

#### Why Every Orbit Closes: The Orbit-Stabilizer Theorem

A natural question: if you pick a "random" direction like green and apply all 60 rotations, do you get a finite or infinite set of directions? The answer is **always finite**, for two independent reasons:

**Reason 1 — The group is finite.** The icosahedral rotation group has exactly 60 elements. Applying all 60 to any direction produces *at most* 60 distinct directions. The exact count is determined by the **orbit-stabilizer theorem**: if *k* of the 60 rotations map a direction back to itself (the *stabilizer*), then the orbit has exactly 60/*k* distinct directions. The orbit size is always a divisor of 60.

| Direction type | Stabilizer (rotations that preserve it) | *k* | Orbit = 60/*k* |
|---------------|----------------------------------------|-----|---------------|
| 5-fold axis (red) | {id, 72°, 144°, 216°, 288°} | 5 | **12** |
| 3-fold axis (yellow) | {id, 120°, 240°} | 3 | **20** |
| 2-fold axis (blue) | {id, 180°} | 2 | **30** |
| Generic direction (green, etc.) | {id} only | 1 | **60** |

The standard blue/yellow/red orbits have fewer than 60 axes because they align with symmetry axes, so multiple rotations map each axis to itself. The extra orbits don't align with any symmetry axis, so only the identity preserves them — giving the full 60.

**Reason 2 — The algebraic field is closed.** Every rotation matrix in the icosahedral group has entries in Q(phi), and every prototype vector has coordinates in Q(phi). Since Q(phi) is closed under addition and multiplication, every rotated vector also lands in Q(phi). This means green struts, orange struts, and all other colors produce **exact algebraic coordinates** — no rounding, no drift. Intersections, midpoints, and symmetry operations on structures built with *any* strut color remain perfectly exact.

This is fundamentally different from a generic rotation by an irrational angle, which *would* generate infinitely many distinct directions. The icosahedral group's finiteness guarantees that every orbit closes.

#### Directions Close, but Positions Don't

An important subtlety: orbital closure is about **directions**, not **positions**. If you keep placing blue struts end-to-end in the same direction (zero rotation), you reach points at distances 1, 2, 3, ... along that line — infinitely many positions. The set of *directions* is finite (30 for blue), but the set of *reachable points* along any direction is infinite.

It gets richer: since strut lengths come in powers of phi (short = phi^0, medium = phi^1, long = phi^2, ...), the reachable distances along a single axis include all values of the form `a + b*phi` where a, b are non-negative integers. By subtracting (building in the opposite direction), you can reach any `a + b*phi` with integer a, b. This set **Z[phi] = {a + b*phi : a, b in Z}** is infinite and, remarkably, **dense** in the real number line — you can get arbitrarily close to any distance, though any finite construction uses finitely many points.

The full set of all points reachable from the origin by any sequence of Zometool struts is a module over Z[phi] in 3D, known as the **Z-lattice**. It is:

| Property | Value |
|----------|-------|
| **Infinite?** | Yes — unbounded in every direction |
| **Dense?** | Yes — points get arbitrarily close together |
| **Periodic?** | No — it has no translational symmetry (unlike a crystal lattice) |
| **Exact?** | Yes — every point has coordinates in Q(phi), zero error |
| **Any finite construction** | Uses finitely many points from this infinite set |

This is precisely the mathematical structure underlying **icosahedral quasicrystals** — the aperiodic materials discovered by Dan Shechtman (Nobel Prize 2011). The Z-lattice is infinite and aperiodic, yet has perfect icosahedral symmetry and long-range order. See [Connections to Quasicrystals](#9-connections-to-quasicrystals) for more.

#### Closed Paths and Exact Closure

Although positions extend to infinity, you can always build **closed paths** (loops) that return exactly to the origin. A path closes when the sum of all strut vectors equals zero. For example, an icosahedron built from 30 blue struts is a closed structure — the 30 offset vectors sum to exactly (0, 0, 0) in Q(phi).

A natural computational question: **given N struts of various colors and lengths, what is the longest closed path you can form using a subset of them?** This is the *Maximum Zero-Sum Subset* problem — find the largest subset of N vectors in Q(phi)^3 whose sum is zero.

This problem is **NP-hard**. To see why, note that each strut vector has coordinates in Q(phi), meaning each coordinate is `a + b*phi` with integer a, b. For the path to close, both the rational parts and the phi-parts must independently sum to zero in all 3 dimensions — giving 6 integer equations:

```
Sum of a_x = 0,  Sum of b_x = 0    (x-coordinates)
Sum of a_y = 0,  Sum of b_y = 0    (y-coordinates)
Sum of a_z = 0,  Sum of b_z = 0    (z-coordinates)
```

This is a 6-dimensional subset sum problem. Even the 1-dimensional case (standard subset sum) is NP-complete, so the Zometool version is at least as hard.

| Aspect | Details |
|--------|---------|
| **Problem** | Find the largest subset of N strut vectors that sums to zero |
| **Complexity** | NP-hard (reduces to multi-dimensional subset sum) |
| **Best exact algorithm** | O(2^(N/2)) via meet-in-the-middle |
| **Exactness guarantee** | Yes — Q(phi) arithmetic means a path either closes *exactly* or doesn't close at all. No "almost closed" ambiguity. |
| **Zometool structure helps?** | The finite number of directions (at most 60 per orbit) constrains the problem, but choosing which directions and lengths to include remains combinatorial. |

Note the silver lining of exact arithmetic: unlike floating-point geometry where you'd need an epsilon tolerance to decide if a path "almost" closes, in Q(phi) the answer is always exact — the vector sum is either precisely zero or precisely nonzero. The *decision* is trivial once you've chosen the subset; it's *finding* the optimal subset that's hard.

| Color | Prototype Direction (phi notation) | Axes | Notes |
|-------|-----------------------------------|------|-------|
| **Blue** | (1, 1+phi, -1+phi) | 30 | Standard: 2-fold axis, rectangular holes |
| **Yellow** | (1+phi, phi, -1) | 20 | Standard: 3-fold axis, triangular holes |
| **Red** | (phi, 1+phi, phi) | 12 | Standard: 5-fold axis, pentagonal holes |
| **Green** | (1+phi, 1+phi, phi) | 60 | Related to tetrahedral subgroups inscribed in icosahedron |
| **Orange** | (1+phi, phi, phi) | 60 | Distinct intermediate direction |
| **Purple** | (1+phi, 1+phi, phi) / phi | 60 | Same direction family as green, rescaled |
| **Black** | (phi, 1+phi, 1-phi) | 60 | Near the red axis but distinct |
| **Lavender** | (2-phi, phi, 2-phi) | 60 | Higher-order phi combination |
| **Olive** | (phi, phi, 2-phi) | 60 | Similar to lavender, different angle |
| **Maroon** | (-1+phi, 3-phi, 1-phi) | 60 | Complex phi expression |
| **Rose** | (2-phi, -1+2phi, phi) | 60 | Asymmetric coordinates |
| **Navy** | (-1+2phi, 1+phi, phi) / phi | 60 | Rescaled direction |
| **Turquoise** | (2, 2-phi, -3+2phi) | 60 | Integer first coordinate |
| **Coral** | (-3+3phi, phi, 1+phi) | 60 | Higher-order Fibonacci coefficients |
| **Sulfur** | (-3+3phi, 2-phi, phi) | 60 | Similar to coral |

**Why these specific directions?** Every prototype vector has components in Q(phi) — the golden field. This means every coordinate is of the form `a + b*phi` with integer a, b. Under any of the 60 icosahedral rotations, such a vector maps to another vector in Q(phi), keeping everything exact. The extra orbits are chosen because they arise naturally in geometric constructions (intersections, midpoints, cross products, etc.) within vZome models.

**The orbit triangle**: All orbits can be visualized as points on a *fundamental domain triangle* on the unit sphere, with blue, yellow, and red at the three vertices. The extra orbits project to unique points inside this triangle, each representing a geometrically distinct direction. This triangle is used in vZome's UI for selecting strut directions.

### What vZome Adds

vZome extends physical Zometool into a virtual environment:

| Feature | Physical Zometool | vZome |
|---------|-------------------|-------|
| Strut colors | Blue, yellow, red | 15+ colors including green, orange, purple, and more |
| Lengths | 2-3 standard sizes | Arbitrary powers of phi |
| Symmetry | Manual construction | One-click symmetry operations |
| 4D geometry | Not possible | Full 4D polytope construction with 3D projection |
| Algebraic fields | Golden ratio only | 11+ fields (sqrt(2), sqrt(3), heptagonal, etc.) |
| Precision | Physical tolerances | Exact algebraic arithmetic, zero error |
| Export | Physical object | STL, glTF, POV-Ray, PDF, SVG, VRML, and more |

---

## 2. The Golden Ratio: Why Zometool Works

The golden ratio phi = (1 + sqrt(5)) / 2 ~ 1.618... is not an arbitrary choice. It is **intrinsic** to icosahedral symmetry:

### Where Phi Appears

![The Golden Ratio](images/golden-ratio.svg)

- **Regular pentagon**: The diagonal-to-side ratio is exactly phi.
- **Icosahedron vertices**: Three mutually perpendicular golden rectangles (aspect ratio phi:1) define all 12 vertices.
- **Dodecahedron vertices**: Expressible using coordinates involving phi.
- **Zometool strut lengths**: Each successive size is phi times the previous.

### Why It Closes

The deep mathematical reason Zometool works is that the **golden field Q(phi)** is algebraically closed under all operations needed by icosahedral symmetry:

1. The 60 rotations of the icosahedral group can be represented as 3x3 matrices with entries in Q(phi).
2. Any point with coordinates in Q(phi) maps to another point in Q(phi) under these rotations.
3. Midpoints, intersections, and other constructions all stay within Q(phi).

This means starting from a single ball at the origin, every valid construction produces coordinates that are exact elements of the golden field — no rounding, no drift, no accumulated error.

### Fibonacci Connection

Powers of phi produce Fibonacci numbers as coefficients:

```
phi^0 = 1 + 0*phi       (F(1), F(0))
phi^1 = 0 + 1*phi       (F(2), F(1))
phi^2 = 1 + 1*phi       (F(3), F(2))   [since phi^2 = phi + 1]
phi^3 = 1 + 2*phi       (F(4), F(3))
phi^4 = 3 + 2*phi       (F(5), F(4))
phi^5 = 5 + 3*phi       (F(6), F(5))
...
phi^n = F(n) + F(n+1)*phi
```

This is not a coincidence — the Fibonacci recurrence `F(n+2) = F(n+1) + F(n)` is a direct consequence of `phi^2 = phi + 1`.

![Powers of Phi and Fibonacci Numbers](images/fibonacci-powers.svg)

---

## 3. Exact Arithmetic: Algebraic Number Fields

The mathematical heart of vZome is its exact arithmetic system. Every coordinate is a linear combination of algebraic basis values with rational coefficients — **never floating-point**.

![Algebraic Number Representation](images/algebraic-numbers.svg)

### The Layered Architecture

```
BigRational          Arbitrary-precision fractions (always reduced)
    |
AlgebraicNumber      Coefficient tuples: [c0, c1, ..., c_{n-1}]
    |                Evaluated as: c0*1 + c1*beta1 + c2*beta2 + ...
AlgebraicField       Defines the basis elements and multiplication rules
    |
AlgebraicVector      Multi-dimensional vectors of AlgebraicNumbers
    |
AlgebraicMatrix      Transformation matrices
```

### How Numbers Are Represented

An `AlgebraicNumber` in a field of order N is stored as N rational coefficients:

```
Number = [c0, c1, c2, ..., c_{N-1}]
Value  = c0 * beta0 + c1 * beta1 + ... + c_{N-1} * beta_{N-1}
```

where `beta0 = 1` and `beta1, beta2, ...` are the field's irrational basis elements.

### Example: Pentagon Field (Order 2)

The golden field represents every number as `a + b*phi`:

```
1       = [1, 0]
phi     = [0, 1]
2 + 3*phi = [2, 3]
1/phi   = [-1, 1]     (since phi^2 = phi + 1, so 1/phi = phi - 1)
```

**Multiplication rule** (derived from phi^2 = phi + 1):

```
(a + b*phi) * (c + d*phi)
= ac + (ad + bc)*phi + bd*phi^2
= ac + (ad + bc)*phi + bd*(phi + 1)    [substitute phi^2 = phi + 1]
= (ac + bd) + (ad + bc + bd)*phi
```

So in tuple form: `[a,b] * [c,d] = [ac + bd, ad + bc + bd]`

### Available Fields

| Field | Order | Basis | Irrational(s) | Primary Use |
|-------|-------|-------|---------------|-------------|
| **PentagonField** ("golden") | 2 | {1, phi} | phi = (1+sqrt(5))/2 | Icosahedral/Zometool geometry |
| **RootTwoField** | 2 | {1, sqrt(2)} | sqrt(2) | Octahedral symmetry |
| **RootThreeField** | 2 | {1, sqrt(3)} | sqrt(3) | Tetrahedral/hexagonal |
| **HeptagonField** | 3 | {1, rho, sigma} | rho ~ 1.802, sigma ~ 2.247 | 7-fold symmetry |
| **SnubDodecField** | 6 | {1, phi, xi, phi*xi, xi^2, phi*xi^2} | phi, xi ~ 1.716 | Snub dodecahedron |
| **PolygonField(N)** | varies | parameterized | N-gon roots | Arbitrary N-fold symmetry |
| **SqrtField(N)** | 2 | {1, sqrt(N)} | sqrt(N) | General sqrt fields |

### How Reciprocals Work

Division in algebraic fields uses an elegant linear-algebra approach:

1. Build a matrix where row 0 is the number to invert.
2. Additional rows are the number scaled by each basis element.
3. Apply Gauss-Jordan elimination to reduce to identity.
4. The first row of the result gives the reciprocal's coefficients.

This works for **any** algebraic field, automatically computing exact reciprocals without numerical approximation.

### Why This Matters

Consider building an icosahedron and computing where two edges intersect. With floating-point, every operation introduces tiny errors. After hundreds of operations, points that should be identical differ by accumulated rounding. With algebraic arithmetic, every intermediate result is **exact** — two points are either identical or they aren't. There is no tolerance, no epsilon, no "close enough."

---

## 4. Symmetry Systems

### Core Concepts

vZome's symmetry system is built on three key abstractions:

**Axis (Zone)**: An infinite family of parallel lines in space. Despite the name, an Axis represents not a single line but a *direction* — all struts pointing the same way belong to the same zone.

**Direction (Orbit)**: The complete family of all axes related by symmetry. For example, the "blue" direction in icosahedral symmetry contains 30 axes (15 pairs of opposite directions), all related by the 60 rotations of the icosahedron.

**Permutation**: A group element (symmetry operation) represented as an index-mapping array. Composing permutations corresponds to composing rotations.

### How Symmetry Groups Are Built

The system constructs complete symmetry groups from generators using **group closure**:

1. Start with identity plus 2-3 generator rotations.
2. Compose all known elements pairwise.
3. Add any new elements found.
4. Repeat until no new elements appear.
5. Result: the complete group with proper closure.

For icosahedral symmetry, 3 generators produce all 60 rotations.

### The Four Main Systems

#### Icosahedral Symmetry (Order 60)

The primary symmetry for Zometool, representing the rotation group of the icosahedron/dodecahedron.

- **60 orientations** (rotations only, no reflections)
- **3 generators**: 2-fold (blue), 3-fold (yellow), 5-fold (red) rotations
- **Algebraic field**: Golden (PentagonField)
- **Standard orbits**: blue (30 axes), yellow (20 axes), red (12 axes), green, orange, purple, and 10+ more

The 60 orientations map directly to connector positions on a Zometool ball. Each orbit defines multiple scale variants (shorter, short, medium, long) using powers of phi.

**Five tetrahedral subgroups** of order 12 each are embedded within, reflecting the fact that five tetrahedra can be inscribed in a dodecahedron.

#### Octahedral Symmetry (Order 24)

The rotation group of the cube/octahedron.

- **24 orientations**
- **3 generators**: 4-fold (blue), 3-fold (yellow), 2-fold (green) rotations
- **Algebraic field**: RootTwoField
- **Standard orbits**: blue, green, yellow

#### Dodecagonal Symmetry (Order 12)

12-fold rotational symmetry around a single axis.

- **12 orientations**
- **1 generator**: 30-degree rotation around Z axis
- **Simple structure**: planar symmetry

#### Antiprism Symmetry (Order 2N, parameterized)

Generalized symmetry for arbitrary N-fold axes, used for heptagonal, pentagonal, and other polygon fields.

- **Order = 2N**
- **2 generators**: N-fold rotation around Z, 2-fold rotation around X
- **Special feature**: principal reflection for odd polygons
- **Shear transform**: adjusts 3D embedding for odd-gon geometries

### Orbit Triangle Visualization

Each symmetry system defines a **fundamental domain triangle** on the unit sphere. The three vertices correspond to the special orbits (blue, red, yellow). All other orbits project to unique points within this triangle, providing a natural UI for orbit selection.

### Scale Variants

Each orbit (direction) supports multiple strut lengths, computed as powers of the field's characteristic irrational:

```
shorter = base * phi^{-1}
short   = base * phi^0 = base
medium  = base * phi^1
long    = base * phi^2
```

In the golden field, this means each successive length is phi ~ 1.618 times the previous, matching physical Zometool strut ratios.

---

## 5. Geometric Construction

### The Construction Hierarchy

All geometric elements derive from an abstract `Construction` class:

```
Construction (abstract)
  |
  +-- Point
  |     +-- FreePoint              (arbitrary position)
  |     +-- SegmentEndPoint        (endpoint of a segment)
  |     +-- TransformedPoint       (result of a transformation)
  |     +-- LineLineIntersectionPoint
  |     +-- LinePlaneIntersectionPoint
  |     +-- SegmentMidpoint
  |     +-- CentroidPoint          (center of mass)
  |     +-- PointRotated4D         (4D rotation)
  |
  +-- Segment
  |     +-- SegmentJoiningPoints   (connects two points)
  |     +-- AnchoredSegment        (from anchor + axis + length)
  |     +-- TransformedSegment
  |     +-- SegmentCrossProduct
  |     +-- SegmentRotated4D
  |
  +-- Polygon
  |     +-- PolygonFromVertices
  |     +-- TransformedPolygon
  |     +-- PolygonRotated4D
  |
  +-- Transformation
        +-- Translation
        +-- PointReflection        (inversion through a center)
        +-- LineReflection
        +-- PlaneReflection
        +-- Scaling
        +-- SymmetryTransformation
        +-- MatrixTransformation
```

Every construction stores its state as **algebraic vectors/matrices** — never floating-point.

### Segments: Anchor + Offset

Segments are stored as a start point and an offset vector (not two endpoints). This is more efficient and mirrors how Zometool struts work: you place a strut at a connector ball in a specific direction and length.

```
AnchoredSegment:
  anchor = Point (the ball where the strut starts)
  axis   = symmetry Axis (direction)
  length = AlgebraicNumber (how long)
  offset = axis.normal() * length   (computed vector)
  end    = anchor + offset          (the other endpoint)
```

### Transformations

All transformations are affine: `v' = M * (v - center) + center`

| Transformation | Parameters | Formula |
|---------------|------------|---------|
| **Translation** | displacement vector d | `p' = p + d` |
| **Point Reflection** | center point c | `p' = 2c - p` |
| **Line Reflection** | line with normal n | `p' = p - 2((p.n)/(n.n)) * n` |
| **Plane Reflection** | plane with normal n, base b | `p' = p - 2(((p-b).n)/(n.n)) * n` |
| **Scaling** | center c, scale factor s | `p' = c + s * (p - c)` |
| **Symmetry** | rotation matrix M, center c | `p' = M * (p - c) + c` |

### The Edit System

User operations are represented as **undoable edits** that modify the model:

**Key Edit Operations:**

- **StrutCreation**: Build a strut from an anchor point along a symmetry axis at a given length.
- **JoinPoints**: Connect selected points with segments (modes: closed loop, chain, all-to-last, all-possible).
- **Polygon**: Create a face from selected points.
- **TransformSelection**: Apply any transformation to all selected elements.
- **ConvexHull**: Compute 2D or 3D convex hull of selected points.
- **CrossProduct**: Create segment from cross product of two vectors.
- **Centroid**: Create a point at the center of mass.
- **LineLineIntersection**: Find where two lines meet in 3D.
- **LinePlaneIntersection**: Find where a line pierces a plane.

### Manifestations

The bridge between mathematical constructions and visual rendering:

| Manifestation | Construction | Visual |
|--------------|-------------|--------|
| **Connector** (ball) | Point | Rendered sphere at position |
| **Strut** | Segment | Rendered cylinder with color from orbit |
| **Panel** | Polygon | Rendered face with transparency |

### Building a Model: Step by Step

![Construction Workflow](images/construction-steps.svg)

1. **Create origin point**: `FreePoint(0, 0, 0)` in the chosen algebraic field.
2. **Build first strut**: `AnchoredSegment(origin, blueAxis[0], medium)` — creates a blue strut from the origin.
3. **Select the endpoint**: The strut's far end becomes a new connector ball.
4. **Apply symmetry**: "Icosahedral symmetry around origin" creates 59 copies of the strut, one for each rotation in the group.
5. **Connect endpoints**: `JoinPoints` to create edges between nearby balls.
6. **Create faces**: `Polygon` from coplanar connected points.
7. **Every step is recorded** in the edit history for undo/redo and file saving.

---

## 6. The Zomic Scripting Language

Zomic is a procedural scripting language for building vZome models programmatically. It operates on a **turtle-graphics** metaphor in 3D space.

### Virtual Machine State

The Zomic VM maintains four state variables:

| State | Description |
|-------|-------------|
| **Location** | Current position (AlgebraicVector) |
| **Orientation** | Current facing direction (rotation state) |
| **Scale** | Current step size |
| **Build mode** | Whether to create geometry or just move |

### Core Commands

```
move <direction> <length>    Move and optionally build a strut
rotate <axis> <steps>        Rotate the turtle's orientation
reflect <axis>               Mirror the turtle state
scale <factor>               Change the step size

repeat <count> { ... }       Loop a block of commands
symmetry { ... }             Apply all symmetry operations to a block
save { ... }                 Save state, execute block, restore state
build { ... }                Enable/disable geometry creation
```

### Example: Building a Spiral

```zomic
// Build a logarithmic spiral of blue struts
build {
  repeat 20 {
    move blue 0    // step in blue direction, length 0 (short)
    rotate yellow 1  // rotate 120 degrees around yellow axis
    scale phi        // scale up by golden ratio
  }
}
```

### Compilation Pipeline

```
Zomic source text
    |  (ANTLR4 lexer + parser)
    v
Abstract Syntax Tree
    |  (ZomicASTCompiler)
    v
Program statements (Build, Move, Rotate, Repeat, Symmetry, ...)
    |  (Interpreter)
    v
vZome edit operations (StrutCreation, etc.)
```

---

## 7. 4D Polytopes and Projections

One of vZome's most powerful features is constructing and visualizing 4-dimensional polytopes.

### 4D Polytope Families

vZome supports polytopes from several 4D Coxeter groups:

| Group | Polytope Family | Notable Members |
|-------|----------------|-----------------|
| **H4** | 120-cell family | 120-cell (hecatonicosachoron), 600-cell |
| **F4** | 24-cell family | 24-cell (icositetrachoron) |
| **B4** | Hyperoctahedral | 8-cell (tesseract), 16-cell |
| **A4** | Simplex family | 5-cell (pentachoron) |

### The 120-Cell

The 120-cell is the 4D analog of the dodecahedron:
- 120 dodecahedral cells
- 720 pentagonal faces
- 1200 edges
- 600 vertices
- Symmetry group H4 has order 14,400

It can be constructed using **quaternion arithmetic** in the golden field, making it a natural fit for vZome's exact algebraic framework.

### Wythoff Construction

The `WythoffConstruction` class generates uniform polytopes from Coxeter group data:

1. Define the Coxeter group (simple roots and Cartan matrix).
2. Choose weights (which mirrors to be "active").
3. Generate the vertex orbit under the group action.
4. Connect vertices that are related by single reflections.
5. Result: a complete uniform polytope with vertices, edges, and faces.

### Projection to 3D

4D polytopes are projected to 3D for visualization using:

- **Perspective projection**: Closer 4D "layers" appear larger, giving depth cues.
- **Orthographic projection**: Parallel projection, preserving some symmetry.
- **Quaternionic projection**: Uses quaternion multiplication for specific viewpoints.

Classes like `ProjectionTool` and `PerspectiveProjectionTool` handle these transformations. The 4D coordinates use `AlgebraicVector` with 4 components, and `PointRotated4D`, `SegmentRotated4D`, `PolygonRotated4D` handle 4D rotations before projection.

---

## 8. File Formats

### .vZome Format (XML)

The native vZome format stores the **complete edit history** as XML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<vzome:vZome xmlns:vzome="http://xml.vzome.com/vZome/4.0.0/"
             field="golden" version="5.0">

  <EditHistory editNumber="42" lastStickyEdit="10">
    <StrutCreation anchor="0 0 0 0 0 0" dir="blue" index="7" len="1 2"/>
    <SelectManifestation point="0 0 2 3 -1 -2"/>
    <IcosahedralSymmetry/>
    <BeginBlock/>
      <JoinPoints closedLoop="true"/>
      <Polygon/>
    </EndBlock/>
  </EditHistory>

  <SymmetrySystem name="icosahedral" renderingStyle="solid connectors">
    <Direction name="blue" color="0,118,149">
      <LengthModel divisor="1" ones="1" scale="3" taus="0"/>
    </Direction>
  </SymmetrySystem>

  <Viewing>
    <ViewModel distance="50.0">
      <LookAtPoint x="0.0" y="0.0" z="0.0"/>
    </ViewModel>
  </Viewing>
</vzome:vZome>
```

**Coordinate encoding** (golden field): 6 integers representing 3 algebraic numbers:

```
"a0 a1 b0 b1 c0 c1" = ((a0 + a1*phi), (b0 + b1*phi), (c0 + c1*phi))
```

Opening a .vZome file **replays every edit** from the beginning, reconstructing the complete model.

### VEF Format (Vertex-Edge-Face)

A simpler text format for importing polyhedra:

```
vZome VEF 4
field golden

8               # number of vertices
(0,1) (0,1) (0,1) (0,0)    # vertex coordinates in field format
(0,1) (0,1) (0,-1) (0,0)
...

12              # number of edges
0 1             # edge connecting vertex 0 to vertex 1
0 2
...

6               # number of faces
4 0 1 3 2       # face with 4 vertices
...
```

VEF supports multiple versions with features like explicit dimensions (for 4D), per-coordinate scaling, and explicit ball rendering.

### .shapes.json Format

A pre-computed JSON format for fast web preview, containing the final geometry without edit history. Used by the `<vzome-viewer>` web component for quick loading.

---

## 9. Connections to Quasicrystals

### The Forbidden Symmetry

Classical crystallography proves that periodic crystals cannot have 5-fold symmetry. Yet in 1984, Dan Shechtman discovered **quasicrystals** — materials with sharp diffraction patterns exhibiting icosahedral symmetry (Nobel Prize, 2011).

### The Mathematical Bridge

The connection between Zometool/vZome and quasicrystals is direct:

- **Penrose tilings** (2D quasicrystalline tilings) are governed by the golden ratio — the same phi underlying all Zometool.
- **3D quasicrystals** with icosahedral symmetry have atomic positions in Q(phi), the same number field vZome uses.
- **Cut-and-project method**: Quasicrystal structures are generated by projecting higher-dimensional periodic lattices into 3D. vZome's 4D projection tools are directly related.

### The Z-Lattice

Every point in a Zometool model lies on the **Z-lattice** — a module over Z[phi] in 3D. Unlike a crystal lattice (discrete and periodic), this module is **dense** in R^3 but any finite construction uses finitely many points. This is precisely the mathematical structure underlying icosahedral quasicrystals.

### Beyond the Golden Ratio

vZome's support for multiple algebraic fields connects to broader aperiodic and crystallographic structures:
- **RootTwoField** (sqrt(2)): Octahedral symmetry, relevant to traditional cubic crystals
- **RootThreeField** (sqrt(3)): Hexagonal/trigonal crystal systems
- **PolygonField(N)**: Arbitrary N-fold symmetries, encompassing both crystallographic (N = 2, 3, 4, 6) and non-crystallographic (N = 5, 7, 8, ...) cases

---

## 10. Physics in Zome Geometry

Zome geometry is not just a mathematical curiosity — icosahedral symmetry over Q(φ) appears throughout physics, from atomic-scale crystals to string theory. The unifying principle: **whenever nature uses icosahedral symmetry, the mathematical description lives in the same Q(φ)³ vector space as Zometool.**

![Physics Problems Connected to Zome Geometry](images/physics-overview.svg)

### 10.1 Quasicrystals — The Strongest Connection

In 1984, Dan Shechtman discovered materials with sharp X-ray diffraction patterns exhibiting **icosahedral symmetry** — something classical crystallography said was impossible (Nobel Prize 2011). These **quasicrystals** are aperiodic structures with long-range order governed by the golden ratio.

The connection to Zometool is direct and deep:

| Quasicrystal concept | Zometool equivalent |
|---------------------|---------------------|
| Atomic positions | Connector ball positions |
| Icosahedral point group | Same 60-rotation group |
| Coordinates in Q(φ) | Same algebraic field |
| Z[φ] lattice in 3D | Exact same module |
| Aperiodic, non-repeating | Same — no translational symmetry |
| Non-periodic but ordered | Same — long-range orientational order without translational periodicity |

#### The Cut-and-Project Method

The standard technique for generating quasicrystal structures is the **cut-and-project method** (also called the "strip projection method"). The idea:

1. Start with a periodic lattice in a **higher-dimensional space** (e.g., 6D for icosahedral quasicrystals, 2D in the simplified diagram below).
2. Define a "physical space" subspace at an **irrational angle** relative to the lattice (the angle involves φ for icosahedral symmetry).
3. Select lattice points that fall within a narrow **acceptance strip** around physical space.
4. **Project** those points onto physical space.

The result is an aperiodic sequence of points with two spacings — Long (L) and Short (S) — whose ratio is φ. The sequence of L's and S's is the **Fibonacci word**, and the ratio of their counts approaches φ as the strip extends.

![Cut-and-Project Method](images/cut-and-project.svg)

In the icosahedral case, this generalizes from 2D→1D to **6D→3D**: a 6-dimensional hypercubic lattice is sliced and projected along icosahedral directions to produce the 3D atomic positions of a quasicrystal. This is mathematically identical to what vZome does — the 6 integer coordinates per 3D point (two integers per Q(φ) coordinate) are exactly the 6D lattice coordinates before projection.

#### Why It Matters for Zometool

Many Zometool models can be interpreted as **finite patches sampled from quasicrystal-compatible point sets**. The connector ball positions are points in the Z[φ] module used in icosahedral quasicrystal models, but physical stability still depends on chemistry, occupancy, and energetics.

### 10.2 Viral Capsids — Biology's Icosahedra

Many viruses package their genetic material inside **icosahedral protein shells** called capsids. Nature uses icosahedral symmetry because it is the most efficient way to enclose a volume with identical protein subunits — the same 60-fold symmetry that drives Zometool.

![Icosahedral Viral Capsid](images/viral-capsid.svg)

#### The Caspar-Klug Classification

Caspar and Klug (1962, Nobel Prize 1982) showed that icosahedral capsids are classified by a **triangulation number** T = h² + hk + k², where h and k are non-negative integers. This T-number determines how the icosahedral faces are subdivided:

| T-number | Subunits | Virus examples |
|----------|----------|----------------|
| T = 1 | 60 | Satellite tobacco necrosis virus |
| T = 3 | 180 | Poliovirus, rhinovirus (common cold) |
| T = 4 | 240 | Hepatitis B, Sindbis virus |
| T = 7 | 420 | Rotavirus, papillomavirus (HPV) |
| T = 13 | 780 | Herpes simplex virus |
| T = 25 | 1500 | Adenovirus |

Every T-number capsid has exactly **12 pentamers** (protein clusters of 5 at the icosahedron vertices) plus 10(T−1) **hexamers** (clusters of 6). The pentamers sit at the 5-fold symmetry axes — the exact same 12 positions as the red (pentagonal) holes on a Zometool connector ball.

#### Connection to Zome Geometry

The vertex positions of a geodesic subdivided icosahedron (which models the capsid) are constructible in Zometool's algebraic framework. The 60-element rotation group that relates protein subunits is the same icosahedral group. The protein-protein contact angles and distances can all be expressed in Q(φ), making vZome a natural tool for modeling capsid geometry.

### 10.3 Fullerenes — Carbon's Icosahedral Molecules

In 1985, Kroto, Smalley, and Curl discovered **C₆₀** — a molecule of 60 carbon atoms arranged as a **truncated icosahedron** (Nobel Prize 1996). Named "buckminsterfullerene" after Buckminster Fuller's geodesic domes, it is a perfect example of icosahedral symmetry in chemistry.

![C₆₀ Buckminsterfullerene](images/c60-fullerene.svg)

#### Structure

C₆₀ has the geometry of a soccer ball:
- **60 vertices** (one carbon atom each)
- **90 edges** (carbon-carbon bonds)
- **12 pentagonal faces** + **20 hexagonal faces** = 32 faces
- Full icosahedral symmetry group (I_h, order 120 including reflections)

This is the **truncated icosahedron** — obtained by cutting each of the 12 vertices of an icosahedron to reveal a pentagon, leaving the 20 original triangular faces as hexagons. It is directly constructible in Zometool (all vertex coordinates lie in Q(φ)³).

#### The Fullerene Family

Beyond C₆₀, the fullerene family includes:
- **C₇₀** (rugby-ball shape, D₅h symmetry — an icosahedral subgroup)
- **C₈₀**, C₂₄₀, and larger icosahedral fullerenes
- **Carbon nanotubes** (cylinders with icosahedral caps)
- **Endohedral fullerenes** (atoms trapped inside the cage)

All icosahedral fullerenes obey Euler's formula with exactly 12 pentagons (the rest being hexagons), mirroring the 12 pentagonal holes on the connector ball. The electronic structure calculations for these molecules exploit the icosahedral symmetry to block-diagonalize the Hamiltonian, reducing a 60-dimensional eigenvalue problem to much smaller irreducible blocks.

### 10.4 Penrose Tilings — Aperiodic Order in 2D

Penrose tilings are the 2D counterpart of 3D icosahedral quasicrystals. Discovered by Roger Penrose in 1974, they tile the plane with two shapes governed by the golden ratio — never repeating, yet maintaining long-range 5-fold orientational order.

![Penrose Tiling](images/penrose-tiling.svg)

#### The Two Rhombi

The Penrose P3 tiling uses two rhombus shapes:
- **Fat rhombus**: angles 72° and 108° (related to the regular pentagon)
- **Thin rhombus**: angles 36° and 144°

Both have edge length 1, but the fat rhombus has diagonals in ratio φ:1, and the thin rhombus has diagonals in ratio 1:φ. The ratio of the number of fat to thin rhombi approaches φ as the tiling grows — a Fibonacci proportion.

#### Self-Similarity

Penrose tilings are **self-similar**: you can group tiles into larger tiles of the same two types (a process called "deflation" or "composition"), and the larger tiles form another Penrose tiling at a larger scale. This self-similarity at every scale is a hallmark of quasicrystalline order — the same φ-based scaling that makes Zometool strut lengths come in powers of φ.

#### From 2D to 3D

The 3D generalization of Penrose tilings uses two **rhombohedra** (3D rhombi) — a prolate (fat) and oblate (thin) one — to fill 3D space aperiodically with icosahedral symmetry. This is the **Ammann-Kramer-Neri tiling**, and its vertex positions form exactly the Z[φ] lattice that Zometool inhabits. Building 3D Penrose-tiled structures is one of the natural applications of Zometool.

### 10.5 E₈, Lie Algebras, and String Theory

The **E₈** lattice — the densest lattice packing in 8 dimensions — has a remarkable connection to icosahedral symmetry. When the 240 root vectors of E₈ are projected from 8D to 3D along icosahedral directions, they land on **concentric shells with exact icosahedral symmetry**, all with coordinates in Q(φ).

![E₈ Root System Projected to 3D](images/e8-projection.svg)

#### The H₃ Connection

The icosahedral symmetry group H₃ (the 3D Coxeter group of the icosahedron) embeds naturally into E₈'s Weyl group. This means there is a canonical projection from E₈ to 3D that preserves icosahedral symmetry. The 240 E₈ roots project onto several concentric icosahedral shells:

| Shell | Polyhedron | Vertices | Radius |
|-------|-----------|----------|--------|
| 1 | Icosahedron | 12 | 1 |
| 2 | Dodecahedron | 20 | φ |
| 3 | Icosidodecahedron | 30 | φ² |
| 4+ | Larger icosahedral shells | ... | φ³, 2φ, ... |

Every projected vertex has coordinates in Q(φ)³, making them exactly representable in Zometool/vZome.

#### String Theory and Exceptional Geometry

In theoretical physics, E₈ appears in:
- **Heterotic string theory**: The E₈×E₈ gauge group is one of the two consistent 10D heterotic string theories.
- **Garrett Lisi's "An Exceptionally Simple Theory of Everything"** (2007, controversial): attempts to embed all particles and forces in E₈, with the icosahedral projection providing the 3D spatial geometry.
- **M-theory compactifications**: Certain Calabi-Yau manifolds have E₈ symmetry that reduces to icosahedral symmetry in lower dimensions.

The fact that E₈ → H₃ projection preserves φ-coordinates means Zometool can physically model the 3D shadows of these 8-dimensional structures.

### 10.6 Nuclear and Atomic Cluster Physics

#### Alpha-Particle Cluster Models

In nuclear physics, some models describe nuclei as clusters of **alpha particles** (⁴He nuclei) arranged at vertices of polyhedra:
- **¹²C (carbon-12)**: 3 alpha particles at vertices of an equilateral triangle
- **¹⁶O (oxygen-16)**: 4 alpha particles at vertices of a tetrahedron
- **⁴⁰Ca (calcium-40)** and heavier nuclei: speculative models with icosahedral arrangements

While these models are approximate, the icosahedral configurations have particularly low energy in Lennard-Jones and Coulomb-type potentials, and the associated symmetry analysis uses the same group theory that Zometool embodies.

#### Metallic Clusters and Glasses

The **Mackay icosahedron** — a 13-atom cluster with 1 central atom and 12 on the vertices of an icosahedron — is the most stable small cluster for many elements under Lennard-Jones potentials. Larger Mackay icosahedra (55, 147, 309, ... atoms, following the magic numbers 10n²+2) form multi-shell icosahedral structures.

These appear in:
- **Metallic glasses**: Short-range icosahedral order in amorphous metals
- **Frank-Kasper phases**: Crystal structures with icosahedral coordination polyhedra
- **Noble gas clusters**: Argon and xenon clusters preferentially form icosahedral shapes

### 10.7 The Unifying Theme

Across all these domains, the pattern is the same:

| Property | Physics | Zometool |
|----------|---------|----------|
| Symmetry group | Icosahedral (60 rotations) | Same |
| Coordinate field | Q(φ) = {a + bφ : a,b ∈ Q} | Same |
| Position lattice | Z[φ] module in 3D | Same |
| Scaling relation | Powers of φ between shells | Powers of φ between strut lengths |
| Aperiodicity | No translational symmetry | Same |
| Exact arithmetic | Algebraic, zero rounding | Same |

Whenever a physical system exhibits icosahedral symmetry — whether it's a quasicrystal, a virus, a carbon molecule, or a projection from higher-dimensional physics — its mathematical description naturally lives in the golden field Q(φ), and its geometric structure is exactly representable in Zometool/vZome. The toy, the software, and the physics all share the same deep mathematical foundation.

### 10.8 Materials Discovery: From Z[φ] Geometry to an Executable Pipeline

The core idea is still powerful: use icosahedral/golden-ratio structure to constrain search. But for software and physics, the search space must be defined in a way that is both computable and chemically meaningful.

![Materials Discovery via Zome-Constrained Optimization](images/materials-optimization.svg)

#### 10.8.1 Two Corrections Before Optimization

**Correction A — exact coordinates, not exact total energies.**  
Coordinates and symmetry operations can be represented exactly in `Q(φ)`, which is excellent for duplicate detection, symmetry checks, and deterministic geometry transforms. But practical energies from empirical or machine-learned potentials are still numerical approximations.

**Correction B — use bounded or periodic families, not raw dense `Z[φ]^3`.**  
`Z[φ]^3` is countable but dense in `R^3`; naive nearest-neighbor moves are not well-defined. In practice, optimize over:

- **Periodic approximants** generated from 6D cut-and-project data
- **Bounded coefficient windows** in integer coordinate space
- **Template families** (e.g., known approximant topologies) with variable decoration

These choices create a finite candidate set per iteration.

#### 10.8.2 Practical Decision Variables

A realistic candidate is not just geometry. It includes chemistry and periodicity:

- `T`: approximant/template type (or tiling family)
- `A`: lattice/cell parameters and phason/window parameters
- `R`: site coordinates (stored as integer pairs for each `Q(φ)` component)
- `Sigma`: species assignment / site occupancy variables

So optimization is over `(T, A, R, Sigma)` rather than only a set of points `S`.

#### 10.8.3 Objective Functions and Constraints

A practical no-DFT multi-objective target:

```
minimize   [ DeltaE_proxy_hull(x), U_committee(x), P_phonon_mlip(x), P_target(x) ]
subject to stoichiometry, minimum-distance, and synthesis constraints
```

where:

- `DeltaE_proxy_hull`: model-based estimate of energy above hull vs competing phases
- `U_committee`: disagreement across model committee predictions (uncertainty)
- `P_phonon_mlip`: penalty for dynamical instability from MLIP-based phonon checks
- `P_target`: property-specific penalty (e.g., catalytic descriptor or thermal target)

This keeps the pipeline tied to measurable stability and application goals.

#### 10.8.4 Optimization Moves That Actually Work

Instead of "nearest lattice neighbors," use moves in bounded discrete parameter space:

- Increment/decrement bounded integer coefficients in `R`
- Tile substitution / inflation-deflation moves in template space
- Species swaps and occupancy toggles in `Sigma`
- Cell and window parameter perturbations in `A`

These moves preserve representability while remaining algorithmically well-defined.

#### 10.8.5 Actionable Software Plan (Suggested 20-Week v0.1)

| Phase | Weeks | Build | Deliverable |
|------|------|-------|-------------|
| **1. Data + scope** | 1-3 | Ingest quasicrystal/approximant corpora and competing phases | Unified candidate + reference dataset |
| **2. Candidate generator** | 3-6 | Implement approximant/template + decoration generator | Reproducible structure generation API |
| **3. Fast screening** | 6-10 | Relax with ML potentials, filter by geometry and coarse energy proxies | Top-k shortlist for high-fidelity digital validation |
| **4. High-fidelity digital validation** | 10-15 | Committee relaxations, uncertainty scoring, proxy hull analysis, selected phonon/MD checks | Ranked candidates with uncertainty bands |
| **5. Active learning loop** | 15-18 | Retrain surrogate and resample uncertain low-energy regions using digital labels | Improved model + new candidates |
| **6. Experiment-facing outputs** | 18-20 | Simulated diffraction and synthesis-ready reports | Prioritized list for validation |

#### 10.8.6 Recommended Tooling Stack

- **Geometry/materials plumbing**: `pymatgen`, `ASE`, `spglib`
- **Pipeline orchestration/provenance**: `Prefect` or `Snakemake`, plus run-tracking (`MLflow`/`DVC`)
- **Model committee**: `MACE`, `CHGNet`, `MatterSim` (optionally `NequIP`)
- **Thermodynamic proxy layer**: `pycalphad` plus known competing-phase datasets
- **Dynamics/vibrations (no DFT)**: MLIP-driven MD (`ASE`/`LAMMPS`) and `phonopy` with ML forces
- **Benchmark sanity checks**: Cambridge Cluster Database-style cluster tests for optimizer behavior

#### 10.8.7 Minimum Success Criteria

Before claiming discovery, require all of the following:

1. Reproduce at least one known quasicrystal/approximant family as a calibration check.
2. Achieve stable ranking convergence under surrogate retraining.
3. Produce candidates with low `DeltaE_proxy_hull` and low committee disagreement.
4. Show no major dynamical instabilities in selected MLIP phonon/MD checks.
5. Generate distinguishing simulated diffraction signatures for experimental follow-up.
6. Mark outputs clearly as **digitally prioritized candidates** pending optional first-principles or experimental confirmation.

#### 10.8.8 Data and Literature Starting Points

- HYPOD-X quasicrystal datasets and metadata  
  https://www.nature.com/articles/s41597-024-04043-z
- Matbench Discovery benchmark (for model quality tracking)  
  https://www.nature.com/articles/s42256-025-01055-1
- Matbench Discovery project repository  
  https://github.com/janosh/matbench-discovery
- CHGNet (universal interatomic potential)  
  https://github.com/CederGroupHub/chgnet
- MACE (foundation MLIP framework)  
  https://github.com/ACEsuit/mace
- MatterSim (foundation model for atomistic simulation)  
  https://github.com/microsoft/mattersim
- Machine-learning discovery of quasicrystals (ternary systems)  
  https://doi.org/10.1103/PhysRevMaterials.7.093805
- Quasicrystal structure prediction review (approximants, methods, limitations)  
  https://euler.phys.cmu.edu/widom/pubs/PDF/IJCR2023.pdf
- Deep-learning XRD-assisted quasicrystal identification  
  https://pubmed.ncbi.nlm.nih.gov/37964402/

#### 10.8.9 Companion Build Blueprint

For a concrete repository scaffold, module boundaries, milestones, and acceptance criteria aligned to this chapter, see:

- [Materials Discovery Software Scaffold](materials-discovery-software-scaffold.md)

#### 10.8.10 Implementation Status and Quickstart

Current status in this repository:

- `M1 ingest`: implemented.
- `M2 generate`: implemented.
- `M3 screen`: implemented.
- `M4 hifi-validate`: implemented.
- `hifi-rank`, `active-learn`, `report`: interface-complete stubs pending stage logic.

Quickstart (local fixture mode):

```bash
cd materials-discovery
uv sync --extra dev
uv run mdisc ingest --config configs/systems/al_cu_fe.yaml
uv run mdisc generate --config configs/systems/al_cu_fe.yaml --count 50
uv run mdisc screen --config configs/systems/al_cu_fe.yaml
uv run mdisc hifi-validate --config configs/systems/al_cu_fe.yaml --batch all
uv run pytest
uv run ruff check .
uv run mypy src
```

This reframing keeps the original vision intact while making it implementable as a real materials-discovery software program.

---

## 11. Further Resources

### Within the Repository

- [Quick Start Guide](../website/docs/quick-start.md) — Interactive tutorial for building your first dodecahedron
- [Zometool Introduction](../website/docs/zometool-intro.md) — Web-based introduction to Zometool geometry
- [Zomic Language Reference](../core/docs/ZomicReference.md) — Complete Zomic scripting reference
- [Materials Discovery Software Scaffold](materials-discovery-software-scaffold.md) — Practical implementation blueprint for Chapter 10.8
- [Copilot Instructions](../.github/copilot-instructions.md) — Detailed architecture and codebase guide
- [Zomod History](../website/docs/history/zomod/index.md) — History of vZome's predecessor

### Key Source Directories

| Directory | Contents |
|-----------|----------|
| `core/src/main/java/com/vzome/core/algebra/` | Algebraic fields, numbers, vectors, matrices |
| `core/src/main/java/com/vzome/core/math/symmetry/` | Symmetry groups, axes, orbits, permutations |
| `core/src/main/java/com/vzome/core/construction/` | Point, segment, polygon, transformation classes |
| `core/src/main/java/com/vzome/core/edits/` | User-facing edit operations |
| `core/src/main/java/com/vzome/core/zomic/` | Zomic scripting language |
| `core/src/main/java/com/vzome/core/exporters/` | Export to STL, glTF, POV-Ray, etc. |

### External

- **vZome Online**: https://vzome.com/app
- **vZome Website**: https://vzome.com
- **Zometool**: https://zometool.com
- **"Zome Geometry"** by George Hart and Henri Picciotto — the definitive book on Zometool mathematics
- **Discord Community**: discord.gg/vhyFsNAFPS

---

### Interactive Visualization

For an interactive 3D visualization of icosahedral symmetry axes, open [symmetry-visualization.html](symmetry-visualization.html) in a browser. It lets you rotate the icosahedron, toggle each axis type, and see the hole shapes on the surface.

---

*This tutorial was generated from deep analysis of the vZome source code repository at github.com/vZome/vzome.*
