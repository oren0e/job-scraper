#!/usr/bin/env python

if __name__ == '__main__':
    from core_files.backend import Notifier
    import argparse
    from config.common import ROOT_DIR, CURRENT_DATE
    from utils.logger import logger

    # CLI
    parser = argparse.ArgumentParser(prog='jobs',
                                     description='Get html table of recent jobs from indeed.com'
                                                 ' according to query and optional'
                                                 ' search terms in jobs description')
    # arguments
    parser.add_argument('query', metavar='query', type=str, help='Query string. Example: "software engineer"')
    parser.add_argument('-t', '--terms', type=str, action='store', help='Search terms for job description separated by ",".'
                                                                        'Example: "dog, cat lover, high quality"')
    parser.add_argument('-n', '--num_jobs', action='store', type=int, help='Number of search results to fetch. Default: 15')
    parser.add_argument('-sbr', '--sortby_relevance', action='store_true',
                        help='Sort by relevance. Default is by date')
    parser.add_argument('-a', '--all_terms', action='store_true',
                        help='If specified, all search terms must be found in job description')
    parser.set_defaults(sortby_relevance=False)
    args = parser.parse_args()

    # num jobs has to be greater than or equal to 15
    if args.num_jobs < 15:
        print('num_jobs has to be greater or equal to 15, try again')

    else:
        if args.sortby_relevance:
            myjob = Notifier(query=args.query, terms=args.terms, num_recent_jobs=args.num_jobs,
                             sort_by='relevance', all_terms=args.all_terms)
        else:
            myjob = Notifier(query=args.query, terms=args.terms, num_recent_jobs=args.num_jobs,
                             all_terms=args.all_terms)

        df = myjob.build_jobs_table()

        if df is None:
            logger.info("No results were found")
            print("No matching results were found!")
        else:
            with open(ROOT_DIR + f'/jobs_{CURRENT_DATE}.html', 'w') as file:
                file.write(df.to_html(justify='center', render_links=True, index=False))
            logger.info(f"HTML file saved successfully to {ROOT_DIR}")
            print(f'HTML file written successfully to {ROOT_DIR}')
