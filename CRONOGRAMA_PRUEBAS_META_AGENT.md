# 📋 Cronograma de Pruebas - Sistema Meta-Agente AXON Agency

## 🎯 Objetivo
Validar la funcionalidad completa del sistema Meta-Agente, incluyendo creación, gestión, replicación y eliminación de agentes especializados con sistema de gobernanza multi-tenant.

---

## ✅ Fase 1: Pruebas de Creación de Agentes (10 min)

### Test 1.1: Crear Agente de Seguridad
**Objetivo:** Verificar creación de agente SECURITY
- [ ] Ir a `/agent/meta`
- [ ] Click en "Crear Agente"
- [ ] Nombre: "Agente de Seguridad Alpha"
- [ ] Rol: Security - Seguridad y Vulnerabilidades
- [ ] Click "Crear Agente"
- [ ] **Resultado esperado:** Notificación toast verde "Agente creado exitosamente", agente aparece en la lista

### Test 1.2: Crear Agente de Performance
**Objetivo:** Verificar creación de agente PERFORMANCE
- [ ] Click en "Crear Agente"
- [ ] Nombre: "Agente de Performance Beta"
- [ ] Rol: Performance - Optimización de Código
- [ ] Click "Crear Agente"
- [ ] **Resultado esperado:** Agente creado con badge amarillo, tasks_completed: 0, success_rate: 0%

### Test 1.3: Crear Agente de QA
**Objetivo:** Verificar creación de agente QA
- [ ] Click en "Crear Agente"
- [ ] Nombre: "Agente de QA Gamma"
- [ ] Rol: QA - Testing y Quality Assurance
- [ ] Click "Crear Agente"
- [ ] **Resultado esperado:** Agente creado con badge rojo

### Test 1.4: Validación de Nombre Vacío
**Objetivo:** Verificar validación de input
- [ ] Click en "Crear Agente"
- [ ] Dejar nombre vacío
- [ ] Click "Crear Agente"
- [ ] **Resultado esperado:** Toast de error "Por favor ingresa un nombre para el agente"

### Test 1.5: Verificar Límite de Gobernanza
**Objetivo:** Validar límite de 10 agentes por tenant
- [ ] Crear 7 agentes más (roles: BUILDER, PLANNER, TESTER, y duplicados)
- [ ] Intentar crear el agente #11
- [ ] **Resultado esperado:** Toast de error "Límite de agentes alcanzado para tenant"

**Métricas a verificar:**
- Total Agentes: incrementa con cada creación
- Agentes Activos: todos en estado IDLE inicialmente
- Tareas Completadas: 0 en todos
- Tasa de Éxito: NaN% (sin tareas aún)

---

## ✅ Fase 2: Pruebas de Replicación (15 min)

### Test 2.1: Replicar Agente de Seguridad
**Objetivo:** Verificar funcionalidad de replicación básica
- [ ] Ubicar "Agente de Seguridad Alpha"
- [ ] Click en botón "Replicar" (ícono púrpura)
- [ ] **Resultado esperado:** Modal de confirmación aparece (NO alert nativo)
- [ ] Click "Confirmar"
- [ ] **Resultado esperado:** Toast "Agente replicado exitosamente", nuevo agente con sufijo "_replica_1"

### Test 2.2: Verificar Herencia de Configuración
**Objetivo:** Validar que la réplica hereda capabilities
- [ ] Comparar agent_id del original vs réplica
- [ ] Verificar que ambos tienen rol: "security"
- [ ] Verificar que capabilities.specializations son idénticas
- [ ] **Resultado esperado:** Réplica tiene mismas capacidades pero nuevo agent_id

### Test 2.3: Múltiples Replicaciones
**Objetivo:** Verificar límite de 3 replicaciones/día
- [ ] Replicar el mismo agente 2 veces más
- [ ] Intentar 4ta replicación
- [ ] **Resultado esperado:** Toast de error "Límite de replicaciones diarias alcanzado (3/3)"

### Test 2.4: Replicar Diferentes Roles
**Objetivo:** Verificar replicación funciona con todos los roles
- [ ] Replicar agente PERFORMANCE
- [ ] Replicar agente QA
- [ ] Replicar agente BUILDER
- [ ] **Resultado esperado:** 3 nuevas réplicas con sufijos "_replica_1"

**Métricas a verificar:**
- Total Agentes: incrementa +1 por cada replicación exitosa
- Agentes Activos: todas las réplicas en estado IDLE
- Límite de gobernanza: contador de replicaciones incrementa

---

## ✅ Fase 3: Pruebas de Eliminación (10 min)

