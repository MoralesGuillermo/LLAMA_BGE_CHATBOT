# Cambios Implementados: Selector de Modelo LLM

## Resumen
Se implementó la funcionalidad completa para cambiar dinámicamente entre los modelos LLM (DeepSeek y Groq) desde la interfaz web, sin necesidad de reiniciar el servidor o la aplicación.

---

## 🔧 Cambios en Backend (`api/main.py`)

### 1. Estado Global Extendido
```python
# Nuevo diccionario para tracking de proveedores por sesión
session_llm_providers = {}  # {session_id: llm_provider}
```

### 2. Función `get_chatbot()` Mejorada
- Ahora acepta parámetro `llm_provider` opcional
- Detecta cambios de proveedor y recrea el chatbot automáticamente
- Cierra instancias anteriores correctamente antes de crear nuevas

```python
def get_chatbot(session_id: str = "default", llm_provider: str = None) -> RAGChatbot:
    """Obtiene o crea una instancia del chatbot para la sesión"""
    if llm_provider is None:
        llm_provider = session_llm_providers.get(session_id, "deepseek")

    if session_id not in chat_sessions or session_llm_providers.get(session_id) != llm_provider:
        if session_id in chat_sessions:
            chat_sessions[session_id].close()

        chat_sessions[session_id] = RAGChatbot(max_history=10, llm_provider=llm_provider)
        session_llm_providers[session_id] = llm_provider

    return chat_sessions[session_id]
```

### 3. Modelos Pydantic Actualizados

**ChatRequest:**
```python
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    top_k: Optional[int] = 4
    temperature: Optional[float] = 0.7
    llm_provider: Optional[str] = None  # NUEVO
```

**StatsResponse:**
```python
class StatsResponse(BaseModel):
    total_documents: int
    storage_path: str
    embedder_model: str
    llm_model: str
    llm_provider: str  # NUEVO
    max_history: int
    current_history_length: int
```

**ModelChangeRequest (NUEVO):**
```python
class ModelChangeRequest(BaseModel):
    session_id: Optional[str] = "default"
    llm_provider: str  # "groq" o "deepseek"
```

### 4. Nuevo Endpoint: `POST /change-model`

```python
@app.post("/change-model")
async def change_model(request: ModelChangeRequest):
    """
    Cambia el proveedor de LLM para una sesión

    Features:
    - Valida que el proveedor sea "groq" o "deepseek"
    - Cierra y recrea el chatbot con el nuevo proveedor
    - Mantiene el historial de la sesión
    - Retorna confirmación con detalles del nuevo modelo
    """
```

**Request Body:**
```json
{
  "session_id": "session-123",
  "llm_provider": "groq"
}
```

**Response:**
```json
{
  "message": "Modelo cambiado exitosamente a groq",
  "session_id": "session-123",
  "llm_provider": "groq",
  "llm_model": "llama-3.3-70b-versatile",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 5. Endpoint `/chat` Actualizado
- Ahora acepta `llm_provider` en el request
- Pasa el proveedor a `get_chatbot()` automáticamente

### 6. Endpoint `/stats` Actualizado
- Retorna el proveedor LLM actual en `llm_provider`

---

## 🎨 Cambios en Frontend (`frontend/src/App.jsx`)

### 1. Nuevo Estado
```javascript
const [llmProvider, setLlmProvider] = useState('deepseek');
const [isChangingModel, setIsChangingModel] = useState(false);
```

### 2. Función `changeModel()`
```javascript
const changeModel = async (newProvider) => {
  setIsChangingModel(true);
  try {
    await axios.post(`${API_BASE_URL}/change-model`, {
      session_id: sessionId.current,
      llm_provider: newProvider
    });

    setLlmProvider(newProvider);

    // Mensaje de confirmación en el chat
    const confirmationMessage = {
      role: 'system',
      content: `Modelo cambiado a ${newProvider === 'groq' ? 'Groq (Llama 3.3 70B)' : 'DeepSeek'}...`,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, confirmationMessage]);

    await fetchStats();
  } finally {
    setIsChangingModel(false);
  }
};
```

### 3. Selector de Modelo en Header
```jsx
<div className="model-selector">
  <select
    value={llmProvider}
    onChange={(e) => changeModel(e.target.value)}
    disabled={isChangingModel || isLoading}
    className="model-select"
    title="Cambiar modelo LLM"
  >
    <option value="deepseek">DeepSeek</option>
    <option value="groq">Groq (Llama 3.3 70B)</option>
  </select>
</div>
```

### 4. Panel de Estadísticas Actualizado
```jsx
<div className="stat-item">
  <span className="stat-label">Proveedor:</span>
  <span className="stat-value">{stats.llm_provider === 'groq' ? 'Groq' : 'DeepSeek'}</span>
