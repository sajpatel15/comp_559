# RouteDoodle GNN v3: Ordered Safety-Aware Route Snapping

RouteDoodle turns a hand-drawn route shape into a valid walking or jogging route on the Houston street network. The project combines an ordered doodle encoder, PyTorch Geometric graph attention layers, edge-level safety features, and a neural-impedance routing step that keeps generated routes graph-valid.

## Start Here

Run exactly one file:

- `routedoodle_gnn_v2.ipynb`

The notebook is the project entry point. It installs missing Python packages when allowed, clones and copies prebuilt assets when needed, loads or rebuilds caches, restores or trains the RouteGAT checkpoint, evaluates against Dijkstra, launches the browser map UI, and writes sample GPX/KML exports.

Do not run `routedoodle_webapp.py` directly. The web page depends on the live notebook namespace and is started from the notebook after the graph, model, and routing helpers are loaded.

## Step-By-Step Run Guide

### Option A: Google Colab Website

1. Open <https://colab.research.google.com/>.
2. Select the `GitHub` tab.
3. Paste this repository URL:

   ```text
   https://github.com/sajpatel15/comp_559
   ```

4. Open `routedoodle_gnn_v2.ipynb`.
5. Choose a GPU runtime if available:
   `Runtime > Change runtime type > Hardware accelerator > GPU`.
6. Choose `Runtime > Run all`.
7. Approve any notebook prompts Colab shows.
8. Wait for the asset bootstrap cell to finish. On a fresh runtime it prints:

   ```text
   Cloning asset repo from https://github.com/sajpatel15/comp_559.git ...
   ```

   This step downloads Git LFS assets and can be quiet while large files are transferring.

9. Confirm the setup cell prints the run configuration, including:

   ```text
   Run profile:             full
   Prebuilt repo loaded:    True
   Persistent storage root: /content/routedoodle_artifacts
   ```

10. Let the notebook continue until the interactive-map section. If you used `Run all`, the web launch cell runs automatically.

### Option B: Local Jupyter

1. Clone the repository:

   ```bash
   git clone https://github.com/sajpatel15/comp_559.git
   cd comp_559
   ```

2. If Git LFS is available, pull the large assets:

   ```bash
   git lfs pull
   ```

3. Create the optional conda environment:

   ```bash
   conda env create -f environment.yml
   conda activate comp559
   ```

4. Start Jupyter:

   ```bash
   jupyter lab
   ```

5. Open `routedoodle_gnn_v2.ipynb`.
6. Choose `Run > Run All Cells`.

The notebook can also install missing packages into the active kernel by default. To prevent automatic installs, set `ROUTEDOODLE_AUTO_INSTALL=0` before starting Jupyter and install the packages from `environment.yml` yourself.

### Option C: VS Code Notebook

1. Open this repository folder in VS Code.
2. Open `routedoodle_gnn_v2.ipynb`.
3. Select either a local `comp559` kernel or a connected Colab/Jupyter runtime.
4. Run all cells.

When VS Code is connected to a Colab runtime, the notebook still runs on the Colab machine. Asset paths use `/content/...`, and the web page launch flow is the same as Colab.

## Exact Web Page Launch Guide

The main interactive web page is launched by notebook section `8.3 Launch full-page web map`.

1. Run the notebook until it prints a line starting with:

   ```text
   Interactive map helpers ready
   ```

2. Run the next cell, titled:

   ```text
   8.3 Launch full-page web map
   ```

3. The cell starts the notebook-backed web server on port `8765`.
4. The launch cell is configured to require a public URL, so it attempts a tunnel in Colab, remote Jupyter, and local Jupyter runs. It tries Cloudflare Quick Tunnel first and downloads `cloudflared` if needed. Expected messages look like:

   ```text
   Starting public RouteDoodle URL tunnel; this can take 15-45 seconds on a fresh runtime ...
   Trying public tunnel provider: cloudflared
   Downloading cloudflared for public URL support ...
   ```

5. When the tunnel is ready, the output shows a card named:

   ```text
   RouteDoodle GNN v3 - Full-Page Map
   ```

6. Click the `Open https://...` link in that output card. The notebook also prints the same URL:

   ```text
   RouteDoodle web app running at https://.../
   ```

7. Keep the notebook runtime running while using the page. The page sends route requests back to the notebook kernel, so the URL stops working when the runtime disconnects, restarts, or the tunnel process exits.

### Using The Web Page

1. Wait for the page header to show the active profile and artifact version.
2. Use the Leaflet draw toolbar on the map to draw a polyline route shape in Houston.
3. Click one of the route buttons:
   - `GNN v3`: route with the trained RouteGAT model.
   - `Dijkstra`: route with the graph baseline.
   - `Compare Both`: draw both routes on the map.
   - `Clear`: remove the doodle and route overlays.
4. Read the route metrics in the left panel after a route completes.

The dashed blue line is the drawn doodle, the red route is `GNN v3`, and the green route is `Dijkstra`.

### Comparison Map