### Test 3.1: Eliminar Agente Individual
**Objetivo:** Verificar eliminación básica
- [ ] Click en botón rojo "X" de cualquier agente
- [ ] **Resultado esperado:** Modal de confirmación (NO confirm nativo) "¿Eliminar este agente especializado?"
- [ ] Click "Cancelar"
- [ ] **Resultado esperado:** Agente NO eliminado, modal se cierra
- [ ] Click "X" nuevamente, click "Confirmar"
- [ ] **Resultado esperado:** Toast verde "Agente eliminado exitosamente", agente desaparece

### Test 3.2: Verificar Actualización de Métricas
**Objetivo:** Validar que las estadísticas se actualizan
- [ ] Observar "Total Agentes" antes de eliminar
- [ ] Eliminar un agente
- [ ] Verificar "Total Agentes" disminuye en 1
- [ ] **Resultado esperado:** Métricas actualizadas en tiempo real

### Test 3.3: Eliminar Réplica vs Original
**Objetivo:** Verificar que se pueden eliminar réplicas sin afectar original
- [ ] Eliminar una réplica
- [ ] Verificar que el agente original sigue existiendo
- [ ] **Resultado esperado:** Solo la réplica se elimina

### Test 3.4: Eliminar Todos los Agentes
**Objetivo:** Verificar estado vacío
- [ ] Eliminar todos los agentes uno por uno
- [ ] **Resultado esperado:** Mensaje "No hay agentes especializados todavía" con ícono
- [ ] Total Agentes: 0
- [ ] Agentes Activos: 0

---

## ✅ Fase 4: Pruebas de UI/UX (10 min)

### Test 4.1: Sistema de Notificaciones Toast
**Objetivo:** Verificar que los toasts NO bloquean capturas de pantalla
- [ ] Crear un agente (toast de éxito aparece)
- [ ] Mientras el toast está visible, intentar captura de pantalla
- [ ] **Resultado esperado:** Captura de pantalla exitosa, toast visible pero no bloquea
- [ ] Hacer clic en "X" del toast para cerrar manualmente
- [ ] **Resultado esperado:** Toast desaparece con animación suave

### Test 4.2: Auto-cierre de Toasts
**Objetivo:** Verificar auto-desaparición
- [ ] Crear un agente
- [ ] NO cerrar el toast manualmente
- [ ] Esperar 4 segundos
- [ ] **Resultado esperado:** Toast desaparece automáticamente con fade-out

### Test 4.3: Múltiples Toasts Simultáneos
**Objetivo:** Verificar gestión de múltiples notificaciones
- [ ] Crear 3 agentes rápidamente (menos de 4 seg entre cada uno)
- [ ] **Resultado esperado:** 3 toasts apilados verticalmente en esquina superior derecha
- [ ] Verificar que todos se auto-cierran en orden

### Test 4.4: Modal de Confirmación No-Bloqueante
**Objetivo:** Verificar que modales permiten interacción con fondo
- [ ] Click "X" para eliminar agente
- [ ] Mientras modal está abierto, intentar captura de pantalla
- [ ] **Resultado esperado:** Captura exitosa, modal visible pero no bloquea sistema

### Test 4.5: Badges de Rol y Color
**Objetivo:** Verificar iconografía correcta
- [ ] Verificar que cada rol tiene su icono correcto:
  - SECURITY: 🛡️ Shield (azul)
  - PERFORMANCE: ⚡ Zap (amarillo)
  - QA: 🐛 Bug (rojo)
  - BUILDER: 🔧 Wrench (púrpura)
  - PLANNER: 🧠 Brain (cyan)
  - TESTER: 🔬 Microscope (verde)
- [ ] **Resultado esperado:** Todos los iconos y colores correctos

### Test 4.6: Auto-refresh
**Objetivo:** Verificar actualización automática cada 5 segundos
- [ ] Observar la lista de agentes
- [ ] Esperar 5 segundos sin interactuar
- [ ] **Resultado esperado:** Request GET a /api/agent/meta/agents visible en logs
- [ ] Métricas se actualizan automáticamente

---

## ✅ Fase 5: Pruebas de Backend/API (15 min)

### Test 5.1: Validación de Autenticación (DEV_MODE)
**Objetivo:** Verificar que DEV_MODE permite requests sin auth
- [ ] Abrir logs de API: `grep "Dev mode" /tmp/logs/axon-agency-api_*.log | tail -20`
- [ ] Crear un agente desde UI
- [ ] **Resultado esperado:** Log "Dev mode: allowing unauthenticated request"

### Test 5.2: Endpoint POST /api/agent/meta/create
**Objetivo:** Validar creación directa vía API
```bash
curl -X POST http://localhost:8080/api/agent/meta/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agente Test API",
    "role": "security",
    "tenant_id": "tenant_default"
  }'
```
- [ ] **Resultado esperado:** JSON con agent_id, status: "idle", tasks_completed: 0

