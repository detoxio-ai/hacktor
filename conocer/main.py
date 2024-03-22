import argparse
import logging
import json
from conocer.webapp.scanner import GenAIWebScanner, CrawlerOptions, ScannerOptions, FUZZING_MARKERS

def save_json_report(out_path, report):
    if out_path:
        with open(out_path+".", "w") as out:
            json.dump(report.as_dict(), out)

def save_markdown_report(out_path, report):
    if out_path:
        with open(out_path+".", "w") as out:
            json.dump(report.markdown(), out)

def main():
    parser = argparse.ArgumentParser(
        description="""
Human Assisted Testing of GenAI Apps and Models: 

[1] python conocer/main.py webapps <<GenAI APP URL>>

[2] Browser window will open, type [FUZZ] or [CONOCER] in a text area to be used for testing

[3] Once recording is done, close the browser

[4] Tool will start fuzzing requests with prompts

[5] Report will be generated or printed on console

        """,
        epilog="Thank you. Happy GenAI Testing."
    )
    
    subparsers = parser.add_subparsers(dest='subcommand', help='sub-command help')

    # Subparser for scanning webapps
    webapps_parser = subparsers.add_parser('webapps', help='Scan web apps')
    webapps_parser.add_argument("url", type=str, help="Starting URL for crawling.")
    webapps_parser.add_argument("-s", "--session", type=str, help="Path to session file for storing crawl results")
    webapps_parser.add_argument("--skip_crawling", action="store_true", help="Skip crawling, use recorded session to test")
    webapps_parser.add_argument("--skip_testing", action="store_true", help="Skill Testing, possibly just record session")
    webapps_parser.add_argument("--save_session", action="store_true", help="Save Crawling Session for next time")
    webapps_parser.add_argument("--prompt_prefix", type=str, default="", help="Add a prefix to every prompt to make prompts more contextual")
    webapps_parser.add_argument("-m", "--speed", type=int, default=300, help="set time in milliseconds for executions of APIs.")
    webapps_parser.add_argument("-b", "--browser", type=str, help="Browser type to run playwright automation on. Allowed values are Webkit, Firefox and Chromium.")
    # Common Options
    webapps_parser.add_argument("--json", type=str, help="Path to store the report of scanning in json format")
    webapps_parser.add_argument("--markdown", type=str, help="Path to store the report of scanning in markdown format ")
    webapps_parser.add_argument("-n", "--no_of_tests", type=int, default=10, help="No of Tests to run. Default 10")
    webapps_parser.add_argument("-l", "--log_level", type=str, default="WARN", help="Path to session file for storing crawl results")
    webapps_parser.add_argument("--marker", type=str, default="", help=f"FUZZ marker. By Default, the tool will detect any of these markers: {' '.join(FUZZING_MARKERS)}")



    # Subparser for scanning models
    models_parser = subparsers.add_parser('models', help='Scan models')
    models_parser.add_argument("model_path", type=str, help="Path to the model to scan.")

    args = parser.parse_args()

    if args.log_level:
        level = logging.getLevelName(args.log_level)
        logging.basicConfig(level=level)

    report = None
    if args.subcommand == 'webapps':
        try:
            if not args.skip_testing and not args.skip_crawling:
                logging.warning("Both Testing and Crawling can not be specified")
            crawl_options = CrawlerOptions(speed=args.speed, browser_name=args.browser, headless=False)
            scan_options = ScannerOptions(session_file_path=args.session, 
                                          skip_crawling=args.skip_crawling, 
                                          skip_testing=args.skip_testing, 
                                          save_session=args.save_session, 
                                          crawler_options=crawl_options, 
                                          no_of_tests=args.no_of_tests, 
                                          prompt_prefix=args.prompt_prefix)
            scanner = GenAIWebScanner(scan_options)
            report = scanner.scan(args.url)
        except Exception as ex:
            if "playwright install" in str(ex):
                print("[Error]: It seems Playbright is not install on this system. \n Run following command and try again: \n playright install")
            else:
                raise ex
    elif args.subcommand == 'models':
        # Code to scan models
        print("Scanning models...")
        # Placeholder for model scanning functionality
    else:
        parser.print_help()
    
    if report:
        if args.json or args.markdown:
            print("Output will be saved to json or markdown file: ")
            save_json_report(args.json, report)
            save_markdown_report(args.markdown, report)
        else:
            print(report.as_markdown())

if __name__ == "__main__":
    main()
