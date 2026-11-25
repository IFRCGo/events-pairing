# Events Pairing

Events Pairing is a process of identifying and grouping disaster or hazard events that refer to the same real-world occurrence but are reported by multiple independent data sources. In the context of Montandon, this application is designed to consolidate and harmonize event information collected from various providers in order to improve event tracking, analysis, and interoperability across datasets.

As of 10 May 2026, Montandon integrates data from 11 different sources, out of which 9 are currently active. These sources publish information related to a wide range of hazards, including but not limited to earthquakes, floods, tropical cyclones, droughts, wildfires, and severe weather events. Since multiple organizations may report the same event independently, the resulting datasets often contain duplicated or overlapping records with slight variations in location, timing, naming conventions, or metadata.

The primary objective of this application is to automatically identify events that are spatially and temporally related, and group them into clusters representing the same or highly similar hazard occurrences. By pairing related events across sources, the system helps reduce duplication, improves consistency, and enables more reliable downstream analysis and decision-making.

# Methodology

- The workflow begins by retrieving event data from the Montandon eoAPI STAC items on a daily basis. Data is collected from multiple active sources, ensuring that newly reported hazard events are continuously incorporated into the system.

- The application applies the DBSCAN (Density-Based Spatial Clustering of Applications with Noise) clustering algorithm to group events that are likely to represent the same real-world occurrence. DBSCAN is particularly suitable for this use case because it can discover clusters of arbitrary shapes while also identifying isolated records as noise.

  More information about the algorithm can be found here:
  https://en.wikipedia.org/wiki/DBSCAN

- Unlike algorithms such as K-Means, DBSCAN does not require prior knowledge of the number of clusters to be generated. This is an important advantage because the number of disaster events occurring globally can vary significantly from day to day.

- Events are clustered primarily using spatial and temporal proximity:
  - **Spatial proximity** evaluates how geographically close events are to one another.
  - **Temporal proximity** evaluates how close the reported event timestamps are.

- If an event cannot be associated with any neighboring events based on the defined clustering conditions, it is labeled with a cluster identifier of `-1`, which represents noise or an ungrouped event.

- To determine the most suitable clustering configuration, the application performs a Grid Search over multiple combinations of:
  - spatial weight values,
  - temporal weight values,
  - DBSCAN parameters such as `eps` and `min_samples`.

- Each parameter combination is evaluated using the `DBCV` (Density-Based Clustering Validation) score, which measures the quality and validity of density-based clusters. The configuration with the highest valid score is selected as the recommended clustering setup.

- In situations where an optimal configuration cannot be identified, the system falls back to a predefined set of recommended parameter values based on empirical observations and prior experimentation.

- Clustering is performed independently for each hazard category. This hazard-specific processing helps ensure that unrelated hazard types are not incorrectly grouped together. For example, earthquake events are clustered separately from flood or tropical cyclone events.

- Once clustering is completed, the generated hazard-based cluster outputs are stored in the `outputs` directory. This directory also contains associated visualizations and plots that help analyze the clustering behavior, spatial distributions, and temporal relationships between events.

- The resulting paired-event datasets can then be used for further analysis, validation, visualization, or integration into downstream disaster management and monitoring workflows.


# Run the application

Execute the following command to run the main application script using `uv`:

```bash
uv run python src/events_pairing/main.py
```

# Install the application

```bash
pip install git+https://github.com/IFRCGo/events-pairing.git
```

# Usage

```python
from events_pairing.utils import Utils
from events_pairing.main import run_pipeline
from events_pairing.grid_search import GridSearch

data = Utils.load_data(file_path=PATH_OF_DATA_SOURCE)
processed_data = Utils.preprocess_data(event_data=data)
optimal_params = GridSearch.run_grid_search(...)
run_pipeline(...)

Note: check the usage in the events_pairing/src/main.py
```
