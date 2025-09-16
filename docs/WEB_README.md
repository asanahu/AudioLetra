# 🌐 Frontend Web - Dictado Inteligente

## 🚀 Inicio Rápido

### 1. **Iniciar el Servidor Web**
```bash
python start_web.py
```

### 2. **Abrir en el Navegador**
Ve a: http://127.0.0.1:5000

## ✨ Características del Frontend

### 🎙️ **Grabación por Botón**
- **Botón grande y claro** para iniciar/detener grabación
- **Timer en tiempo real** mostrando duración de grabación
- **Indicador visual** de estado de grabación
- **Grabación manual** - solo graba cuando presionas el botón

### 🤖 **Opción LLM Integrada**
- **Checkbox para habilitar LLM** en cada grabación
- **Detección automática** de disponibilidad de LLM
- **Mejora automática** del texto transcrito cuando está habilitado

### 📝 **Gestión de Últimos 3 Dictados**
- **Muestra solo los últimos 3 dictados** automáticamente
- **Elimina automáticamente** los más antiguos cuando hay más de 3
- **Acciones rápidas**: copiar al portapapeles y eliminar
- **Timestamps** con fecha y hora de cada dictado

### 🎨 **Interfaz Profesional**
- **Diseño moderno** con gradientes y efectos glassmorphism
- **Responsive** - funciona en móviles y escritorio
- **Animaciones suaves** y feedback visual
- **Notificaciones toast** para acciones del usuario

## 🔧 Configuración

### **Configurar OpenRouter (Opcional)**
1. Edita el archivo `.env`:
   ```env
   LLM_ENABLED=true
   LLM_PROVIDER=openrouter
   OPENAI_API_KEY=tu_api_key_aqui
   ```

2. Reinicia el servidor web

### **Configurar Audio**
- El sistema detecta automáticamente tu micrófono
- Si tienes problemas, verifica los permisos de micrófono en tu navegador

## 📱 Uso del Frontend

### **1. Verificar Estado**
- **Whisper**: Debe mostrar "Disponible"
- **LLM**: Muestra "Disponible" si está configurado correctamente
- **Estado**: Debe mostrar "Listo"

### **2. Grabar Audio**
1. **Opcional**: Marca "Mejorar con LLM" si quieres post-procesado
2. **Presiona** el botón "Iniciar Grabación"
3. **Habla** normalmente en tu micrófono
4. **Presiona** "Detener Grabación" cuando termines

### **3. Ver Resultados**
- **Transcripción actual** aparece inmediatamente
- **Últimos dictados** se actualizan automáticamente
- **Acciones disponibles**: copiar y eliminar

## 🛠️ API Endpoints

El frontend usa estos endpoints:

- `GET /api/status` - Estado del sistema
- `POST /api/start_recording` - Iniciar grabación
- `POST /api/stop_recording` - Detener grabación
- `GET /api/dictations` - Obtener últimos dictados
- `DELETE /api/dictations/<id>` - Eliminar dictado

## 🎯 Ventajas del Frontend Web

### **vs. Línea de Comandos:**
- ✅ **Más fácil de usar** - interfaz visual intuitiva
- ✅ **Grabación manual** - control total sobre cuándo grabar
- ✅ **Gestión automática** de archivos (solo últimos 3)
- ✅ **Acciones rápidas** - copiar y eliminar con un clic
- ✅ **Feedback visual** - timer, indicadores, notificaciones

### **Funcionalidades Únicas:**
- 🎨 **Interfaz profesional** y moderna
- 📱 **Responsive** - funciona en cualquier dispositivo
- 🔄 **Tiempo real** - actualizaciones instantáneas
- 💾 **Gestión inteligente** de almacenamiento
- 🎛️ **Control granular** de opciones LLM

## 🚨 Solución de Problemas

### **Servidor no inicia:**
```bash
# Instalar dependencias faltantes
pip install flask flask-cors

# Verificar que el puerto 5000 esté libre
netstat -an | findstr :5000
```

### **Audio no funciona:**
- Verifica permisos de micrófono en el navegador
- Asegúrate de que el micrófono esté conectado
- Prueba con diferentes navegadores

### **LLM no disponible:**
- Verifica tu API key en el archivo `.env`
- Asegúrate de tener conexión a internet
- Revisa los logs del servidor para errores

## 🌟 Próximas Mejoras

- [ ] **Grabación continua** con VAD automático
- [ ] **Exportación** a diferentes formatos
- [ ] **Historial completo** con búsqueda
- [ ] **Configuración avanzada** desde la interfaz
- [ ] **Temas** personalizables
- [ ] **Atajos de teclado** para acciones rápidas

---

**¡Disfruta del dictado inteligente con una interfaz web profesional!** 🎉
