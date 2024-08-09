from transitions import Machine

from chakra.utils.printer import BasePrinter

class ScanWorkflow:
    def __init__(self, printer:BasePrinter):
        """
        Initialize the assessment process.

        :param printer: An instance of a Printer class that handles message output.
        """
        self.printer = printer

        # Define the phases (states)
        states = ['Detection', 'Crawling', 'Planning', 'Scanning', 'Reporting']

        # Initialize the state machine
        self.machine = Machine(model=self, states=states, initial='Detection')

        # Define transitions with a callback to print an info message
        self.machine.add_transition('to_crawling', 'Detection', 'Crawling', before=self.before_transition, after=self.on_transition)
        self.machine.add_transition('to_planning', 'Crawling', 'Planning', before=self.before_transition, after=self.on_transition)
        self.machine.add_transition('to_scanning', 'Planning', 'Scanning', before=self.before_transition, after=self.on_transition)
        self.machine.add_transition('to_reporting', 'Scanning', 'Reporting', before=self.before_transition, after=self.on_transition)
        
        # Transitions for moving back if needed
        self.machine.add_transition('to_detection', 'Crawling', 'Detection', before=self.before_transition, after=self.on_transition)
        self.machine.add_transition('to_crawling', 'Planning', 'Crawling', before=self.before_transition, after=self.on_transition)
        self.machine.add_transition('to_planning', 'Scanning', 'Planning', before=self.before_transition, after=self.on_transition)
        self.machine.add_transition('to_scanning', 'Reporting', 'Scanning', before=self.before_transition, after=self.on_transition)

    def start(self):
        self.printer.heading(f"Started: {self.state}")

    def before_transition(self):
        """
            Callback function before making transition
        """
        self.printer.info(f"Completed: {self.state}")
        

    def on_transition(self):
        """
        Callback function that prints an info message during a transition.
        """
        self.printer.heading(f"Started: {self.state}")

        
    

# # Example Usage
# printer = Printer()
# assessment = AssessmentProcess(printer=printer, verbose=True)

# # Start the assessment process by manually triggering transitions
# assessment.to_crawling()
# assessment.to_planning()
# assessment.to_scanning()
# assessment.to_reporting()

# # Example of a warning message
# printer.warn("This is a warning message.")

# # Example of a critical message
# printer.critical("This is a critical error message.")
