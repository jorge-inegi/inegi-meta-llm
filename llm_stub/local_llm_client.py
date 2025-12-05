class LocalLlmClient:
    
    def __init__(self, model_name=None):
        self.model_name = model_name
        self._pipe = None
        
        if model_name:
            try:
                from transformers import pipeline
                self._pipe = pipeline(
                    'text-generation',
                    model=model_name,
                    device_map='auto',
                    trust_remote_code=True
                )
                print(f"Modelo {model_name} cargado correctamente")
            except Exception as e:
                print(f"No se pudo cargar el modelo {model_name}: {e}")
                self._pipe = None
    
    def _build_instruct_prompt(self, user_question: str, context_docs: list[dict]) -> str:
        context_lines = []
        for doc in context_docs[:5]:
            title = doc.get('title', 'Sin título')
            text = doc.get('text', '')
            context_lines.append(f"- Título: {title}")
            context_lines.append(f"  Texto: {text}")
            context_lines.append("")
        
        context_block = "\n".join(context_lines)
        
        prompt = f"""[INSTRUCCIONES]
Eres un asistente técnico que responde preguntas sobre metadatos de encuestas (tablas y columnas).
Usa exclusivamente la información del contexto. Si no hay información suficiente, responde claramente que no puedes responder.

[CONTEXTO]
{context_block}

[PREGUNTA]
{user_question}

[RESPUESTA]
"""
        return prompt
    
    def generate(self, prompt: str, context_docs: list[dict]) -> str:
        if not context_docs:
            return "No encontré información relevante en los metadatos para responder esta pregunta."
        
        if self._pipe:
            try:
                result = self._pipe(
                    prompt,
                    max_new_tokens=300,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    truncation=True,
                    return_full_text=False
                )
                
                generated_text = result[0]['generated_text'].strip()
                
                if '[RESPUESTA]' in generated_text:
                    generated_text = generated_text.split('[RESPUESTA]')[-1].strip()
                
                return generated_text
                
            except Exception as e:
                return f"Error al generar respuesta: {e}"
        
        tables = [doc['title'] for doc in context_docs if doc['id'].startswith('TABLE:')]
        columns = [doc['title'] for doc in context_docs if doc['id'].startswith('COL:')]
        
        parts = []
        if tables:
            parts.append(f"Tablas: {', '.join(tables[:3])}")
        if columns:
            parts.append(f"Columnas: {', '.join([c.split(' en ')[0].replace('Columna ', '') for c in columns[:5]])}")
        
        return "Información encontrada: " + ". ".join(parts) + "."
    
    def generate_with_template(self, user_question: str, context_docs: list[dict]) -> str:
        if not context_docs:
            return "No encontré información relevante en los metadatos para responder esta pregunta."
        
        prompt = self._build_instruct_prompt(user_question, context_docs)
        return self.generate(prompt, context_docs)