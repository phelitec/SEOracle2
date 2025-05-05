"""
SEO Content Generator
==================
Main class for generating and publishing SEO optimized content.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
import datetime

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
        
        # 2. Generate SEO-optimized title and meta description
        self.logger.info(f"Otimizando título e meta description para: {keyword}")
        seo_metadata = self._generate_seo_metadata(keyword, content_plan)
        
        # Brief delay to avoid rate limits
        time.sleep(2)
        
        # 3. Generate article based on plan and SEO metadata
        self.logger.info(f"Gerando artigo otimizado para SEO com base no plano: {seo_metadata.get('seo_title', '')}")
        article = self._generate_article(content_plan, keyword, seo_metadata)
        
        # Brief delay to avoid rate limits
        time.sleep(2)
        
        # 4. Review and improve content
        self.logger.info(f"Revisando artigo: {article.get('seo_title', '')}")
        reviewed_article = self._review_content(article, keyword)
        
        # 5. Publish to WordPress
        category_id = None
        if self.config["content"]["target_category"]:
            category_id = self.wp_client.get_category_id(self.config["content"]["target_category"])
        
        result = self.wp_client.publish_post(
            title=reviewed_article["seo_title"],
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
        current_year = datetime.datetime.now().year
        
        prompt = f"""
        Crie um plano detalhado para um artigo de blog focado na palavra-chave "{keyword}".
        O artigo precisa ser otimizado para SEO e gerar tráfego orgânico.
        
        Forneça:
        1. Sugestões de títulos atraentes, incluindo a palavra-chave principal no início, seguido de um gancho como ano atual ({current_year}), adjetivo ou número
        2. Pelo menos 5 subtópicos relevantes para estruturar o artigo como seções H2, incluindo obrigatoriamente:
           - Um passo a passo sobre o tema
           - Uma lista de recursos/sites/ferramentas recomendados
           - Uma comparação entre opções/métodos
           - Dicas práticas ou erros a evitar
           - Perguntas frequentes (FAQs)
        3. Palavras-chave secundárias relacionadas, incluindo 3 variações de cauda longa
        4. Sugestões para elementos visuais e onde posicioná-los (tabelas, listas com marcadores, imagens)
        5. Ideias para links internos relevantes
        6. Sugestão de URL amigável
        7. Meta descrição otimizada para SEO (até 160 caracteres)
        
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
                "title_suggestions": plan.get("titulos", plan.get("title_suggestions", [])),
                "subtopics": plan.get("subtopicos", plan.get("subtopics", [])),
                "secondary_keywords": plan.get("palavras_chave_secundarias", plan.get("secondary_keywords", [])),
                "visual_elements": plan.get("elementos_visuais", plan.get("visual_elements", [])),
                "internal_links": plan.get("links_internos", plan.get("internal_links", [])),
                "friendly_url": plan.get("url_amigavel", plan.get("friendly_url", "")),
                "meta_description": plan.get("meta_descricao", plan.get("meta_description", ""))
            }
            
            return standardized_plan
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar plano de conteúdo: {str(e)}")
            raise Exception(f"Falha ao gerar plano de conteúdo: {str(e)}")
    
    def _generate_seo_metadata(self, keyword: str, content_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate SEO-optimized title and meta description.
        
        Args:
            keyword: Target keyword
            content_plan: Content plan dictionary
            
        Returns:
            SEO metadata dictionary
        """
        current_year = datetime.datetime.now().year
        
        prompt = f"""
        Com base na palavra-chave "{keyword}" e no plano de conteúdo, otimize os seguintes elementos SEO:

        1. Título SEO: 
           - Inclua a palavra-chave principal no início
           - Adicione um gancho (ano atual {current_year}, adjetivo chamativo ou número)
           - Máximo de 60 caracteres
           - Seja claro e atrativo

        2. Meta description:
           - Limite de 160 caracteres
           - Inclua a palavra-chave principal + verbo de ação
           - Mencione o benefício principal para o leitor
           - Inclua um elemento de urgência ou curiosidade

        3. URL amigável:
           - Formato: /palavra-chave-principal-{current_year}
           - Use apenas letras minúsculas, números e hífens
           - Evite preposições e artigos

        Retorne apenas o JSON com estes três elementos.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.choices[0].message.content
            seo_data = extract_json_from_text(content)
            
            # Ensure consistent keys
            standardized_seo = {
                "seo_title": seo_data.get("titulo_seo", seo_data.get("seo_title", "")),
                "meta_description": seo_data.get("meta_description", ""),
                "friendly_url": seo_data.get("url_amigavel", seo_data.get("friendly_url", ""))
            }
            
            return standardized_seo
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar metadados SEO: {str(e)}")
            
            # Fallback to content plan data if available
            return {
                "seo_title": content_plan.get("title_suggestions", [""])[0] if content_plan.get("title_suggestions") else f"Como {keyword} em {current_year}",
                "meta_description": content_plan.get("meta_description", f"Aprenda sobre {keyword} com este guia completo. Dicas, exemplos e melhores práticas para resultados eficientes."),
                "friendly_url": content_plan.get("friendly_url", keyword.lower().replace(" ", "-"))
            }
    
    def _generate_article(self, content_plan: Dict[str, Any], keyword: str, seo_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an SEO-optimized article based on the content plan.
        
        Args:
            content_plan: Content plan dictionary
            keyword: Target keyword
            seo_metadata: SEO metadata dictionary
            
        Returns:
            Generated article dictionary
            
        Raises:
            Exception: If article generation fails
        """
        # Extract information from the plan and metadata
        title = seo_metadata.get("seo_title", f"Como {keyword}")
        meta_description = seo_metadata.get("meta_description", "")
        subtopics = content_plan.get("subtopics", [])
        secondary_keywords = content_plan.get("secondary_keywords", [])
        visual_elements = content_plan.get("visual_elements", [])
        internal_links = content_plan.get("internal_links", [])
        
        # Convert lists to string format for prompt
        subtopics_text = "\n".join([f"- {s}" for s in subtopics])
        keywords_text = ", ".join(secondary_keywords)
        visuals_text = "\n".join([f"- {v}" for v in visual_elements]) if visual_elements else "Adicione elementos visuais relevantes"
        internal_links_text = "\n".join([f"- {l}" for l in internal_links]) if internal_links else "Sugira links internos relevantes"
        
        # CTA details
        cta_url = self.config["cta"]["url"]
        cta_text = self.config["cta"]["text"]
        
        current_year = datetime.datetime.now().year
        
        prompt = f"""
        Crie um artigo de blog completo e otimizado para SEO com base nas seguintes instruções:
        
        # Informações Básicas
        - Palavra-chave principal: "{keyword}"
        - Título SEO: "{title}"
        - Meta descrição: "{meta_description}"
        - Palavras-chave secundárias: {keywords_text}
        
        # Estrutura Obrigatória
        1. **Introdução (150 palavras):**
           - Contextualize o problema que o leitor enfrenta
           - Mencione a palavra-chave principal e uma variação
           - Apresente o que o leitor vai aprender no artigo
           - Inclua um hook emocional ou estatística impactante
        
        2. **Corpo do Artigo (use os subtópicos como H2):**
           {subtopics_text}
           - Para cada H2, crie pelo menos um H3 relevante
           - Inclua pelo menos uma lista com marcadores (✓ ou ✗) em uma seção
           - Para o subtópico "passo a passo", numere claramente os passos
           - Para o subtópico de "comparação", crie uma tabela comparativa em HTML
        
        3. **Seção FAQ:**
           - Inclua pelo menos 3 perguntas frequentes com respostas diretas
           - Use a palavra-chave principal em pelo menos uma pergunta
        
        4. **Conclusão (100 palavras):**
           - Resuma os principais pontos
           - Reforce o benefício principal
           - Termine com um Call-to-Action natural para o leitor
        
        # Elementos de Otimização
        - Densidade da palavra-chave principal: 1-1.5% (bem distribuída)
        - Insira marcadores de imagem com [IMAGEM: descrição com palavra-chave]
        - Sugestões para elementos visuais:
          {visuals_text}
        - Sugestões para links internos:
          {internal_links_text}
        
        # Call-to-Action Final
        Termine com este CTA personalizado:
        "Quer acelerar seus resultados com {keyword}? Conheça nossa solução premium que entrega resultados comprovados. <a href="{cta_url}" class="cta-button" target="_blank">{cta_text}</a>"
        
        # Diretrizes Técnicas
        - Formate o artigo com HTML semântico (h2, h3, p, ul, ol, table, etc.)
        - Adicione classes CSS para elementos visuais (cta-button, comparison-table, etc.)
        - Inclua marcações schema JSON-LD para FAQ no final do artigo
        - Otimize para leitura em dispositivos móveis

        Forneça apenas o conteúdo HTML do artigo, sem comentários adicionais.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.choices[0].message.content
            
            # Package the article content with SEO metadata
            return {
                "seo_title": title,
                "content": content,
                "meta_description": meta_description,
                "friendly_url": seo_metadata.get("friendly_url", "")
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar artigo: {str(e)}")
            raise Exception(f"Falha ao gerar artigo: {str(e)}")
    
    def _review_content(self, article: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """
        Review and improve the generated article for SEO optimization.
        
        Args:
            article: Generated article dictionary
            keyword: Target keyword
            
        Returns:
            Reviewed article dictionary
            
        Raises:
            Exception: If content review fails
        """
        prompt = f"""
        Revise este artigo de blog para melhorar a otimização SEO e qualidade editorial:
        
        # Informações Básicas
        - Palavra-chave principal: "{keyword}"
        - Título: "{article['seo_title']}"
        
        # Conteúdo Atual
        {article['content']}
        
        # Checklist de Otimização SEO
        Por favor, verifique e corrija:
        
        1. **Estrutura e Formatação**
           - Título H1 contém a palavra-chave principal no início?
           - H2s e H3s estão formatados corretamente e incluem palavras-chave secundárias?
           - Parágrafos são curtos e fáceis de ler (3-4 linhas por parágrafo)?
           - Todos os elementos visuais solicitados foram incluídos?
        
        2. **Densidade e Distribuição de Palavras-chave**
           - A palavra-chave principal aparece na densidade ideal (1-1.5%)?
           - A palavra-chave principal aparece nos primeiros 100 caracteres?
           - Palavras-chave secundárias estão distribuídas naturalmente?
           - Há variações semânticas das palavras-chave?
        
        3. **Elementos Técnicos**
           - As marcações de imagem estão corretas e incluem a palavra-chave?
           - Os links internos sugeridos estão implementados?
           - A tabela comparativa está formatada corretamente?
           - O schema JSON-LD para FAQ está implementado corretamente?
        
        4. **Qualidade do Conteúdo**
           - Há erros gramaticais ou ortográficos?
           - O conteúdo é original e informativo?
           - As seções de passo a passo são claras e acionáveis?
           - O CTA final está bem integrado e persuasivo?
        
        Forneça o conteúdo HTML revisado, preservando toda a formatação e otimização SEO.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.choices[0].message.content
            
            # Try to extract any structured JSON data if present
            json_data = extract_json_from_text(content)
            
            # If we found valid structured data
            if any([key in json_data for key in ["meta_description", "seo_title", "title", "friendly_url"]]):
                return {
                    "seo_title": json_data.get("seo_title", json_data.get("title", article["seo_title"])),
                    "content": json_data.get("content", content),
                    "meta_description": json_data.get("meta_description", article["meta_description"]),
                    "friendly_url": json_data.get("friendly_url", article["friendly_url"])
                }
            else:
                # If no JSON found, return the revised content with original metadata
                return {
                    "seo_title": article["seo_title"],
                    "content": content,
                    "meta_description": article["meta_description"],
                    "friendly_url": article["friendly_url"]
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao revisar artigo: {str(e)}")
            return article  # Return original article if review fails
