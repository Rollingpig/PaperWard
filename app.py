from search.fusion_search import get_fusion_search_results
from analysis.base_process import batch_analysis
from analysis.rank_results import rank_results
from configs.read_yaml import load_config
from utils.app_types import DatabaseItem
from visualization.write_html import write_html
from storage.database import add_arxiv
import asyncio


def main(yaml_path: str = "configs/example_config.yaml",
         html_path: str = "output.html",
         rpm_limit: int = 10):
    # TODO: enable multiple configs
    config = load_config(yaml_path)
    logging.info(f"config loaded from {yaml_path}")
    
    # search related papers
    search_results = get_fusion_search_results(config.queries)
    logging.info(f"search results fetched")

    # TODO: compare the search results with the database to avoid duplicate analysis

    # use LLMs to answer the questions in the search results
    # avoid breaking the rpm limit of the API
    analyse_results = []
    for i in range(0, len(search_results), rpm_limit):
        logging.info(f"Analysing search item {i} to {i+rpm_limit}")
        analyse_batch = asyncio.run(batch_analysis(search_results[i:i+rpm_limit], config.questions))
        analyse_results.extend(analyse_batch)

    # weave the analysis results with the search results
    database_items = [DatabaseItem(search_result, analysis) for search_result, analysis in zip(search_results, analyse_results)]

    for i in database_items:
        add_arxiv(i)

    # rank the analysis results
    ranked_results = rank_results(database_items)
    
    # write the results to an HTML file
    write_html(ranked_results, html_path)

    # open the html file in the default web browser
    import webbrowser
    webbrowser.open(html_path)

    

if __name__ == '__main__':
    import logging
    logging_level = logging.INFO
    logging.basicConfig(level=logging_level)
    logging.debug(f"Logging initialized at level {logging_level}")
    main()
