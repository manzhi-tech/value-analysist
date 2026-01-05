import sys
import os
# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
    import inspect
    
    print("PDFKnowledgeSource init signature:")
    print(inspect.signature(PDFKnowledgeSource.__init__))
    
    # Check if there is a way to set embedder/embedding_function
    print("\nPDFKnowledgeSource attributes/methods:")
    for name, _ in inspect.getmembers(PDFKnowledgeSource):
        if not name.startswith('_'):
            print(name)

except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
