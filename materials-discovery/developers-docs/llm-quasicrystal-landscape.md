# Using Language Models to Simulate Quasicrystals

While there are powerful Large Language Models (LLMs) capable of generating and analyzing standard crystal structures, **directly generating true quasicrystals using an LLM remains a significant challenge** due to the unique geometry of these materials. However, LLMs and other forms of Artificial Intelligence are actively being used to simulate, discover, and study quasicrystals and their periodic counterparts (approximants).

Here is a breakdown of how LLMs and other AI models are currently interacting with quasicrystals:

## The Challenge with LLMs and Quasicrystals

Most crystal-generating LLMs—such as **CrystaLLM** (a GPT-based model), **CrystalTextLLM** (fine-tuned on LLaMA-2), and **MatLLMSearch**—are trained to read and generate Crystallographic Information Files (CIFs) or simple text representations.

These standard formats fundamentally rely on "periodic boundary conditions" (a repeating unit cell) and standard space groups to describe a material. Because quasicrystals exhibit long-range order but **strictly lack translational periodicity**, they cannot be accurately described by standard 3D unit cells. To properly represent a quasicrystal for a machine learning model, the lattice math must often be scaled up to 4, 5, or 6 dimensions before being mathematically projected back down into 3D space. Because of this, current text-based LLMs struggle to natively propose true quasicrystal structures from scratch.

## How LLMs are Used in Quasicrystal Workflows

Despite the generation barrier, specialized LLMs are highly valuable in the quasicrystal research pipeline:

*   **Predicting Synthesizability (CSLLM):** The Crystal Synthesis Large Language Model (CSLLM) is a specialized framework with a 98.6% accuracy rate for predicting whether a proposed theoretical structure can actually be synthesized in a lab. It is specifically highlighted for its capability to suggest the exact chemical precursors needed to attempt the synthesis of complex materials like quasicrystals.
*   **Data Interpretation:** LLMs are currently being used alongside diffusion models to interpret complex neutron scattering patterns. This helps researchers bridge the gap between molecular-level interactions and the emergence of global quasiperiodicity in soft matter quasicrystals.

## AI Models That Can Simulate and Generate Quasicrystals

While text-based LLMs handle the theoretical and synthesis planning, other specialized deep learning architectures are responsible for the actual generation and simulation of quasicrystals:

*   **Simulating Stability (MLIPs):** To simulate whether a proposed quasicrystal will be physically stable, researchers bypass slow traditional calculations (like Density Functional Theory) and use **Machine-Learned Interatomic Potentials (MLIPs)**. Neural networks like MACE, CHGNet, and MatterSim act as surrogate models that can simulate the molecular dynamics, phonon stability, and structural relaxation of quasicrystal candidates in a matter of seconds.
*   **Generative Diffusion Models (SCIGEN):** To actively design materials with complex aperiodic or quasiperiodic geometries, researchers use diffusion models rather than LLMs. The **SCIGEN** tool acts as a gatekeeper for diffusion models, forcing the AI to respect strict geometric constraints. It has been used to generate millions of candidates with Archimedean lattices (complex 2D tilings associated with quantum materials and quasicrystal approximants).
*   **Discovering Electronic Quasicrystals:** Using an AI method called Neural-Network Variational Monte Carlo (NN-VMC), researchers recently discovered an entirely new quantum phase of matter: the *electronic quasicrystal*. The AI simulated electrons in a semiconductor and found that they naturally arranged themselves into a quasicrystalline charge order without an underlying atomic lattice.
*   **The TSAI Model:** The first stable quasicrystals ever discovered by AI were found by "TSAI," a Random Forest machine learning model. It screened thousands of alloy compositions and successfully predicted the exact formulas needed to synthesize three brand new decagonal quasicrystals.

## The LLM-Quasicrystal Analogy

A fascinating theoretical note: Researchers in computer science have actually drawn a formal analogy between how LLMs "think" and how quasicrystals form. Just as quasicrystals generate infinite, non-repeating structures based strictly on local geometric rules (like Penrose tiles), LLMs generate coherent, non-repeating language based entirely on local statistical constraints (predicting the next token). Both systems create highly structured, complex emergent patterns without a centralized, repeating blueprint.

## How This Pipeline Bridges the Gap

Our materials-discovery pipeline addresses the LLM-quasicrystal generation gap through a hybrid approach:

1. **Zomic as the representation language.** Instead of CIF, we use vZome's Zomic language, which operates natively in the golden field Z[phi] and supports aperiodic geometry without periodic boundary conditions. See [LLM Integration Architecture](llm-integration.md) for the full technical design.
2. **LLMs generate Zomic, not coordinates.** This means the LLM produces a compact program that the Zomic compiler expands into exact geometry—eliminating the "approximately right" failure mode.
3. **MLIPs for physical validation.** Generated candidates flow through MACE/CHGNet/MatterSim screening for stability assessment without DFT.
4. **CSLLM-inspired synthesizability.** The planned `llm-evaluate` stage will assess whether candidates can actually be made in the lab.

See [LLM Integration Architecture](llm-integration.md) for implementation details and [Zomic LLM Data Plan](zomic-llm-data-plan.md) for the training corpus strategy.
