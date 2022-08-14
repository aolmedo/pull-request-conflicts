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

## Reproducibility Assessment

We conduct the reproducibility assessment for our empirical study according to the methodological framework of González-Barahona and Robles [1]. González-Barahona and Robles have designed a framework for assessing empirical studies using five criteria applied on eight study elements. The five criteria defined in the framework are the following:

- **Identification:** where the elements of the study are stored, i.e., where their originals can be found
- **Description:** the level of detail of each study elements.
    - "Textual" refers to a textual description of your data or your process.
    - "Source code" refers to an implementation used to obtain, exploit or analyze the data.
- **Availability:** easiness with which other researchers can obtain the research material.
- **Persistence:** persistence of the research elements over time.
- **Flexibility:** adaptability of research elements to new environments.

Using them, González-Barahona and Robles characterize eight study elements:

1. **Data Source.** This source may be the software repository(ies) used for the study. This source may also concern study objects (libraries, packages, etc.) or a set of concatenated data.
2.  **Retrieval methodology.** Extraction process from the raw data source, using manual or automated tools.
3.  **Raw dataset.** Data obtained after extraction without any modification.
4.  **Methodology extraction.** Process used to extract and clean the relevant data from the raw data.
5.  **Study parameters.** The study parameters affecting the processes changing the dataset. These can be time periods, types of information, etc.
6.  **Processed dataset.** A set of data processed through the extraction methodology that will be the inputs to the methodological analysis. This data can be, for example, an SQL database, a CSV file for use in a spreadsheet or any other analysis tool.
7.  **Analysis methodology.** The process of analysing all or part of the data to obtain results.
8.  **Results dataset.** Data produced by the analysis methodology and using the processed dataset. These data are the basis of the research results. They can be of different forms: textual, graphical, mathematical, etc.

Each pair of criteria / element can take the following values:

-  **Complete:** value used to describe the availability of all the information necessary to locate or identify an element of the study. The information given may be textual only or from the source code of the experiment.
- **Partial:** indicates a lack of information or too much generality around the study element.
- **No:** total lack of information on the element.
- **N/A (Not Applicable):** implies that the attribute is not applicable to the element in question.
- **Private/Public:** value characterising the availability of the search item.
- **Probable:** value applying to the persistence attribute in the case where there is a possibility that an item will be available for future access.
- **Unknown:** value used for the persistence attribute in case it is impossible to determine any persistence over time.

The reproducibility assessment for our study is given in the following table:


|                            | **Identification** |    **Description**    | **Availability** | **Persistence** | **Flexibility** |
|:--------------------------:|:------------------:|:---------------------:|:----------------:|:---------------:|:---------------:|
| **Data source**            |      Complete      |        Textual        |      Public      |     Probable    |       N/A       |
| **Retrieval Methodology**  |      Complete      | Source code + Textual |        No        |       N/A       |       N/A       |
| **Raw Dataset** [[here]](https://github.com/aolmedo/pull-request-conflicts/tree/main/ghtorrent_data)            |      Complete      | Source code + Textual |      Public      |     Probable    |     Partial     |
| **Extraction Methodology** [[here]](https://github.com/aolmedo/pull-request-conflicts/tree/main/)|      Complete      | Source code + Textual |      Public      |     Probable    |        No       |
| **Study Parameters**       |      Complete      | Source code + Textual |        N/A       |       N/A       |       N/A       |
| **Processed Dataset**      |       Partial      |        Textual        |        No        |     Unknown     |       N/A       |
| **Analysis Methodology** [[here]](https://github.com/DedalArmy/empirical-study-architectural-contributions) |      Complete      | Source code + Textual |      Public      |       N/A       |       N/A       |
| **Results Dataset**        |      Complete      |        Textual        |      Public      |     Probable    |       N/A       |


We achieve a good reproducibility for this contribution due to the availability of the raw data used but also due to the availability of the source code related to the experiments and analysis. A point of improvement could be to provide the various intermediate data sets between the raw data and the results. Indeed, as shown by the table we not provide the intermediate dataset created at each step of processing.

[1] González-Barahona, J. M., & Robles, G. (2012). On the reproducibility of empirical software engineering studies based on data retrieved from development repositories. Empirical Software Engineering, 17(1), 75-89.
