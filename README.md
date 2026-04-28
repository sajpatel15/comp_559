# RouteDoodle GNN v3: Ordered Safety-Aware Route Snapping

RouteDoodle is a graph machine learning project for turning a hand-drawn route shape into a valid walking/jogging route on the Houston street network. The model combines an ordered doodle encoder, PyTorch Geometric graph attention layers, edge-level safety features, and a neural-impedance routing step that keeps outputs graph-valid.

## Submission Entry Point

Run exactly one file:

- `routedoodle_gnn_v2.ipynb`

The notebook is self-contained. It bootstraps Python packages, clones/copies repo assets when needed, loads or rebuilds caches, trains or restores the RouteGAT checkpoint, evaluates against a Dijkstra baseline, displays the interactive map UI, and exports sample GPX/KML routes.

## How To Run

### Google Colab

1. Open `routedoodle_gnn_v2.ipynb` in Colab.
2. Choose `Runtime > Run all`.

No Google Drive mount is required. The notebook clones this repository, copies `artifacts/` and `cache/`, and runs the default full profile.

### Local Jupyter

1. Open `routedoodle_gnn_v2.ipynb` in any local Jupyter kernel.
2. Run all cells.

The notebook installs missing Python packages into the active kernel by default. If root-level assets are missing, it clones `https://github.com/sajpatel15/comp_559.git` into `.routedoodle_prebuilt_repo/` and copies `artifacts/` and `cache/` into the runtime.

An optional reproducible environment file is included:

```bash
conda env create -f environment.yml
conda activate comp559
jupyter lab
```

This environment is convenient but not required by the submission workflow.

## Run Profiles

The default is the full project run:

- `ROUTEDOODLE_RUN_PROFILE=full`
- 1,000 synthetic samples via the prebuilt PyG dataset cache
- compatible RouteGAT checkpoint restored from `artifacts/routegat_v3_full.pt`
- crime-aware safety graph restored from `artifacts/houston_danger_v3.pkl`
- static full-network plots disabled by default to keep Colab noninteractive

For a quick debugging run:

```bash
ROUTEDOODLE_RUN_PROFILE=smoke jupyter lab
```

The smoke profile is useful for fast local testing, but the submitted notebook runs the full profile unless overridden.

## Assets And Reproducibility

Minimum artifact expected in the repo:

- `artifacts/houston_walk_graph.graphml`

Required full-profile artifacts for the default noninteractive run:

- `artifacts/NIBRSPublicView2025.csv`
- `artifacts/houston_danger_v3.pkl`
- `artifacts/houston_danger_v3_meta.json`
- `artifacts/pyg_dataset_v3_full.pkl`
- `artifacts/pyg_dataset_v3_full_meta.json`
- `artifacts/routegat_v3_full.pt`

Optional smoke artifacts:

- `artifacts/dataset_raw_v3_smoke.pkl`
- `artifacts/pyg_dataset_v3_smoke.pkl`
- `artifacts/pyg_dataset_v3_smoke_meta.json`
- `artifacts/routegat_v3_smoke.pt`

If the NIBRS crime CSV and prebuilt safety graph are unavailable, the notebook still runs end-to-end with zero-valued safety features. That fallback preserves reproducibility for reviewers while clearly reporting that crime-aware scoring is disabled.

Large assets are tracked through Git LFS via `.gitattributes`.

## Config Overrides

- `ROUTEDOODLE_REPO_URL`: asset repository URL
- `ROUTEDOODLE_REPO_REF`: branch, tag, or ref to clone
- `ROUTEDOODLE_RUN_PROFILE`: `smoke` or `full`
- `ROUTEDOODLE_AUTO_INSTALL`: install missing packages into the active kernel, default `1`
- `ROUTEDOODLE_FORCE_PRELOAD_ASSETS`: force re-copy from the cloned asset repo
- `ROUTEDOODLE_RENDER_PLOTS`: force static plots on or off
- `ROUTEDOODLE_FORCE_REBUILD_GRAPH`
- `ROUTEDOODLE_FORCE_REBUILD_DANGER`
- `ROUTEDOODLE_FORCE_REBUILD_DATASET`
- `ROUTEDOODLE_FORCE_REBUILD_PYG`
- `ROUTEDOODLE_FORCE_REBUILD_CHECKPOINT`

## Repository Layout

```text
routedoodle_gnn_v2.ipynb   # only notebook to run
README.md                  # project and grading instructions
environment.yml            # optional local environment
artifacts/                 # graph, datasets, checkpoints
cache/                     # OSMnx request cache
```

Generated files are written to `outputs/` and ignored by Git.

## Project Components

- Full Houston walking graph from OpenStreetMap via OSMnx.
- Ordered multi-waypoint synthetic route generation.
- Doodle perturbation and resampling to model user-drawn shapes.
- RouteGAT v3 model with a CNN doodle encoder and graph attention layers.
- Edge features for length, crime score, danger overlap, lighting, sidewalks, and crossings.
- Neural-impedance inference that converts GNN edge probabilities into route weights.
- Evaluation against Dijkstra using discrete Frechet distance and route safety score.
