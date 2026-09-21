from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


def redact_pii(text: str):
    results = analyzer.analyze(text=text, language="en")

    if not results:
        return text

    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized_result.text
