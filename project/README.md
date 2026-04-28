# RouteDoodle GNN v3 Notebook

The project notebook is `routedoodle_gnn_v2.ipynb`. It is set up for non-interactive Colab runs that first try to clone a public repo containing prebuilt artifacts and cache files. If that preload fails, the notebook falls back to rebuilding in the Colab runtime under `/content`.

## Colab cold-start flow

1. Make the artifact repo public.
2. Put the prebuilt artifacts under the configured artifact directory, currently `ML/artifacts`.
3. Optionally put OSMnx cache files under `ML/cache` or `cache`.
4. Open `routedoodle_gnn_v2.ipynb` in Colab and run from the top.
5. Leave `FORCE_REBUILD_* = False` to prefer cloned artifacts.
6. Switch `RUN_PROFILE` between `"smoke"` and `"full"` depending on which artifact set you want.

The notebook does not mount Google Drive and should not prompt the user for Drive access.

## Public repo config

The config cell defaults to:

- `PREBUILT_REPO_URL = "https://github.com/sajpatel15/comp_559.git"`
- `PREBUILT_REPO_REF = "main"`
- `PREBUILT_ARTIFACT_SUBDIR = "ML/artifacts"`
- `PREBUILT_CACHE_SUBDIRS = ["ML/cache", "cache"]`

These can also be overridden in Colab with environment variables:

- `ROUTEDOODLE_REPO_URL`
- `ROUTEDOODLE_REPO_REF`
- `ROUTEDOODLE_ARTIFACT_SUBDIR`
- `ROUTEDOODLE_CACHE_SUBDIRS`

## Required artifact files

Shared artifacts:

- `houston_walk_graph.graphml`
- `houston_danger_v3.pkl`
- `houston_danger_v3_meta.json`
- `NIBRSPublicView2025.csv`

Profile-specific artifacts:

- `dataset_raw_v3_smoke.pkl`
- `pyg_dataset_v3_smoke.pkl`
- `pyg_dataset_v3_smoke_meta.json`
- `routegat_v3_smoke.pt`
- `dataset_raw_v3_full.pkl`
- `pyg_dataset_v3_full.pkl`
- `pyg_dataset_v3_full_meta.json`
- `routegat_v3_full.pt`

The notebook will still run without some caches, but missing graph, danger, dataset, or checkpoint artifacts will be rebuilt when needed. The crime CSV is required for a danger rebuild.

## Important GitHub note

The current full artifacts are larger than normal GitHub file limits, so store them with Git LFS or another public download mechanism. The notebook attempts `git lfs pull` in Colab after cloning; if LFS download fails, it continues and rebuilds anything it cannot load.

## Local environment

```bash
cd /Users/sajpatel/projects/comp_559/project
conda env create -f environment.yml
conda activate comp559
python -m ipykernel install --user --name comp559 --display-name "comp559"
jupyter lab
```

Open `routedoodle_gnn_v2.ipynb` and run it from the top.
