from processors.docx_processor import DOCXProcessor
from base_processor import DocProcessor


class DocProcessorFactory:
    def __init__(self):
        self.processors = {
            '.docx': DOCXProcessor()
        }

    def __getitem__(self, item) -> DocProcessor:
        return self.processors.get(item)