Later in the notebook, the static comparison-map cell starts a second page on port `8766`. It follows the same public URL flow and prints:

```text
RouteDoodle comparison map running at https://.../
```

Use the main `8765` web app for drawing new routes. The comparison map is for viewing a generated validation example.

## Expected Runtime Behavior

The default run profile is `full`:

- `ROUTEDOODLE_RUN_PROFILE=full`
- 1,000 synthetic samples via the prebuilt PyG dataset cache.
- RouteGAT checkpoint restored from `artifacts/routegat_v3_full.pt`.
- Crime-aware safety graph restored from `artifacts/houston_danger_v3.pkl`.
- Static full-network plots disabled by default so Colab stays responsive.

For a quick debugging run, start the notebook process with:

```bash
ROUTEDOODLE_RUN_PROFILE=smoke jupyter lab
```

The smoke profile is useful for local checks, but the submitted workflow uses the full profile unless overridden.

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

The notebook checks usable local artifacts first. If the required cached-run artifacts are missing or are only Git LFS pointer files, it clones `https://github.com/sajpatel15/comp_559.git` into a prebuilt asset directory and copies `artifacts/` and `cache/` into the runtime. In Colab this directory is `/content/routedoodle_prebuilt_repo`; locally it is `.routedoodle_prebuilt_repo/`. If Git LFS preload fails, the notebook continues into its rebuild/download paths.

If the NIBRS crime CSV and prebuilt safety graph are unavailable, the notebook still runs end-to-end with zero-valued safety features. That fallback preserves reproducibility while reporting that crime-aware scoring is disabled.

Large assets are tracked through Git LFS via `.gitattributes`.

## Configuration Overrides

- `ROUTEDOODLE_REPO_URL`: asset repository URL.
- `ROUTEDOODLE_REPO_REF`: branch, tag, or ref to clone.
- `ROUTEDOODLE_RUN_PROFILE`: `smoke` or `full`.
- `ROUTEDOODLE_AUTO_INSTALL`: install missing packages into the active kernel, default `1`.
- `ROUTEDOODLE_FORCE_PRELOAD_ASSETS`: force re-copy from the cloned asset repo.
- `ROUTEDOODLE_RENDER_PLOTS`: force static plots on or off.
- `ROUTEDOODLE_FORCE_REBUILD_GRAPH`
- `ROUTEDOODLE_FORCE_REBUILD_DANGER`
- `ROUTEDOODLE_FORCE_REBUILD_DATASET`
- `ROUTEDOODLE_FORCE_REBUILD_PYG`
- `ROUTEDOODLE_FORCE_REBUILD_CHECKPOINT`
- `ROUTEDOODLE_TUNNEL`: public URL provider, default `auto`; supported values include `cloudflared` and `ngrok`.
- `ROUTEDOODLE_PUBLIC_URL`: use an already-published reverse proxy URL instead of creating a tunnel.
- `ROUTEDOODLE_AUTO_INSTALL_TUNNEL`: download/install missing tunnel helpers into the runtime, default `1`.
- `ROUTEDOODLE_CLOUDFLARED_BIN`: path to an existing `cloudflared` binary.
- `ROUTEDOODLE_NGROK_AUTHTOKEN` or `NGROK_AUTHTOKEN`: required when forcing `ROUTEDOODLE_TUNNEL=ngrok`.

## Troubleshooting

### Asset clone appears stuck

The bootstrap checks local cache files first, then runs `git clone --depth 1` and `git lfs pull` only when the cached-run artifacts are incomplete. The notebook captures subprocess output, so Git LFS progress may not stream to the notebook. Fresh Colab runtimes can take several minutes because the full artifacts are multiple gigabytes. If Git LFS cannot provide the files, the notebook removes unusable pointer files and falls back to rebuilding/downloading what it needs.

### Web link does not appear

Rerun section `8.3 Launch full-page web map`. If Cloudflare Quick Tunnel fails repeatedly, use ngrok by setting these before the launch cell:

```python
%env ROUTEDOODLE_TUNNEL=ngrok
%env NGROK_AUTHTOKEN=your_ngrok_token
```

Then rerun the launch cell.

For a local Jupyter run, the server starts before the tunnel is created. If the tunnel fails but the server started, open this URL from the same machine:

```text
http://127.0.0.1:8765/
```

### Web page opens but routing fails

Confirm that earlier cells completed successfully and that the notebook printed a loaded graph, dataset, and checkpoint. The web app calls back into the live notebook kernel; if the kernel restarted after the launch cell, rerun the notebook from the setup cells through section `8.3`.

## Repository Layout

```text
routedoodle_gnn_v2.ipynb   # only notebook to run
routedoodle_webapp.py      # web helper imported by the notebook
README.md                  # project and run instructions
environment.yml            # optional local environment
final_report/report.pdf    # final project report
call-for-projects.pdf      # course project prompt
artifacts/                 # graph, datasets, checkpoints
cache/                     # OSMnx request cache
outputs/                   # generated GPX/KML and runtime outputs
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
