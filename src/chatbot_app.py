"""
Interfaz web Gradio para el chatbot RAG
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
from chatbot.chatbot import RAGChatbot


# Inicializar chatbot (se hace una sola vez)
print("Inicializando chatbot RAG...")
chatbot = RAGChatbot(max_history=5)
print("Chatbot listo!\n")


def chat_response(message, history, top_k, temperature, use_rag):
    """
    Función que procesa mensajes y devuelve respuestas

    Args:
        message: Mensaje del usuario
        history: Historial de Gradio (no usado, usamos el interno del chatbot)
        top_k: Número de documentos a recuperar
        temperature: Temperatura para DeepSeek
        use_rag: Si usar RAG o solo conversación

    Returns:
        Respuesta del chatbot
    """
    if not message or not message.strip():
        return "Por favor, escribe un mensaje."

    # Obtener respuesta del chatbot
    result = chatbot.chat(
        user_message=message,
        top_k=int(top_k),
        temperature=float(temperature),
        use_rag=use_rag
    )

    # Formatear respuesta con fuentes si están disponibles
    answer = result["answer"]

    if result.get("relevant_documents") and use_rag:
        answer += "\n\n📚 **Fuentes consultadas:**\n"
        for i, doc in enumerate(result["relevant_documents"], 1):
            answer += f"{i}. {doc['filename']} (similitud: {doc['similarity']:.3f})\n"

    return answer


def clear_conversation():
    """Limpia el historial de conversación"""
    chatbot.clear_history()
    return None


def get_system_stats():
    """Obtiene estadísticas del sistema"""
    stats = chatbot.get_stats()

    stats_text = f"""
📊 **Estadísticas del Sistema**

- Documentos en BD: {stats['total_documents']}
- Base de datos: {stats['database']}
- Modelo embeddings: {stats['embedder_model']}
- Modelo LLM: {stats['llm_model']}
- Historial máximo: {stats['max_history']} mensajes
- Historial actual: {stats['current_history_length']} mensajes
"""
    return stats_text


# Crear la interfaz Gradio
with gr.Blocks(title="RAG Chatbot") as demo:
    gr.Markdown(
        """
        # 🤖 RAG Chatbot - Sistema de Consultas Inteligente

        Chatbot con Retrieval-Augmented Generation (RAG) usando BGE-M3, SQL Server y DeepSeek.
        Mantiene historial de conversación para respuestas contextuales.
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            # Interfaz de chat
            chatbot_interface = gr.Chatbot(
                label="Conversación",
                height=500
            )

            with gr.Row():
                msg = gr.Textbox(
                    label="Tu mensaje",
                    placeholder="Escribe tu pregunta aquí...",
                    scale=4
                )
                submit = gr.Button("Enviar", variant="primary", scale=1)

            with gr.Row():
                clear = gr.Button("🗑️ Limpiar conversación")
                stats_btn = gr.Button("📊 Ver estadísticas")

        with gr.Column(scale=1):
            # Panel de configuración
            gr.Markdown("### ⚙️ Configuración")

            use_rag = gr.Checkbox(
                label="Usar RAG (búsqueda en documentos)",
                value=True,
                info="Si está desactivado, solo usa conversación"
            )

            top_k = gr.Slider(
                minimum=1,
                maximum=10,
                value=3,
                step=1,
                label="Documentos a recuperar (top-k)",
                info="Número de documentos relevantes"
            )

            temperature = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                value=0.7,
                step=0.1,
                label="Temperatura",
                info="0 = más preciso, 1 = más creativo"
            )

            gr.Markdown("---")

            stats_display = gr.Markdown("")

    # Event handlers
    msg.submit(
        chat_response,
        inputs=[msg, chatbot_interface, top_k, temperature, use_rag],
        outputs=chatbot_interface
    ).then(
        lambda: "",
        outputs=msg
    )

    submit.click(
        chat_response,
        inputs=[msg, chatbot_interface, top_k, temperature, use_rag],
        outputs=chatbot_interface
    ).then(
        lambda: "",
        outputs=msg
    )

    clear.click(
        clear_conversation,
        outputs=chatbot_interface
    )

    stats_btn.click(
        get_system_stats,
        outputs=stats_display
    )

    # Ejemplos de preguntas
    gr.Examples(
        examples=[
            "¿Qué información tienes sobre becas?",
            "¿Qué son las menciones honoríficas?",
            "Resume los documentos disponibles",
            "¿Puedes darme más detalles sobre lo anterior?"
        ],
        inputs=msg
    )

    gr.Markdown(
        """
        ---
        💡 **Consejos:**
        - El chatbot mantiene historial de los últimos 5 mensajes
        - Activa RAG para buscar en documentos, desactívalo para solo conversar
        - Ajusta top-k para recuperar más o menos documentos
        - Temperatura baja = respuestas más precisas, alta = más creativas
        """
    )


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Iniciando interfaz web del chatbot RAG")
    print("="*60 + "\n")

    # Lanzar la aplicación
    demo.launch(
        server_name="127.0.0.1",  # Local
        server_port=7860,
        share=True,  # Genera URL pública temporal
        show_error=True
    )
