# Generative Fonts Framework

The Generative Fonts Framework is a tool that allows designers and developers to easily create unique fonts in an instant manner. With this framework, you can create multilingual fonts, shuffled fonts or fonts with a specific set of glyphs.

## Features

- Easy to use: the framework is designed to be user-friendly, with a simple interface that makes it easy to create custom fonts.
- Customizable: you can adjust the configuration of the dynamic DAGs to collect fonts from a website to your liking.
- Open-source: the framework is available on GitHub, so you can modify and improve it as needed.

## Getting Started

To get started with the Generative Fonts Framework, follow these steps:

1. Clone the repository to your local machine.
2. Initiate airflow environment, we recommend using the astronomer CLI:
```
astro dev start
```

This will start the airflow environment and install all the required dependencies.
you can access the airflow UI at http://localhost:8080

3. Initiate the Fonts Server as described in the Server README
4. Obtain a Google Fonts API Key and Edit the Config File

To use the `collect_google_fonts` DAG, you will need to obtain a Google Fonts API Key. You can get a key by following the instructions on the [Google Fonts Developer API](https://developers.google.com/fonts/docs/developer_api) page. Once you have obtained a key, you will need to edit the `config.json` file and add your key to the `GOOGLE_FONTS_API_KEY` field.

## Usage

To use the Generative Fonts Framework, follow these steps:

1. Open the Airflow UI and navigate to the DAGs section.
2. Run the following DAGs in order:

   ### etl_collect_<website_name>
   ![etl_collect_website_name DAG](/images/etl_collect_website_name_dag.png)

   Repeat this step for each website you want to collect fonts from. This DAG extracts, transforms, and loads the font data from the specified website.

   ### collect_google_fonts
   ![collect_google_fonts DAG](/images/collect_google_fonts_dag.png)

   This DAG collects fonts from Google Fonts.

   ### data_enrichment
   ![data_enrichment DAG](/images/data_enrichment_dag.png)

   This DAG enriches the collected fonts with granulated glyph information and converts glyphs to SVG format.

   ### clustering
   ![clustering DAG](/images/clustering_dag.png)

   This DAG clusters the fonts based on their features.

   ### data_generation
   ![data_generation DAG](/images/data_generation_dag.png)

   This DAG generates fonts using the generative algorithms.

3. Once the data_generation DAG has finished running, you can find the generated fonts in the local airflow directory under `generated_fonts`.

## Contributing

If you want to contribute to the Generative Fonts Framework, follow these steps:

1. Fork the repository.
2. Create a new branch with your changes.
3. Submit a pull request.

## License

The Generative Fonts Framework is licensed under the MIT License. See LICENSE for more information.
