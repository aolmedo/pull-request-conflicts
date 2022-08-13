# Pull Requests Integration Process Optimization: An Empirical Study

## GHTorrent data

The data extracted from GHTorrent dataset is [here](https://github.com/aolmedo/pull-request-conflicts/tree/main/ghtorrent_data).

## Scripts

### Stage 1: GHtorrent data extraction

To extract the data from GHTorrent we use the following script:

     python ghtorrent_extract_data.py

The extracted data can be found [here](https://github.com/aolmedo/pull-request-conflicts/tree/main/ghtorrent_data).

### Stage 2: Pairwise conflict dataset creation

Import projects:

     python manage.py import_projects

Upgrade project info:

     python manage.py upgrade_project_info

Import commits, import pull requests, upgrade pull requests info, get pairwise conflicts:

     python build_dataset.py

### Stage 3: Integration process analysis

Calculate projects time windows info:

     python calculate_projects_time_windows.py

Calculate projects time windows statistics:

     python calculate_projects_ipe_stats.py

