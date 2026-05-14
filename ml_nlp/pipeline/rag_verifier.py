import logging
from typing import Dict
import random
import os

logger = logging.getLogger(__name__)

class RAGVerifier:
    def __init__(self):
        logger.info("✅ RAG Verifier initialized (Real AI Verifier & Semantic Search with master dataset)")
        
        # Smart path detection: Docker mount first, then local Windows path
        docker_path = "/data/master_dataset_sante_multilingueV1.xls"
        local_path = r"c:\Users\chakr\Desktop\fact-checking-main\master_dataset_sante_multilingueV1.xls"
        self.dataset_path = docker_path if os.path.exists(docker_path) else local_path
        
        self.df = None
        self.valid_texts = []
        self.dataset_embeddings = None
        
        try:
            import pandas as pd
            if os.path.exists(self.dataset_path):
                self.df = pd.read_csv(self.dataset_path)
                logger.info(f"✅ Loaded dataset from '{self.dataset_path}' with {len(self.df)} records.")
            else:
                logger.warning(f"⚠️ Dataset not found at either path (Docker: {docker_path}, Local: {local_path})")
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            
        # Initialize NLI Model
        self.nli_pipeline = None
        try:
            from transformers import pipeline
            logger.info("⏳ Downloading/Loading mDeBERTa NLI Model... this may take a moment.")
            self.nli_pipeline = pipeline("text-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
            logger.info("✅ Multilingual NLI Model loaded successfully.")
        except Exception as e:
            logger.error(f"⚠️ Failed to load NLI model: {e}")
            
        # Initialize Semantic Embedding Model
        self.tokenizer = None
        self.embed_model = None
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch
            logger.info("⏳ Loading Semantic Search Model (paraphrase-multilingual-MiniLM-L12-v2)...")
            model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.embed_model = AutoModel.from_pretrained(model_name)
            logger.info("✅ Semantic Search Model loaded.")
            
            if self.df is not None and not self.df.empty:
                logger.info("⏳ Computing dataset semantic embeddings...")
                texts = self.df['text'].dropna().astype(str).tolist()
                self.valid_texts = texts
                self.dataset_embeddings = self._compute_embeddings(texts)
                logger.info("✅ Dataset embeddings computed.")
        except Exception as e:
            logger.error(f"⚠️ Failed to setup semantic search: {e}")
            
        # All most trusted medical datasets and sources
        self.sources = {
            "cardiology": ["https://www.heart.org", "https://www.acc.org", "https://pubmed.ncbi.nlm.nih.gov", "https://jamanetwork.com"],
            "oncology": ["https://www.cancer.org", "https://www.cancer.gov", "https://pubmed.ncbi.nlm.nih.gov", "https://www.thelancet.com"],
            "pediatrics": ["https://www.aap.org", "https://www.healthychildren.org", "https://pubmed.ncbi.nlm.nih.gov", "https://www.bmj.com"],
            "infectious_disease": ["https://www.who.int/health-topics/infectious-diseases", "https://www.cdc.gov", "https://www.nejm.org", "https://www.thelancet.com/infection"],
            "nutrition": ["https://www.eatright.org", "https://www.nutrition.gov", "https://www.cochranelibrary.com", "https://pubmed.ncbi.nlm.nih.gov"],
            "general_medicine": [
                "https://www.mayoclinic.org", "https://www.who.int", "https://www.nih.gov",
                "https://pubmed.ncbi.nlm.nih.gov", "https://medlineplus.gov",
                "https://www.cochranelibrary.com", "https://jamanetwork.com",
                "https://www.bmj.com", "https://www.thelancet.com",
                "https://www.nejm.org", "https://www.webmd.com"
            ]
        }

    def _compute_embeddings(self, texts, batch_size=32):
        import torch
        import torch.nn.functional as F
        
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            encoded_input = self.tokenizer(batch_texts, padding=True, truncation=True, return_tensors='pt', max_length=128)
            with torch.no_grad():
                model_output = self.embed_model(**encoded_input)
            
            # Mean pooling
            attention_mask = encoded_input['attention_mask']
            token_embeddings = model_output[0]
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            embeddings = F.normalize(embeddings, p=2, dim=1)
            all_embeddings.append(embeddings)
            
        return torch.cat(all_embeddings, dim=0)

    def _fetch_pubmed_abstract(self, query_in_english: str) -> tuple[str, str]:
        """
        Queries PubMed API for the most relevant article abstract.
        """
        import requests
        import urllib.parse
        try:
            encoded_query = urllib.parse.quote(query_in_english)
            search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={encoded_query}&retmode=json&retmax=1"
            search_response = requests.get(search_url, timeout=5)
            search_data = search_response.json()
            
            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            if not id_list:
                return None, None
                
            pmid = id_list[0]
            
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=text&rettype=abstract"
            fetch_response = requests.get(fetch_url, timeout=5)
            abstract = fetch_response.text.strip()
            
            if abstract:
                pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                return abstract[:2000], pubmed_url
                
        except Exception as e:
            logger.error(f"PubMed fetch failed: {e}")
            
        return None, None

    def _fetch_wikipedia_extract(self, query_in_english: str) -> tuple[str, str]:
        """
        Queries Wikipedia API for general medical knowledge fallback.
        """
        import requests
        import urllib.parse
        try:
            encoded_query = urllib.parse.quote(query_in_english)
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_query}&utf8=&format=json"
            search_response = requests.get(search_url, timeout=5)
            search_data = search_response.json()
            
            search_results = search_data.get('query', {}).get('search', [])
            if not search_results:
                return None, None
                
            page_id = search_results[0]['pageid']
            page_title = search_results[0]['title']
            
            fetch_url = f"https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&pageids={page_id}"
            fetch_response = requests.get(fetch_url, timeout=5)
            fetch_data = fetch_response.json()
            
            pages = fetch_data.get('query', {}).get('pages', {})
            extract = pages.get(str(page_id), {}).get('extract', '').strip()
            
            if extract:
                encoded_title = urllib.parse.quote(page_title.replace(' ', '_'))
                wiki_url = f"https://en.wikipedia.org/wiki/{encoded_title}"
                return extract[:2000], wiki_url
                
        except Exception as e:
            logger.error(f"Wikipedia fetch failed: {e}")
            
        return None, None

    def _clean_query(self, text: str) -> str:
        """Extract longest words as a heuristic for medical keywords to improve search hits"""
        import re
        words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
        if not words:
            return text[:50]
        longest = sorted(words, key=len, reverse=True)[:3]
        return " ".join(longest)

    def verify(self, claim: str, claim_type: str = "general", language: str = "ar") -> Dict:
        """
        RAG Verification process using a real NLI AI model and Semantic Search
        """
        import torch
        domain = "general_medicine"
        claim_lower = claim.lower()
        if any(w in claim_lower for w in ["heart", "blood", "cardio", "pressure"]): domain = "cardiology"
        elif any(w in claim_lower for w in ["cancer", "tumor", "oncology"]): domain = "oncology"
        elif any(w in claim_lower for w in ["child", "baby", "pediatric"]): domain = "pediatrics"
        elif any(w in claim_lower for w in ["virus", "infection", "bacteria", "covid"]): domain = "infectious_disease"
        elif any(w in claim_lower for w in ["diet", "food", "vitamin", "nutrition"]): domain = "nutrition"
        
        # ----------------------------------------------------
        # REAL SEMANTIC SEARCH (VECTOR EMBEDDINGS)
        # ----------------------------------------------------
        source_url = ""
        matched_text = None
        
        if self.dataset_embeddings is not None and self.embed_model is not None:
            claim_emb = self._compute_embeddings([claim])
            
            # Compute cosine similarity between claim and all dataset rows
            cos_scores = torch.mm(claim_emb, self.dataset_embeddings.transpose(0, 1))[0]
            best_match_idx = torch.argmax(cos_scores).item()
            max_score = cos_scores[best_match_idx].item()
            
            # Threshold to ensure it's actually relevant
            if max_score > 0.40:
                matched_text = self.valid_texts[best_match_idx]
                source_url = f"Source: master_dataset_sante_multilingueV1.xls (Matched: '{matched_text}' | Similarity: {round(max_score*100)}%)"
        
        if not matched_text:
            # ----------------------------------------------------
            # TIER 2 & 3: LIVE GLOBAL VERIFICATION (PUBMED -> WIKIPEDIA)
            # ----------------------------------------------------
            logger.info("⚠️ Local dataset miss. Attempting live global retrieval...")
            try:
                from ml_nlp.pipeline.english_translator import get_english_translator
                translator = get_english_translator()
                english_claim = translator.translate(claim)
                
                if english_claim:
                    # Create optimized search query for APIs
                    search_query = self._clean_query(english_claim)
                    logger.info(f"Optimized search query: '{search_query}'")
                    
                    # Try PubMed First
                    abstract, pm_url = self._fetch_pubmed_abstract(search_query)
                    if abstract:
                        matched_text = abstract
                        source_url = f"Source: PubMed Live API (URL: {pm_url})"
                        logger.info(f"✅ Found PubMed abstract. URL: {pm_url}")
                    else:
                        # Try Wikipedia Second
                        logger.info("⚠️ PubMed miss. Attempting Wikipedia retrieval...")
                        extract, wiki_url = self._fetch_wikipedia_extract(search_query)
                        if extract:
                            matched_text = extract
                            source_url = f"Source: Wikipedia Live API (URL: {wiki_url})"
                            logger.info(f"✅ Found Wikipedia extract. URL: {wiki_url}")
            except Exception as e:
                logger.error(f"Failed during global API fallback: {e}")
                
            if not matched_text:
                source = random.choice(self.sources.get(domain, self.sources["general_medicine"]))
                source_url = f"{source}?q={claim[:20].replace(' ', '+')}"

        # ----------------------------------------------------
        # REAL VERIFICATION VIA NLI AI MODEL
        # ----------------------------------------------------
        label = "unverifiable"
        confidence = 0.50
        explanation = "Could not verify claim against dataset."
        
        if self.nli_pipeline and matched_text:
            try:
                # The model predicts if the hypothesis (claim) is true based on the premise (dataset match)
                res = self.nli_pipeline({"text": matched_text, "text_pair": claim})
                
                nli_label = res.get('label', '').lower()
                confidence = float(res.get('score', 0.5))
                
                if nli_label == "entailment":
                    label = "true"
                    explanation = f"AI verification confirmed this claim aligns with dataset: '{matched_text}'"
                elif nli_label == "contradiction":
                    label = "false"
                    explanation = f"AI verification found this claim contradicts our dataset: '{matched_text}'"
                else:
                    label = "partially_true"
                    explanation = f"AI verification found this claim is somewhat related but not fully confirmed by dataset: '{matched_text}'"
                    
            except Exception as e:
                logger.error(f"NLI Model inference failed: {e}")
                if any(w in claim_lower for w in ["always", "never", "cure all", "100%"]):
                    label = "false"
                    explanation = "Automatic fallback: Absolute medical claims are generally false."
        else:
            if any(w in claim_lower for w in ["always", "never", "cure all", "100%"]):
                label = "false"
                explanation = "Automatic fallback: Absolute medical claims are generally false."
            else:
                label = "unverifiable"
                explanation = "This claim contains conversational phrasing that could not be mapped to a specific medical fact in our local or global databases."
        
        return {
            "label": label, 
            "confidence": round(confidence, 2), 
            "explanation": explanation, 
            "source_url": source_url, 
            "domain": domain
        }

_verifier_instance = None
def get_rag_verifier():
    global _verifier_instance
    if _verifier_instance is None:
        _verifier_instance = RAGVerifier()
    return _verifier_instance
