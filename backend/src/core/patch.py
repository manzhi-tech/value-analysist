import os
import logging

logger = logging.getLogger(__name__)

def apply_monkey_patches():
    """
    Apply monkey patches to fix compatibility issues with CrewAI/ChromaDB/LangChain
    when using custom OpenAI-compatible endpoints (like Volcengine/Aliyun).
    """
    logger.info("Applying monkey patches for Embedding compatibility...")
    
    # -------------------------------------------------------------------------
    # Patch 1: ChromaDB OpenAIEmbeddingFunction
    # Issues fixed:
    # 1. Force batch size = 1 (some APIs don't support batching)
    # 2. Force usage of Environment variables for Model/API Key/Base 
    #    (Chroma defaults to 'text-embedding-ada-002' which fails on custom APIs)
    # -------------------------------------------------------------------------
    try:
        from chromadb.utils import embedding_functions
        
        # Guard against double patching
        if getattr(embedding_functions.OpenAIEmbeddingFunction, '_is_patched_by_antigravity', False):
            logger.info("ChromaDB already patched.")
        else:
            # Store original methods
            if not hasattr(embedding_functions.OpenAIEmbeddingFunction, '_original_call'):
                embedding_functions.OpenAIEmbeddingFunction._original_call = embedding_functions.OpenAIEmbeddingFunction.__call__

            if not hasattr(embedding_functions.OpenAIEmbeddingFunction, '_original_init'):
                embedding_functions.OpenAIEmbeddingFunction._original_init = embedding_functions.OpenAIEmbeddingFunction.__init__

            def batched_openai_ef_call(self, input):
                # Force batch size of 1
                all_embeddings = []
                for text in input:
                    # Call original with single item list
                    embeddings = self._original_call(input=[text])
                    all_embeddings.extend(embeddings)
                return all_embeddings

            def patched_openai_ef_init(self, api_key=None, model_name='text-embedding-ada-002', **kwargs):
                import sys
                # Check Environment Variables
                env_model = os.getenv("EMBEDDING_MODEL") or os.getenv("OPENAI_EMBEDDING_MODEL")
                # Specific Embedding Key/Base take precedence over generic OpenAI structure
                env_key = os.getenv("EMBEDDING_API_KEY") or os.getenv("OPENAI_EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY")
                env_base = os.getenv("EMBEDDING_API_BASE") or os.getenv("OPENAI_EMBEDDING_API_BASE") or os.getenv("OPENAI_API_BASE") or os.getenv("OPENAI_BASE_URL")
                
                print(f"DEBUG_PATCH: Init call. Original Model={model_name}, Env Model={env_model}", file=sys.stderr)
                
                # FORCE overrides from Environment if available
                if env_model:
                    model_name = env_model
                    
                if env_key:
                    api_key = env_key
                    
                if env_base:
                    kwargs['api_base'] = env_base

                # Clean up kwargs if they contain conflicting keys that we just set
                if 'model' in kwargs:
                    del kwargs['model']
                
                print(f"DEBUG_PATCH: Final config. Model={model_name}, Base={kwargs.get('api_base')}", file=sys.stderr)
                
                self._original_init(api_key=api_key, model_name=model_name, **kwargs)

            # Apply patches
            embedding_functions.OpenAIEmbeddingFunction.__call__ = batched_openai_ef_call
            embedding_functions.OpenAIEmbeddingFunction.__init__ = patched_openai_ef_init
            embedding_functions.OpenAIEmbeddingFunction._is_patched_by_antigravity = True
            
            logger.info("Successfully patched chromadb.utils.embedding_functions.OpenAIEmbeddingFunction")
            
    except ImportError:
        logger.warning("Could not patch chromadb (module not found)")
    except Exception as e:
        logger.error(f"Error patching chromadb: {e}")

    # -------------------------------------------------------------------------
    # Patch 2: LangChain OpenAIEmbeddings
    # Issues fixed:
    # 1. Force chunk_size = 1
    # 2. Force usage of Environment variables for Model
    # -------------------------------------------------------------------------
    try:
        from langchain_openai import OpenAIEmbeddings
        
        if getattr(OpenAIEmbeddings, '_is_patched_by_antigravity', False):
             logger.info("LangChain OpenAIEmbeddings already patched.")
        else:
            original_init = OpenAIEmbeddings.__init__
            
            def patched_lc_init(self, *args, **kwargs):
                # Force chunk_size (batch size) to 1
                kwargs['chunk_size'] = 1
                
                # FORCE MODEL from Environment if not provided
                env_model = os.getenv("EMBEDDING_MODEL") or os.getenv("OPENAI_EMBEDDING_MODEL")
                if env_model:
                     kwargs['model'] = env_model
                
                # FORCE API KEY from Environment
                env_key = os.getenv("EMBEDDING_API_KEY") or os.getenv("OPENAI_EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY")
                if env_key:
                    # LangChain can take openai_api_key in kwargs
                    kwargs['openai_api_key'] = env_key

                # FORCE API BASE from Environment
                env_base = os.getenv("EMBEDDING_API_BASE") or os.getenv("OPENAI_EMBEDDING_API_BASE") or os.getenv("OPENAI_API_BASE") or os.getenv("OPENAI_BASE_URL")
                if env_base:
                    kwargs['openai_api_base'] = env_base
                     
                original_init(self, *args, **kwargs)
                
            OpenAIEmbeddings.__init__ = patched_lc_init
            OpenAIEmbeddings._is_patched_by_antigravity = True
            logger.info("Successfully patched langchain_openai.OpenAIEmbeddings")
            
    except ImportError:
        logger.warning("Could not patch langchain_openai (module not found)")
    except Exception as e:
        logger.error(f"Error patching langchain_openai: {e}")