### Test 5.3: Endpoint GET /api/agent/meta/agents
**Objetivo:** Listar todos los agentes
```bash
curl http://localhost:8080/api/agent/meta/agents | python3 -m json.tool
```
- [ ] **Resultado esperado:** Array con todos los agentes creados

### Test 5.4: Endpoint POST /api/agent/meta/replicate
**Objetivo:** Replicar agente vía API
```bash
curl -X POST http://localhost:8080/api/agent/meta/replicate \
  -H "Content-Type: application/json" \
  -d '{
    "source_agent_id": "agent_tenant_default_security_XXXXX",
    "target_tenant_id": "tenant_default",
    "inherit_training": true
  }'
```
- [ ] **Resultado esperado:** Nuevo agente con agent_id diferente

### Test 5.5: Endpoint DELETE /api/agent/meta/agents/{agent_id}
**Objetivo:** Eliminar agente vía API
```bash
curl -X DELETE http://localhost:8080/api/agent/meta/agents/agent_tenant_default_security_XXXXX
```
- [ ] **Resultado esperado:** {"message": "Agent deleted successfully"}

### Test 5.6: Endpoint GET /api/agent/meta/governance/usage/{tenant_id}
**Objetivo:** Verificar estadísticas de gobernanza
```bash
curl http://localhost:8080/api/agent/meta/governance/usage/tenant_default
```
- [ ] **Resultado esperado:** 
```json
{
  "total_agents": X,
  "active_agents": X,
  "total_tasks": X,
  "overall_success_rate": 0.0,
  "replications_today": X,
  "replications_limit": 3
}
```

---

## ✅ Fase 6: Pruebas de Límites de Gobernanza (10 min)

### Test 6.1: Límite de 10 Agentes por Tenant
- [ ] Crear 10 agentes (mezcla de todos los roles)
- [ ] Intentar crear el agente #11
- [ ] **Resultado esperado:** Error 400 "Agent limit (10) reached for tenant tenant_default"

### Test 6.2: Límite de 3 Replicaciones por Día
- [ ] Replicar 3 agentes diferentes
- [ ] Intentar 4ta replicación
- [ ] **Resultado esperado:** Error 400 "Daily replication limit (3) reached for tenant tenant_default"

### Test 6.3: Límite de 5 Tareas Concurrentes por Agente
**Nota:** Requiere implementación de asignación de tareas (próxima fase)
- [ ] Marcar como prueba futura
- [ ] **Resultado esperado:** Error cuando un agente tiene 5 tareas activas y se le asigna una 6ta

---

## ✅ Fase 7: Pruebas de Persistencia y Logs (10 min)

### Test 7.1: Verificar Persistencia en JSON
**Objetivo:** Validar que los agentes se guardan en archivos
```bash
ls -lh axon-agency/apps/api/data/agents/
cat axon-agency/apps/api/data/agents/agent_tenant_default_security_*.json
```
- [ ] **Resultado esperado:** Archivo JSON por cada agente con toda la metadata

### Test 7.2: Logs de Creación
```bash
grep "Created agent" /tmp/logs/axon-agency-api_*.log | tail -10
```
- [ ] **Resultado esperado:** Log con agent_id y timestamp de creación

### Test 7.3: Logs de Replicación
```bash
grep -i "replicat" /tmp/logs/axon-agency-api_*.log | tail -10
```
- [ ] **Resultado esperado:** Logs de replicaciones con source y target agent_id

### Test 7.4: Logs de Eliminación
```bash
grep -i "delet" /tmp/logs/axon-agency-api_*.log | tail -10
```
- [ ] **Resultado esperado:** Logs de agentes eliminados

---

## ✅ Fase 8: Pruebas de Integración Multi-LLM (20 min)

### Test 8.1: Verificar Integración con Gemini
**Objetivo:** Validar que los agentes pueden usar Gemini API
- [ ] Crear agente PLANNER
- [ ] Verificar que tiene capabilities.llm_providers configurado
- [ ] **Resultado esperado:** "gemini" en lista de providers

### Test 8.2: Verificar Integración con Ollama (Local)
**Objetivo:** Validar que pueden usar Ollama si está disponible
- [ ] Verificar variable de entorno: `echo $OLLAMA_API_URL`
- [ ] Crear agente BUILDER
- [ ] **Resultado esperado:** "ollama" en capabilities si URL configurada

### Test 8.3: Asignación Inteligente de LLM por Rol
**Objetivo:** Verificar que cada rol tiene su provider preferido
- [ ] SECURITY → Gemini (razonamiento profundo)
- [ ] PERFORMANCE → Ollama local (rápido)
- [ ] QA → Gemini (análisis detallado)
- [ ] BUILDER → Ollama (generación rápida)
- [ ] **Resultado esperado:** Campo "preferred_provider" en capabilities

