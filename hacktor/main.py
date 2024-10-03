import os
import argparse
import logging
import tempfile
from urllib.parse import urlunparse
from hacktor.dtx.scanner import DetoxioGeneratorFilterBuilder
from hacktor.workflow.scanner import (
    GenAIWebScanner, LLMScanner, CrawlerOptions, ScannerOptions, FUZZING_MARKERS, LLMScannerOptions
)
from hacktor.utils.printer import Printer
from hacktor.workflow.phases import ScanWorkflow
from hacktor.models.wrapper import Registry

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

MODULES_LINEAGE_MAP = {
    "OWASP-LLM-APP":"DETOXIO.ATTACKIO",
    "LLM-RISKS": "DETOXIO",
    "JAILBREAK-BENCH": "DETOXIO.JAILBREAKBENCH"
}

def _create_prompt_filter(args):
    filterb = DetoxioGeneratorFilterBuilder()
    filterb = filterb.threat_class(args.threat_class).threat_category(args.threat_category)
    attack_module = MODULES_LINEAGE_MAP.get(args.attack_module, "")
    filterb = filterb.lineage(attack_module)
    filter = filterb.industry(args.industry).deceptiveness(args.deceptiveness).build_filter()
    return filter

def create_parser():
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
    
    common_options = argparse.ArgumentParser(add_help=False)
    common_options.add_argument("--json", type=str, help="Path to store the report of scanning in json format")
    common_options.add_argument("--markdown", type=str, help="Path to store the report of scanning in markdown format")
    common_options.add_argument("-n", "--no_of_tests", type=int, default=10, help="No of Tests to run. Default 10")
    common_options.add_argument("-l", "--log_level", type=str, default="WARN", help="Log Levels - DEBUG, INFO, WARN, ERROR. Default: WARN")
    common_options.add_argument("-v", "--verbose", action="store_true", help="Show Verbose Output")
    common_options.add_argument("--industry", type=str, choices=industries, help=f"Filter Prompts related to the industry.")
    common_options.add_argument("--threat-class", type=str, choices=threat_classes, help=f"Filter Prompts related to the threat classes.")
    common_options.add_argument("--threat-category", type=str, choices=threat_cats, help=f"Filter Prompts related to the threat categories.")
    common_options.add_argument("--deceptiveness", type=str, choices=["LOW", "MEDIUM", "HIGH"], help="How deceptive the prompts are?")
    common_options.add_argument("--attack_module", type=str, choices=MODULES_LINEAGE_MAP.keys(), help="Activate specific attack modules")
    common_options.add_argument("--max_crawling_depth", type=int, default=4,  help="Depth of crawling")
    common_options.add_argument("--max_crawling_steps", type=int, default=10,  help="Number of GenAI States to discover")
    common_options.add_argument("--initial_crawling_prompt", type=str, default="Hello",  help="Initial Crawling Prompt to start conversation")


    subparsers = parser.add_subparsers(dest='subcommand', help='sub-command help')

    # Subparser for scanning webapps
    webapps_parser = subparsers.add_parser('webapps', parents=[common_options], help='Scan web apps')
    webapps_parser.add_argument("url", type=str, help="Starting URL for crawling.")
    webapps_parser.add_argument("-s", "--session", type=str, help="Path to session file for storing crawl results")
    webapps_parser.add_argument("--skip_crawling", action="store_true", help="Skip crawling, use recorded session to test")
    webapps_parser.add_argument("--skip_testing", action="store_true", help="Skip Testing, possibly just record session")

    webapps_parser.add_argument("--save_session", action="store_true", help="Save Crawling Session for next time")
    webapps_parser.add_argument("--use_ai", action="store_true", help="Use AI to perform parsing and crawling, if applicable")
    webapps_parser.add_argument("--prompt_prefix", type=str, default="", help="Add a prefix to every prompt to make prompts more contextual")
    webapps_parser.add_argument("-m", "--speed", type=int, default=300, help="Set time in milliseconds for executions of APIs.")
    webapps_parser.add_argument("-b", "--browser", type=str, help="Browser type to run playwright automation on. Allowed values are Webkit, Firefox, and Chromium.")
    webapps_parser.add_argument("--marker", type=str, default="", help=f"FUZZ marker. By Default, the tool will detect any of these markers: {' '.join(FUZZING_MARKERS)}")


    # Subparser for scanning webapps
    llm_parser = subparsers.add_parser('llm', parents=[common_options], help='Scan web apps')
    llm_parser.add_argument("registry", type=str, choices=Registry.list_options(), help="Specify LLM Registry")
    llm_parser.add_argument("uri", type=str, help="Model ID or URL")
    llm_parser.add_argument("--use_ai", action="store_true", help="Use AI to perform parsing and crawling, if applicable")
    llm_parser.add_argument("--prompt_prefix", type=str, default="", help="Add a prefix to every prompt to make prompts more contextual")


    # Subparser for scanning models
    burp_parser = subparsers.add_parser('burp', parents=[common_options], help='Scan burp request from Mobile App.')
    burp_parser.add_argument("url", type=str, help="Starting URL for crawling.")
    burp_parser.add_argument("--prompt_parameter", type=str, default="", help="Parameter which holds the input prompt.")
    burp_parser.add_argument("--prompt_prefix", type=str, default="", help="Add a prefix to every prompt to make prompts more contextual.")
    burp_parser.add_argument("-r", "--request", type=str, help="Path to input burp request file.")
    burp_parser.add_argument("--response_param", type=str, help="Parameter which holds the GenAI response.")
    burp_parser.add_argument("--marker", type=str, default="", help=f"FUZZ marker. By Default, the tool will detect any of these markers: {' '.join(FUZZING_MARKERS)}")
    burp_parser.add_argument("--use_ai", action="store_true", help="Use AI to perform parsing and crawling, if applicable")
    
    return parser