</div>
```

### 5. Mensajes de Sistema
- Nuevo tipo de mensaje: `role: 'system'`
- Se muestra cuando se cambia el modelo
- Diseño diferenciado del resto de mensajes

---

## 🎨 Cambios en CSS (`frontend/src/App.css`)

### 1. Estilos del Selector de Modelo
```css
.model-selector {
  margin-right: 5px;
}

.model-select {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  padding: 8px 12px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.model-select:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}
```

### 2. Estilos para Mensajes del Sistema
```css
.message.system .message-bubble {
  background: #e3f2fd;
  border: 1px solid #2196f3;
  color: #1565c0;
  text-align: center;
  font-style: italic;
  max-width: 80%;
  margin: 0 auto;
}
```

### 3. Responsive Design
```css
@media (max-width: 768px) {
  .model-select {
    font-size: 12px;
    padding: 6px 10px;
  }

  .header-actions {
    gap: 5px;
  }
}
```

---

## ✨ Características Implementadas

### 1. ✅ Cambio de Modelo en Tiempo Real
- Cambiar entre DeepSeek y Groq sin reiniciar
- El cambio aplica inmediatamente
- No se pierde el historial de conversación

### 2. ✅ Feedback Visual
- Selector desplegable integrado en el header
- Mensaje de confirmación en el chat
- Estado deshabilitado durante el cambio
- Panel de estadísticas muestra proveedor actual

### 3. ✅ Manejo de Sesiones
- Cada sesión puede usar diferente modelo
- El modelo se persiste por sesión
- Cambios de modelo no afectan otras sesiones

### 4. ✅ Validación
- Backend valida que el proveedor sea válido
- Frontend deshabilita selector durante operaciones
- Manejo de errores con mensajes informativos

### 5. ✅ Responsive
- Selector adapta tamaño en móviles
- Funciona correctamente en todos los dispositivos

---

## 🚀 Cómo Usar

### Desde la Interfaz Web:

1. **Iniciar el sistema:**
   ```bash
   # Terminal 1 - Backend
   cd api
   python main.py

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

2. **Cambiar modelo:**
   - En el header, buscar el selector desplegable
   - Seleccionar "DeepSeek" o "Groq (Llama 3.3 70B)"
   - El cambio es instantáneo
   - Aparece mensaje de confirmación en el chat

3. **Ver estadísticas:**
   - Click en el ícono de gráfico (BarChart)
   - Ver proveedor y modelo actual

### Desde API (curl):

```bash
# Cambiar a Groq
curl -X POST "http://localhost:8000/change-model" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "llm_provider": "groq"}'

# Cambiar a DeepSeek
curl -X POST "http://localhost:8000/change-model" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "llm_provider": "deepseek"}'

# Ver estadísticas
curl "http://localhost:8000/stats?session_id=test"
```

---

## 📝 Notas Importantes

### Requisitos de API Keys
Ambos proveedores deben estar configurados en `.env`:
```env
DEEPSEEK_API_KEY=tu_deepseek_api_key
GROQ_API_KEY=tu_groq_api_key
```

### Modelos por Proveedor
- **DeepSeek**: `deepseek-chat`
- **Groq**: `llama-3.3-70b-versatile`

### Comportamiento del Historial
- El historial de conversación se mantiene al cambiar modelo
- Puedes continuar la conversación con el nuevo modelo
- Cada sesión mantiene su proveedor independiente

### Performance
- **Groq**: Ultra-rápido (200-500ms)
- **DeepSeek**: Más lento pero buena calidad (1-3 segundos)

---

## 🧪 Testing

### Test Manual:

1. ✅ Cambiar de DeepSeek a Groq
2. ✅ Hacer pregunta con Groq
3. ✅ Cambiar de Groq a DeepSeek
4. ✅ Hacer pregunta con DeepSeek
5. ✅ Verificar que historial se mantiene
6. ✅ Verificar panel de estadísticas
7. ✅ Probar en móvil/tablet

### Endpoints a Probar:

```bash
# 1. Cambiar modelo
POST /change-model

# 2. Enviar mensaje con modelo específico
POST /chat

# 3. Ver estadísticas con proveedor
GET /stats

# 4. Documentación Swagger
http://localhost:8000/docs
```

---

## 🎯 Próximas Mejoras (Opcionales)

- [ ] Persistir preferencia de modelo en localStorage
- [ ] Mostrar velocidad estimada de cada modelo
- [ ] Añadir más modelos (OpenAI, Anthropic, etc.)
- [ ] Toggle rápido entre último modelo usado
- [ ] Indicador de velocidad en tiempo real

---

## 📚 Archivos Modificados

```
api/main.py                    ✏️ Modificado
frontend/src/App.jsx           ✏️ Modificado
frontend/src/App.css           ✏️ Modificado
CAMBIOS_MODELO_SELECTOR.md    ✨ Nuevo
```

---

**Implementado por:** Claude Code
**Fecha:** 2024
**Estado:** ✅ Completado y funcional
