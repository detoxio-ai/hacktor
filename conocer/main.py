

import argparse
import logging
import tempfile
from conocer.webapp.scanner import GenAIWebScanner, CrawlerOptions, ScannerOptions


def main():
    parser = argparse.ArgumentParser(
        description="Human Assisted scanning of Web Apps",
        epilog="Thank you. Happy Crawling.")
    parser.add_argument("url", type=str, help="Starting URL for crawling.")
    parser.add_argument("-s",
                        "--session",
                        type=str,
                        help="Path to session file for storing crawl results")
    parser.add_argument("--skip_crawling",
                        action="store_true",
                        help="Run the crawler in a synchronous manner")
    parser.add_argument("--save_session",
                        action="store_true",
                        help="Save Crawling Session for next time")
    # parser.add_argument("-hl",
    #                     "--headless",
    #                     action="store_true",
    #                     help="Run the browser context in a headless manner")
    parser.add_argument("--no_of_tests",
                        type=int,
                        default=10,
                        help="No of Tests to run. Default 10")
    parser.add_argument("--log_level",
                        type=str,
                        default="WARN",
                        help="Path to session file for storing crawl results")

    parser.add_argument("--prompt_prefix",
                        type=str,
                        default="",
                        help="Add a prefix to every prompt to make prompts more contextual")

    parser.add_argument(
        "-m",
        "--slowmotion",
        type=int,
        default=300,
        help=
        "set time im miliseconds for executions of APIs. Setting higher number will make executions of APIs on a page more slower. "
    )
    parser.add_argument(
        "-b",
        "--browser",
        type=str,
        help=
        "Browser type to run playwright automation on. Allowed values are Webkit, Firefox and Chromium."
    )
    args = parser.parse_args()

    level = logging.getLevelName(args.log_level)
    logging.basicConfig(level=level)

    crawl_options = CrawlerOptions(speed=args.slowmotion, 
                                browser_name=args.browser, 
                                headless=False)
    scan_options = ScannerOptions(session_file_path=args.session, 
                                skip_crawling=args.skip_crawling, 
                                save_session=args.save_session, 
                                crawler_options=crawl_options,
                                no_of_tests=args.no_of_tests, 
                                prompt_prefix=args.prompt_prefix)
    scanner = GenAIWebScanner(scan_options)
    report = scanner.scan(args.url)
    print(report.as_markdown())
    print(report.as_dict())


if __name__ == "__main__":
    main()