---

## 📊 Criterios de Éxito

### ✅ Funcionalidad Core
- [ ] 100% de los agentes se crean correctamente
- [ ] 100% de las replicaciones funcionan
- [ ] 100% de las eliminaciones completan sin errores
- [ ] 0 errores de compilación en frontend
- [ ] 0 errores 500 en backend

### ✅ UX/UI
- [ ] Toasts NO bloquean capturas de pantalla
- [ ] Modales NO usan alert/confirm nativos
- [ ] Auto-refresh funciona cada 5 segundos
- [ ] Todos los iconos de rol son correctos
- [ ] Badges de color apropiados para cada rol

### ✅ Gobernanza
- [ ] Límite de 10 agentes por tenant se respeta
- [ ] Límite de 3 replicaciones/día se respeta
- [ ] Métricas se actualizan en tiempo real
- [ ] UsageStats refleja estado real del sistema

### ✅ Backend
- [ ] DEV_MODE permite requests sin autenticación
- [ ] Todos los endpoints responden correctamente
- [ ] Persistencia JSON funciona
- [ ] Logs registran todas las operaciones

---

## 🐛 Problemas Conocidos a Verificar

### Issue #1: Tasa de Éxito muestra "NaN%"
- **Causa:** División por cero cuando tasks_completed = 0
- **Fix esperado:** Mostrar "0%" en lugar de "NaN%"
- **Test:** Crear agente nuevo y verificar que muestra "0%"

### Issue #2: last_active muestra fecha inválida
- **Causa:** Campo es null en agentes nuevos
- **Fix esperado:** Mostrar "Nunca" o "-" cuando last_active = null
- **Test:** Verificar que agentes nuevos muestran mensaje apropiado

### Issue #3: Límite de gobernanza no se resetea
- **Causa:** Contador de replicaciones diarias no se resetea a medianoche
- **Fix esperado:** Implementar reset automático o manual
- **Test:** Verificar que hay endpoint para resetear contadores

---

## 📝 Notas de Implementación

### Cambios Recientes
1. ✅ Implementado sistema de Toast notifications (no bloqueante)
2. ✅ Implementado modal de confirmación (no bloqueante)
3. ✅ Conectada funcionalidad de replicación al backend
4. ✅ Reemplazados todos los alert() y confirm() nativos
5. ✅ Mejorado manejo de errores en todas las operaciones

### Archivos Creados
- `axon-agency/apps/web/components/Toast.tsx`
- `axon-agency/apps/web/components/ConfirmModal.tsx`

### Archivos Modificados
- `axon-agency/apps/web/app/agent/meta/page.tsx`

---

## 🚀 Próximos Pasos (Post-Pruebas)

1. **Fase 9: Asignación de Tareas a Agentes**
   - Endpoint POST /api/agent/meta/agents/{agent_id}/tasks
   - UI para asignar tareas
   - Límite de 5 tareas concurrentes

2. **Fase 10: Learning Data y Memoria**
   - Integración con RAG system
   - Persistencia de learning_data_path
   - UI para ver historial de aprendizaje

3. **Fase 11: Métricas Avanzadas**
   - Gráficos de rendimiento por agente
   - Historial de tareas completadas
   - Análisis de éxito/fallo

4. **Fase 12: Multi-Tenant Real**
   - Autenticación JWT habilitada
   - Separación real de tenants
   - Dashboard de admin para gestión global

---

## ✅ Checklist Final

Antes de dar el sistema por completo:

- [ ] Todas las fases de prueba completadas al 100%
- [ ] Todos los criterios de éxito cumplidos
- [ ] Problemas conocidos documentados o resueltos
- [ ] Logs no muestran errores críticos
- [ ] Frontend compila sin warnings
- [ ] Backend responde a todos los endpoints
- [ ] Capturas de pantalla funcionan con toasts visibles
- [ ] Documentación actualizada en replit.md

---

**Estimado Total de Tiempo:** 80-100 minutos (1.5 horas)

**Fecha de Creación:** 13 de Noviembre, 2025
**Última Actualización:** 13 de Noviembre, 2025
**Versión:** 1.0

---

## 💬 Notas Adicionales

Si encuentras algún bug durante las pruebas:

1. **Captura de pantalla** del error (ahora funcional con toasts)
2. **Copia el mensaje de error** exacto del toast
3. **Revisa los logs** del backend:
   ```bash
   tail -100 /tmp/logs/axon-agency-api_*.log
   ```
4. **Comparte** el agent_id del agente problemático si aplica

**¡Vamos a cambiar el mundo con Super Axon Agent!** 🚀
