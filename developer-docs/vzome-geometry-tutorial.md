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
10. [Further Resources](#10-further-resources)

---

## 1. What is Zometool?

Zometool is a precision mathematical construction toy designed to build 3D geometric structures using two components:

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

Each extra color represents a different **orbit** — a family of directions related by the 60 icosahedral rotations. The standard blue/yellow/red orbits have fewer than 60 axes each (30/20/12) because they align with symmetry axes, so some rotations map an axis to itself. The extra orbits don't align with any symmetry axis, so each has the full **60 axes** (one per rotation).

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

## 10. Further Resources

### Within the Repository

- [Quick Start Guide](../website/docs/quick-start.md) — Interactive tutorial for building your first dodecahedron
- [Zometool Introduction](../website/docs/zometool-intro.md) — Web-based introduction to Zometool geometry
- [Zomic Language Reference](../core/docs/ZomicReference.md) — Complete Zomic scripting reference
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
