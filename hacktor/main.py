import os
import argparse
import logging
from hacktor.scanner import DetoxioGeneratorFilterBuilder
from hacktor.webapp.scanner import GenAIWebScanner, CrawlerOptions, ScannerOptions, FUZZING_MARKERS

from hacktor.utils.printer import Printer
from hacktor.workflow.scan import ScanWorkflow


def setup_logging(args):
    log_level = getattr(args, 'log_level', 'WARN').upper()
    level = logging.getLevelName(log_level)
    logging.basicConfig(level=level)

def check_prerequisites(args):
    if args.subcommand == "webapps" and not os.getenv("DETOXIO_API_KEY") and not args.skip_testing:
        logging.warn("""DETOXIO_API_KEY is missing. Set it as Env variable as follows:
            export DETOXIO_API_KEY=****
            
            Check Detoxio API docs for more details: https://docs.detoxio.ai/api/authentication
        """)
        return False
    
    return True


def _create_prompt_filter(args):
    filterb = DetoxioGeneratorFilterBuilder()
    filterb = filterb.threat_class(args.threat_class).threat_category(args.threat_category)
    filter = filterb.industry(args.industry).deceptiveness(args.deceptiveness).build_filter()
    return filter

def main():
    parser = argparse.ArgumentParser(
        description="""
Human Assisted Testing of GenAI Apps and Models: 

[1] python hacktor/main.py webapps <<GenAI APP URL>>

[2] Browser window will open, type [FUZZ] or [HACKTOR] in a text area to be used for testing

[3] Once recording is done, close the browser

[4] Tool will start fuzzing requests with prompts

[5] Report will be generated or printed on console

        """,
        epilog="Thank you. Happy GenAI Testing."
    )
    
    industries = DetoxioGeneratorFilterBuilder.get_industries()
    threat_classes = DetoxioGeneratorFilterBuilder.get_threat_classes()
    threat_cats =  DetoxioGeneratorFilterBuilder.get_threat_categories()
    
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
    webapps_parser.add_argument("-l", "--log_level", type=str, default="WARN", help="Log Levels - DEBUG, INFO, WARN, ERROR. Default: INFO")
    webapps_parser.add_argument("--marker", type=str, default="", help=f"FUZZ marker. By Default, the tool will detect any of these markers: {' '.join(FUZZING_MARKERS)}")

    webapps_parser.add_argument("--industry", type=str, choices=industries, help=f"Filter Prompts related to the industry.")
    webapps_parser.add_argument("--threat-class", type=str,  choices=threat_classes, help=f"Filter Prompts related to the threat classes.")
    webapps_parser.add_argument("--threat-category", type=str,  choices=threat_cats, help=f"filter prompts related to the threat categories.")
    webapps_parser.add_argument("--deceptiveness", type=str,  choices=["LOW", "MEDIUM", "HIGH"], help="How desceptive the promopts are?")

    # Subparser for scanning models
    # models_parser = subparsers.add_parser('models', help='Scan models')
    # models_parser.add_argument("model_path", type=str, help="Path to the model to scan.")

    # Subparser for scanning Burp Resquest files - Mobile Apps
    mobileapps_parser = subparsers.add_parser('mobileapp', help='Scan burp request from Mobile App.')
    mobileapps_parser.add_argument("url", type=str, help="Starting URL for crawling.")
    mobileapps_parser.add_argument("--prompt_parameter", type=str, default="", help="Parameter which holds the input prompt.")
    mobileapps_parser.add_argument("--prompt_prefix", type=str, default="", help="Add a prefix to every prompt to make prompts more contextual.")
    mobileapps_parser.add_argument("-r", "--request", type=str, help="Path to input burp request file.")
    mobileapps_parser.add_argument("--response_param", type=str, help="Parameter which holds the GenAI response.")
    mobileapps_parser.add_argument("--marker", type=str, default="", help=f"FUZZ marker. By Default, the tool will detect any of these markers: {' '.join(FUZZING_MARKERS)}")

    mobileapps_parser.add_argument("--industry", type=str, choices=industries, help=f"Filter Prompts related to the industry.")
    mobileapps_parser.add_argument("--threat-class", type=str, choices=threat_classes, help=f"Filter Prompts related to the threat classes.")
    mobileapps_parser.add_argument("--threat-category", type=str, choices=threat_cats, help=f"filter prompts related to the threat categories.")
    mobileapps_parser.add_argument("--deceptiveness", type=str, choices=["LOW", "MEDIUM", "HIGH"], help="How desceptive the promopts are?")
    # Common Options
    mobileapps_parser.add_argument("--json", type=str, help="Path to store the report of scanning in json format")
    mobileapps_parser.add_argument("--markdown", type=str, help="Path to store the report of scanning in markdown format ")
    mobileapps_parser.add_argument("-n", "--no_of_tests", type=int, default=10, help="No of Tests to run. Default 10")
    mobileapps_parser.add_argument("-l", "--log_level", type=str, default="WARN", help="Log Levels - DEBUG, INFO, WARN, ERROR. Default: INFO")


    # Subparser for Gradio Rest Endpoints
    gradio_parser = subparsers.add_parser('gradio-rest-apis', help='Scan Gradio Rest APIs')
    gradio_parser.add_argument("url", type=str, help="Starting URL for crawling. Ex: detoxiodev/Pokebot or https://huggingface.co/spaces/detoxiodev/Pokebot")
    gradio_parser.add_argument("-s", "--session", type=str, help="Path to session file for storing crawl results")
    gradio_parser.add_argument("--prompt_prefix", type=str, default="", help="Add a prefix to every prompt to make prompts more contextual")
    gradio_parser.add_argument("--api-name", type=str, default="", help="API name to test. By Default, predict the API.")
    
    # Common Options
    gradio_parser.add_argument("--json", type=str, help="Path to store the report of scanning in json format")
    gradio_parser.add_argument("--markdown", type=str, help="Path to store the report of scanning in markdown format ")
    gradio_parser.add_argument("-n", "--no_of_tests", type=int, default=10, help="No of Tests to run. Default 10")
    gradio_parser.add_argument("-l", "--log_level", type=str, default="WARN", help="Log Levels - DEBUG, INFO, WARN, ERROR. Default: INFO")

    gradio_parser.add_argument("--industry", type=str, choices=industries, help=f"Filter Prompts related to the industry.")
    gradio_parser.add_argument("--threat-class", type=str, choices=threat_classes, help=f"Filter Prompts related to the threat classes.")
    gradio_parser.add_argument("--threat-category", type=str, choices=threat_cats, help=f"filter prompts related to the threat categories.")
    gradio_parser.add_argument("--deceptiveness", type=str, choices=["LOW", "MEDIUM", "HIGH"], help="How desceptive the promopts are?")

    args = parser.parse_args()

    setup_logging(args)
    # Check if the program should run
    check_prerequisites(args)

    printer = Printer(False, True)
    scan_workflow = ScanWorkflow(printer)

    report = None
    if args.subcommand == 'webapps':
        try:
            if args.skip_testing and args.skip_crawling:
                logging.warning("Both Skip Testing and Crawling should not be specified. Doing Nothing")
                return
            crawl_options = CrawlerOptions(speed=args.speed, browser_name=args.browser, headless=False)
            prompt_filter_options = _create_prompt_filter(args)
            scan_options = ScannerOptions(session_file_path=args.session, 
                                          skip_crawling=args.skip_crawling, 
                                          skip_testing=args.skip_testing, 
                                          save_session=args.save_session, 
                                          crawler_options=crawl_options, 
                                          no_of_tests=args.no_of_tests, 
                                          prompt_prefix=args.prompt_prefix,
                                          prompt_filter=prompt_filter_options)
            scanner = GenAIWebScanner(scan_options, scan_workflow=scan_workflow)
            report = scanner.scan(args.url)
        except Exception as ex:
            if "playwright install" in str(ex):
                print("[Error]: It seems Playright is not install on this system. \n Run following command and try again: \n playright install")
            else:
                raise ex
    elif args.subcommand == 'gradio-rest-apis':
        # Code to scan models
        # print("Scanning models...")
        # Placeholder for model scanning functionality
        pass
        
    elif args.subcommand == 'mobileapp':
        input_markers = None
        if args.marker:
            input_markers = args.marker.split()
        try:
            prompt_filter_options = _create_prompt_filter(args)
            scan_options = ScannerOptions(session_file_path=args.request, 
                                        skip_crawling=True, 
                                        skip_testing=False, 
                                        save_session=False, 
                                        crawler_options=None, 
                                        no_of_tests=args.no_of_tests, 
                                        prompt_prefix=args.prompt_prefix,
                                        output_field=args.response_param,
                                        prompt_param=args.prompt_parameter or input_markers,
                                        prompt_filter=prompt_filter_options)
            scanner = GenAIWebScanner(scan_options)
            report = scanner.scan(args.url, scanType="mobileapp")
        except Exception as ex:
            raise ex
    else:
        parser.print_help()
    
    if report:
        if args.json or args.markdown:
            #print(f"Output will be saved to json file: {args.json}\n" if args.json else f"Output will be saved to markdown file: {args.markdown}\n" if args.markdown else "No output file specified.")
            print(f"Output will be saved to json file: {args.json}" + (f" and markdown file: {args.markdown}" if args.markdown is not None else "") if args.json is not None else f"Output will be saved to markdown file: {args.markdown}" if args.markdown is not None else "No output file specified.")
            report.save_report(args.json, args.markdown)
        else:
            print(report.as_markdown())

if __name__ == "__main__":
    main()