def handle_webapps(args, scan_workflow):
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
                                  max_crawling_depth=args.max_crawling_depth,
                                  max_crawling_steps=args.max_crawling_steps,
                                  initial_crawling_prompts=[args.initial_crawling_prompt],
                                  prompt_filter=prompt_filter_options)
    scanner = GenAIWebScanner(scan_options, scan_workflow=scan_workflow)
    return scanner.scan(args.url, use_ai=args.use_ai)

def handle_llm(args, scan_workflow):
    registry = Registry(args.registry)
    import importlib
    # Check if torch is installed, then import HFModelFactory
    torch_spec = importlib.util.find_spec("torch")
    if torch_spec is None and registry == Registry.HF:
        raise ImportError("Torch is not installed. Please install it to use Hugging Face models.")
        
        
    prompt_filter_options = _create_prompt_filter(args)
    scan_options = LLMScannerOptions(no_of_tests=args.no_of_tests, 
                                  prompt_prefix=args.prompt_prefix,
                                  max_crawling_depth=args.max_crawling_depth,
                                  max_crawling_steps=args.max_crawling_steps,
                                  initial_crawling_prompts=[args.initial_crawling_prompt],
                                  prompt_filter=prompt_filter_options)
    scanner = LLMScanner(scan_options, scan_workflow=scan_workflow)
    
    return scanner.scan(registry=registry, url=args.uri, use_ai=args.use_ai)


def handle_burp(args, scan_workflow):
    input_markers = None
    if args.marker:
        input_markers = args.marker.split()

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
                                  max_crawling_depth=args.max_crawling_depth,
                                  max_crawling_steps=args.max_crawling_steps,
                                  initial_crawling_prompts=[args.initial_crawling_prompt],
                                  prompt_filter=prompt_filter_options)
    scanner = GenAIWebScanner(scan_options, scan_workflow=scan_workflow)
    return scanner.scan(args.url, scanType="burp", use_ai=args.use_ai)

def _create_url(host, port, path):
    # Determine the scheme based on the port
    scheme = "https" if port == 443 else "http"
    netloc = f"{host}:{port}"

    # Create the URL components
    params = ""
    query = ""
    fragment = ""

    # Build the URL
    url = urlunparse((scheme, netloc, path, params, query, fragment))
    return str(url)



def main():
    parser = create_parser()
    args = parser.parse_args()

    # print("Using AI ", args.use_ai)

    dtx_api_host = os.getenv('DETOXIO_API_HOST', "api.detoxio.ai") 
    dtx_api_port = os.getenv('DETOXIO_API_PORT', 443) 

    open_api_key = os.getenv('OPENAI_API_KEY')
    if args.use_ai and not open_api_key:
        openai_base_url = _create_url(dtx_api_host, dtx_api_port, "dtx.services.llms.v1.LlmPlatformProxyService/openai/v1/")
        os.environ['OPENAI_BASE_URL'] = openai_base_url
        os.environ['OPENAI_API_KEY'] = os.getenv('DETOXIO_API_KEY', "")
        # print(openai_base_url)
        

    setup_logging(args)
    check_prerequisites(args)
    printer = Printer(False, verbose=args.verbose)
    scan_workflow = ScanWorkflow(printer)

    report = None
    
    if "session" in args and not args.session:
        outtmp = tempfile.NamedTemporaryFile(prefix="har_file_path", 
                                                        suffix=".har")
        args.session = outtmp.name

    if args.subcommand == 'webapps':
        report = handle_webapps(args, scan_workflow)
    elif args.subcommand == 'burp':
        report = handle_burp(args, scan_workflow)
    elif args.subcommand == "llm":
        report = handle_llm(args, scan_workflow)
    else:
        parser.print_help()
    
    if report:
        if args.json or args.markdown:
            print(f"Output will be saved to json file: {args.json}" + (f" and markdown file: {args.markdown}" if args.markdown is not None else "") if args.json is not None else f"Output will be saved to markdown file: {args.markdown}" if args.markdown is not None else "No output file specified.")
            report.save_report(args.json, args.markdown)
        else:
            print(report.as_markdown())

if __name__ == "__main__":
    main()
    
    