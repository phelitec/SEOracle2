"""
SEO Content Generator
==================
Main class for generating and publishing SEO content.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI

from .utils import extract_json_from_text, load_keywords, select_keywords, word_count
from .wordpress_api import WordPressClient

class SEOContentGenerator:
    """Generator for SEO optimized content."""
    
    def __init__(self, config: Dict[str, Dict[str, Any]], logger: Optional[logging.Logger] = None):
        """
        Initialize the SEO content generator.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance (optional)
        """
        self.config = config
        self.logger = logger or logging.getLogger("SEOContentGenerator")
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=config["openai"]["api_key"])
        self.model = config["openai"]["model"]
        
        # Initialize WordPress client
        self.wp_client = WordPressClient(
            site_url=config["wordpress"]["site_url"],
            username=config["wordpress"]["username"],
            app_password=config["wordpress"]["app_password"],
            logger=self.logger
        )
        
        # Load keywords
        self.keywords_file = config["keywords"]["file"]
        self.keywords = load_keywords(self.keywords_file, self.logger)
    
    def run(self) -> None:
        """Run the content generation and publishing workflow."""
        self.logger.info("Iniciando processo de geração de conteúdo SEO")
        
        posts_to_create = int(self.config["content"]["posts_per_run"])
        selected_keywords = select_keywords(self.keywords, posts_to_create)
        
        self.logger.info(f"Gerando {posts_to_create} posts com as palavras-chave: {selected_keywords}")
        
        for i, keyword in enumerate(selected_keywords):
            try:
                self.logger.info(f"[{i+1}/{len(selected_keywords)}] Processando palavra-chave: {keyword}")
                
                # Generate and publish content for this keyword
                self._process_keyword(keyword)
                
                # Wait between posts to avoid rate limits
                if i < len(selected_keywords) - 1:
                    wait_time = 30
                    self.logger.info(f"Aguardando {wait_time} segundos antes do próximo post...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                self.logger.error(f"Erro ao processar palavra-chave '{keyword}': {str(e)}")
                
        self.logger.info("Processo de geração de conteúdo concluído")
    
    def _process_keyword(self, keyword: str) -> None:
        """
        Process a single keyword through the content generation workflow.
        
        Args:
            keyword: Keyword to process
            
        Raises:
            Exception: If any step in the process fails
        """
        # 1. Generate content plan
        self.logger.info(f"Gerando plano de conteúdo para: {keyword}")
        content_plan = self._generate_content_plan(keyword)
        
        # Brief delay to avoid rate limits
        time.sleep(2)
        
        # 2. Generate article based on plan
        self.logger.info(f"Gerando artigo com base no plano: {content_plan.get('title', '')}")
        article = self._generate_article(content_plan, keyword)
        
        # Brief delay to avoid rate limits
        time.sleep(2)
        
        # 3. Review and improve content
        self.logger.info(f"Revisando artigo: {article.get('title', '')}")
        reviewed_article = self._review_content(article, keyword)
        
        # 4. Publish to WordPress
        category_id = None
        if self.config["content"]["target_category"]:
            category_id = self.wp_client.get_category_id(self.config["content"]["target_category"])
        
        result = self.wp_client.publish_post(
            title=reviewed_article["title"],
            content=reviewed_article["content"],
            excerpt=reviewed_article["meta_description"],
            category_id=category_id
        )
        
        self.logger.info(f"Artigo publicado com sucesso! ID: {result.get('id', 'desconhecido')}")
    
    def _generate_content_plan(self, keyword: str) -> Dict[str, Any]:
        """
        Generate a content plan for the given keyword.
        
        Args:
            keyword: Target keyword
            
        Returns:
            Content plan dictionary
            
        Raises:
            Exception: If content plan generation fails
        """
        prompt = f"""
        Crie um plano detalhado para um artigo de blog focado na palavra-chave "{keyword}".
        O artigo precisa ser otimizado para SEO e gerar tráfego orgânico.
        
        Forneça:
        1. Um título atraente que inclua a palavra-chave principal
        2. Pelo menos 5 subtópicos relevantes para estruturar o artigo
        3. Palavras-chave secundárias relacionadas para incluir naturalmente
        4. Sugestões de tipos de conteúdo que funcionam bem para este tópico (listas, tutoriais, etc.)
        5. Sugestões de perguntas frequentes que podem ser respondidas
        6. Meta descrição otimizada para SEO (até 160 caracteres)
        
        Apresente os resultados em formato JSON estruturado para processamento automático.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.choices[0].message.content
            plan = extract_json_from_text(content)
            
            # Ensure consistent keys
            standardized_plan = {
                "title": plan.get("titulo", plan.get("title", "")),
                "subtopics": plan.get("subtopicos", plan.get("subtopics", [])),
                "secondary_keywords": plan.get("keywords_secundarias", plan.get("secondary_keywords", [])),
                "content_types": plan.get("tipos_de_conteudo", plan.get("content_types", [])),
                "faqs": plan.get("perguntas_frequentes", plan.get("faqs", [])),
                "meta_description": plan.get("meta_descricao", plan.get("meta_description", ""))
            }
            
            return standardized_plan
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar plano de conteúdo: {str(e)}")
            raise Exception(f"Falha ao gerar plano de conteúdo: {str(e)}")
    
    def _generate_article(self, content_plan: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """
        Generate an article based on the content plan.
        
        Args:
            content_plan: Content plan dictionary
            keyword: Target keyword
            
        Returns:
            Generated article dictionary
            
        Raises:
            Exception: If article generation fails
        """
        # Extract information from the plan
        title = content_plan.get("title", f"Artigo sobre {keyword}")
        subtopics = content_plan.get("subtopics", [])
        keywords = content_plan.get("secondary_keywords", [])
        faqs = content_plan.get("faqs", [])
        
        # Prepare prompt
        subtopics_text = "\n".join([f"- {s}" for s in subtopics])
        keywords_text = ", ".join(keywords)
        faqs_text = ", ".join(faqs)
        
        # CTA details
        cta_url = self.config["cta"]["url"]
        cta_text = self.config["cta"]["text"]
        
        prompt = f"""
        Crie um artigo de blog completo e otimizado para SEO com base nas seguintes informações:
        
        Título: {title}
        
        Estrutura de subtópicos:
        {subtopics_text}
        
        Palavras-chave secundárias a incluir naturalmente: {keywords_text}
        
        Diretrizes:
        1. Escreva um artigo com {self.config["content"]["min_words"]} a {self.config["content"]["max_words"]} palavras
        2. Inclua uma introdução atraente que mencione a palavra-chave principal
        3. Desenvolva cada subtópico com informações valiosas e específicas
        4. Inclua uma seção de perguntas frequentes respondendo às seguintes perguntas: {faqs_text}
        5. Termine com uma conclusão que incentive o engajamento
        6. Use subtítulos H2 e H3 adequadamente
        7. Inclua algumas sugestões de links internos indicados com [LINK INTERNO: tópico sugerido]
        8. Termine com uma conclusão motivacional e inclua um call-to-action (CTA) natural usando este template:
    "Quer acelerar seu crescimento no Instagram? Conheça nossa solução premium para 
    [seguidores/curtidas/views] que [benefício principal] em [tempo de resultado]. 
    <a href="{cta_url}" target="_blank">{cta_text}</a>"

        Forneça apenas o conteúdo do artigo formatado em HTML, sem comentários adicionais.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.choices[0].message.content
            
            return {
                "title": title,
                "content": content,
                "meta_description": content_plan.get("meta_description", "")
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar artigo: {str(e)}")
            raise Exception(f"Falha ao gerar artigo: {str(e)}")
    
    def _review_content(self, article: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """
        Review and improve the generated article.
        
        Args:
            article: Generated article dictionary
            keyword: Target keyword
            
        Returns:
            Reviewed article dictionary
            
        Raises:
            Exception: If content review fails
        """
        prompt = f"""
        Revise este artigo de blog para otimização SEO e qualidade editorial:
        
        Título: {article["title"]}
        
        Conteúdo:
        {article["content"]}
        
        Palavra-chave principal: {keyword}
        
        Por favor, revise e corrija:
        1. Qualquer erro gramatical ou ortográfico
        2. Melhore a densidade da palavra-chave (deve aparecer naturalmente, sem exagero)
        3. Verifique se os subtítulos usam as tags H2 e H3 corretamente
        4. Certifique-se de que o conteúdo está completo e coerente
        5. Melhore a meta descrição se necessário
        6. Sugira algumas melhorias para links internos
        
        Forneça o conteúdo revisado em HTML e uma meta descrição atualizada em formato JSON.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.choices[0].message.content
            
            # Try to extract JSON with meta description
            json_data = extract_json_from_text(content)
            
            # Extract HTML content (anything that's not JSON)
            html_content = content
            
            # Check if we found valid JSON
            if "meta_description" in json_data:
                # Remove JSON parts from the content
                import re
                html_content = re.sub(r'```json\s*[\s\S]*?\s*```|{[\s\S]*}', '', content).strip()
                
                return {
                    "title": article["title"],
                    "content": html_content or article["content"],  # Fallback to original if extraction failed
                    "meta_description": json_data.get("meta_description", article["meta_description"])
                }
            else:
                # If no JSON found, assume it's just the HTML content
                return {
                    "title": article["title"],
                    "content": content,
                    "meta_description": article["meta_description"]
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao revisar artigo: {str(e)}")
            return article  # Return original article if review fails